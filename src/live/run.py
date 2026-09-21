"""Estimativa ao vivo durante um evento em curso.

Difere do pipeline das Fases 6-8 num ponto essencial: não há validação cruzada
porque não há rótulo — o evento ainda não aconteceu. O treino usa TODO o
histórico e o teste é a hora corrente, que por definição nunca esteve no
treino. Em compensação, o único controle de qualidade disponível é o
BACKTEST DO PRÓPRIO EVENTO: previsões emitidas há h horas cujo alvo já foi
observado. É esse viés medido, e não a métrica histórica, que qualifica os
números desta rodada.

Modelo por horizonte, conforme o veredito da Fase 7: regressão linear de lags
em h<=6, LightGBM em h>=12.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from ..eval.figures import AZUL, LARANJA, OBS, TEXTO, TEXTO_2, _estilo
from ..features import build as features_build
from ..ingest.common import REFERENCE, ROOT
from ..models import baselines, gbm
from . import ingest, merge_live

INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"
FIGS = ROOT / "reports" / "figs"

ALVOS = {86510000: ("Muçum", "mu"), 86720000: ("Encantado", "en"),
         86879300: ("Estrela", "es")}
MONTANTES = [(86472000, "jj", "Linha José Julio"), (86472600, "st", "Santa Tereza")]
H_LINEAR, H_GBM = (3, 6), (12, 24)
TZ_LOCAL = "Etc/GMT+3"


def atualizar_fontes() -> None:
    """Busca o que falta em cada fonte e regrava o interim consolidado."""
    ingest.ana_recente().to_parquet(INTERIM / "ana_hourly.parquet", index=False)
    ingest.ons_recente().to_parquet(INTERIM / "ons_hourly.parquet", index=False)
    merge_live.diaria_incremental()
    merge_live.horaria_live(pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=8))


def prever(frame: pd.DataFrame) -> pd.DataFrame:
    """Previsão na hora mais recente com features completas, por alvo/horizonte.

    Cada horizonte tem seu próprio t de referência: as features de chuva têm
    ~5h de latência (MERGE), as de cota têm ~1h. Forçar um t comum jogaria
    fora as horas de cota mais frescas, que são justamente as que sustentam
    o horizonte curto.
    """
    linhas = []
    for codigo, (nome, ap) in ALVOS.items():
        ds = pd.read_parquet(PROCESSED / f"dataset_{codigo}.parquet").set_index("ts_utc")
        for h, motor in [(h, "linear") for h in H_LINEAR] + [(h, "gbm") for h in H_GBM]:
            cols = (baselines._cols_lags(ds, codigo) if motor == "linear"
                    else gbm.colunas_features(ds))
            vivo = frame[cols].dropna()
            if vivo.empty:
                print(f"[live] {nome} h={h} ({motor}): sem linha completa", flush=True)
                continue
            if motor == "linear":
                pred = baselines.regressao_lags(ds, vivo, codigo, h)
            else:
                pred, _ = gbm.treinar_prever(ds, vivo, codigo, h)
            t = vivo.index[-1]
            linhas.append({
                "alvo": nome, "codigo": codigo, "motor": motor, "h": h,
                "t_ref_utc": t, "nivel_em_t": float(frame.loc[t, f"nivel_{ap}"]),
                "previsto_cm": float(pred.loc[t]),
                "valido_para_utc": t + pd.Timedelta(hours=h),
            })
    return pd.DataFrame(linhas)


def backtest_evento(frame: pd.DataFrame, horas: int = 12) -> pd.DataFrame:
    """Previsões das últimas `horas` cujo alvo JÁ foi observado.

    É a única aferição possível durante o evento — e a que importa, porque
    mede o modelo no regime de agora, não no regime médio do histórico.
    """
    linhas = []
    for codigo, (nome, ap) in ALVOS.items():
        ds = pd.read_parquet(PROCESSED / f"dataset_{codigo}.parquet").set_index("ts_utc")
        obs = frame[f"nivel_{ap}"]
        for h, motor in [(h, "linear") for h in H_LINEAR] + [(h, "gbm") for h in H_GBM]:
            cols = (baselines._cols_lags(ds, codigo) if motor == "linear"
                    else gbm.colunas_features(ds))
            vivo = frame[cols].dropna()
            if vivo.empty:
                continue
            if motor == "linear":
                pred = baselines.regressao_lags(ds, vivo, codigo, h)
            else:
                pred, _ = gbm.treinar_prever(ds, vivo, codigo, h)
            for t in vivo.index[-horas:]:
                alvo_t = t + pd.Timedelta(hours=h)
                if alvo_t in obs.index and pd.notna(obs.loc[alvo_t]) and pd.notna(pred.loc[t]):
                    linhas.append({
                        "alvo": nome, "motor": motor, "h": h, "emitido_em": t,
                        "valido_para": alvo_t, "previsto_cm": float(pred.loc[t]),
                        "observado_cm": float(obs.loc[alvo_t]),
                        "erro_cm": float(pred.loc[t] - obs.loc[alvo_t]),
                    })
    return pd.DataFrame(linhas)


def aplicar_vies(prev: pd.DataFrame, bt: pd.DataFrame) -> pd.DataFrame:
    """Soma à previsão o viés médio medido no evento para o mesmo alvo/horizonte.

    Correção aritmética sobre poucas amostras, NÃO um modelo: serve para
    dimensionar o erro sistemático que o backtest revelou, não para substituir
    a previsão. Sem amostra suficiente, devolve NaN em vez de fingir precisão.
    """
    if bt.empty:
        prev["vies_cm"] = pd.NA
        prev["corrigido_cm"] = pd.NA
        return prev
    vies = bt.groupby(["alvo", "h"]).agg(vies_cm=("erro_cm", "mean"),
                                         n_amostras=("erro_cm", "size")).reset_index()
    vies.loc[vies["n_amostras"] < 3, "vies_cm"] = pd.NA
    out = prev.merge(vies, on=["alvo", "h"], how="left")
    out["corrigido_cm"] = out["previsto_cm"] - out["vies_cm"]
    return out


def figura(frame: pd.DataFrame, prev: pd.DataFrame, horas: int = 36) -> None:
    """Painel do evento: chuva, defluência CERAN e um hidrograma por alvo."""
    cotas = pd.read_csv(REFERENCE / "cotas_referencia.csv").set_index("codigo")
    fim = frame.index.max()
    jan = frame.loc[fim - pd.Timedelta(hours=horas):]
    loc = lambda s: s.tz_convert(TZ_LOCAL)

    # sharex deliberado: com o eixo comum, a defasagem de cada fonte (MERGE ~5h,
    # ONS ~1h, ANA ~0h) aparece como o vazio à direita de cada painel — é a
    # informação que decide em qual horizonte dá para confiar.
    fig, axes = plt.subplots(5, 1, figsize=(11, 14), sharex=True,
                             constrained_layout=True,
                             gridspec_kw={"height_ratios": [1, 1, 1.4, 1.4, 1.4]})

    ax = axes[0]
    chuva = jan["chuva_antas_1h"].dropna()
    ax.bar(loc(chuva.index), chuva.values, width=0.035, color=AZUL)
    ax.set_ylabel("chuva Antas\n(mm/h)", fontsize=8, color=TEXTO_2)
    ax.set_title("Chuva média na bacia do rio das Antas (MERGE/CPTEC)",
                 fontsize=9, color=TEXTO, loc="left")
    _estilo(ax)

    ax = axes[1]
    for col, rotulo, cor in [("defluente_qj", "14 de Julho", AZUL),
                             ("defluente_ca", "Castro Alves", LARANJA),
                             ("defluente_mc", "Monte Claro", OBS)]:
        if col in jan:
            s = jan[col].dropna()
            ax.plot(loc(s.index), s.values, color=cor, linewidth=1.6, label=rotulo)
    ax.set_ylabel("defluência\n(m³/s)", fontsize=8, color=TEXTO_2)
    ax.set_title("Defluência das UHEs da CERAN (ONS)", fontsize=9, color=TEXTO, loc="left")
    ax.legend(fontsize=8, frameon=False, loc="upper left")
    _estilo(ax)

    for ax, (codigo, (nome, ap)) in zip(axes[2:], ALVOS.items()):
        s = jan[f"nivel_{ap}"].dropna()
        ax.plot(loc(s.index), s.values, color=OBS, linewidth=2, label="observado")
        g = prev[prev["alvo"] == nome]
        for motor, cor, rotulo in [("linear", AZUL, "linear h=3/6"),
                                   ("gbm", LARANJA, "GBM h=12/24")]:
            gm = g[g["motor"] == motor].sort_values("h")
            if gm.empty:
                continue
            t0 = gm["t_ref_utc"].iloc[0]
            xs = [t0] + list(gm["valido_para_utc"])
            ys = [gm["nivel_em_t"].iloc[0]] + list(gm["previsto_cm"])
            ax.plot([loc(pd.Timestamp(x)) for x in xs], ys, color=cor, linewidth=1.6,
                    linestyle="--", marker="o", markersize=4, label=rotulo)
            if gm["corrigido_cm"].notna().any():
                gc = gm[gm["corrigido_cm"].notna()]
                ax.plot([loc(pd.Timestamp(x)) for x in gc["valido_para_utc"]],
                        gc["corrigido_cm"], color=cor, linewidth=1, linestyle=":",
                        marker="x", markersize=5, alpha=0.8,
                        label=f"{rotulo.split()[0]} + viés do evento")
        for nome_cota, estilo in (("alerta_cm", ":"), ("inundacao_cm", "--")):
            y = float(cotas.loc[codigo, nome_cota])
            ax.axhline(y, color="#a8a7a1", linestyle=estilo, linewidth=1)
            ax.annotate(nome_cota.replace("_cm", ""), (0.995, y), xycoords=("axes fraction", "data"),
                        fontsize=7, color="#8a8984", ha="right", va="bottom")
        ax.set_title(nome, fontsize=10, color=TEXTO, loc="left")
        ax.set_ylabel("cota (cm)", fontsize=8, color=TEXTO_2)
        ax.legend(fontsize=7, frameon=False, loc="upper left")
        _estilo(ax)

    for ax in axes:
        ax.axvline(loc(fim), color="#c9c8c2", linewidth=1)
    axes[0].annotate("última cota observada", (loc(fim), 1.02), xycoords=("data", "axes fraction"),
                     fontsize=7, color="#8a8984", ha="right")
    axes[-1].set_xlabel("horário local (UTC-3)", fontsize=8, color=TEXTO_2)
    fig.suptitle(
        f"Taquari — evento em curso, rodada de {loc(fim):%d/%m/%Y %H:%M} local",
        fontsize=12, color=TEXTO)
    FIGS.mkdir(parents=True, exist_ok=True)
    destino = FIGS / f"live_{fim:%Y%m%d_%H}.png"
    fig.savefig(destino, dpi=150)
    plt.close(fig)
    print(f"[live] figura em {destino}", flush=True)
    return destino


def run(atualizar: bool = True) -> None:
    if atualizar:
        atualizar_fontes()
    frame = features_build.montar()
    prev = prever(frame)
    bt = backtest_evento(frame)
    prev = aplicar_vies(prev, bt)
    destino = figura(frame, prev, horas=36)

    prev.to_parquet(PROCESSED / "live_previsoes.parquet", index=False)
    bt.to_parquet(PROCESSED / "live_backtest.parquet", index=False)
    print()
    print(prev.to_string(index=False))
    print()
    print(bt.assign(ae=bt["erro_cm"].abs())
          .groupby(["alvo", "motor", "h"])
          .agg(MAE_cm=("ae", "mean"), vies_cm=("erro_cm", "mean"), n=("ae", "size"))
          .round(1).to_string())
    return prev, bt, destino


if __name__ == "__main__":
    import sys
    run(atualizar="--sem-atualizar" not in sys.argv)
