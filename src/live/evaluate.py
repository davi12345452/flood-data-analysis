"""Comparação cronológica de 6/9/12h, com latência simulada por fonte.

Seleção em eventos de 2023–2025; 2026 reservado para teste posterior.
Executar: uv run python -m src.live.evaluate [--frame caminho.parquet]
"""

from __future__ import annotations

import argparse
import json

import pandas as pd

from ..features.build import montar
from ..ingest.common import ROOT
from .operational import (
    ATRASOS,
    MOTORES,
    dataset_operacional,
    prever_modelo,
    treino_antes,
)

ALVOS = {86510000: ("Muçum", "mu"), 86720000: ("Encantado", "en"),
         86879300: ("Estrela", "es")}
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"


def avaliar(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cotas = pd.read_csv(ROOT / "data/reference/cotas_referencia.csv").set_index("codigo")
    linhas, previsoes = [], []
    for codigo, (nome, ap) in ALVOS.items():
        original = pd.read_parquet(PROCESSED / f"dataset_{codigo}.parquet").set_index("ts_utc")
        ds = dataset_operacional(frame, original, codigo)
        eventos = sorted(ds.loc[(ds.tipo == "evento")
                                & (ds.janela_id >= "ev2023"), "janela_id"].unique())
        for ev in eventos:
            test = ds[ds.janela_id == ev]
            for h in (6, 9, 12):
                train = treino_antes(ds, test.index.min(), h)
                if len(train) < 500:
                    continue
                obs = test[f"y_{h}h"]
                preds = {motor: prever_modelo(train, test, codigo, h, motor)
                         for motor in MOTORES}
                preds["persistencia"] = test[f"nivel_{ap}"]
                tabela = pd.DataFrame(preds)
                comum = tabela.notna().all(axis=1) & obs.notna()
                alto = ((obs >= cotas.loc[codigo, "atencao_cm"])
                        | (test[f"nivel_{ap}"] >= cotas.loc[codigo, "atencao_cm"]))
                for motor, pred in preds.items():
                    for regime, mask in {"todos": comum, "alto": comum & alto,
                                          "subida": comum & alto
                                          & (test[f"dnivel_1h_{ap}"] > 0)}.items():
                        erro = (pred - obs)[mask]
                        linhas.append({"codigo": codigo, "alvo": nome, "evento": ev,
                                       "particao": "selecao" if ev < "ev2026" else "teste",
                                       "h": h, "motor": motor, "regime": regime,
                                       "n": len(erro), "mae_cm": erro.abs().mean(),
                                       "vies_cm": erro.mean(),
                                       "cobertura_pareada": comum.sum() / max(1, obs.notna().sum())})
                    bloco = pd.DataFrame({"t_ref_utc": test.index, "observado_cm": obs.values,
                                          "previsto_cm": pred.values, "pareado": comum.values,
                                          "alto": alto.values})
                    bloco = bloco.assign(codigo=codigo, alvo=nome, evento=ev, h=h, motor=motor)
                    previsoes.append(bloco)
            print(f"[validacao] {nome} {ev}", flush=True)
            pd.DataFrame(linhas).to_csv(PROCESSED / "live_validacao_parcial.csv", index=False)
    return pd.DataFrame(linhas), pd.concat(previsoes, ignore_index=True)


def publicar(metricas: pd.DataFrame, preds: pd.DataFrame) -> None:
    metricas.to_csv(REPORTS / "11_validacao_live_metricas.csv", index=False)
    preds.to_parquet(PROCESSED / "live_validacao_previsoes.parquet", index=False)
    selecao = metricas[(metricas.particao == "selecao") & (metricas.regime == "alto")
                      & (metricas.motor != "persistencia")]
    score = selecao.groupby(["codigo", "h", "motor"]).mae_cm.mean()
    escolhas = []
    for (codigo, h), grupo in score.groupby(level=[0, 1]):
        motor = grupo.idxmin()[2]
        escolhas.append({"codigo": int(codigo), "h": int(h), "motor": motor,
                         "mae_selecao_cm": float(grupo.min())})
    manifesto = {"protocolo": "cronologico_latencia_v1", "atrasos_h": ATRASOS,
                 "selecao": "eventos 2023–2025; MAE médio por evento no regime alto",
                 "teste": "eventos 2026, sem escolher modelo com estes resultados",
                 "modelos": escolhas}
    (REPORTS / "11_live_modelos.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n")
    agregado = metricas.groupby(["particao", "alvo", "h", "motor", "regime"]).agg(
        MAE_cm=("mae_cm", "mean"), vies_cm=("vies_cm", "mean"),
        eventos=("mae_cm", "count"), n=("n", "sum")).reset_index()
    tabela = agregado[agregado.regime == "alto"].drop(columns="regime")
    escolhidos = pd.DataFrame(escolhas)
    teste = metricas[(metricas.particao == "teste") & (metricas.regime == "alto")]
    selecionado = teste.merge(escolhidos[["codigo", "h", "motor"]],
                              on=["codigo", "h", "motor"])
    resumo_teste = selecionado.groupby(["alvo", "h", "motor"]).agg(
        MAE_cm=("mae_cm", "mean"), pior_MAE_evento_cm=("mae_cm", "max"),
        eventos_com_pares=("mae_cm", "count"), pares=("n", "sum")).reset_index()
    texto = """# Validação de previsões de 6, 9 e 12 horas

Todas as previsões partem da cota instantânea em t e apontam para t+h.
Chuva usa features de t−5h, ONS de t−1h, API diário de t−24h e
disponibilidade de sensor de t−1h, tanto no treino quanto na previsão.
Não há preenchimento de lacunas. Atrasos são hipóteses fixas do replay;
não existem arquivos históricos de horário de publicação para comprová-los.
O atraso de transmissão da cota (~15 min na rodada de setembro) também
reduz a antecedência real em relação ao horário nominal da observação.

Treino: somente janelas completas anteriores ao início da janela testada,
com os rótulos também anteriores ao corte. Early stopping apenas no treino.
Comparação nas mesmas horas observáveis para todos os modelos; cobertura
registrada no CSV. Regime alto: cota atual OU futura acima de atenção.
O CSV também contém o regime de subida e o conjunto completo.

Seleção: menor MAE médio por evento em 2023–2025, por estação/horizonte.
Teste separado: eventos de 2026. As médias abaixo dão o mesmo peso a cada
evento; n é a soma dos pares. Eventos sem pares no regime não entram na média.
Persistência mantém a cota atual. Linear usa cota e derivadas próprias e de
montante. GBM nível prevê a cota; GBM delta prevê a variação desde a cota atual.
Nenhum modelo recebe ajuste de viés calculado no evento testado.

O desenvolvimento foi motivado pelo erro já visto em setembro. O replay de
setembro é diagnóstico, não teste cego. A escolha automática usa só 2023–2025.
Estas métricas não validam uso operacional nem estabelecem um teto físico.

## Modelos escolhidos

"""
    texto += escolhidos.round(1).to_markdown(index=False)
    texto += "\n\n## Teste de 2026: modelos escolhidos sem estes eventos\n\n"
    texto += ("Três janelas: janeiro, junho/julho e julho. Janeiro não tem pares "
              "no regime alto em Encantado/Estrela e tem apenas 1–5 em Muçum. "
              "O erro médio por evento deve ser lido junto dessa amostra pequena. "
              "Setembro não está nesta tabela.\n\n")
    texto += resumo_teste.round(1).to_markdown(index=False)
    texto += "\n\n## Comparação no regime alto (cm)\n\n"
    texto += tabela.round(1).to_markdown(index=False)
    texto += ("\n\nReprodução: `uv run python -m src.live.evaluate`. "
              "Métricas detalhadas: [CSV](11_validacao_live_metricas.csv).\n")
    (REPORTS / "11_validacao_live.md").write_text(texto)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame", help="Pool local já montado, opcional")
    args = parser.parse_args()
    frame = pd.read_parquet(args.frame) if args.frame else montar()
    publicar(*avaliar(frame))


if __name__ == "__main__":
    main()
