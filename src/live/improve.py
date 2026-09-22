"""Experimento reproduzível: montante, ajuste causal e faixas empíricas.

Base v2 congelada. Escolha das alterações: eventos 2023–2024. Confirmação e
calibração: 2025. Aceitação: 2026 (já inspecionado; não é teste cego).
"""

from __future__ import annotations

import argparse
import json

import pandas as pd

from ..ingest.common import ROOT
from . import adaptation
from . import operational as op

P = ROOT / "data/processed"
R = ROOT / "reports"
VARIANTES = {"original": (0.0, 6), "meio_6h": (0.5, 6), "integral_6h": (1.0, 6),
             "meio_12h": (0.5, 12), "integral_12h": (1.0, 12)}


def particao(evento: str) -> str:
    return "desenvolvimento" if evento < "ev2025" else (
        "calibracao" if evento < "ev2026" else "teste")


def experimentar(frame: pd.DataFrame) -> pd.DataFrame:
    anteriores = pd.read_parquet(P / "live_validacao_previsoes.parquet")
    modelos = json.loads((R / "11_live_modelos.json").read_text())["modelos"]
    base = {(m["codigo"], m["h"]): m["motor"] for m in modelos}
    partes = []
    for codigo, (nome, ap) in op.ALVOS.items():
        ds = op.dataset_operacional(frame, pd.read_parquet(
            P / f"dataset_{codigo}.parquet").set_index("ts_utc"), codigo)
        for ev in sorted(anteriores.evento.unique()):
            te = ds[ds.janela_id == ev]
            if te.empty:
                continue
            for h in (6, 9, 12):
                tr = op.treino_antes(ds, te.index.min(), h)
                velho = anteriores[(anteriores.codigo == codigo) & (anteriores.evento == ev)
                                    & (anteriores.h == h) & (anteriores.motor == base[codigo, h])]
                velho = velho.set_index("t_ref_utc").reindex(te.index)
                ridge = op.prever_modelo(tr, te, codigo, h, "ridge_montante")
                postos = op.prever_modelo(tr, te, codigo, h, "gbm_postos")
                obs = te[f"y_{h}h"]
                comum = (velho.pareado.fillna(False).astype(bool) & ridge.notna()
                         & postos.notna() & obs.notna())
                velocidade = te[f"dnivel_1h_{ap}"]
                raro = velocidade > tr[f"dnivel_1h_{ap}"].quantile(.99)
                for motor, bruto in {base[codigo, h]: velho.previsto_cm,
                                      "ridge_montante": ridge, "gbm_postos": postos}.items():
                    for ajuste, (ganho, janela) in VARIANTES.items():
                        saida = adaptation.corrigir(bruto, frame[f"nivel_{ap}"], h,
                                                    ganho=ganho, janela_h=janela)
                        saida = saida.assign(
                            observado_cm=obs, pareado=comum, alto=velho.alto.fillna(False),
                            subindo=velocidade > 0, descendo=velocidade < 0,
                            subida_rapida=raro, velocidade_cm_h=velocidade,
                            codigo=codigo, alvo=nome, evento=ev,
                            h=h, motor=motor, ajuste=ajuste, particao=particao(ev))
                        saida["erro_cm"] = saida.previsto_cm - obs
                        partes.append(saida.reset_index(names="t_ref_utc"))
            print(f"[melhoria] {nome} {ev}", flush=True)
    out = pd.concat(partes, ignore_index=True)
    out.to_parquet(P / "live_experimento_previsoes.parquet", index=False)
    return out


def metricas(preds: pd.DataFrame) -> pd.DataFrame:
    grupos = ["codigo", "alvo", "evento", "particao", "h", "motor", "ajuste"]
    partes = []
    for regime, mask in {
        "todos": preds.pareado, "alto": preds.pareado & preds.alto,
        "subida": preds.pareado & preds.alto & preds.subindo,
        "descida": preds.pareado & preds.alto & preds.descendo,
        "rapida": preds.pareado & preds.subida_rapida,
    }.items():
        p = preds[mask].copy()
        p["ae"] = p.erro_cm.abs()
        g = p.groupby(grupos).agg(n=("ae", "size"), mae_cm=("ae", "mean"),
                                  vies_cm=("erro_cm", "mean"), max_erro_cm=("ae", "max"))
        partes.append(g.reset_index().assign(regime=regime))
    return pd.concat(partes, ignore_index=True)


