"""Previsto × observado da cheia de 21–22/09/2026.

Confere cada estimativa publicada durante o evento contra a cota que a ANA
mediu depois. Só entram números que já estavam gravados antes da observação:
a rodada original das 18h, o replay revisado publicado às 19:27 e as emissões
arquivadas em ``data/processed/live_runs/emissao_*``. Nada é recalculado.
"""

from __future__ import annotations

import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from ..eval.figures import AZUL, LARANJA, OBS, TEXTO, TEXTO_2, _estilo
from ..ingest.common import REFERENCE, ROOT
from .operational import ALVOS

PROCESSED = ROOT / "data" / "processed"
FIGS = ROOT / "reports" / "figs"
TZ_LOCAL = "Etc/GMT+3"
INICIO_EVENTO = pd.Timestamp("2026-09-21 03:00", tz="UTC")  # 00:00 local

# A rodada original das 18h antecede o registro por execução; o horário é o
# de gravação do arquivo publicado no commit f9cb0f8 (19:07 local).
EMITIDO_18H_UTC = pd.Timestamp("2026-09-21 22:07", tz="UTC")
# O replay v2 foi publicado no mesmo commit das 21h, mas gerado às 19:27 local.
GERADO_V2_UTC = pd.Timestamp("2026-09-21 22:27", tz="UTC")

COLUNAS = ["emissao", "tipo", "alvo", "codigo", "motor", "h", "t_ref_utc", "emitido_em_utc",
           "valido_para_utc", "antecedencia_real_h", "previsto_cm", "corrigido_cm",
           "observado_cm", "erro_cm", "erro_corrigido_cm", "status"]


def carregar_publicadas() -> pd.DataFrame:
    """Reúne o que foi publicado durante o evento, com horário de emissão explícito."""
    partes = []
    p18 = pd.read_parquet(PROCESSED / "live_previsoes.parquet")
    p18["emissao"], p18["tipo"] = "18h original", "emissao"
    p18["emitido_em_utc"] = EMITIDO_18H_UTC
    partes.append(p18)

    v2 = pd.read_parquet(PROCESSED / "live_v2_previsoes.parquet")
    v2["emissao"], v2["tipo"] = "18h revisada (replay 19:27)", "replay"
    v2["emitido_em_utc"] = GERADO_V2_UTC
    partes.append(v2)

    for arquivo in sorted((PROCESSED / "live_runs").glob("emissao_*/previsoes.parquet")):
        p = pd.read_parquet(arquivo)
        p = p[p["modo"] == "emissao"].copy()
        if p.empty:
            continue
        rotulo = p["t_ref_utc"].max().tz_convert(TZ_LOCAL).strftime("%d/%m %Hh")
        p["emissao"], p["tipo"] = f"{rotulo} (emissão)", "emissao"
        partes.append(p)

    todas = pd.concat(partes, ignore_index=True, sort=False)
    todas = todas[todas["codigo"].isin(ALVOS)]
    if "corrigido_cm" not in todas:
        todas["corrigido_cm"] = float("nan")
    todas["antecedencia_real_h"] = (
        (todas["valido_para_utc"] - todas["emitido_em_utc"]).dt.total_seconds() / 3600)
    return todas


def parear(publicadas: pd.DataFrame, frame: pd.DataFrame, agora: pd.Timestamp) -> pd.DataFrame:
    """Casa cada previsão com a cota observada na validade. Sem observação, fica pendente."""
    out = publicadas.copy()
    obs = []
    for p in out.itertuples(index=False):
        serie = frame[f"nivel_{ALVOS[p.codigo][1]}"]
        obs.append(serie.get(p.valido_para_utc, float("nan")) if p.valido_para_utc <= agora
                   else float("nan"))
    out["observado_cm"] = obs
    out["erro_cm"] = out["previsto_cm"] - out["observado_cm"]
    out["erro_corrigido_cm"] = out["corrigido_cm"] - out["observado_cm"]
    out["status"] = "conferido"
    out.loc[out["observado_cm"].isna() & (out["valido_para_utc"] > agora), "status"] = "pendente"
    out.loc[out["observado_cm"].isna() & (out["valido_para_utc"] <= agora), "status"] = "sem observação"
    out.loc[out["previsto_cm"].isna(), "status"] = "não emitida"
    return out[COLUNAS].sort_values(["emitido_em_utc", "alvo", "h"]).reset_index(drop=True)


