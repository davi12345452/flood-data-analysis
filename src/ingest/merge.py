"""Ingestão do MERGE/CPTEC (chuva em grade, GRIB2).

- Diário: período completo de modelagem (config periodo.inicio → hoje).
- Horário: apenas as janelas de eventos de referência (config janelas_eventos);
  o histórico horário completo (~70k arquivos) não se justifica antes da Fase 5
  definir as amostras de período normal.

Desvio consciente da regra "todo download vira Parquet": GRIB2 é mantido como
GRIB2 em data/raw/ (com .meta.json). Converter grade inteira da América do Sul
para Parquet aqui seria retrabalho — o recorte da bacia e a tabularização
acontecem na Fase 3 com xarray/cfgrib. O que a regra protege (análise nunca
depender de rede) continua garantido pelo cache local.

Nota (regra 8): o "arquivo histórico único 1998-2024" mencionado no idea.md
não existe no FTP — a raiz de GPM/ só tem DAILY/, HOURLY/, CLIMATOLOGY/ etc.
"""

from __future__ import annotations

import datetime as dt
import sys
import time

import httpx

from .common import RAW, download_binary, load_config, make_client


def url_daily(base: str, d: dt.date) -> str:
    return f"{base}/DAILY/{d:%Y}/{d:%m}/MERGE_CPTEC_{d:%Y%m%d}.grib2"


def url_hourly(base: str, ts: dt.datetime) -> str:
    return f"{base}/HOURLY/{ts:%Y}/{ts:%m}/{ts:%d}/MERGE_CPTEC_{ts:%Y%m%d%H}.grib2"


def _baixar(client, url: str, dest, pausa: float, faltantes: list[str]) -> bool:
    try:
        novo = download_binary(client, url, dest)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            faltantes.append(url)
            return False
        raise
    if novo:
        time.sleep(pausa)
    return novo


def run_daily() -> None:
    cfg = load_config("ingest")
    base, pausa = cfg["merge"]["base_url"], cfg["merge"]["pausa_s"]
    inicio = dt.date.fromisoformat(cfg["periodo"]["inicio"])
    fim = dt.date.today() - dt.timedelta(days=1)

    baixados, faltantes = 0, []
    with make_client() as client:
        d = inicio
        while d <= fim:
            dest = RAW / "merge" / "daily" / f"{d:%Y}" / f"MERGE_CPTEC_{d:%Y%m%d}.grib2"
            if _baixar(client, url_daily(base, d), dest, pausa, faltantes):
                baixados += 1
            d += dt.timedelta(days=1)
    _reportar("daily", baixados, faltantes)


def run_events() -> None:
    cfg = load_config("ingest")
    base, pausa = cfg["merge"]["base_url"], cfg["merge"]["pausa_s"]

    baixados, faltantes = 0, []
    with make_client() as client:
        for ev in cfg["janelas_eventos"]:
            ini = dt.datetime.fromisoformat(ev["inicio"])
            fim = dt.datetime.fromisoformat(ev["fim"]) + dt.timedelta(hours=23)
            ts = ini
            while ts <= fim:
                dest = (RAW / "merge" / "hourly" / f"{ts:%Y}" / f"{ts:%m}"
                        / f"MERGE_CPTEC_{ts:%Y%m%d%H}.grib2")
                if _baixar(client, url_hourly(base, ts), dest, pausa, faltantes):
                    baixados += 1
                ts += dt.timedelta(hours=1)
            print(f"[merge] evento {ev['nome']}: ok", flush=True)
    _reportar("hourly/eventos", baixados, faltantes)


def _reportar(rotulo: str, baixados: int, faltantes: list[str]) -> None:
    print(f"[merge] {rotulo}: baixados={baixados} faltantes(404)={len(faltantes)}")
    if faltantes:
        # 404 no FTP é lacuna real da fonte: registrar, nunca fabricar.
        log = RAW / "merge" / f"faltantes_{rotulo.replace('/', '_')}.txt"
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text("\n".join(faltantes) + "\n", encoding="utf-8")
        print(f"[merge] URLs faltantes registradas em {log}")


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "all"
    if modo in ("daily", "all"):
        run_daily()
    if modo in ("events", "all"):
        run_events()