def escolher(m: pd.DataFrame) -> list[dict]:
    """Promove só com ganho >=3% em alta e subida, sem piora >5% na descida.

    Ranking em 2023–2024; confirmação em 2025 e veto por regressão em 2026.
    Empate favorece menor correção; mantém v2 quando não há evidência de ganho.
    """
    base = json.loads((R / "11_live_modelos.json").read_text())["modelos"]
    escolhas = []
    for anterior in base:
        c, h = anterior["codigo"], anterior["h"]
        g = m[(m.codigo == c) & (m.h == h) & (m.particao == "desenvolvimento")]
        tabela = g.groupby(["motor", "ajuste", "regime"]).mae_cm.mean().unstack("regime")
        atual = tabela.loc[(anterior["motor"], "original")]
        elegivel = tabela[(tabela.alto <= atual.alto * .97)
                          & (tabela.subida <= atual.subida * .97)
                          & (tabela.descida <= atual.descida * 1.05)]
        if elegivel.empty:
            motor, ajuste = anterior["motor"], "original"
        else:
            ranking = elegivel.assign(score=(elegivel.alto + elegivel.subida) / 2).reset_index()
            ranking["ganho"] = ranking.ajuste.map(lambda a: VARIANTES[a][0])
            melhor = ranking.sort_values(["score", "ganho", "motor", "ajuste"]).iloc[0]
            motor, ajuste = melhor.motor, melhor.ajuste
        candidato_motor, candidato_ajuste = motor, ajuste
        # Uma única confirmação posterior, sem tentar o segundo colocado
        # quando o primeiro falha. Nunca consulta os erros de 2026 aqui.
        cal = m[(m.codigo == c) & (m.h == h) & (m.particao == "calibracao")]
        ct = cal.groupby(["motor", "ajuste", "regime"]).mae_cm.mean().unstack("regime")
        anterior_cal = ct.loc[(anterior["motor"], "original")]
        candidato_cal = ct.loc[(motor, ajuste)]
        confirmado = bool(candidato_cal.alto <= anterior_cal.alto
                          and candidato_cal.subida <= anterior_cal.subida
                          and candidato_cal.descida <= anterior_cal.descida * 1.05)
        if not confirmado:
            motor, ajuste = anterior["motor"], "original"
        # Aceitação de release: 2026 pode vetar a mudança, nunca escolher uma
        # alternativa. Logo não é avaliação independente do modelo promovido.
        teste = m[(m.codigo == c) & (m.h == h) & (m.particao == "teste")]
        tt = teste.groupby(["motor", "ajuste", "regime"]).mae_cm.mean().unstack("regime")
        antigo_teste = tt.loc[(anterior["motor"], "original")]
        novo_teste = tt.loc[(motor, ajuste)]
        aceito = bool(all(novo_teste[r] <= antigo_teste[r] * 1.05
                          for r in ("alto", "subida", "descida", "rapida")))
        motor_testado, ajuste_testado = motor, ajuste
        if not aceito:
            motor, ajuste = anterior["motor"], "original"
        ganho, janela = VARIANTES[ajuste]
        escolhas.append({"codigo": c, "h": h, "motor": motor, "ajuste": ajuste,
                         "ganho": ganho, "janela_h": janela, "min_amostras": 3,
                         "motor_anterior": anterior["motor"],
                         "candidato_motor": candidato_motor, "candidato_ajuste": candidato_ajuste,
                         "confirmado_2025": confirmado, "motor_testado_2026": motor_testado,
                         "ajuste_testado_2026": ajuste_testado, "aceito_2026": aceito})
    return escolhas


def selecionadas(preds: pd.DataFrame, escolhas: list[dict]) -> pd.DataFrame:
    keys = pd.DataFrame(escolhas)[["codigo", "h", "motor", "ajuste"]]
    return preds.merge(keys, on=["codigo", "h", "motor", "ajuste"])


