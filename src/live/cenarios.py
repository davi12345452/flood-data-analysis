"""Projeção condicionada a cenários de chuva (perfect prognosis).

O GBM operacional só enxerga chuva MERGE com 5h de atraso. Aqui o modelo
recebe, além das mesmas entradas, a chuva que ele ainda não viu: as 5h de
latência do MERGE e as h horas até a validade. No treino essa chuva é a
observada (MERGE); na inferência ela vem de cenários — postos ANA para as
horas já decorridas e modelos meteorológicos (Open-Meteo) para o futuro.

Limites: o treino supõe chuva perfeita, então todo erro da previsão de
chuva passa direto para a cota. Os postos cobrem mal a bacia do Antas
(um posto para ~12.900 km²). O resultado é um leque de cenários, não uma
probabilidade, e não é sistema de alerta.
"""

from __future__ import annotations

import json
import os
import sys

import geopandas as gpd
import httpx
import lightgbm as lgb
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import Point
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from ..ingest.common import REFERENCE, ROOT, load_config
from ..models import baselines, gbm
from .operational import ALVOS, ATRASOS, dataset_operacional, features_disponiveis, treino_antes

HORIZONTES = (6, 12, 18, 24)
LATENCIA = ATRASOS["chuva"]
UNIDADES = {"antas": [86472000], "medio": [86510000, 86720000],
            "baixo": [86879300, 86895000, 86950000]}
POSTOS = {"antas": ["jj"], "medio": ["st", "mu", "en"], "baixo": ["es", "pm", "tq"]}
MODELOS_MET = {"ecmwf_ifs025": "ECMWF", "gfs_seamless": "GFS",
               "icon_seamless": "ICON", "gem_seamless": "GEM"}
TZ_LOCAL = "America/Sao_Paulo"
RUNS = ROOT / "data/processed/live_runs"


def chuva_por_hora(serie_1h: pd.Series) -> pd.Series:
    """Acumulado de t reflete a hora [t-1, t); reindexa para o início da hora."""
    s = serie_1h.copy()
    s.index = s.index - pd.Timedelta(hours=1)
    return s


def chuva_nao_vista(r: pd.Series, h: int) -> pd.DataFrame:
    """Em t: chuva das horas [t-5, t-1] (latência) e [t, t+h-1] (futuro)."""
    passada = r.rolling(LATENCIA, min_periods=LATENCIA).sum()
    passada.index = passada.index + pd.Timedelta(hours=1)
    futura = r.rolling(h, min_periods=h).sum()
    futura.index = futura.index - pd.Timedelta(hours=h - 1)
    return pd.DataFrame({"passada": passada, "futura": futura})


def features_cenario(frame: pd.DataFrame, h: int) -> pd.DataFrame:
    partes = {}
    for u in UNIDADES:
        nv = chuva_nao_vista(chuva_por_hora(frame[f"chuva_{u}_1h"]), h)
        partes[f"nova_passada_{u}"] = nv.passada
        partes[f"nova_futura_{u}"] = nv.futura
    return pd.DataFrame(partes).reindex(frame.index)


def montar(frame: pd.DataFrame, codigo: int) -> pd.DataFrame:
    original = pd.read_parquet(ROOT / f"data/processed/dataset_{codigo}.parquet").set_index("ts_utc")
    ds = dataset_operacional(frame, original, codigo)
    nivel = frame[f"nivel_{baselines.PROPRIA[codigo]}"]
    for h in HORIZONTES:
        ds[f"y_{h}h"] = nivel.reindex(ds.index + pd.Timedelta(hours=h)).to_numpy()
    return ds


def colunas_base(ds: pd.DataFrame) -> list[str]:
    return [c for c in gbm.colunas_features(ds)
            if not c.startswith(("posto_", "nova_"))]


