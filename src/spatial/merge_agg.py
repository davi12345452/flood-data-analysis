"""Agregação do MERGE/CPTEC por sub-bacia incremental (média ponderada por área).

Método: os polígonos incrementais (subbacias.gpkg) são sobrepostos à grade de
0,1° do MERGE uma única vez, gerando pesos = fração da célula dentro da
sub-bacia. Cada GRIB2 vira então um produto escalar (rápido).

Convenção temporal do MERGE: o GRIB não declara o período de acumulação
(stepType=instant). O rótulo do arquivo é tratado como FIM da acumulação
(diário AAAAMMDD = 24h terminando 12 UTC do dia; horário AAAAMMDDHH = 1h
terminando HH UTC) e o rótulo de saída é deslocado para o INÍCIO do período,
como no resto do projeto. A verificação empírica dessa convenção (correlação
com pluviômetros ANA por defasagem) está em reports/03_espacial.md.

Saídas em data/interim/merge/:
- diaria/ano=YYYY.parquet   (1998 -> hoje; rótulo = início do período de 24h)
- horaria/evento=NOME.parquet (janelas de eventos; rótulo = início da hora)
"""

from __future__ import annotations

import datetime as dt
import re
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from shapely.geometry import box

from ..ingest.common import RAW, REFERENCE, ROOT, load_config

INTERIM_MERGE = ROOT / "data" / "interim" / "merge"
RE_DIA = re.compile(r"MERGE_CPTEC_(\d{8})\.grib2$")
RE_HORA = re.compile(r"MERGE_CPTEC_(\d{10})\.grib2$")


def abrir_precip(caminho: Path) -> xr.DataArray:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ds = xr.open_dataset(caminho, engine="cfgrib", decode_timedelta=True,
                             backend_kwargs={"indexpath": ""})
    nome = next(n for n in ds.data_vars if ds[n].attrs.get("units") == "kg m**-2")
    return ds[nome]


def assinatura_grade(da: xr.DataArray) -> tuple:
    """Identifica a grade: origem, resolução e dimensões. Pesos NUNCA são
    aplicados a uma grade diferente da que os gerou — arquivos das bases
    antigas do MERGE podem mudar de domínio e produzir valores errados em
    silêncio se os índices forem reaproveitados."""
    lats, lons = da.latitude.values, da.longitude.values
    return (len(lats), len(lons), round(float(lats[0]), 3), round(float(lons[0]), 3),
            round(float(lats[1] - lats[0]), 4), round(float(lons[1] - lons[0]), 4))


class PesosPorGrade:
    """Cache de pesos por assinatura de grade."""

    def __init__(self) -> None:
        self._cache: dict[tuple, pd.DataFrame] = {}
        self._unidades = gpd.read_file(REFERENCE / "subbacias.gpkg", layer="incremental")

    def para(self, da: xr.DataArray) -> pd.DataFrame:
        chave = assinatura_grade(da)
        if chave not in self._cache:
            print(f"[merge_agg] nova grade {chave} — calculando pesos", flush=True)
            self._cache[chave] = calcular_pesos(da, self._unidades)
        return self._cache[chave]


def calcular_pesos(da: xr.DataArray, unidades: gpd.GeoDataFrame) -> pd.DataFrame:
    """Pesos célula->sub-bacia para a grade do DataArray dado."""
    lats, lons = da.latitude.values, da.longitude.values
    res = round(float(lats[1] - lats[0]), 4)
    bounds = unidades.total_bounds  # lon em -180..180
    lon360 = lambda x: x % 360

    lat_sel = [(i, la) for i, la in enumerate(lats)
               if bounds[1] - 0.2 <= la <= bounds[3] + 0.2]
    lon_sel = [(j, lo) for j, lo in enumerate(lons)
               if lon360(bounds[0]) - 0.2 <= lo <= lon360(bounds[2]) + 0.2]

    celulas = []
    for i, la in lat_sel:
        for j, lo in lon_sel:
            lo180 = lo - 360 if lo > 180 else lo
            celulas.append({
                "i": i, "j": j,
                "geometry": box(lo180 - res / 2, la - res / 2, lo180 + res / 2, la + res / 2),
            })
    grade = gpd.GeoDataFrame(celulas, crs=unidades.crs)

    # Áreas em projeção equivalente (EPSG:6933) — em graus a distorção de
    # cos(lat) entre o norte e o sul da bacia chega a ~1,5%.
    grade_ea = grade.to_crs(6933)
    unidades_ea = unidades.to_crs(6933)
    pesos = []
    for (_, un), (_, un_ea) in zip(unidades.iterrows(), unidades_ea.iterrows()):
        inter = grade.copy()
        inter["frac"] = grade_ea.geometry.intersection(un_ea.geometry).area / grade_ea.geometry.area
        inter = inter[inter["frac"] > 0]
        total = inter["frac"].sum()
        for _, c in inter.iterrows():
            pesos.append({"codigo": un["codigo"], "nome": un["nome"],
                          "i": c["i"], "j": c["j"], "peso": c["frac"] / total})
    df = pd.DataFrame(pesos)
    print(f"[merge_agg] pesos: {len(df)} pares célula-subbacia", flush=True)
    return df


def agregar_arquivo(caminho: Path, cache: PesosPorGrade) -> dict[int, float] | None:
    try:
        da = abrir_precip(caminho)
        if da.dims != ("latitude", "longitude"):
            raise ValueError(f"dims inesperadas: {da.dims}")
        pesos = cache.para(da)
    except Exception as exc:
        print(f"[merge_agg] ILEGÍVEL {caminho.name}: {type(exc).__name__}: {exc} — registrado")
        return None
    valores = da.values  # (lat, lon)
    out = {}
    for codigo, grupo in pesos.groupby("codigo"):
        v = valores[grupo["i"].values, grupo["j"].values]
        ok = ~np.isnan(v)
        out[int(codigo)] = float(np.sum(v[ok] * grupo["peso"].values[ok])) if ok.any() else np.nan
    return out


