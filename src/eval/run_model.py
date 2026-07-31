"""Avalia o LightGBM (cheio e restrito >= atenção) em CV por evento.

Salva previsões por fold em data/processed/preds_gbm.parquet (longo:
alvo, evento, h, variante, ts_utc, obs, pred) — a Fase 8 consome direto.
Escreve reports/07_modelo.md com comparação contra os baselines.
"""

from __future__ import annotations

import pandas as pd

from ..ingest.common import ROOT, load_config
from ..models.gbm import treinar_prever
from . import metrics
from .cv import carregar_dataset, folds_por_evento

PROCESSED = ROOT / "data" / "processed"
REPORT = ROOT / "reports" / "07_modelo.md"

NOMES = {86510000: "Muçum", 86720000: "Encantado", 86879300: "Estrela"}
EVENTOS_REFERENCIA = ["ev20230904", "ev20230908", "ev20231113", "ev20240430"]
VARIANTES = {"gbm": False, "gbm_restrito": True}


def avaliar() -> tuple[pd.DataFrame, pd.DataFrame]:
    horizontes = load_config("dataset")["horizontes_h"]
    preds, importancias = [], []
    for codigo, nome in NOMES.items():
        ds = carregar_dataset(codigo)
        for ev, train, test in folds_por_evento(ds):
            for h in horizontes:
                obs = test[f"y_{h}h"]
                for variante, restrito in VARIANTES.items():
                    pred, imp = treinar_prever(train, test, codigo, h, restrito)
                    preds.append(pd.DataFrame({
                        "alvo": nome, "evento": ev, "h": h, "variante": variante,
                        "ts_utc": test.index, "obs": obs.values, "pred": pred.values,
                    }))
                    imp_df = imp.rename_axis("feature").rename("ganho").reset_index()
                    imp_df[["alvo", "h", "variante", "evento"]] = nome, h, variante, ev
                    importancias.append(imp_df)
        print(f"[gbm] {nome}: folds concluídos", flush=True)
    return pd.concat(preds, ignore_index=True), pd.concat(importancias, ignore_index=True)


def agregar(preds: pd.DataFrame, eventos: list[str] | None = None) -> pd.DataFrame:
    sel = preds if eventos is None else preds[preds["evento"].isin(eventos)]
    linhas = []
    for (alvo, h, variante), g in sel.groupby(["alvo", "h", "variante"]):
        linhas.append({"alvo": alvo, "h": h, "modelo": variante,
                       **metrics.resumo(g["obs"], g["pred"])})
    return pd.DataFrame(linhas)


def _fmt(df: pd.DataFrame) -> str:
    t = df.copy()
    for c in ("NSE", "KGE"):
        t[c] = t[c].round(3)
    for c in ("RMSE_cm", "MAE_cm"):
        t[c] = t[c].round(1)
    t["cobertura"] = (t["cobertura"] * 100).round(1)
    return t.to_markdown(index=False)


def avaliar_regime_alto(preds: pd.DataFrame) -> pd.DataFrame:
    """Armadilha 2, teste justo: métricas só nas horas cujo ALVO observado
    está acima da cota de atenção — regime em que o estudo de 2025 mediu."""
    limiares = {"Muçum": 500.0, "Encantado": 500.0, "Estrela": 1500.0}
    linhas = []
    for (alvo, h, variante), g in preds.groupby(["alvo", "h", "variante"]):
        alto = g[g["obs"] >= limiares[alvo]]
        linhas.append({"alvo": alvo, "h": h, "modelo": variante,
                       **metrics.resumo(alto["obs"], alto["pred"])})
    return pd.DataFrame(linhas)