def picos(frame: pd.DataFrame, agora: pd.Timestamp) -> pd.DataFrame:
    """Pico observado até agora, hora do pico e situação em relação à cota de inundação."""
    cotas = pd.read_csv(REFERENCE / "cotas_referencia.csv").set_index("codigo")
    linhas = []
    for codigo, (nome, ap) in ALVOS.items():
        s = frame.loc[INICIO_EVENTO:agora, f"nivel_{ap}"].dropna()
        if s.empty:
            continue
        inund = float(cotas.loc[codigo, "inundacao_cm"])
        acima = s[s >= inund]
        ultimas = s.iloc[-4:]
        tendencia = ultimas.iloc[-1] - ultimas.iloc[0] if len(ultimas) > 1 else float("nan")
        linhas.append({
            "alvo": nome, "pico_cm": s.max(), "hora_pico_utc": s.idxmax(),
            "ultima_cota_cm": s.iloc[-1], "ultima_hora_utc": s.index[-1],
            "variacao_3h_cm": tendencia, "inundacao_cm": inund,
            "cruzou_inundacao_utc": acima.index[0] if not acima.empty else pd.NaT,
            "horas_acima_inundacao": int(acima.size),
        })
    return pd.DataFrame(linhas)


def resumo(pares: pd.DataFrame) -> pd.DataFrame:
    ok = pares[pares["status"] == "conferido"]
    if ok.empty:
        return pd.DataFrame()
    g = ok.assign(ae=ok["erro_cm"].abs(), sub=ok["erro_cm"] < 0)
    return g.groupby(["emissao", "alvo", "h"]).agg(
        previsto_cm=("previsto_cm", "first"), observado_cm=("observado_cm", "first"),
        erro_cm=("erro_cm", "first"), n=("ae", "size")).reset_index()


def figura(pares: pd.DataFrame, frame: pd.DataFrame, agora: pd.Timestamp):
    cotas = pd.read_csv(REFERENCE / "cotas_referencia.csv").set_index("codigo")
    loc = lambda s: s.tz_convert(TZ_LOCAL)
    emissoes = list(dict.fromkeys(pares["emissao"]))
    cores = dict(zip(emissoes, [AZUL, "#9a9994", LARANJA, "#6c8c55", "#8d64b4", "#cb872d"]))

    fig, axes = plt.subplots(3, 1, figsize=(11, 11), sharex=True, constrained_layout=True)
    for ax, (codigo, (nome, ap)) in zip(axes, ALVOS.items()):
        s = frame.loc[INICIO_EVENTO:agora, f"nivel_{ap}"].dropna()
        ax.plot(loc(s.index), s.values, color=OBS, linewidth=2.2, label="observado (ANA)")
        for emissao in emissoes:
            g = pares[(pares["alvo"] == nome) & (pares["emissao"] == emissao)
                      & pares["previsto_cm"].notna()]
            if g.empty:
                continue
            estilo = ":" if g["tipo"].iloc[0] == "replay" else "--"
            for t0, gg in g.groupby("t_ref_utc"):
                gg = gg.sort_values("h")
                xs = [t0] + list(gg["valido_para_utc"])
                nivel0 = frame[f"nivel_{ap}"].get(t0, float("nan"))
                ys = [nivel0] + list(gg["previsto_cm"])
                ax.plot([loc(pd.Timestamp(x)) for x in xs], ys, color=cores[emissao],
                        linewidth=1.5, linestyle=estilo, marker="o", markersize=4,
                        label=emissao if t0 == g["t_ref_utc"].min() else None)
            corr = g.dropna(subset=["corrigido_cm"]).sort_values("valido_para_utc")
            if not corr.empty:
                ax.plot([loc(t) for t in corr["valido_para_utc"]], corr["corrigido_cm"],
                        color=cores[emissao], linewidth=0, marker="^", markersize=6,
                        label=f"{emissao}, com viés corrigido")
        y = float(cotas.loc[codigo, "inundacao_cm"])
        ax.axhline(y, color="#a8a7a1", linestyle="--", linewidth=1)
        ax.annotate("inundação", (0.995, y), xycoords=("axes fraction", "data"),
                    fontsize=7, color="#8a8984", ha="right", va="bottom")
        ax.axvline(loc(agora), color="#c9c8c2", linewidth=1)
        ax.set_title(nome, fontsize=10, color=TEXTO, loc="left")
        ax.set_ylabel("cota (cm)", fontsize=8, color=TEXTO_2)
        ax.legend(fontsize=7, frameon=False, loc="upper left")
        _estilo(ax)
    axes[-1].set_xlabel("horário local (UTC−3)", fontsize=8, color=TEXTO_2)
    fig.suptitle(f"Taquari, 21–22/09/2026: previsto × observado até {loc(agora):%d/%m %H:%M}",
                 fontsize=12, color=TEXTO)
    FIGS.mkdir(parents=True, exist_ok=True)
    destino = FIGS / f"verificacao_{agora:%Y%m%d_%H}.png"
    fig.savefig(destino, dpi=150)
    plt.close(fig)
    return destino


