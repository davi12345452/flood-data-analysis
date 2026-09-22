"""Atualização MERGE limitada ao período encerrado e ao cache existente."""

from contextlib import nullcontext

import pandas as pd

from src.live import merge_live


def test_merge_recente_reutiliza_cache_e_nao_pede_diario_futuro(tmp_path, monkeypatch):
    monkeypatch.setattr(merge_live, "RAW", tmp_path)
    monkeypatch.setattr(merge_live, "make_client", lambda: nullcontext(None))
    monkeypatch.setattr(merge_live, "load_config", lambda _: {
        "merge": {"base_url": "https://example.test", "pausa_s": 0}})
    chamadas = []
    monkeypatch.setattr(merge_live.merge, "_baixar", lambda client, url, dest, pausa, fal:
                        chamadas.append((url, dest)) or False)
    monkeypatch.setattr(merge_live.merge, "_reportar", lambda *args: None)
    cache = tmp_path / "merge/hourly/2026/09/21/MERGE_CPTEC_2026092100.grib2"
    cache.parent.mkdir(parents=True)
    cache.write_bytes(b"cache")
    agora = pd.Timestamp("2026-09-22 00:00", tz="UTC")
    merge_live.baixar_recentes(agora, dias=1)
    horarios = [(u, p) for u, p in chamadas if "/HOURLY/" in u]
    diarios = [(u, p) for u, p in chamadas if "/DAILY/" in u]
    assert len(horarios) == 25
    assert horarios[0][1] == cache
    assert horarios[-1][0].endswith("MERGE_CPTEC_2026092200.grib2")
    assert len(diarios) == 1
    assert diarios[0][0].endswith("MERGE_CPTEC_20260921.grib2")
