"""Estimativas de 3/6/9/12h com latência explícita e registro de cada rodada.

--sem-atualizar produz replay do cache, sem alegar emissão em tempo real.
Escolha de modelos documentada em reports/11_validacao_live.md.
"""

from __future__ import annotations

import hashlib
import json
import shutil

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from ..eval.figures import AZUL, LARANJA, OBS, TEXTO, TEXTO_2, _estilo
from ..features import build as features_build
from ..ingest.common import REFERENCE, ROOT
from . import ingest, merge_live, operational, verification

INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"
FIGS = ROOT / "reports" / "figs"

ALVOS = {86510000: ("Muçum", "mu"), 86720000: ("Encantado", "en"),
         86879300: ("Estrela", "es")}
MONTANTES = [(86472000, "jj", "Linha José Julio"), (86472600, "st", "Santa Tereza")]
TZ_LOCAL = "Etc/GMT+3"


def atualizar_fontes() -> None:
    """Busca o que falta em cada fonte e regrava o interim consolidado."""
    ingest.ana_recente().to_parquet(INTERIM / "ana_hourly.parquet", index=False)
    ingest.ons_recente().to_parquet(INTERIM / "ons_hourly.parquet", index=False)
    merge_live.baixar_recentes()
    merge_live.diaria_incremental()
    merge_live.horaria_live(pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=8))


def figura(frame: pd.DataFrame, prev: pd.DataFrame, horas: int = 36):
    """Painel do evento: chuva, defluência CERAN e um hidrograma por alvo."""
    cotas = pd.read_csv(REFERENCE / "cotas_referencia.csv").set_index("codigo")
    fim = prev["t_ref_utc"].max()
    jan = frame.loc[fim - pd.Timedelta(hours=horas):fim]
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
        for motor, cor, rotulo in [("linear", AZUL, "linear"),
                                   ("gbm_nivel", LARANJA, "GBM nível"),
                                   ("gbm_delta", "#6c8c55", "GBM variação"),
                                   ("ridge_montante", "#8d64b4", "montante ampliado"),
                                   ("gbm_postos", "#cb872d", "GBM + chuva de postos")]:
            gm = g[g["motor"] == motor].sort_values("h")
            if gm.empty:
                continue
            t0 = gm["t_ref_utc"].iloc[0]
            xs = [t0] + list(gm["valido_para_utc"])
            ys = [gm["nivel_em_t"].iloc[0]] + list(gm["previsto_cm"])
            ax.plot([loc(pd.Timestamp(x)) for x in xs], ys, color=cor, linewidth=1.6,
                    linestyle="--", marker="o", markersize=4, label=rotulo)
        if "inferior_cm" in g:
            faixa = g.dropna(subset=["inferior_cm", "superior_cm"]).sort_values("h")
            if not faixa.empty:
                ax.errorbar([loc(t) for t in faixa.valido_para_utc], faixa.previsto_cm,
                            yerr=[faixa.previsto_cm - faixa.inferior_cm,
                                  faixa.superior_cm - faixa.previsto_cm],
                            fmt="none", ecolor="#777777", capsize=3,
                            label="faixa empírica (sem garantia)")
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
    modo = "replay" if "modo" in prev and prev.modo.iloc[0] == "replay" else "estimativa"
    fig.suptitle(
        f"Taquari — {modo}, referência de {loc(fim):%d/%m/%Y %H:%M} local",
        fontsize=12, color=TEXTO)
    FIGS.mkdir(parents=True, exist_ok=True)
    destino = FIGS / f"live_v3_{fim:%Y%m%d_%H}.png"
    fig.savefig(destino, dpi=150)
    plt.close(fig)
    print(f"[live] figura em {destino}", flush=True)
    return destino


