"""Figuras da Fase 8: dispersão previsto×observado e hidrogramas dos eventos.

Convenções de dataviz: um eixo por gráfico, no máximo 3 séries por painel,
cores categóricas fixas (azul=observado é linha de referência cinza-escura;
previsões nos slots 1-2), cotas de referência como linhas neutras tracejadas,
grade recessiva.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from ..ingest.common import REFERENCE, ROOT

FIGS = ROOT / "reports" / "figs"
PROCESSED = ROOT / "data" / "processed"

# Paleta categórica validada (dataviz skill, tema claro)
AZUL, LARANJA = "#2a78d6", "#eb6834"
TEXTO, TEXTO_2 = "#0b0b0b", "#52514e"
OBS = "#3a3a38"

CODIGO = {"Muçum": 86510000, "Encantado": 86720000, "Estrela": 86879300}
EVENTOS_REF = {
    "ev20230904": "set/2023 (1ª onda)",
    "ev20231113": "nov/2023",
    "ev20240430": "mai/2024",
}


def _estilo(ax):
    ax.grid(True, color="#e6e5e1", linewidth=0.6)
    ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(colors=TEXTO_2, labelsize=8)


def dispersao(preds: pd.DataFrame) -> None:
    """Um arquivo por alvo: 4 painéis (horizontes), GBM, obs×pred."""
    for alvo, g_alvo in preds[preds["variante"] == "gbm"].groupby("alvo"):
        fig, axes = plt.subplots(1, 4, figsize=(13, 3.4), constrained_layout=True)
        for ax, (h, g) in zip(axes, sorted(g_alvo.groupby("h"))):
            ok = g.dropna(subset=["obs", "pred"])
            lim = (0, max(ok["obs"].max(), ok["pred"].max()) * 1.05)
            ax.plot(lim, lim, color="#c9c8c2", linewidth=1, zorder=1)
            ax.scatter(ok["obs"], ok["pred"], s=4, alpha=0.15, color=AZUL,
                       edgecolors="none", zorder=2)
            ax.set_xlim(lim), ax.set_ylim(lim)
            ax.set_title(f"h = {h}h", fontsize=10, color=TEXTO)
            ax.set_xlabel("observado (cm)", fontsize=8, color=TEXTO_2)
            _estilo(ax)
        axes[0].set_ylabel("previsto (cm)", fontsize=8, color=TEXTO_2)
        fig.suptitle(f"{alvo} — GBM, previsto × observado (CV por evento)",
                     fontsize=11, color=TEXTO)
        fig.savefig(FIGS / f"dispersao_{alvo}.png", dpi=150)
        plt.close(fig)


def hidrogramas(preds: pd.DataFrame) -> None:
    """Por evento de referência × alvo: observado + GBM h=6 e h=12,
    plotados no tempo-alvo (t + h) para alinhar com o hidrograma real."""
    cotas = pd.read_csv(REFERENCE / "cotas_referencia.csv").set_index("codigo")
    sel = preds[preds["variante"] == "gbm"]
    for ev, rotulo in EVENTOS_REF.items():
        fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True,
                                 constrained_layout=True)
        for ax, (alvo, codigo) in zip(axes, CODIGO.items()):
            g = sel[(sel["evento"] == ev) & (sel["alvo"] == alvo)]
            if g.empty:
                ax.set_visible(False)
                continue
            def continua(sub: pd.DataFrame, coluna: str, h: int) -> pd.Series:
                """Série no tempo-alvo, reindexada à grade horária contínua:
                lacunas de sensor quebram a linha em vez de virar reta."""
                s = sub.sort_values("ts_utc").set_index(
                    sub.sort_values("ts_utc")["ts_utc"] + pd.Timedelta(hours=h)
                )[coluna]
                s = s[~s.index.duplicated()]
                return s.reindex(pd.date_range(s.index.min(), s.index.max(), freq="h"))

            base = g[g["h"] == 6]
            obs6 = continua(base, "obs", 6)
            ax.plot(obs6.index, obs6, color=OBS, linewidth=2, label="observado")
            pred6 = continua(base, "pred", 6)
            ax.plot(pred6.index, pred6, color=AZUL, linewidth=1.6, label="GBM h=6")
            pred12 = continua(g[g["h"] == 12], "pred", 12)
            ax.plot(pred12.index, pred12, color=LARANJA, linewidth=1.6,
                    label="GBM h=12")
            for nome_cota, estilo in (("alerta_cm", ":"), ("inundacao_cm", "--")):
                ax.axhline(float(cotas.loc[codigo, nome_cota]), color="#a8a7a1",
                           linestyle=estilo, linewidth=1)
            ax.set_title(alvo, fontsize=10, color=TEXTO, loc="left")
            ax.set_ylabel("cota (cm)", fontsize=8, color=TEXTO_2)
            _estilo(ax)
        axes[0].legend(loc="upper right", fontsize=8, frameon=False)
        fig.suptitle(f"Evento {rotulo} — observado × previsto "
                     f"(linhas cinza: alerta ⋯ / inundação − −)",
                     fontsize=11, color=TEXTO)
        fig.savefig(FIGS / f"hidrograma_{ev}.png", dpi=150)
        plt.close(fig)


def run() -> None:
    FIGS.mkdir(parents=True, exist_ok=True)
    preds = pd.read_parquet(PROCESSED / "preds_gbm.parquet")
    dispersao(preds)
    hidrogramas(preds)
    print(f"[figures] figuras em {FIGS}")


if __name__ == "__main__":
    run()