def _fmt(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        temporal = (str(df[col].dtype).startswith("datetime64")
                    or any(isinstance(v, pd.Timestamp) for v in df[col].dropna()))
        if temporal:
            # Colunas com NaT podem chegar como object ou naïve; tudo aqui é UTC.
            df[col] = (pd.to_datetime(df[col], utc=True).dt.tz_convert(TZ_LOCAL)
                       .dt.strftime("%d/%m %H:%M"))
    return df.round(1).fillna("—")


def relatorio(pares: pd.DataFrame, pico: pd.DataFrame, fig, agora: pd.Timestamp) -> None:
    loc = agora.tz_convert(TZ_LOCAL)
    conf = pares[pares["status"] == "conferido"]
    emis = conf[conf["tipo"] == "emissao"]
    partes = [
        f"# Cheia de 21–22/09/2026: previsto × observado\n\n"
        f"Conferência feita em {loc:%d/%m/%Y %H:%M} local. Cotas observadas da ANA (grade horária, "
        "QC da Fase 2). Cada linha compara um número que estava publicado antes da validade com "
        "a cota medida na validade. Erro = previsto − observado: negativo é subestimativa. "
        "Nenhuma previsão foi recalculada.\n\n"
        "**Não é sistema de alerta.** Para decisão operacional: SACE/SGB e Defesa Civil (199).\n\n"
        "## O que aconteceu\n\n"
        + _fmt(pico.rename(columns={
            "pico_cm": "pico_cm", "hora_pico_utc": "hora_pico_local",
            "ultima_cota_cm": "ultima_cota_cm", "ultima_hora_utc": "ultima_hora_local",
            "cruzou_inundacao_utc": "cruzou_inundacao_local"})).to_markdown(index=False)
        + "\n\nA variação de 3h é a diferença entre a última cota e a de três horas antes: "
        "negativa indica recessão. Um pico igual à última cota significa que o rio ainda não "
        "baixou neste cache.\n\n"
        f"![Previsto × observado](figs/{fig.name})\n\n"
    ]
    if not emis.empty:
        g = emis.assign(ae=emis["erro_cm"].abs(), sub=emis["erro_cm"] < 0)
        por_h = g.groupby(["emissao", "h"]).agg(MAE_cm=("ae", "mean"), vies_cm=("erro_cm", "mean"),
                                                 n=("ae", "size"), subestimou=("sub", "sum"))
        total_sub, total = int(g["sub"].sum()), len(g)
        partes.append(
            "## Emissões reais: erro por horizonte\n\n"
            f"{total_sub} de {total} pares conferidos subestimaram a cota observada.\n\n"
            + por_h.round(1).reset_index().to_markdown(index=False) + "\n\n")
    for emissao, g in pares.groupby("emissao", sort=False):
        tipo = g["tipo"].iloc[0]
        emitido = g["emitido_em_utc"].iloc[0].tz_convert(TZ_LOCAL)
        aviso = (" Este bloco é um replay gerado com cache depois da referência; não conta como "
                 "emissão, está aqui porque foi publicado." if tipo == "replay" else "")
        cols = ["alvo", "motor", "h", "t_ref_utc", "valido_para_utc", "antecedencia_real_h",
                "previsto_cm", "corrigido_cm", "observado_cm", "erro_cm", "erro_corrigido_cm",
                "status"]
        tabela = g[cols].rename(columns={"t_ref_utc": "referencia_local",
                                         "valido_para_utc": "validade_local"})
        if tabela["corrigido_cm"].isna().all():
            tabela = tabela.drop(columns=["corrigido_cm", "erro_corrigido_cm"])
        partes.append(f"## {emissao}\n\nGerada em {emitido:%d/%m %H:%M} local.{aviso} "
                      "A antecedência real desconta o tempo entre a observação de referência "
                      "e a gravação do número.\n\n" + _fmt(tabela).to_markdown(index=False) + "\n\n")
    partes.append(
        "## Leitura\n\n"
        "Os números acima são o registro. A interpretação, escrita depois de ver os "
        "resultados, está no README e em `10_setembro2026.md`. O CSV com todos os pares "
        "está em `13_verificacao_pares.csv`. Para refazer com cache mais novo: "
        "`uv run python -m src.live.evento`.\n")
    (ROOT / "reports/13_verificacao_setembro2026.md").write_text("".join(partes))


def run(agora: pd.Timestamp | None = None):
    agora = agora or pd.Timestamp.now(tz="UTC").floor("h")
    # Ordena pelo carimbo da execução, não pelo nome: "replay_" viria depois de "emissao_".
    pastas = sorted((PROCESSED / "live_runs").glob("*/features.parquet"),
                    key=lambda p: p.parent.name.split("_", 1)[1])
    frame = pd.read_parquet(pastas[-1], columns=[f"nivel_{ap}" for _, ap in ALVOS.values()])
    agora = min(agora, frame.dropna(how="all").index.max())
    pares = parear(carregar_publicadas(), frame, agora)
    pico = picos(frame, agora)
    fig = figura(pares, frame, agora)
    pares.to_csv(ROOT / "reports/13_verificacao_pares.csv", index=False)
    relatorio(pares, pico, fig, agora)
    print(pares.to_string(index=False))
    print(pico.to_string(index=False))
    print(f"[evento] figura em {fig}; frame de {pastas[-1].parent.name}")
    return pares, pico


if __name__ == "__main__":
    run(pd.Timestamp(sys.argv[1], tz="UTC") if len(sys.argv) > 1 else None)
