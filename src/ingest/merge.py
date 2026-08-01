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

Nota: o arquivo histórico único (DAILY/MERGE_NEW_1998_2024.tar.gz, 4,1 GB)
existe e foi baixado na Fase 3 para data/raw/merge/historico/ — a nota
anterior dizendo o contrário estava errada (listing truncado na Fase 1).

Modo "windows": baixa o horário das janelas amostradas da Fase 5
(data/processed/janelas_amostradas.json).
"""

from __future__ import annotations

import datetime as dt
import sys
import time
from pathlib import Path

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


def run_windows(caminho_json: str, workers: int = 6, margem_h: int = 120) -> None:
    """Baixa o horário para janelas arbitrárias (Fase 5: janelas amostradas).

    O arquivo JSON é uma lista de {nome, inicio, fim} (timestamps ISO, UTC).
    Idempotente; paralelizado com pool moderado (o sequencial levaria ~12h
    para as ~29k horas amostradas).
    """
    import json
    import threading
    from concurrent.futures import ThreadPoolExecutor

    cfg = load_config("ingest")
    base, pausa = cfg["merge"]["base_url"], cfg["merge"]["pausa_s"]
    janelas = json.loads(Path(caminho_json).read_text(encoding="utf-8"))

    pendentes = []
    vistos: set[str] = set()
    for j in janelas:
        # margem: a janela de acumulado mais longa (120h) precisa de chuva
        # ANTES do início da amostragem
        ini = (dt.datetime.fromisoformat(j["inicio"]).replace(tzinfo=None)
               - dt.timedelta(hours=margem_h))
        fim = dt.datetime.fromisoformat(j["fim"]).replace(tzinfo=None)
        ts = ini.replace(minute=0, second=0, microsecond=0)
        while ts <= fim:
            chave = f"{ts:%Y%m%d%H}"
            if chave not in vistos:
                vistos.add(chave)
                pendentes.append(ts)
            ts += dt.timedelta(hours=1)

    local = threading.local()
    faltantes: list[str] = []
    trava = threading.Lock()
    contagem = {"baixados": 0, "feitos": 0}

    def worker(ts: dt.datetime) -> None:
        if not hasattr(local, "client"):
            local.client = make_client()
        dest = (RAW / "merge" / "hourly" / f"{ts:%Y}" / f"{ts:%m}"
                / f"MERGE_CPTEC_{ts:%Y%m%d%H}.grib2")
        fal: list[str] = []
        novo = _baixar(local.client, url_hourly(base, ts), dest, pausa, fal)
        with trava:
            faltantes.extend(fal)
            contagem["baixados"] += int(novo)
            contagem["feitos"] += 1
            if contagem["feitos"] % 2000 == 0:
                print(f"[merge] {contagem['feitos']}/{len(pendentes)} horas", flush=True)

    print(f"[merge] janelas: {len(janelas)}, horas únicas: {len(pendentes)}", flush=True)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(worker, pendentes))
    _reportar("hourly/janelas", contagem["baixados"], faltantes)


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
    if modo == "windows":
        run_windows(sys.argv[2] if len(sys.argv) > 2
                    else "data/processed/janelas_amostradas.json")