class RidgeChuva:
    """Ridge da variação de cota com interação chuva nova × cota atual.

    A árvore não extrapola além das subidas do treino; a Ridge escala com a
    chuva e com o estado do rio (rio alto responde mais à mesma chuva).
    Sem imputação: só usa linhas com todas as entradas presentes.
    """

    def __init__(self, cols: list[str], propria: str):
        self.propria = propria
        self.feature_name_ = [c for c in cols if c.startswith(("nivel_", "dnivel_", "nova_"))
                              or c in {f"chuva_{u}_24h" for u in UNIDADES}]
        self.modelo = make_pipeline(StandardScaler(), Ridge(alpha=10.0))

    def _x(self, d: pd.DataFrame) -> pd.DataFrame:
        x = d[self.feature_name_].copy()
        for u in UNIDADES:
            x[f"int_{u}"] = d[f"nova_futura_{u}"] * d[self.propria] / 1000
        return x

    def fit(self, d: pd.DataFrame, y: pd.Series) -> RidgeChuva:
        ok = d[self.feature_name_].notna().all(axis=1)
        self.modelo.fit(self._x(d[ok]), y[ok])
        return self

    def predict(self, d: pd.DataFrame) -> np.ndarray:
        pred = np.full(len(d), np.nan)
        ok = d[self.feature_name_].notna().all(axis=1).to_numpy()
        if ok.any():
            pred[ok] = self.modelo.predict(self._x(d[ok]))
        return pred


def treinar(train: pd.DataFrame, codigo: int, h: int, cols: list[str], motor: str = "gbm"):
    propria = f"nivel_{baselines.PROPRIA[codigo]}"
    alvo = f"y_{h}h"
    train = train.dropna(subset=[alvo, propria, *[c for c in cols if c.startswith("nova_")]]).copy()
    train[alvo] = train[alvo] - train[propria]
    if motor == "ridge":
        return RidgeChuva(cols, propria).fit(train, train[alvo])
    cfg = load_config("model")
    tr, ev = gbm._split_early_stopping(train, cfg["valid_frac_janelas"])
    modelo = lgb.LGBMRegressor(**(cfg["lgbm"] | {"n_jobs": 4, "random_state": 42}))
    modelo.fit(tr[cols], tr[alvo], eval_set=[(ev[cols], ev[alvo])],
               callbacks=[lgb.early_stopping(cfg["early_stopping_rounds"], verbose=False)])
    return modelo


def prever(modelo, x: pd.DataFrame, codigo: int) -> np.ndarray:
    base = x[f"nivel_{baselines.PROPRIA[codigo]}"].to_numpy()
    return base + (modelo.predict(x) if isinstance(modelo, RidgeChuva)
                   else modelo.predict(x[modelo.feature_name_]))


# --------------------------------------------------------------- validação

def validar(frame: pd.DataFrame, corte: str = "2025-01-01") -> pd.DataFrame:
    """Treino em janelas antes do corte; teste nas janelas depois dele e na
    cheia de 21/09/2026 (fora do dataset, lida direto do frame).

    Compara o GBM sem chuva nova (equivalente ao operacional), o mesmo com
    chuva observada (limite superior: previsão de chuva perfeita) e com
    chuva futura zerada (cenário "parou de chover").
    """
    disp = features_disponiveis(frame)
    linhas = []
    for codigo, (nome, ap) in ALVOS.items():
        ds = montar(frame, codigo)
        inicio_jan = ds.groupby("janela_id").apply(lambda g: g.index.min(), include_groups=False)
        treino_ids = inicio_jan[inicio_jan < pd.Timestamp(corte, tz="UTC")].index
        base = colunas_base(ds)
        setembro = disp.loc["2026-09-19":"2026-09-25", base].copy()
        nivel = frame[f"nivel_{ap}"]
        for h in HORIZONTES:
            nova = features_cenario(frame, h)
            dsh = ds.join(nova)
            train = dsh[dsh.janela_id.isin(treino_ids)
                        & (dsh.index + pd.Timedelta(hours=h) < pd.Timestamp(corte, tz="UTC"))]
            # Mesmas linhas para as duas variantes: só a entrada de chuva muda.
            train = train.dropna(subset=list(nova.columns))
            testes = {"2025-26": dsh[~dsh.janela_id.isin(treino_ids)],
                      "set/2026": setembro.join(nova).assign(
                          **{f"y_{h}h": nivel.reindex(setembro.index + pd.Timedelta(hours=h)).to_numpy()})}
            m_op = treinar(train, codigo, h, base)
            m_pp = treinar(train, codigo, h, base + list(nova.columns))
            m_rd = treinar(train, codigo, h, base + list(nova.columns), "ridge")
            for conjunto, test in testes.items():
                test = test.dropna(subset=[f"y_{h}h", f"nivel_{ap}", *nova.columns])
                zerada = test.copy()
                zerada[[c for c in nova if "futura" in c]] = 0.0
                y = test[f"y_{h}h"].to_numpy()
                subida = (y - test[f"nivel_{ap}"].to_numpy()) > 50
                for variante, pred in (("sem chuva nova", prever(m_op, test, codigo)),
                                       ("chuva observada", prever(m_pp, test, codigo)),
                                       ("futura zerada", prever(m_pp, zerada, codigo)),
                                       ("ridge chuva observada", prever(m_rd, test, codigo))):
                    erro = pred - y
                    ok = ~np.isnan(erro)
                    erro, sub = erro[ok], subida[ok]
                    linhas.append({"alvo": nome, "h": h, "conjunto": conjunto, "variante": variante,
                                   "n": len(erro), "MAE_cm": np.abs(erro).mean(),
                                   "MAE_subida_cm": np.abs(erro[sub]).mean() if sub.any() else np.nan,
                                   "vies_subida_cm": erro[sub].mean() if sub.any() else np.nan,
                                   "n_subida": int(sub.sum())})
    return pd.DataFrame(linhas)


