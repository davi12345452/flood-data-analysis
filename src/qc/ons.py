"""QC e alinhamento temporal dos dados hidráulicos horários do ONS (CERAN).

Fuso: mesmo das séries da ANA, UTC-3 fixo (validado por cross-correlação
defluência 14 de Julho × vazão ANA em José Júlio: máximo em lag 0, r=0,998 —
ver reports/02_qc.md).

Convenção temporal da fonte: "hora fim" (dicionário do ONS: o registro 01:00
representa o intervalo 00:00-00:59). Aqui o rótulo é deslocado para o INÍCIO
do período, alinhando com a grade da ANA.

Filtro por cod_usina (97/98/99), não por nome: desde 2026-02 o ONS preenche
nom_reservatorio com espaços extras.
"""

from __future__ import annotations

import pandas as pd

from ..ingest.common import RAW, ROOT, load_config, source_order
from . import flags

INTERIM = ROOT / "data" / "interim"

USINAS = {97: "CASTRO ALVES", 98: "MONTE CLARO", 99: "14 DE JULHO"}
COLUNAS_VALOR = [
    "val_vazaoafluente", "val_vazaodefluente", "val_vazaoturbinada",
    "val_vazaovertida", "val_nivelmontante",
]


def carregar() -> pd.DataFrame:
    arquivos = sorted((RAW / "ons" / "dados_hidrologicos_ho").glob("*.parquet"))
    partes = []
    for a in sorted(arquivos, key=source_order):
        df = pd.read_parquet(a, columns=["cod_usina", "din_instante"] + COLUNAS_VALOR)
        df["cod_usina"] = pd.to_numeric(df["cod_usina"], errors="coerce")
        df["_versao_fonte"] = len(partes)
        partes.append(df[df["cod_usina"].isin(USINAS)])
    df = pd.concat(partes, ignore_index=True)
    ultima = df.groupby(["cod_usina", "din_instante"])["_versao_fonte"].transform("max")
    return df[df._versao_fonte == ultima].drop(columns="_versao_fonte")


def normalizar_hora_24(hist: pd.DataFrame) -> pd.DataFrame:
    """Repara históricos gravados antes da correção da hora 24 (23:59 local).

    A hora que o ONS grava como 23:59 é o fim da hora 23-24; o rótulo UTC
    correto é a hora cheia seguinte. Se a mesma chave já existir, vale a
    linha que já estava alinhada.
    """
    ts = pd.DatetimeIndex(hist["ts_utc"])
    desalinhado = ts.minute == 59
    if not desalinhado.any():
        return hist
    out = hist.copy()
    out.loc[desalinhado, "ts_utc"] = ts[desalinhado].ceil("h")
    out["_reparado"] = desalinhado
    out = out.sort_values(["usina", "ts_utc", "_reparado"]).drop_duplicates(["usina", "ts_utc"])
    return out.drop(columns="_reparado").reset_index(drop=True)


def processar(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """QC único, usado tanto pelo histórico quanto pela atualização incremental."""
    df = df.copy()
    tz_horas = cfg["tz_fixo_horas"]
    romp = cfg["rompimento_14julho"]

    df["dt_local"] = pd.to_datetime(df["din_instante"], errors="coerce")
    df = df.dropna(subset=["dt_local"])
    # O ONS grava a hora 24 como 23:59 do mesmo dia; é o fim da hora 23-24.
    fim_do_dia = (df["dt_local"].dt.hour == 23) & (df["dt_local"].dt.minute == 59)
    df.loc[fim_do_dia, "dt_local"] = df.loc[fim_do_dia, "dt_local"].dt.ceil("h")
    df["usina"] = df["cod_usina"].map(USINAS)

    partes = []
    for usina, grupo in df.groupby("usina"):
        g = grupo.copy()
        g["flag_fora_de_ordem"] = flags.flag_fora_de_ordem(g["dt_local"])
        g["flag_duplicado"] = flags.flag_duplicado(g["dt_local"])
        g = g.sort_values("dt_local")
        g = g[~g["flag_duplicado"]]

        # Armadilha 0 espelhada: defluência/afluência zero em usina a fio
        # d'água é falha de transmissão, não operação.
        g["flag_defluente_zero"] = flags.flag_zero(g["val_vazaodefluente"])
        g.loc[g["flag_defluente_zero"], "val_vazaodefluente"] = pd.NA
        g.loc[g["val_vazaoafluente"] == 0, "val_vazaoafluente"] = pd.NA

        g["flag_stuck"] = flags.flag_stuck(
            g["val_vazaodefluente"], cfg["stuck_min_steps_nivel"] // 2  # 12h na grade horária
        )
        partes.append(g)

    df = pd.concat(partes, ignore_index=True)

    # Hora-fim -> rótulo no início do período; depois local fixo -> UTC
    df["ts_utc"] = (
        (df["dt_local"] - pd.Timedelta(hours=1))
        .dt.tz_localize(f"Etc/GMT+{-tz_horas}")
        .dt.tz_convert("UTC")
    )
    df["flag_dst_incerto"] = flags.flag_dst_incerto(pd.DatetimeIndex(df["ts_utc"]))

    # Armadilha 6: janela pós-rompimento da 14 de Julho
    df["flag_pos_rompimento"] = (
        (df["usina"] == romp["usina"])
        & (df["ts_utc"] >= pd.Timestamp(romp["inicio"], tz="UTC"))
        & (df["ts_utc"] <= pd.Timestamp(romp["fim"], tz="UTC"))
    )

    colunas = (["usina", "cod_usina", "ts_utc"] + COLUNAS_VALOR
               + [c for c in df.columns if c.startswith("flag_")])
    final = df[colunas].rename(columns={
        "val_vazaoafluente": "afluente_m3s",
        "val_vazaodefluente": "defluente_m3s",
        "val_vazaoturbinada": "turbinada_m3s",
        "val_vazaovertida": "vertida_m3s",
        "val_nivelmontante": "nivel_montante_m",
    })
    return final


def run() -> None:
    from ..core.storage import parquet
    final = processar(carregar(), load_config("qc"))
    parquet(final, INTERIM / "ons_hourly.parquet")
    print(f"[qc.ons] {len(final)} linhas")


if __name__ == "__main__":
    run()