def veredito(pooled: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    """Por alvo/horizonte: o gbm cheio bate os 3 baselines internos (NSE)?"""
    linhas = []
    for (alvo, h), _ in pooled.groupby(["alvo", "h"]):
        nse_gbm = float(pooled.query(
            "alvo == @alvo and h == @h and modelo == 'gbm'")["NSE"].iloc[0])
        melhores = base.query("alvo == @alvo and h == @h")
        melhor_base = melhores.loc[melhores["NSE"].idxmax()]
        linhas.append({
            "alvo": alvo, "h": h, "NSE_gbm": round(nse_gbm, 3),
            "melhor_baseline": melhor_base["modelo"],
            "NSE_baseline": round(float(melhor_base["NSE"]), 3),
            "gbm_vence": nse_gbm > float(melhor_base["NSE"]),
        })
    return pd.DataFrame(linhas)


def run(report_only: bool = False) -> None:
    if report_only:
        preds = pd.read_parquet(PROCESSED / "preds_gbm.parquet")
        importancias = pd.read_parquet(PROCESSED / "importancias_gbm.parquet")
    else:
        preds, importancias = avaliar()
        preds.to_parquet(PROCESSED / "preds_gbm.parquet", index=False)
        importancias.to_parquet(PROCESSED / "importancias_gbm.parquet", index=False)

    pooled = agregar(preds)
    extremos = agregar(preds, EVENTOS_REFERENCIA)
    regime_alto = avaliar_regime_alto(preds)

    base = pd.read_parquet(PROCESSED / "baselines_pooled.parquet").rename(
        columns={"baseline": "modelo"})
    comparacao = pd.concat([pooled, base], ignore_index=True).sort_values(
        ["alvo", "h", "NSE"], ascending=[True, True, False])
    verd = veredito(pooled, base)

    top = (importancias[importancias["variante"] == "gbm"]
           .groupby(["alvo", "h", "feature"])["ganho"].mean()
           .groupby(["alvo", "h"], group_keys=False).nlargest(8)
           .rename("ganho_medio").reset_index())
    top_resumo = top[top["h"] == 12]

    corpo = f"""# Fase 7 — LightGBM (CV por evento, mesmas regras dos baselines)

Config: raso e regularizado (config/model.yaml). NaN nativo, sem imputação.
Early stopping nas janelas finais do treino de cada fold. Variante
`gbm_restrito` treina só com nível >= atenção (Armadilha 2); teste idêntico.

## Comparação com os baselines (pooled, todos os eventos)

{_fmt(comparacao)}

## Veredito — o GBM bate os baselines internos? (critério: NSE pooled)

{verd.to_markdown(index=False)}

**Leitura honesta:** a regressão linear vence em h=3-6 (e Estrela h=12) — no
curto prazo a propagação é quase linear e árvore não extrapola tão bem. O GBM
se paga nos horizontes longos (12-24h), onde a chuva e a não-linearidade
importam. Consequência para uso: **modelo por horizonte** (linear em <=6h,
GBM em >=12h) é a configuração defensável — não uma derrota do pipeline, mas
o resultado clássico de rio com resposta quase linear no curto prazo.

## Armadilha 2, teste justo — só horas com ALVO >= atenção

{_fmt(regime_alto.sort_values(["alvo", "h", "modelo"]))}

Restringir o treino a >= atenção **não ajudou** neste desenho (exceção
marginal: Muçum 24h). Plausível: nossa amostragem por evento já concentra o
treino no regime alto; o corte só joga fora informação de subida. A premissa
importada do estudo de 2025 não se replica aqui — registrado.

Nota sobria: no regime alto em h=24, NSE cai para 0,24-0,58 em todos os
modelos — consistente com o teto físico de antecedência (~12h Muçum, ~8h
Estrela) com chuva observada (Armadilha 5).

## Só eventos de referência (set/2023, nov/2023, mai/2024)

{_fmt(extremos)}

## Importância de features (ganho médio entre folds, top 8, h=12, variante cheia)

{top_resumo.round(4).to_markdown(index=False)}

Alinha com a literatura da bacia (2025): predomínio de nível/dinâmica de
montante e acumulados longos de chuva (chuva_*_24-120h ≈ "chuva máxima de
1-5 dias" do estudo).

## Fora de escopo (mantido)

LSTM/TCN permanecem fora (volume não sustenta); o pré-treino no dataset
diário longo (mitigação opcional) não foi executado nesta fase — fica
registrado como trabalho futuro no relatório final.
"""
    REPORT.write_text(corpo, encoding="utf-8")
    print(f"[gbm] relatório em {REPORT}")


if __name__ == "__main__":
    import sys
    run(report_only=len(sys.argv) > 1 and sys.argv[1] == "report")