# --------------------------------------------------------------- cenários ao vivo

def pontos_unidade(passo: float = 0.2) -> dict[str, list[tuple[float, float]]]:
    inc = gpd.read_file(REFERENCE / "subbacias.gpkg", layer="incremental")
    out = {}
    for u, codigos in UNIDADES.items():
        poli = inc[inc.codigo.isin(codigos)].union_all()
        x0, y0, x1, y1 = poli.bounds
        pts = [(round(la, 3), round(lo, 3))
               for la in np.arange(y0 + passo / 2, y1, passo)
               for lo in np.arange(x0 + passo / 2, x1, passo) if poli.contains(Point(lo, la))]
        out[u] = pts
    return out


def previsao_chuva(horas: int = 36) -> pd.DataFrame:
    """Chuva horária média por unidade e modelo (UTC, hora de início)."""
    if os.environ.get("FLOOD_OFFLINE") == "1":
        raise RuntimeError("Modo offline: previsão meteorológica requer rede.")
    linhas = []
    for u, pts in pontos_unidade().items():
        r = httpx.get("https://api.open-meteo.com/v1/forecast", timeout=60, params={
            "latitude": ",".join(str(p[0]) for p in pts),
            "longitude": ",".join(str(p[1]) for p in pts),
            "hourly": "precipitation", "models": ",".join(MODELOS_MET),
            "timezone": "GMT", "past_hours": 12, "forecast_hours": horas}).json()
        r = r if isinstance(r, list) else [r]
        for m, rotulo in MODELOS_MET.items():
            serie = pd.concat([pd.Series(p["hourly"][f"precipitation_{m}"],
                                         index=pd.to_datetime(p["hourly"]["time"], utc=True))
                               for p in r], axis=1).mean(axis=1)
            # Open-Meteo: valor em T é o acumulado da hora anterior a T.
            serie.index = serie.index - pd.Timedelta(hours=1)
            linhas.append(serie.rename("mm").to_frame().assign(unidade=u, modelo=rotulo))
    return pd.concat(linhas).rename_axis("hora_utc").reset_index()


