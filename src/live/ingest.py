"""Ingestão incremental para o run ao vivo.

O pipeline das Fases 1-8 é retrospectivo: reconstrói tudo do cache. Para uma
estimativa durante o evento só interessa a cauda recente, então aqui cada
fonte é buscada apenas nos meses/dias que faltam e costurada ao interim já
consolidado. O QC é o MESMO das Fases 2 — nenhuma regra é reimplementada.
"""

from __future__ import annotations

import datetime as dt
import io
import time

import pandas as pd

from ..core.contracts import merge_observations
from ..core.storage import atomic_write
from ..ingest.ana_soap import fetch_month
from ..ingest.common import RAW, ROOT, get, load_config, make_client, write_meta, write_parquet
from ..qc.ana import para_grade_horaria, qc_15min
from ..qc.ons import COLUNAS_VALOR, USINAS, normalizar_hora_24, processar

INTERIM = ROOT / "data" / "interim"


def _meses_desde(inicio: dt.date, hoje: dt.date) -> list[tuple[int, int]]:
    meses, ano, mes = [], inicio.year, inicio.month
    while (ano, mes) <= (hoje.year, hoje.month):
        meses.append((ano, mes))
        ano, mes = (ano + 1, 1) if mes == 12 else (ano, mes + 1)
    return meses


def ana_recente(hoje: dt.date | None = None) -> pd.DataFrame:
    """Busca no SOAP os meses posteriores ao fim do interim e aplica o QC da Fase 2."""
    hoje = hoje or dt.date.today()
    cfg_qc, cfg_ing = load_config("qc"), load_config("ingest")
    estacoes = load_config("stations")["estacoes_fluviometricas"]

    hist = pd.read_parquet(INTERIM / "ana_hourly.parquet")

    partes = []
    with make_client() as client:
        for est in estacoes:
            proprio = hist.loc[hist.codigo == est["codigo"], "ts_utc"]
            ultima = proprio.max() if not proprio.empty else hist.ts_utc.min()
            desde = ultima.tz_convert("Etc/GMT+3").date().replace(day=1)
            meses = _meses_desde(desde, hoje)
            blocos = []
            for ano, mes in meses:
                ini = dt.date(ano, mes, 1)
                fim = min(dt.date(ano + mes // 12, mes % 12 + 1, 1) - dt.timedelta(days=1), hoje)
                try:
                    df = fetch_month(client, cfg_ing["ana_soap"]["base_url"],
                                     est["codigo"], ini, fim)
                except Exception as exc:
                    print(f"[live.ana] FALHA {est['nome']} {ano}-{mes:02d}: {exc}", flush=True)
                    continue
                finally:
                    time.sleep(cfg_ing["ana_soap"].get("pausa_s", 0.6))
                dest = RAW / "ana_live" / str(est["codigo"]) / f"{ano}-{mes:02d}.parquet"
                write_parquet(df, dest, url=cfg_ing["ana_soap"]["base_url"],
                              params={"codigo": est["codigo"], "inicio": str(ini), "fim": str(fim)},
                              partial=True)
                if not df.empty:
                    df["origem"] = f"ano={ano}/mes={mes:02d}"
                    blocos.append(df)
            if not blocos:
                print(f"[live.ana] {est['nome']}: sem dados recentes", flush=True)
                continue
            bruto = pd.concat(blocos, ignore_index=True)
            bruto["dt_local"] = pd.to_datetime(bruto["DataHora"], errors="coerce")
            bruto = bruto.dropna(subset=["dt_local"])
            horario = para_grade_horaria(qc_15min(bruto, cfg_qc), cfg_qc["tz_fixo_horas"])
            horario.insert(0, "codigo", est["codigo"])
            horario.insert(1, "estacao", est["nome"])
            partes.append(horario)
            print(f"[live.ana] {est['nome']}: até {horario['ts_utc'].max()}", flush=True)

    recente = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()
    return merge_observations(hist, recente, "codigo")


def ons_recente(hoje: dt.date | None = None) -> pd.DataFrame:
    """Baixa os parquets mensais do ONS ainda não consolidados e aplica o QC da Fase 2.

    O ONS republica o arquivo do mês corrente várias vezes ao dia; o catálogo
    pode trazer recursos homônimos, então vale o de last_modified mais recente.
    """
    hoje = hoje or dt.date.today()
    cfg_qc, cfg_ing = load_config("qc"), load_config("ingest")

    hist = normalizar_hora_24(pd.read_parquet(INTERIM / "ons_hourly.parquet"))
    desde = hist.groupby("usina").ts_utc.max().min().tz_convert("Etc/GMT+3").date().replace(day=1)
    alvos = {f"{a}-{m:02d}" for a, m in _meses_desde(desde, hoje)}

    brutos = []
    with make_client() as client:
        try:
            resp = get(client, f"{cfg_ing['ons']['ckan_base']}/package_show",
                       params={"id": "dados_hidrologicos_ho"})
            recursos = [r for r in resp.json()["result"]["resources"]
                        if r.get("format", "").upper() == "PARQUET"]
        except Exception as exc:
            print(f"[live.ons] FALHA catálogo: {exc}", flush=True)
            return hist.copy()
        por_mes: dict[str, dict] = {}
        for r in recursos:
            sufixo = r["name"][-7:]
            if sufixo in alvos:
                anterior = por_mes.get(sufixo)
                if anterior is None or (r.get("last_modified") or "") > (anterior.get("last_modified") or ""):
                    por_mes[sufixo] = r
        for sufixo, r in sorted(por_mes.items()):
            dest = RAW / "ons" / "dados_hidrologicos_ho" / f"live_{sufixo}.parquet"
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                content = get(client, r["url"]).content
                df = pd.read_parquet(io.BytesIO(content),
                                     columns=["cod_usina", "din_instante"] + COLUNAS_VALOR)
            except Exception as exc:
                print(f"[live.ons] FALHA {sufixo}: {exc}", flush=True)
                continue
            atomic_write(dest, lambda tmp, data=content: tmp.write_bytes(data))
            write_meta(dest, url=r["url"], partial=True,
                       extra={"last_modified": r.get("last_modified")})
            df["cod_usina"] = pd.to_numeric(df["cod_usina"], errors="coerce")
            brutos.append(df[df["cod_usina"].isin(USINAS)])
            print(f"[live.ons] {sufixo}: {r.get('last_modified')}", flush=True)

    if not brutos:
        return hist.copy()
    bruto = pd.concat(brutos, ignore_index=True)
    if bruto.empty:
        return hist.copy()
    novo = processar(bruto, cfg_qc)
    return merge_observations(hist, novo, "usina")
