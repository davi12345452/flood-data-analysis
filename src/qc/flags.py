"""Detectores de anomalia — funções puras, testáveis, que MARCAM e nunca apagam.

Armadilha 0 do projeto: sensores falham preferencialmente durante cheias,
registrando nível zero. Zero de nível nunca é dado válido — vira NaN explícito
com flag, em todas as fontes.
"""

from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

TZ_OFICIAL_SP = ZoneInfo("America/Sao_Paulo")


def flag_zero(valores: pd.Series) -> pd.Series:
    """Zero exato em nível/vazão é falha de sensor (Armadilha 0)."""
    return valores == 0


def flag_stuck(valores: pd.Series, min_passos: int) -> pd.Series:
    """Valor idêntico por >= min_passos consecutivos (NaN não conta como run)."""
    mudou = valores.ne(valores.shift()) | valores.isna()
    grupo = mudou.cumsum()
    tamanho_run = valores.groupby(grupo).transform("size")
    return valores.notna() & (tamanho_run >= min_passos)


def flag_spike(valores: pd.Series, indice_dt: pd.Series, max_delta: float,
               passo: pd.Timedelta = pd.Timedelta("15min")) -> pd.Series:
    """|variação| > max_delta entre amostras consecutivas regulares.

    Só compara pares separados exatamente por `passo`: através de lacunas
    a variação grande pode ser real acumulada, não salto de sensor.
    """
    delta = valores.diff().abs()
    dt_regular = indice_dt.diff() == passo
    return (delta > max_delta) & dt_regular.values


def flag_duplicado(indice_dt: pd.Series) -> pd.Series:
    """Timestamp repetido (mantém a primeira ocorrência sem flag)."""
    return indice_dt.duplicated(keep="first")


def flag_fora_de_ordem(indice_dt: pd.Series, origem: pd.Series | None = None) -> pd.Series:
    """Quebra de monotonicidade dentro de cada resposta da fonte.

    O SOAP da ANA devolve cada mês em ordem DESCENDENTE — isso é convenção,
    não anomalia. A flag marca apenas registros que violam a direção dominante
    do próprio bloco de origem (timestamps realmente embaralhados).
    """
    if origem is None:
        origem = pd.Series(0, index=indice_dt.index)

    def _violacoes(grupo: pd.Series) -> pd.Series:
        if len(grupo) < 3:
            return pd.Series(False, index=grupo.index)
        difs = grupo.diff()
        descendente = (difs.dropna() < pd.Timedelta(0)).mean() > 0.5
        return difs > pd.Timedelta(0) if descendente else difs < pd.Timedelta(0)

    return indice_dt.groupby(origem, group_keys=False).apply(_violacoes).fillna(False)


def flag_dst_incerto(ts_utc: pd.DatetimeIndex) -> np.ndarray:
    """True quando o horário oficial de São Paulo estava em DST (UTC-2).

    Assumimos fuso fixo UTC-3 para as fontes; se a fonte seguia o horário
    oficial, os timestamps dessas janelas (verões até fev/2019) podem estar
    deslocados em 1h. Marcação de incerteza, não correção.
    """
    if ts_utc.tz is None:
        raise ValueError("flag_dst_incerto espera timestamps tz-aware em UTC")
    # DST brasileiro acabou em 2019; corte barato antes da conversão cara.
    candidatos = ts_utc < pd.Timestamp("2019-12-31", tz="UTC")
    out = np.zeros(len(ts_utc), dtype=bool)
    if candidatos.any():
        locais = ts_utc[candidatos].tz_convert(TZ_OFICIAL_SP)
        out[np.where(candidatos)[0]] = np.array(
            [t.utcoffset() == dt.timedelta(hours=-2) for t in locais]
        )
    return out