def chuva_postos(frame: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({u: pd.concat([chuva_por_hora(frame[f"posto_{p}_1h"]) for p in ps], axis=1)
                        .mean(axis=1) for u, ps in POSTOS.items()})


def referencia(frame: pd.DataFrame, base: list[str], ap: str, postos: pd.DataFrame,
               recuo_max_h: int = 3) -> pd.Timestamp:
    """Última hora com o alvo, todas as réguas do subconjunto e a chuva das
    horas de latência presentes. Réguas de montante chegam com uma hora de
    atraso; sem isso a Ridge descarta justamente o sinal da onda que vem.
    Sem dado completo no recuo máximo, usa a última cota do alvo."""
    fim = frame[f"nivel_{ap}"].last_valid_index()
    reguas = [c for c in base if c.startswith("nivel_")]
    for recuo in range(recuo_max_h + 1):
        t = fim - pd.Timedelta(hours=recuo)
        if t not in frame.index or frame.loc[t, reguas].isna().any():
            continue
        horas = pd.date_range(t - pd.Timedelta(hours=LATENCIA), periods=LATENCIA, freq="h")
        chuva_ok = all(chuva_por_hora(frame[f"chuva_{u}_1h"]).reindex(horas)
                       .fillna(postos[u].reindex(horas)).notna().all() for u in UNIDADES)
        if chuva_ok:
            return t
    return fim


def cenarios(frame: pd.DataFrame, prev_chuva: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    disp = features_disponiveis(frame)
    postos = chuva_postos(frame)
    tabela, chuvas = [], []
    for codigo, (nome, ap) in ALVOS.items():
        ds = montar(frame, codigo)
        base = colunas_base(ds)
        t = referencia(frame, base, ap, postos)
        x0 = disp.loc[[t], base]
        # Horas não vistas antes de t: MERGE quando existe, senão postos.
        for h in HORIZONTES:
            nova = features_cenario(frame, h)
            presentes = [c for c in base if x0[c].notna().all()]
            treino = treino_antes(ds.join(nova), t, h)
            modelos = {"gbm": treinar(treino, codigo, h, base + list(nova.columns)),
                       "ridge": treinar(treino, codigo, h, presentes + list(nova.columns), "ridge")}
            horas_passadas = pd.date_range(t - pd.Timedelta(hours=LATENCIA), periods=LATENCIA, freq="h")
            horas_futuras = pd.date_range(t, periods=h, freq="h")
            cenas = {"sem mais chuva": {u: 0.0 for u in UNIDADES}}
            for m, g in prev_chuva.groupby("modelo"):
                cenas[m] = {u: g[g.unidade == u].set_index("hora_utc").mm.reindex(horas_futuras).sum(min_count=h)
                            for u in UNIDADES}
            for cena, futura in cenas.items():
                x = x0.copy()
                for u in UNIDADES:
                    merge = chuva_por_hora(frame[f"chuva_{u}_1h"]).reindex(horas_passadas)
                    x[f"nova_passada_{u}"] = merge.fillna(postos[u].reindex(horas_passadas)).sum(min_count=LATENCIA)
                    x[f"nova_futura_{u}"] = futura[u]
                completa = x.filter(regex="^nova_").notna().all(axis=None)
                for motor, modelo in modelos.items():
                    valor = prever(modelo, x, codigo)[0] if completa else np.nan
                    tabela.append({"alvo": nome, "codigo": codigo, "h": h, "cenario": cena, "motor": motor,
                                   "t_ref_utc": t, "valido_para_utc": t + pd.Timedelta(hours=h),
                                   "nivel_em_t": frame.loc[t, f"nivel_{ap}"], "previsto_cm": valor})
                chuvas.append({"alvo": nome, "h": h, "cenario": cena,
                               **{f"passada_{u}": x[f"nova_passada_{u}"].iloc[0] for u in UNIDADES},
                               **{f"futura_{u}": futura[u] for u in UNIDADES}})
    return pd.DataFrame(tabela), pd.DataFrame(chuvas)


def figura(frame: pd.DataFrame, tab: pd.DataFrame, destino) -> None:
    cotas = pd.read_csv(REFERENCE / "cotas_referencia.csv").set_index("codigo")
    cores = {"sem mais chuva": "#555555", "ECMWF": "#2a78d6", "GFS": "#3aa35b",
             "ICON": "#d6602a", "GEM": "#8a5cc2"}
    fig, eixos = plt.subplots(len(ALVOS), 1, figsize=(10, 11), sharex=True)
    for ax, (codigo, (nome, ap)) in zip(eixos, ALVOS.items()):
        t = tab[tab.codigo == codigo].t_ref_utc.iloc[0]
        obs = frame[f"nivel_{ap}"].loc[t - pd.Timedelta(hours=36):t]
        ax.plot(obs.index.tz_convert(TZ_LOCAL), obs, color="black", lw=2, label="observado")
        for (cena, motor), g in tab[tab.codigo == codigo].groupby(["cenario", "motor"], sort=False):
            xs = [t, *g.valido_para_utc]
            ys = [g.nivel_em_t.iloc[0], *g.previsto_cm]
            # Ridge (acompanha a escala da chuva) em traço cheio; GBM (piso provável) pontilhado.
            ax.plot(pd.DatetimeIndex(xs).tz_convert(TZ_LOCAL), ys, "o-" if motor == "ridge" else "o:",
                    color=cores.get(cena), label=cena if motor == "ridge" else None, ms=4,
                    lw=1.8 if motor == "ridge" else 1, alpha=1 if motor == "ridge" else .6)
        for c, estilo in (("atencao_cm", "-."), ("alerta_cm", ":"), ("inundacao_cm", "--")):
            ax.axhline(cotas.loc[codigo, c], color="grey", ls=estilo, lw=1)
            ax.annotate(c.removesuffix("_cm").replace("atencao", "atenção").replace("inundacao", "inundação"),
                        (1.0, cotas.loc[codigo, c]), xycoords=("axes fraction", "data"),
                        ha="right", va="bottom", fontsize=8, color="grey")
        ax.set_title(nome, loc="left")
        ax.set_ylabel("cota (cm)")
        ax.grid(alpha=.3)
    eixos[0].legend(fontsize=8, ncol=3, loc="upper left")
    eixos[-1].set_xlabel("horário local (UTC−3)")
    t_loc = tab.t_ref_utc.max().tz_convert(TZ_LOCAL).strftime("%d/%m/%Y %H:%M")
    fig.suptitle(f"Taquari — cota por cenário de chuva, referência {t_loc} local\n"
                 "traço cheio: Ridge com chuva · pontilhado: GBM (subestima subidas grandes) · "
                 "treino com chuva perfeita", fontsize=11)
    fig.tight_layout()
    fig.savefig(destino, dpi=110)
    plt.close(fig)


def ultima_emissao():
    pastas = sorted(RUNS.glob("emissao_*"), key=lambda p: p.stat().st_mtime)
    return pastas[-1]


def main() -> None:
    pasta = ultima_emissao()
    frame = pd.read_parquet(pasta / "features.parquet")
    if "--validar" in sys.argv:
        m = validar(frame)
        m.to_csv(ROOT / "reports/14_cenarios_validacao.csv", index=False)
        print(m.pivot_table(index=["conjunto", "alvo", "h"], columns="variante",
                            values=["MAE_subida_cm", "vies_subida_cm"]).round(0).to_string())
        return
    chuva = previsao_chuva()
    tab, chuvas = cenarios(frame, chuva)
    carimbo = pd.Timestamp.now(tz="UTC").strftime("%Y%m%dT%H%MZ")
    chuva.to_parquet(pasta / f"chuva_prevista_{carimbo}.parquet", index=False)
    tab.to_parquet(pasta / f"cenarios_{carimbo}.parquet", index=False)
    chuvas.to_parquet(pasta / f"cenarios_chuva_{carimbo}.parquet", index=False)
    destino = ROOT / f"reports/figs/cenarios_{carimbo}.png"
    figura(frame, tab, destino)
    local = tab.assign(validade=tab.valido_para_utc.dt.tz_convert(TZ_LOCAL).dt.strftime("%d/%m %H:%M"))
    print(local.pivot_table(index=["alvo", "validade", "motor"], columns="cenario", values="previsto_cm",
                            sort=False).round(0).to_string())
    print(chuvas[chuvas.alvo == "Muçum"].drop(columns="alvo").round(1).to_string(index=False))
    print(json.dumps({"pasta": str(pasta), "figura": str(destino)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
