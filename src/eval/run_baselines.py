"""Executa os baselines 1-3 em validação cruzada por evento e escreve
reports/06_baselines.md. O baseline 4 (SACE) entra pelo módulo
src.ingest.sace_forecasts e é anexado ao relatório.
"""

from __future__ import annotations

import pandas as pd

from ..ingest.common import ROOT, load_config
from ..models import baselines
from . import metrics
from .cv import carregar_dataset, folds_por_evento

REPORT = ROOT / "reports" / "06_baselines.md"
PROCESSED = ROOT / "data" / "processed"

NOMES = {86510000: "Muçum", 86720000: "Encantado", 86879300: "Estrela"}
EVENTOS_REFERENCIA = ["ev20230904", "ev20230908", "ev20231113", "ev20240430"]

BASELINES = {
    "persistencia": lambda tr, te, cod, h: baselines.persistencia(te, cod, h),
    "regressao_lags": baselines.regressao_lags,
    "propagacao": baselines.propagacao,
}


def avaliar_alvo(codigo: int, horizontes: list[int]) -> pd.DataFrame:
    ds = carregar_dataset(codigo)
    linhas = []
    for ev, train, test in folds_por_evento(ds):
        for h in horizontes:
            obs = test[f"y_{h}h"]
            for nome, fn in BASELINES.items():
                pred = fn(train, test, codigo, h)
                linhas.append({
                    "alvo": NOMES[codigo], "evento": ev, "h": h,
                    "baseline": nome, "obs": obs, "pred": pred,
                })
    return pd.DataFrame(linhas)


def agregar(resultados: pd.DataFrame, so_eventos: list[str] | None = None) -> pd.DataFrame:
    """Métricas pooled: concatena obs/pred de todos os folds e calcula uma vez."""
    sel = resultados
    if so_eventos is not None:
        sel = resultados[resultados["evento"].isin(so_eventos)]
    linhas = []
    for (alvo, h, nome), grupo in sel.groupby(["alvo", "h", "baseline"]):
        obs = pd.concat(list(grupo["obs"]))
        pred = pd.concat(list(grupo["pred"]))
        linhas.append({"alvo": alvo, "h": h, "baseline": nome,
                       **metrics.resumo(obs, pred)})
    return pd.DataFrame(linhas)


def run() -> None:
    horizontes = load_config("dataset")["horizontes_h"]
    todos = []
    for codigo in NOMES:
        print(f"[baselines] avaliando {NOMES[codigo]}...", flush=True)
        todos.append(avaliar_alvo(codigo, horizontes))
    resultados = pd.concat(todos, ignore_index=True)

    pooled = agregar(resultados)
    extremos = agregar(resultados, EVENTOS_REFERENCIA)
    pooled.to_parquet(PROCESSED / "baselines_pooled.parquet", index=False)
    extremos.to_parquet(PROCESSED / "baselines_extremos.parquet", index=False)

    # Previsões em formato longo para a Fase 8 (hidrogramas, picos)
    longos = []
    for _, r in resultados.iterrows():
        longos.append(pd.DataFrame({
            "alvo": r["alvo"], "evento": r["evento"], "h": r["h"],
            "variante": r["baseline"], "ts_utc": r["obs"].index,
            "obs": r["obs"].values, "pred": r["pred"].values,
        }))
    pd.concat(longos, ignore_index=True).to_parquet(
        PROCESSED / "preds_baselines.parquet", index=False)

    def tabela(df: pd.DataFrame) -> str:
        t = df.copy()
        for c in ("NSE", "KGE"):
            t[c] = t[c].round(3)
        for c in ("RMSE_cm", "MAE_cm"):
            t[c] = t[c].round(1)
        t["cobertura"] = (t["cobertura"] * 100).round(1)
        return t.to_markdown(index=False)

    corpo = f"""# Fase 6 — Baselines (validação cruzada por evento)

Protocolo: fold = evento (59 folds), treino = demais janelas, métricas pooled
sobre todos os folds. `cobertura` = fração de pares obs/pred válidos — onde é
baixa, a métrica mede só o caso fácil (Armadilha 0).

Baselines: **persistencia** (cota atual se mantém), **regressao_lags** (linear
com nível e derivadas da própria estação e do montante imediato),
**propagacao** (montante deslocado pelo tempo de viagem estimado no treino,
reescalado linearmente). O benchmark externo (SACE) está na seção final.

## Métricas pooled — todos os eventos

{tabela(pooled)}

## Só os eventos de referência (set/2023, nov/2023, mai/2024)

{tabela(extremos)}

## Leitura

Os números que o modelo da Fase 7 precisa bater, por alvo e horizonte, são o
MELHOR baseline de cada linha — tipicamente persistência em h=3 e
regressão/propagação em h=12-24.
"""
    REPORT.write_text(corpo, encoding="utf-8")
    print(f"[baselines] relatório em {REPORT}")


if __name__ == "__main__":
    run()
