"""Delineamento de bacias de contribuição via HydroBASINS nível 8.

Escolha de método (documentada em reports/03_espacial.md): o idea.md pedia MDE
ou ottobacias da ANA. O geoserviço da ANA expõe trechos otto (linhas), não os
polígonos; delinear do MDE seria retrabalho para o uso real — agregar chuva em
células de 0,1° (~90 km²). HydroBASINS lev08 (~130 km²/polígono, derivado de
SRTM pela WWF, topologia NEXT_DOWN) resolve com validação contra áreas oficiais:
Muçum = 16.000/15.937 km² (RIGEO).

Saídas:
- data/reference/subbacias.gpkg, camadas `catchment_total` e `incremental`
- data/reference/subbacias_areas.csv (validação)
"""

from __future__ import annotations

from collections import defaultdict, deque

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from ..ingest.common import RAW, REFERENCE, load_config, make_client, write_meta

HYBAS_URL = "https://data.hydrosheds.org/file/HydroBASINS/standard/hybas_sa_lev08_v1c.zip"
HYBAS_DIR = RAW / "hydrosheds"

# Áreas oficiais para validação (km²)
AREAS_OFICIAIS = {
    86510000: 16000.0,   # Muçum — RIGEO doc/24429 (inventário ANA 2023)
}
TOLERANCIA = 0.10  # 10%


def garantir_hybas() -> gpd.GeoDataFrame:
    shp = HYBAS_DIR / "hybas_sa_lev08_v1c.shp"
    if not shp.exists():
        import io
        import zipfile

        HYBAS_DIR.mkdir(parents=True, exist_ok=True)
        with make_client(timeout_s=300) as client:
            resp = client.get(HYBAS_URL)
            resp.raise_for_status()
        zipfile.ZipFile(io.BytesIO(resp.content)).extractall(HYBAS_DIR)
    if not (HYBAS_DIR / "hybas_sa_lev08_v1c.zip.meta.json").exists() and (
        HYBAS_DIR / "hybas_sa_lev08_v1c.zip"
    ).exists():
        write_meta(HYBAS_DIR / "hybas_sa_lev08_v1c.zip", url=HYBAS_URL,
                   extra={"licenca": "HydroSHEDS v1 — uso livre com atribuição"})
    # bbox generosa da bacia Taquari-Antas
    return gpd.read_file(shp, bbox=(-53.5, -30.5, -49.0, -27.5))


def upstream_ids(gdf: gpd.GeoDataFrame, semente: int) -> set[int]:
    """BFS reversa em NEXT_DOWN a partir do polígono semente (inclusive)."""
    filhos: dict[int, list[int]] = defaultdict(list)
    for hid, nxt in zip(gdf["HYBAS_ID"], gdf["NEXT_DOWN"]):
        filhos[nxt].append(hid)
    achado, fila = {semente}, deque([semente])
    while fila:
        for filho in filhos.get(fila.popleft(), []):
            if filho not in achado:
                achado.add(filho)
                fila.append(filho)
    return achado


def run() -> None:
    estacoes = pd.read_csv(REFERENCE / "estacoes_coords.csv")
    gdf = garantir_hybas()
    print(f"[spatial.basins] {len(gdf)} polígonos lev08 na região")

    catchments = {}
    for _, est in estacoes.iterrows():
        ponto = Point(est["lon"], est["lat"])
        contem = gdf[gdf.contains(ponto)]
        if contem.empty:
            raise RuntimeError(f"{est['nome']}: fora de qualquer polígono lev08")
        ids = upstream_ids(gdf, int(contem.iloc[0]["HYBAS_ID"]))
        sub = gdf[gdf["HYBAS_ID"].isin(ids)]
        catchments[int(est["codigo"])] = {
            "nome": est["nome"],
            "ids": ids,
            "area_km2": float(sub["SUB_AREA"].sum()),
            "geom": sub.union_all(),
        }
        print(f"[spatial.basins] {est['nome']}: {len(ids)} polígonos, "
              f"{catchments[int(est['codigo'])]['area_km2']:.0f} km²")

    # Validação contra áreas oficiais — divergência é erro, não warning
    for codigo, oficial in AREAS_OFICIAIS.items():
        calc = catchments[codigo]["area_km2"]
        erro = abs(calc - oficial) / oficial
        if erro > TOLERANCIA:
            raise RuntimeError(
                f"Área de {catchments[codigo]['nome']} divergente: "
                f"calculada {calc:.0f} km² vs oficial {oficial:.0f} km² ({erro:.0%})"
            )
        print(f"[spatial.basins] validação {catchments[codigo]['nome']}: "
              f"{calc:.0f} vs {oficial:.0f} km² oficial ({erro:+.1%}) OK")

    # Unidades incrementais: bacia da estação menos bacias das estações
    # imediatamente a montante (aninhamento detectado pelos conjuntos de ids)
    incrementais = []
    for codigo, c in catchments.items():
        internas = [o for o in catchments.values()
                    if o["ids"] < c["ids"]]  # subconjunto próprio
        # a montante direta = maximal entre as internas
        diretas = [o for o in internas
                   if not any(o["ids"] < p["ids"] for p in internas)]
        ids_inc = c["ids"] - set().union(*(o["ids"] for o in diretas)) if diretas else c["ids"]
        sub = gdf[gdf["HYBAS_ID"].isin(ids_inc)]
        incrementais.append({
            "codigo": codigo,
            "nome": c["nome"],
            "montante_direta": ", ".join(o["nome"] for o in diretas) or "(cabeceira)",
            "area_incremental_km2": float(sub["SUB_AREA"].sum()),
            "geometry": sub.union_all(),
        })

    gdf_tot = gpd.GeoDataFrame(
        [{"codigo": k, "nome": v["nome"], "area_km2": v["area_km2"], "geometry": v["geom"]}
         for k, v in catchments.items()], crs=gdf.crs,
    )
    gdf_inc = gpd.GeoDataFrame(incrementais, crs=gdf.crs)
    out = REFERENCE / "subbacias.gpkg"
    gdf_tot.to_file(out, layer="catchment_total", driver="GPKG")
    gdf_inc.to_file(out, layer="incremental", driver="GPKG")
    resumo = gdf_inc.drop(columns="geometry").merge(
        gdf_tot.drop(columns="geometry"), on=["codigo", "nome"]
    )
    resumo.to_csv(REFERENCE / "subbacias_areas.csv", index=False)
    print(resumo.to_string(index=False))
    print(f"[spatial.basins] salvo em {out}")


if __name__ == "__main__":
    run()
