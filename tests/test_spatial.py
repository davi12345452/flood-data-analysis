"""Testes do delineamento e da agregação espacial."""

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import box

from src.spatial.basins import upstream_ids


class TestUpstream:
    def _gdf(self, arestas):
        # arestas: {id: next_down}
        return gpd.GeoDataFrame({
            "HYBAS_ID": list(arestas.keys()),
            "NEXT_DOWN": list(arestas.values()),
            "geometry": [box(0, 0, 1, 1)] * len(arestas),
        })

    def test_cadeia_linear(self):
        gdf = self._gdf({1: 2, 2: 3, 3: 0})
        assert upstream_ids(gdf, 3) == {1, 2, 3}
        assert upstream_ids(gdf, 2) == {1, 2}
        assert upstream_ids(gdf, 1) == {1}

    def test_confluencia(self):
        # dois braços (1->3, 2->3) e exutório 3->4
        gdf = self._gdf({1: 3, 2: 3, 3: 4, 4: 0})
        assert upstream_ids(gdf, 4) == {1, 2, 3, 4}
        assert upstream_ids(gdf, 3) == {1, 2, 3}

    def test_braco_paralelo_nao_entra(self):
        gdf = self._gdf({1: 2, 2: 5, 3: 4, 4: 5, 5: 0})
        assert upstream_ids(gdf, 2) == {1, 2}  # braço 3-4 fica fora


class TestConvencoesTemporais:
    def test_rotulo_diario_vira_inicio_do_periodo(self):
        # arquivo AAAAMMDD acumula 24h terminando 12 UTC do dia:
        # início correto = dia anterior 12 UTC
        rotulo = pd.Timestamp("2024-05-01", tz="UTC")
        inicio = rotulo + pd.Timedelta(hours=12) - pd.Timedelta(hours=24)
        assert inicio == pd.Timestamp("2024-04-30 12:00", tz="UTC")

    def test_rotulo_horario_vira_inicio_do_periodo(self):
        rotulo = pd.Timestamp("2024-05-01 12:00", tz="UTC")
        assert rotulo - pd.Timedelta(hours=1) == pd.Timestamp("2024-05-01 11:00", tz="UTC")


class TestPesos:
    def test_media_ponderada_ignora_nan(self):
        # replica a lógica de agregar_arquivo
        valores = np.array([10.0, np.nan, 30.0])
        pesos = np.array([0.5, 0.3, 0.2])
        ok = ~np.isnan(valores)
        resultado = float(np.sum(valores[ok] * pesos[ok]))
        assert resultado == pytest.approx(10.0 * 0.5 + 30.0 * 0.2)

    def test_pesos_reais_somam_um(self):
        from pathlib import Path
        if not Path("data/reference/subbacias.gpkg").exists():
            pytest.skip("subbacias.gpkg ainda não gerado")
        amostra = next(Path("data/raw/merge/daily").rglob("*.grib2"), None)
        if amostra is None:
            pytest.skip("sem GRIB2 de amostra")
        from src.spatial.merge_agg import abrir_precip, calcular_pesos
        unidades = gpd.read_file("data/reference/subbacias.gpkg", layer="incremental")
        pesos = calcular_pesos(abrir_precip(amostra), unidades)
        somas = pesos.groupby("codigo")["peso"].sum()
        assert np.allclose(somas, 1.0, atol=1e-9)