def processar_diarios(cache: PesosPorGrade) -> None:
    arquivos = sorted(
        list((RAW / "merge" / "daily_hist").rglob("*.grib2"))
        + list((RAW / "merge" / "daily").rglob("*.grib2"))
    )
    por_ano: dict[int, list[Path]] = {}
    for a in arquivos:
        m = RE_DIA.search(a.name)
        if m:
            por_ano.setdefault(int(m.group(1)[:4]), []).append(a)

    ano_corrente = dt.date.today().year
    destino = INTERIM_MERGE / "diaria"
    destino.mkdir(parents=True, exist_ok=True)
    ilegiveis = []
    for ano, lista in sorted(por_ano.items()):
        out = destino / f"ano={ano}.parquet"
        if out.exists() and ano != ano_corrente:
            continue
        linhas = []
        for a in sorted(lista):
            rotulo = pd.Timestamp(dt.datetime.strptime(RE_DIA.search(a.name).group(1), "%Y%m%d"), tz="UTC")
            valores = agregar_arquivo(a, cache)
            if valores is None:
                ilegiveis.append(a.name)
                continue
            # rótulo do arquivo = fim da acumulação (12 UTC do dia); início = -24h
            inicio = rotulo + pd.Timedelta(hours=12) - pd.Timedelta(hours=24)
            linhas.extend({"ts_utc": inicio, "codigo": c, "chuva_mm": v}
                          for c, v in valores.items())
        pd.DataFrame(linhas).to_parquet(out, index=False)
        print(f"[merge_agg] diária {ano}: {len(lista)} arquivos", flush=True)
    if ilegiveis:
        (INTERIM_MERGE / "ilegiveis_diaria.txt").write_text("\n".join(ilegiveis) + "\n")


def processar_horarios(cache: PesosPorGrade) -> None:
    eventos = load_config("ingest")["janelas_eventos"]
    destino = INTERIM_MERGE / "horaria"
    destino.mkdir(parents=True, exist_ok=True)
    arquivos = sorted((RAW / "merge" / "hourly").rglob("*.grib2"))
    ilegiveis = []
    for ev in eventos:
        out = destino / f"evento={ev['nome']}.parquet"
        if out.exists():
            continue
        ini = pd.Timestamp(ev["inicio"], tz="UTC")
        fim = pd.Timestamp(ev["fim"], tz="UTC") + pd.Timedelta(hours=23)
        linhas = []
        for a in arquivos:
            m = RE_HORA.search(a.name)
            if not m:
                continue
            rotulo = pd.Timestamp(dt.datetime.strptime(m.group(1), "%Y%m%d%H"), tz="UTC")
            if not (ini <= rotulo <= fim):
                continue
            valores = agregar_arquivo(a, cache)
            if valores is None:
                ilegiveis.append(a.name)
                continue
            # rótulo = fim da acumulação horária; início = -1h
            linhas.extend({"ts_utc": rotulo - pd.Timedelta(hours=1), "codigo": c, "chuva_mm": v}
                          for c, v in valores.items())
        pd.DataFrame(linhas).to_parquet(out, index=False)
        print(f"[merge_agg] horária {ev['nome']}: ok", flush=True)
    if ilegiveis:
        (INTERIM_MERGE / "ilegiveis_horaria.txt").write_text("\n".join(ilegiveis) + "\n")


def processar_janelas(cache: PesosPorGrade, caminho_json: Path,
                      margem_h: int = 120) -> None:
    """Agrega o horário das janelas amostradas da Fase 5 (eventos + normais).

    margem_h espelha o download: chuva anterior ao início da amostragem para
    os acumulados longos.
    """
    import json

    janelas = json.loads(Path(caminho_json).read_text(encoding="utf-8"))
    destino = INTERIM_MERGE / "horaria"
    destino.mkdir(parents=True, exist_ok=True)
    ilegiveis = []
    for j in janelas:
        out = destino / f"janela={j['nome']}.parquet"
        if out.exists():
            continue
        ini = pd.Timestamp(j["inicio"]).floor("h") - pd.Timedelta(hours=margem_h)
        fim = pd.Timestamp(j["fim"]).floor("h")
        linhas = []
        ts = ini
        while ts <= fim:
            a = (RAW / "merge" / "hourly" / f"{ts:%Y}" / f"{ts:%m}"
                 / f"MERGE_CPTEC_{ts:%Y%m%d%H}.grib2")
            if a.exists():
                valores = agregar_arquivo(a, cache)
                if valores is None:
                    ilegiveis.append(a.name)
                else:
                    linhas.extend(
                        {"ts_utc": ts - pd.Timedelta(hours=1), "codigo": c, "chuva_mm": v}
                        for c, v in valores.items()
                    )
            ts += pd.Timedelta(hours=1)
        pd.DataFrame(linhas).to_parquet(out, index=False)
        print(f"[merge_agg] janela {j['nome']}: {len(linhas)} linhas", flush=True)
    if ilegiveis:
        (INTERIM_MERGE / "ilegiveis_janelas.txt").write_text("\n".join(ilegiveis) + "\n")


def run(modo: str = "all") -> None:
    cache = PesosPorGrade()
    if modo in ("daily", "all"):
        processar_diarios(cache)
    if modo in ("events", "all"):
        processar_horarios(cache)
    if modo == "windows":
        import sys as _sys
        caminho = (_sys.argv[2] if len(_sys.argv) > 2
                   else ROOT / "data" / "processed" / "janelas_amostradas.json")
        processar_janelas(cache, Path(caminho))


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "all")
