"""Fase 8 — avaliação completa a partir das previsões salvas (sem retreinar).

Produz reports/08_avaliacao.md com:
- detecção de ultrapassagem da cota de inundação (POD/FAR/CSI/viés)
- erro de valor e tempo de pico, evento a evento (com cobertura no pico)
- comparação justa com o SACE (mesmas horas de emissão)
- referências às figuras (dispersão, hidrogramas)
"""

from __future__ import annotations

import pandas as pd

from ..ingest.common import REFERENCE, ROOT
from . import metrics
from .detection import deteccao, pico_por_evento

PROCESSED = ROOT / "data" / "processed"
INTERIM = ROOT / "data" / "interim"
REPORT = ROOT / "reports" / "08_avaliacao.md"

CODIGO = {"Muçum": 86510000, "Encantado": 86720000, "Estrela": 86879300}
EVENTOS_REF = ["ev20230904", "ev20230908", "ev20231113", "ev20240430"]


def carregar_preds() -> pd.DataFrame:
    gbm = pd.read_parquet(PROCESSED / "preds_gbm.parquet")
    base = pd.read_parquet(PROCESSED / "preds_baselines.parquet")
    return pd.concat([gbm, base], ignore_index=True)


def tabela_deteccao(preds: pd.DataFrame, cotas: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for (alvo, h, var), g in preds.groupby(["alvo", "h", "variante"]):
        if var not in ("gbm", "regressao_lags", "persistencia"):
            continue
        limiar = float(cotas.loc[CODIGO[alvo], "inundacao_cm"])
        linhas.append({"alvo": alvo, "h": h, "modelo": var,
                       **deteccao(g["obs"], g["pred"], limiar)})
    return pd.DataFrame(linhas)


def tabela_picos(preds: pd.DataFrame, cotas: pd.DataFrame,
                 so_referencia: bool = False) -> pd.DataFrame:
    sel = preds[preds["variante"].isin(["gbm", "regressao_lags"])]
    if so_referencia:
        sel = sel[sel["evento"].isin(EVENTOS_REF)]
    linhas = []
    for (alvo, ev, h, var), g in sel.groupby(["alvo", "evento", "h", "variante"]):
        atencao = float(cotas.loc[CODIGO[alvo], "atencao_cm"])
        r = pico_por_evento(g)
        if r is None or r["pico_obs_cm"] < atencao:
            continue  # pico abaixo da atenção não é pico de interesse
        linhas.append({"alvo": alvo, "evento": ev, "h": h, "modelo": var, **r})
    return pd.DataFrame(linhas)


def resumo_picos(picos: pd.DataFrame) -> pd.DataFrame:
    return (picos.groupby(["alvo", "h", "modelo"])
            .agg(n_eventos=("evento", "nunique"),
                 vies_valor_cm=("erro_valor_pico_cm", "mean"),
                 mae_valor_cm=("erro_valor_pico_cm", lambda s: s.abs().mean()),
                 mae_tempo_h=("erro_tempo_pico_h", lambda s: s.abs().mean()),
                 cobertura_pico=("cobertura_pico", "mean"))
            .round(2).reset_index())


def sace_justo(preds: pd.DataFrame) -> pd.DataFrame:
    """Modelo × SACE nas MESMAS horas de emissão: SACE h=4 vs modelo h=3
    (vantagem SACE) e h=6 vs h=6."""
    prev = pd.read_parquet(INTERIM / "sace_previsoes.parquet")
    prev = prev[prev["horizonte_h"].notna()]
    inv_cod = {v: k for k, v in CODIGO.items()}
    prev["alvo"] = prev["codigo"].map(inv_cod)
    prev = prev.dropna(subset=["alvo"])
    pares = {4: 3, 6: 6}

    linhas = []
    for (alvo, hz), g_sace in prev.groupby(["alvo", "horizonte_h"]):
        h_modelo = pares.get(int(hz))
        if h_modelo is None:
            continue
        ana_obs = g_sace.set_index(g_sace["referencia_utc"].dt.round("h"))["prevista_cm"]
        for var in ("gbm", "regressao_lags"):
            g_m = preds[(preds["alvo"] == alvo) & (preds["h"] == h_modelo)
                        & (preds["variante"] == var)]
            g_m = g_m.drop_duplicates(subset="ts_utc").set_index("ts_utc")
            comum = ana_obs.index.intersection(g_m.index)
            if len(comum) < 5:
                continue
            obs = g_m.loc[comum, "obs"]
            linhas.append({
                "alvo": alvo, "h_sace": int(hz), "h_modelo": h_modelo,
                "modelo": var, "n_pareado": len(comum),
                "MAE_modelo_cm": metrics.mae(obs, g_m.loc[comum, "pred"]),
                "MAE_sace_cm": metrics.mae(obs, ana_obs.loc[comum]),
            })
    return pd.DataFrame(linhas).round(1)


def _fmt(df: pd.DataFrame, casas: int = 3) -> str:
    return df.round(casas).to_markdown(index=False)


def run() -> None:
    cotas = pd.read_csv(REFERENCE / "cotas_referencia.csv").set_index("codigo")
    preds = carregar_preds()

    det = tabela_deteccao(preds, cotas)
    picos = tabela_picos(preds, cotas)
    picos_ref = tabela_picos(preds, cotas, so_referencia=True)
    comparacao_sace = sace_justo(preds)

    picos.to_parquet(PROCESSED / "picos_por_evento.parquet", index=False)

    corpo = f"""# Fase 8 — Avaliação completa

Fonte: previsões por fold da CV por evento (Fases 6-7), sem retreino.
Figuras: `figs/dispersao_*.png` (previsto×observado por horizonte) e
`figs/hidrograma_ev*.png` (eventos de referência com previsão sobreposta).

## Detecção de ultrapassagem da cota de inundação (hora a hora)

POD = acertos/(acertos+perdas); FAR = falsos/(alarmes); CSI combina ambos;
viés >1 = alarmista, <1 = conservador. `horas_obs_acima` mostra o quão raro é
o que se tenta detectar.

{_fmt(det)}

## Erro de pico, evento a evento (picos ≥ cota de atenção)

Resumo (média entre eventos; `vies_valor` <0 = subestima o pico — o erro que
mata; `cobertura_pico` <1 = sensor falhou perto do pico e o número mede menos
do que parece — Armadilha 0):

{_fmt(resumo_picos(picos))}

### Só os eventos de referência (set/2023, nov/2023, mai/2024)

{_fmt(resumo_picos(picos_ref))}

Detalhe por evento em `data/processed/picos_por_evento.parquet`.

## Modelo × SACE nas mesmas horas de emissão

Comparação pareada: mesmas horas de referência dos boletins (2022+). SACE
h=4 contra modelo h=3 (vantagem para o SACE) e h=6 contra h=6. MAE contra a
mesma observação.

{_fmt(comparacao_sace)}

## Ressalvas de leitura (obrigatórias)

1. **Cobertura no pico**: onde `cobertura_pico` < 0,9, o erro de pico está
   calculado sobre um pico possivelmente truncado pelo sensor. Em mai/2024
   isso atinge Encantado e Estrela em cheio.
2. **Detecção**: com poucas horas acima da inundação em CV, POD/FAR têm
   variância alta; leia com o `horas_obs_acima` ao lado.
3. **Curva-chave**: tudo aqui é cota, nunca vazão (Armadilha 1).
"""
    REPORT.write_text(corpo, encoding="utf-8")
    print(f"[full_eval] relatório em {REPORT}")


if __name__ == "__main__":
    run()