def calibrar(preds: pd.DataFrame) -> list[dict]:
    """Quantil 90% do erro absoluto em 2025; mínimo 30 pares por regime.

    Sem amostra mínima no regime, não publica faixa. A faixa é empírica:
    dependência temporal e mudança de regime impedem
    prometer cobertura de 90%. Teste de cobertura é separado, em 2026.
    """
    cal = preds[(preds.particao == "calibracao") & preds.pareado]
    linhas = []
    for (codigo, h), g in cal.groupby(["codigo", "h"]):
        for rapido in (False, True):
            amostra = g[g.subida_rapida == rapido]
            origem = "regime" if len(amostra) >= 30 else "amostra_insuficiente"
            largura = (float(amostra.erro_cm.abs().quantile(.9, interpolation="higher"))
                       if len(amostra) >= 30 else None)
            linhas.append({"codigo": int(codigo), "h": int(h), "subida_rapida": rapido,
                           "margem_cm": largura, "n": len(amostra), "origem": origem,
                           "velocidade_max_cm_h": (float(amostra.velocidade_cm_h.max())
                                                    if len(amostra) else None),
                           "velocidade_min_cm_h": (float(amostra.velocidade_cm_h.min())
                                                    if len(amostra) else None)})
    return linhas


def publicar(preds: pd.DataFrame) -> None:
    m = metricas(preds)
    m.to_csv(R / "12_melhoria_metricas.csv", index=False)
    escolhas = escolher(m)
    selecionado = selecionadas(preds, escolhas)
    faixas = calibrar(selecionado)
    manifesto = {"protocolo": "ajuste_causal_v1", "atrasos_h": op.ATRASOS,
                 "desenvolvimento": "2023–2024", "calibracao": "2025", "aceitacao": "2026",
                 "modelos": escolhas, "faixas": faixas}
    (R / "12_live_modelos.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n")
    atual = m.merge(pd.DataFrame(escolhas)[["codigo", "h", "motor", "ajuste"]],
                   on=["codigo", "h", "motor", "ajuste"])
    bases = pd.DataFrame(escolhas)[["codigo", "h", "motor_anterior"]].rename(
        columns={"motor_anterior": "motor"}).assign(ajuste="original")
    antigo = m.merge(bases, on=["codigo", "h", "motor", "ajuste"])
    chaves = ["particao", "alvo", "h", "regime"]
    resumo = atual.groupby(chaves).mae_cm.mean().rename("MAE_novo_cm").to_frame()
    resumo = resumo.join(antigo.groupby(chaves).mae_cm.mean().rename("MAE_anterior_cm"))
    resumo["ganho_pct"] = 100 * (1 - resumo.MAE_novo_cm / resumo.MAE_anterior_cm)
    resumo.reset_index().to_csv(R / "12_melhoria_comparacao.csv", index=False)
    faixas_df = pd.DataFrame(faixas)
    teste = selecionado[(selecionado.particao == "teste") & selecionado.pareado].merge(
        faixas_df, on=["codigo", "h", "subida_rapida"])
    teste["coberto"] = (teste.erro_cm.abs() <= teste.margem_cm).astype(float).where(
        teste.margem_cm.notna())
    cobertura = teste.groupby(["alvo", "h", "subida_rapida"]).agg(
        cobertura=("coberto", "mean"), n=("coberto", "size"),
        n_com_faixa=("coberto", "count"), margem_cm=("margem_cm", "first")).reset_index()
    cobertura.to_csv(R / "12_faixas_cobertura.csv", index=False)
    selecionado.to_parquet(P / "live_melhoria_selecionadas.parquet", index=False)
    texto = """# Melhoria de previsões durante o evento

Foram comparados o modelo da revisão anterior e uma regressão Ridge da
variação de cota usando todas as réguas do subconjunto físico a montante.
Ridge usa alpha=100, padronização só no treino e recorre ao linear anterior
quando faltam réguas adicionais. Nenhuma cota é interpolada.
Também foi testado GBM da variação com acumulados de chuva dos postos ANA
de 1/3/6/12/24h, apenas estações próprias e de montante, com quatro leituras
por hora. A hora corrente nunca entra: usa-se somente chuva de horas completas.
Chuva de posto não substitui a média de bacia; oferece sinal recente adicional.

Para cada modelo, foram testados ajuste desligado ou média dos erros já
observados nas últimas 6/12h, com ganho 0,5/1 e ao menos três pares. O erro
de uma previsão de horizonte h só pode entrar h horas após sua referência.
O ajuste expira se faltarem erros recentes; não atravessa apagões por ffill.

A base v2 foi congelada da revisão anterior (escolhida com 2023–2025).
As alterações são escolhidas em 2023–2024: exigem reduzir MAE médio por
evento em pelo menos 3% no regime alto e na subida, sem piorar a descida em
mais de 5%. O candidato passa por confirmação em 2025: não pode piorar alta
ou subida nem piorar descida em mais de 5%. Se falhar, mantém-se a base, sem
tentar o segundo colocado. 2025 também calibra as faixas, portanto não é
teste independente. Em 2026, uma verificação de aceitação pode VETAR a troca
se o MAE piorar mais de 5% em alta, subida, descida ou subida rápida; não se
busca outro candidato nesse conjunto. Portanto 2026 deixou de ser um teste
independente da versão promovida. Os resultados completos, inclusive os
candidatos rejeitados, estão no CSV. Desenvolvimento iniciado após observar
setembro e 2026: comparação retrospectiva, não teste prospectivo cego.

Faixas: quantil 90% do erro absoluto em 2025, separado por subida rápida
(derivada atual acima do p99 do treino daquele evento) ou demais horas.
Com menos de 30 pares no regime, não se publica faixa para esse regime.
Dependência temporal e mudança de regime impedem garantia de cobertura.
O teste de cobertura em 2026 abaixo mede essa limitação explicitamente.

As métricas de ponto são pareadas nas mesmas horas, com médias por evento.
Regime alto inclui cota atual ou futura acima de atenção; subida/descida
usam a derivada observada na referência. Faixas são avaliadas por hora.

## Configuração escolhida

"""
    texto += pd.DataFrame(escolhas).to_markdown(index=False)
    texto += "\n\n## Versão aceita: comparação retrospectiva em 2026\n\n"
    tabela = resumo.reset_index()
    texto += tabela[(tabela.particao == "teste") & (tabela.regime != "todos")].round(1).to_markdown(index=False)
    texto += "\n\n## Cobertura bruta das faixas em 2026\n\n"
    texto += ("A tabela mede a faixa calibrada antes dos bloqueios de publicação. "
              "Na rodada, faixas também são omitidas fora das velocidades vistas "
              "na calibração ou quando menos de 80% dos últimos erros conhecidos "
              "cabem nas faixas (mínimo três pares nas últimas seis horas). "
              "Isso não corrige a previsão pontual nem cria garantia estatística.\n\n")
    texto += cobertura.round(3).to_markdown(index=False)
    texto += ("\n\nReprodução: `uv run python -m src.live.improve`. "
              "[Métricas por evento](12_melhoria_metricas.csv), "
              "[comparação por partição](12_melhoria_comparacao.csv).\n")
    (R / "12_melhoria_live.md").write_text(texto)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame")
    parser.add_argument("--republicar", action="store_true")
    args = parser.parse_args()
    if args.republicar:
        preds = pd.read_parquet(P / "live_experimento_previsoes.parquet")
    else:
        from ..features.build import montar
        frame = pd.read_parquet(args.frame) if args.frame else montar()
        if not any(c.startswith("posto_") for c in frame):
            from ..features.build import APELIDO_ESTACAO
            from ..features.rain import acumulados_posto
            ana = pd.read_parquet(ROOT / "data/interim/ana_hourly.parquet")
            blocos = [acumulados_posto(ana[ana.codigo == codigo], ap)
                      for codigo, ap in APELIDO_ESTACAO.items() if (ana.codigo == codigo).any()]
            frame = frame.join(pd.concat(blocos, axis=1))
        frame.to_parquet(P / "live_features_postos.parquet")
        preds = experimentar(frame)
    publicar(preds)


if __name__ == "__main__":
    main()
