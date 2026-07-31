"""QC e alinhamento temporal das séries da ANA (SOAP legado, 15 min).

Fuso: timestamps do SOAP são hora local UTC-3 fixa (validado contra o boletim
SACE de 28/07/2026 18:00 — ver reports/02_qc.md). Conversão para UTC acontece
AQUI, uma única vez; daqui para frente todo timestamp do projeto é UTC.

Agregação para a grade horária (rótulo = início do período, UTC):
- nivel_cm, vazao_m3s: valor instantâneo da amostra exatamente no topo da hora
  (sem interpolação; hora sem amostra válida fica NaN — Armadilha 0 proíbe
  fabricar dado em lacuna, sobretudo de cheia).
- chuva_mm: soma das amostras de 15 min dentro da hora; NaN se não houver
  nenhuma amostra; chuva_n registra quantas entraram (0-4) para o QC de soma
  parcial.
- disp_nivel: fração das 4 amostras esperadas com nível válido (não-NaN,
  não-zero). É a variável de disponibilidade da Armadilha 0 — vira métrica na
  Fase 8 e feature na Fase 4.
"""

from __future__ import annotations

import pandas as pd

from ..ingest.common import RAW, ROOT, load_config
from . import flags

INTERIM = ROOT / "data" / "interim"


def carregar_estacao(codigo: int) -> pd.DataFrame:
    arquivos = sorted((RAW / "ana_soap" / f"estacao={codigo}").rglob("*.parquet"))
    if not arquivos:
        return pd.DataFrame()
    partes = []
    for a in arquivos:
        parte = pd.read_parquet(a)
        parte["origem"] = f"{a.parent.name}/{a.name}"
        partes.append(parte)
    df = pd.concat(partes, ignore_index=True)
    df["dt_local"] = pd.to_datetime(df["DataHora"], errors="coerce")
    return df.dropna(subset=["dt_local"])


def qc_15min(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Aplica flags na resolução nativa de 15 min. Marca, não apaga."""
    df = df.copy()
    # Flags de sequência calculados na ordem BRUTA da fonte, por bloco de origem
    origem = df["origem"] if "origem" in df.columns else None
    df["flag_fora_de_ordem"] = flags.flag_fora_de_ordem(df["dt_local"], origem)
    df["flag_duplicado"] = flags.flag_duplicado(df["dt_local"])
    df = df.sort_values("dt_local")
    df = df[~df["flag_duplicado"]].reset_index(drop=True)

    df["flag_nivel_zero"] = flags.flag_zero(df["Nivel"])
    df["flag_stuck"] = flags.flag_stuck(df["Nivel"], cfg["stuck_min_steps_nivel"])
    df["flag_spike"] = flags.flag_spike(
        df["Nivel"], df["dt_local"], cfg["spike_max_cm_15min"]
    )

    # Armadilha 0: zero de nível/vazão vira NaN explícito (o flag preserva o fato)
    df.loc[df["flag_nivel_zero"], ["Nivel", "Vazao"]] = pd.NA
    df.loc[df["Vazao"] == 0, "Vazao"] = pd.NA
    # Spike não é apagado: é marcado e a decisão fica com quem consome
    return df


def para_grade_horaria(df: pd.DataFrame, tz_horas: int) -> pd.DataFrame:
    """Converte local fixo -> UTC e agrega na grade horária."""
    df = df.copy()
    df["ts_utc"] = (
        df["dt_local"].dt.tz_localize(f"Etc/GMT+{-tz_horas}").dt.tz_convert("UTC")
    )
    df["hora"] = df["ts_utc"].dt.floor("h")

    topo = df[df["ts_utc"] == df["hora"]].set_index("hora")
    por_hora = df.groupby("hora")
    out = pd.DataFrame({
        "nivel_cm": topo["Nivel"].astype("Float64"),
        "vazao_m3s": topo["Vazao"].astype("Float64"),
        "chuva_mm": por_hora["Chuva"].sum(min_count=1),
        "chuva_n": por_hora["Chuva"].count(),
        "disp_nivel": por_hora["Nivel"].apply(lambda s: s.notna().mean()),
        "flag_stuck": por_hora["flag_stuck"].any(),
        "flag_spike": por_hora["flag_spike"].any(),
        "flag_nivel_zero": por_hora["flag_nivel_zero"].any(),
        "flag_fora_de_ordem": por_hora["flag_fora_de_ordem"].any(),
    })
    out.index.name = "ts_utc"
    out = out.reset_index()
    out["flag_dst_incerto"] = flags.flag_dst_incerto(
        pd.DatetimeIndex(out["ts_utc"])
    )
    return out


def run() -> None:
    cfg = load_config("qc")
    estacoes = load_config("stations")["estacoes_fluviometricas"]
    tz_horas = cfg["tz_fixo_horas"]

    partes = []
    for est in estacoes:
        bruto = carregar_estacao(est["codigo"])
        if bruto.empty:
            print(f"[qc.ana] {est['nome']}: sem dados brutos — pulando")
            continue
        marcado = qc_15min(bruto, cfg)
        horario = para_grade_horaria(marcado, tz_horas)
        horario.insert(0, "codigo", est["codigo"])
        horario.insert(1, "estacao", est["nome"])
        partes.append(horario)
        print(f"[qc.ana] {est['nome']}: {len(bruto)} amostras 15min -> "
              f"{len(horario)} horas", flush=True)

    final = pd.concat(partes, ignore_index=True)
    INTERIM.mkdir(parents=True, exist_ok=True)
    final.to_parquet(INTERIM / "ana_hourly.parquet", index=False)
    print(f"[qc.ana] {len(final)} linhas em data/interim/ana_hourly.parquet")


if __name__ == "__main__":
    run()