def registrar(frame: pd.DataFrame, prev: pd.DataFrame, bt: pd.DataFrame,
              atualizar: bool):
    """Diretório único por execução; mantém entradas e código para auditoria."""
    agora = pd.Timestamp.now(tz="UTC")
    modo = "emissao" if atualizar else "replay"
    pasta = PROCESSED / "live_runs" / f"{modo}_{agora:%Y%m%dT%H%M%S%fZ}"
    pasta.mkdir(parents=True, exist_ok=False)
    prev = prev.copy()
    prev["gerado_em_utc"] = agora
    prev["modo"] = modo
    prev["emitido_em_utc"] = agora if atualizar else pd.NaT
    prev["antecedencia_real_h"] = (
        (prev["valido_para_utc"] - agora).dt.total_seconds() / 3600 if atualizar else float("nan")
    )
    if atualizar:
        prev.loc[prev.antecedencia_real_h <= 0, "status"] = "validade_expirada"
    prev.to_parquet(pasta / "previsoes.parquet", index=False)
    bt.to_parquet(pasta / "replay.parquet", index=False)
    frame.to_parquet(pasta / "features.parquet")
    arquivos = [ROOT / "uv.lock", ROOT / "reports/11_live_modelos.json"]
    if (ROOT / "reports/12_live_modelos.json").exists():
        arquivos.append(ROOT / "reports/12_live_modelos.json")
    arquivos += [PROCESSED / f"dataset_{codigo}.parquet" for codigo in ALVOS]
    hashes = {}
    for arquivo in arquivos:
        shutil.copy2(arquivo, pasta / arquivo.name)
        hashes[str(arquivo.relative_to(ROOT))] = hashlib.sha256(arquivo.read_bytes()).hexdigest()
    shutil.copytree(ROOT / "src", pasta / "src", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / "config", pasta / "config")
    meta = {"modo": modo, "gerado_em_utc": agora.isoformat(),
            "referencia_utc": prev.t_ref_utc.max().isoformat(),
            "atrasos_assumidos_h": operational.ATRASOS, "sha256": hashes,
            "avaliacao": "replay com latências assumidas; não emissões passadas",
            "sem_correcao_de_vies": bool("ajuste_cm" not in prev or prev.ajuste_cm.eq(0).all())}
    (pasta / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    prev.to_parquet(PROCESSED / "live_v3_previsoes.parquet", index=False)
    bt.to_parquet(PROCESSED / "live_v3_replay.parquet", index=False)
    return prev, pasta


def relatorio(prev: pd.DataFrame, bt: pd.DataFrame, pasta,
              verificadas: pd.DataFrame | None = None) -> None:
    fim = prev.t_ref_utc.max()
    tabela = prev[["alvo", "motor", "h", "t_ref_utc", "nivel_em_t", "previsto_cm",
                   "valido_para_utc", "antecedencia_real_h", "status"]].copy()
    tabela["t_ref_utc"] = tabela.t_ref_utc.dt.tz_convert(TZ_LOCAL).dt.strftime("%d/%m %H:%M")
    tabela["valido_para_utc"] = tabela.valido_para_utc.dt.tz_convert(TZ_LOCAL).dt.strftime("%d/%m %H:%M")
    tabela = tabela.rename(columns={"valido_para_utc": "validade_local", "t_ref_utc": "referencia_local",
                                    "nivel_em_t": "observado_cm"})
    if prev.modo.iloc[0] == "replay":
        tabela = tabela.drop(columns="antecedencia_real_h")
    faixas = prev[["alvo", "h", "inferior_cm", "superior_cm", "faixa_status",
                   "cobertura_recente", "n_faixa_recente"]].copy()
    nomes_faixa = {"sem_calibracao": "sem calibração", "dados_insuficientes": "faltam dados",
                   "amostra_insuficiente": "poucos exemplos neste regime",
                   "regime_fora_calibracao": "subida fora da calibração",
                   "cobertura_recente_baixa": "erros recentes excedem a faixa",
                   "empirica_sem_garantia": "empírica, sem garantia"}
    faixas.faixa_status = faixas.faixa_status.replace(nomes_faixa)
    faixas.cobertura_recente = 100 * faixas.cobertura_recente
    faixas = faixas.rename(columns={"cobertura_recente": "cobertura_recente_pct"})
    # Recorte explícito da subida de setembro; janela móvel para outros eventos.
    dia_local = fim.tz_convert(TZ_LOCAL).date().isoformat()
    inicio = (pd.Timestamp("2026-09-21 09:00", tz="UTC")
              if dia_local == "2026-09-21" else fim - pd.Timedelta(hours=24))
    avaliavel = bt[(bt.t_ref_utc >= inicio) & (bt.valido_para <= fim)]
    resumo = avaliavel.assign(ae=avaliavel.erro_cm.abs()).groupby(["alvo", "h"]).agg(
        MAE_cm=("ae", "mean"), vies_cm=("erro_cm", "mean"), n=("ae", "size"))
    ressalva = ""
    if dia_local == "2026-09-21":
        linhas_9 = resumo.xs(9, level="h") if 9 in resumo.index.get_level_values("h") else None
        detalhe = ("; ".join(f"{alvo}: MAE {row.MAE_cm:.0f} cm, n={int(row.n)}"
                             for alvo, row in linhas_9.iterrows())
                   if linhas_9 is not None else "sem pares verificáveis")
        ressalva = (
            "**O fundamento histórico não comprova qualidade nesta subida.** "
            f"Replay de 9h: {detalhe}. "
            "Consulte também n em 12h: poucos pares não bastam para estimar "
            "qualidade neste evento. O desempenho histórico não é uma margem de erro "
            f"válida para setembro. As previsões da referência das {fim.tz_convert(TZ_LOCAL):%H:%M} ainda "
            "não têm observação futura neste cache.\n\n")
    texto = (f"# Revisão da rodada de {fim.tz_convert(TZ_LOCAL):%d/%m/%Y %H:%M}\n\n"
             f"Modo: **{prev.modo.iloc[0]}**. Referência observada: "
             f"{fim.tz_convert(TZ_LOCAL):%d/%m %H:%M} (UTC−3). "
             "Uma execução com cache não é uma previsão emitida naquele horário.\n\n"
             "Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos "
             "no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. "
             "A coluna de cota é uma estimativa pontual, não uma cota de pico. "
             "Não é sistema de alerta.\n\n"
             + ressalva + tabela.round(1).fillna("—").to_markdown(index=False)
             + "\n\n## Faixas e diagnóstico\n\n"
             "As faixas usam o quantil 90% dos erros de 2025, separado por regime, "
             "sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, "
             "a velocidade está fora da calibração ou a cobertura dos últimos erros "
             "conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). "
             "Uma faixa ausente não significa erro zero.\n\n"
             + faixas.round(1).fillna("—").to_markdown(index=False)
             + f"\n\n![Hidrograma revisado](figs/live_v3_{fim:%Y%m%d_%H}.png)"
             + "\n\n## Replay da subida\n\n"
             + f"Referências a partir de {inicio.tz_convert(TZ_LOCAL):%d/%m %H:%M}; "
             "somente alvos já observados. Horizontes maiores têm menos pares. "
             "Ausência de linha significa ausência de pares, não erro zero.\n\n"
             + resumo.round(1).reset_index().to_markdown(index=False)
             + "\n\nOs candidatos são escolhidos em 2023–2024, confirmados em 2025 "
             "e podem ser vetados por regressão em 2026. A comparação completa está em "
             "[melhoria e aceitação](12_melhoria_live.md). "
             "O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.\n\n"
             + f"Arquivo local da execução: `{pasta.relative_to(ROOT)}`. "
             "Contém previsões, replay, features, datasets de treino, código e configuração.\n")
    if prev.modo.iloc[0] == "emissao":
        emissao = prev.emitido_em_utc.iloc[0].tz_convert(TZ_LOCAL)
        texto = texto.replace("Uma execução com cache não é uma previsão emitida naquele horário.",
                              f"Emissão registrada em {emissao:%d/%m/%Y %H:%M:%S} local. "
                              "A antecedência real desconta o tempo desde a observação.")
    texto += "\n## Emissões reais conferidas\n\n"
    if verificadas is None or verificadas.empty:
        texto += "Nenhuma emissão real arquivada com alvo já observável. Replays não contam como emissões.\n"
    else:
        resumo_real = verificadas.assign(ae=verificadas.erro_cm.abs()).groupby(["alvo", "h"]).agg(
            MAE_cm=("ae", "mean"), n=("ae", "size"))
        texto += resumo_real.round(1).reset_index().to_markdown(index=False) + "\n"
    (ROOT / "reports/live_ultima_rodada.md").write_text(texto)
    (pasta / "relatorio.md").write_text(texto)


def run(atualizar: bool = True):
    if atualizar:
        atualizar_fontes()
    frame = features_build.montar()
    prev, bt = operational.rodada(frame)
    prev, pasta = registrar(frame, prev, bt, atualizar)
    destino = figura(frame, prev, horas=36)
    verificadas = verification.conferir(frame, PROCESSED / "live_runs", pd.Timestamp.now(tz="UTC"))
    verificadas.to_parquet(pasta / "emissoes_conferidas.parquet", index=False)
    verificadas.to_parquet(PROCESSED / "live_emissoes_conferidas.parquet", index=False)
    relatorio(prev, bt, pasta, verificadas)
    print(prev.to_string(index=False))
    print(f"[live] execução arquivada em {pasta}")
    return prev, bt, destino


if __name__ == "__main__":
    import sys
    run(atualizar="--sem-atualizar" not in sys.argv)
