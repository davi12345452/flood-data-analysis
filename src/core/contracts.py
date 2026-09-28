"""Fronteiras de tabelas: UTC, chaves únicas, grade horária e unidades nos nomes."""
import numpy as np
import pandas as pd


def hourly_index(index: pd.Index) -> None:
    if not isinstance(index, pd.DatetimeIndex) or str(index.tz) != 'UTC':
        raise ValueError('A série precisa de um DatetimeIndex em UTC.')
    if index.hasnans or index.has_duplicates or not index.is_monotonic_increasing:
        raise ValueError('Timestamps devem ser válidos, únicos e ordenados.')
    if not index.equals(index.floor('h')):
        raise ValueError('Timestamps devem estar alinhados à hora.')


def observations(df: pd.DataFrame, entity: str) -> None:
    keys = [entity, 'ts_utc']
    if not set(keys).issubset(df):
        raise ValueError(f'Colunas obrigatórias ausentes: {keys}')
    if df[keys].isna().any().any() or df.duplicated(keys).any():
        raise ValueError(f'Chave inválida ou duplicada: {keys}')
    for _, g in df.groupby(entity):
        hourly_index(pd.DatetimeIndex(g.ts_utc).sort_values())
    for col in df:
        if col.endswith(("_cm", "_mm", "_m3s")) and not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Coluna {col} precisa ser numérica na unidade indicada.")
    if np.isinf(df.select_dtypes('number').to_numpy(dtype=float, na_value=np.nan)).any():
        raise ValueError('Observações não podem conter infinito.')


def merge_observations(hist: pd.DataFrame, recent: pd.DataFrame, entity: str) -> pd.DataFrame:
    observations(hist, entity)
    if recent.empty:
        return hist.copy()
    observations(recent, entity)
    # Só substitui chaves recebidas. NaN explícito da fonte permanece NaN;
    # ausência de resposta nunca equivale a exclusão do histórico.
    out = pd.concat([hist, recent], ignore_index=True)
    out = out.drop_duplicates([entity, 'ts_utc'], keep='last')
    return out.sort_values([entity, 'ts_utc']).reset_index(drop=True)
