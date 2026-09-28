"""Features de chuva a partir do MERGE agregado por sub-bacia.

Causalidade: o acumulado de janela W avaliado em t soma as horas [t-W, t-1] —
a chuva da própria hora t (acumulação [t, t+1)) ainda não existe em t.
O API diário avaliado em t usa apenas períodos de 24h já encerrados antes de t.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from ..ingest.common import ROOT, load_config

INTERIM_MERGE = ROOT / "data" / "interim" / "merge"


def acumulados_posto(g: pd.DataFrame, apelido: str) -> pd.DataFrame:
    """Chuva local ANA: somente horas completas, encerradas antes de t.

    Não substitui chuva média de bacia. Exige as quatro leituras de 15 min
    e não transforma ausência em zero. A hora t, possivelmente parcial, é
    excluída de todos os acumulados. Latência de transmissão não é medida.
    """
    g = g.set_index("ts_utc").sort_index()
    grade = pd.date_range(g.index.min(), g.index.max(), freq="h")
    g = g.reindex(grade)
    chuva = g.chuva_mm.astype(float).where(g.chuva_n == 4)
    return pd.DataFrame({f"posto_{apelido}_{h}h": chuva.rolling(h, min_periods=h).sum().shift(1)
                         for h in (1, 3, 6, 12, 24)}, index=grade)


def carregar_macro_horaria() -> pd.DataFrame:
    """Chuva horária por macro-unidade (média das sub-bacias ponderada por
    área incremental), nas janelas em que o MERGE horário existe."""
    cfg = load_config("features")
    areas = pd.read_csv(ROOT / "data" / "reference" / "subbacias_areas.csv")
    arquivos = sorted((INTERIM_MERGE / "horaria").glob("*.parquet"))
    if not arquivos:
        raise RuntimeError("Sem MERGE horário agregado — rode make spatial.")
    df = pd.concat((pd.read_parquet(a) for a in arquivos), ignore_index=True)
    df = df.drop_duplicates(subset=["ts_utc", "codigo"], keep="last")
    return _para_macro(df, cfg["macro_unidades"], areas, freq="h")


def carregar_macro_diaria() -> pd.DataFrame:
    cfg = load_config("features")
    areas = pd.read_csv(ROOT / "data" / "reference" / "subbacias_areas.csv")
    arquivos = sorted((INTERIM_MERGE / "diaria").glob("*.parquet"))
    df = pd.concat((pd.read_parquet(a) for a in arquivos), ignore_index=True)
    return _para_macro(df, cfg["macro_unidades"], areas, freq="24h")


def _para_macro(df: pd.DataFrame, macro: dict, areas: pd.DataFrame, freq: str) -> pd.DataFrame:
    pesos = areas.set_index("codigo")["area_incremental_km2"]
    if df.duplicated(["ts_utc", "codigo"]).any():
        raise ValueError("Chuva com chave (ts_utc, codigo) duplicada.")
    partes = {}
    for nome, codigos in macro.items():
        w = pesos.reindex(codigos)
        if w.isna().any() or (w <= 0).any():
            raise ValueError(f"Áreas incrementais inválidas em {nome}.")
        sub = df[df.codigo.isin(codigos)].pivot(index="ts_utc", columns="codigo", values="chuva_mm")
        sub = sub.reindex(columns=codigos)
        # Exige toda a área: ausência parcial ou total não é chuva zero.
        partes[nome] = sub.mul(w).sum(axis=1, min_count=len(codigos)) / w.sum()
    out = pd.DataFrame(partes).sort_index()
    out.index.name = "ts_utc"
    if out.empty:
        return out
    grade = pd.date_range(out.index.min(), out.index.max(), freq=freq)
    return out.reindex(grade)


def acumulados(horaria: pd.DataFrame, janelas: list[int]) -> pd.DataFrame:
    """Acumulados causais por macro-unidade: janela W em t = soma [t-W, t-1]."""
    feats = {}
    for macro in horaria.columns:
        serie = horaria[macro]
        for w in janelas:
            min_p = w  # toda hora da janela precisa ser observada
            feats[f"chuva_{macro}_{w}h"] = (
                serie.rolling(w, min_periods=min_p).sum().shift(1)
            )
    return pd.DataFrame(feats, index=horaria.index)


def api_diaria(diaria: pd.DataFrame, decaimentos: list[float]) -> pd.DataFrame:
    """Soma exponencial causal, com memória finita até peso de 1%.

    Uma lacuna invalida o API enquanto pertence à memória de k (44/228 dias
    para .90/.98). A origem do histórico assume estado zero; não existe
    imputação de chuva. A implementação numérica usa zero provisório, mas
    mascara toda saída que depende de uma observação ausente.
    """
    feats = {}
    if diaria.empty:
        return pd.DataFrame(index=diaria.index)
    diaria = diaria.reindex(pd.date_range(diaria.index.min(), diaria.index.max(), freq="24h"))
    for macro in diaria.columns:
        serie = diaria[macro]
        for k in decaimentos:
            if not 0 < k < 1:
                raise ValueError("Decaimento do API deve estar entre 0 e 1.")
            memoria = math.ceil(math.log(.01) / math.log(k))
            valores = serie.fillna(0.0)
            estado = valores.ewm(alpha=1-k, adjust=False).mean() / (1-k)
            estado -= valores.iloc[0] * k ** (np.arange(len(serie)) + 1) / (1-k)
            api = estado - k**memoria * estado.shift(memoria, fill_value=0)
            completo = serie.isna().rolling(memoria, min_periods=1).sum().eq(0)
            feats[f"api_{macro}_k{int(k * 100)}"] = api.where(completo)
    return pd.DataFrame(feats, index=diaria.index)


def juntar_api_em_horas(api: pd.DataFrame, horas: pd.DatetimeIndex) -> pd.DataFrame:
    """Para cada hora t, o API do último período diário ENCERRADO antes de t.

    O rótulo do período diário é o início (12 UTC); o período encerra 24h
    depois. merge_asof com o timestamp de encerramento garante causalidade.
    """
    encerra = api.copy()
    encerra.index = (encerra.index + pd.Timedelta(hours=24)).as_unit("ns")
    encerra = encerra.sort_index()
    alvo = pd.DataFrame(index=pd.DatetimeIndex(horas).as_unit("ns"))
    return pd.merge_asof(
        alvo, encerra, left_index=True, right_index=True, direction="backward"
    )
