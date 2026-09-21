"""Ingestão incremental para o run ao vivo.

O pipeline das Fases 1-8 é retrospectivo: reconstrói tudo do cache. Para uma
estimativa durante o evento só interessa a cauda recente, então aqui cada
fonte é buscada apenas nos meses/dias que faltam e costurada ao interim já
consolidado. O QC é o MESMO das Fases 2 — nenhuma regra é reimplementada.
"""

from __future__ import annotations

import datetime as dt

import pandas as pd

from ..ingest.ana_soap import fetch_month
from ..ingest.common import RAW, ROOT, get, load_config, make_client
from ..qc import flags
from ..qc.ana import para_grade_horaria, qc_15min
from ..qc.ons import COLUNAS_VALOR, USINAS

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
    desde = (hist["ts_utc"].max().tz_convert(None).date().replace(day=1))
    meses = _meses_desde(desde, hoje)

    partes = []
    with make_client() as client:
        for est in estacoes:
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

    recente = pd.concat(partes, ignore_index=True)
    corte = recente["ts_utc"].min()
    out = pd.concat([hist[hist["ts_utc"] < corte], recente], ignore_index=True)
    return out.sort_values(["codigo", "ts_utc"]).reset_index(drop=True)


def ons_recente(hoje: dt.date | None = None) -> pd.DataFrame:
    """Baixa os parquets mensais do ONS ainda não consolidados e aplica o QC da Fase 2.

    O ONS republica o arquivo do mês corrente várias vezes ao dia; o catálogo
    pode trazer recursos homônimos, então vale o de last_modified mais recente.
    """
    hoje = hoje or dt.date.today()
    cfg_qc, cfg_ing = load_config("qc"), load_config("ingest")
    romp = cfg_qc["rompimento_14julho"]

    hist = pd.read_parquet(INTERIM / "ons_hourly.parquet")
    desde = hist["ts_utc"].max().tz_convert(None).date().replace(day=1)
    alvos = {f"{a}-{m:02d}" for a, m in _meses_desde(desde, hoje)}

    brutos = []
    with make_client() as client:
        resp = get(client, f"{cfg_ing['ons']['ckan_base']}/package_show",
                   params={"id": "dados_hidrologicos_ho"})
        recursos = [r for r in resp.json()["result"]["resources"]
                    if r.get("format", "").upper() == "PARQUET"]
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
            dest.write_bytes(get(client, r["url"]).content)
            df = pd.read_parquet(dest, columns=["cod_usina", "din_instante"] + COLUNAS_VALOR)
            df["cod_usina"] = pd.to_numeric(df["cod_usina"], errors="coerce")
            brutos.append(df[df["cod_usina"].isin(USINAS)])
            print(f"[live.ons] {sufixo}: {r.get('last_modified')}", flush=True)

    df = pd.concat(brutos, ignore_index=True)
    df["dt_local"] = pd.to_datetime(df["din_instante"], errors="coerce")
    df = df.dropna(subset=["dt_local"])
    df["usina"] = df["cod_usina"].map(USINAS)

    partes = []
    for _, grupo in df.groupby("usina"):
        g = grupo.copy()
        g["flag_fora_de_ordem"] = flags.flag_fora_de_ordem(g["dt_local"])
        g["flag_duplicado"] = flags.flag_duplicado(g["dt_local"])
        g = g.sort_values("dt_local")
        g = g[~g["flag_duplicado"]]
        g["flag_defluente_zero"] = flags.flag_zero(g["val_vazaodefluente"])
        g.loc[g["flag_defluente_zero"], "val_vazaodefluente"] = pd.NA
        g.loc[g["val_vazaoafluente"] == 0, "val_vazaoafluente"] = pd.NA
        g["flag_stuck"] = flags.flag_stuck(g["val_vazaodefluente"],
                                           cfg_qc["stuck_min_steps_nivel"] // 2)
        partes.append(g)
    novo = pd.concat(partes, ignore_index=True)

    # hora-fim -> início do período; local fixo -> UTC (idêntico à Fase 2)
    novo["ts_utc"] = ((novo["dt_local"] - pd.Timedelta(hours=1))
                      .dt.tz_localize(f"Etc/GMT+{-cfg_qc['tz_fixo_horas']}")
                      .dt.tz_convert("UTC"))
    novo["flag_dst_incerto"] = flags.flag_dst_incerto(pd.DatetimeIndex(novo["ts_utc"]))
    novo["flag_pos_rompimento"] = (
        (novo["usina"] == romp["usina"])
        & (novo["ts_utc"] >= pd.Timestamp(romp["inicio"], tz="UTC"))
        & (novo["ts_utc"] <= pd.Timestamp(romp["fim"], tz="UTC"))
    )
    colunas = (["usina", "cod_usina", "ts_utc"] + COLUNAS_VALOR
               + [c for c in novo.columns if c.startswith("flag_")])
    novo = novo[colunas].rename(columns={
        "val_vazaoafluente": "afluente_m3s", "val_vazaodefluente": "defluente_m3s",
        "val_vazaoturbinada": "turbinada_m3s", "val_vazaovertida": "vertida_m3s",
        "val_nivelmontante": "nivel_montante_m",
    })
    corte = novo["ts_utc"].min()
    out = pd.concat([hist[hist["ts_utc"] < corte], novo], ignore_index=True)
    print(f"[live.ons] defluência até {out['ts_utc'].max()}", flush=True)
    return out.sort_values(["usina", "ts_utc"]).reset_index(drop=True)
