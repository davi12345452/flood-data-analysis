"""Previsões com relógio comum e latência explícita no treino e na inferência.

Replay com atrasos assumidos, não arquivo de disponibilidade histórica.
Não preenche lacunas. Ajuste durante o evento só usa erros já amadurecidos
e depende de aprovação na comparação histórica.
"""

from __future__ import annotations

import json

import lightgbm as lgb
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from ..ingest.common import ROOT, load_config
from ..models import baselines, gbm
from .adaptation import corrigir
from .uncertainty import cobertura_recente, faixa_empirica

HORIZONTES = (3, 6, 9, 12)
MOTORES = ("linear", "gbm_nivel", "gbm_delta")
ATRASOS = {"chuva": 5, "ons": 1, "api": 24, "disponibilidade": 1}
ALVOS = {86510000: ("Muçum", "mu"), 86720000: ("Encantado", "en"),
         86879300: ("Estrela", "es")}


def features_disponiveis(frame: pd.DataFrame) -> pd.DataFrame:
    """Deslocamento por TEMPO, inclusive em grades com buracos.

    Chuva horária já termina em t-1 no pool. API: margem adicional de 24h
    sobre o período encerrado; hipótese conservadora, não latência medida.
    Disponibilidade usa a hora anterior, pois a hora t ainda não terminou.
    Cota instantânea em t é mantida; atraso de transmissão não reconstruído.
    """
    out = frame.copy()
    for col in frame:
        horas = (ATRASOS["chuva"] if col.startswith("chuva_") else
                 ATRASOS["ons"] if "defluente" in col else
                 ATRASOS["api"] if col.startswith("api_") else
                 ATRASOS["disponibilidade"] if col.startswith("disp_") else 0)
        if horas:
            serie = frame[col].copy()
            serie.index = serie.index + pd.Timedelta(hours=horas)
            out[col] = serie.reindex(frame.index)
    return out


def dataset_operacional(frame: pd.DataFrame, ds: pd.DataFrame,
                       codigo: int) -> pd.DataFrame:
    cols = gbm.colunas_features(ds)
    # Apenas postos do subconjunto próprio/montante já definido no dataset.
    apelidos = [c.removeprefix("nivel_") for c in cols if c.startswith("nivel_")]
    cols += [c for c in frame if c not in cols
             and any(c.startswith(f"posto_{ap}_") for ap in apelidos)]
    out = features_disponiveis(frame[cols]).reindex(ds.index)
    nivel = frame[f"nivel_{baselines.PROPRIA[codigo]}"]
    for h in HORIZONTES:
        # Busca exata em t+h: shift posicional atravessaria lacunas.
        out[f"y_{h}h"] = nivel.reindex(ds.index + pd.Timedelta(hours=h)).to_numpy()
    out[["janela_id", "tipo"]] = ds[["janela_id", "tipo"]]
    return out


def treino_antes(ds: pd.DataFrame, corte: pd.Timestamp, h: int) -> pd.DataFrame:
    """Só janelas inteiras anteriores e rótulos conhecidos antes do corte."""
    fins = ds.groupby("janela_id").apply(lambda g: g.index.max(), include_groups=False)
    janelas = fins[fins + pd.Timedelta(hours=h) < corte].index
    return ds[ds["janela_id"].isin(janelas)
              & (ds.index + pd.Timedelta(hours=h) < corte)]


def prever_modelo(train: pd.DataFrame, test: pd.DataFrame, codigo: int,
                  h: int, motor: str) -> pd.Series:
    if motor == "linear":
        return baselines.regressao_lags(train, test, codigo, h)
    if motor == "ridge_montante":
        return prever_montante(train, test, codigo, h)
    if motor not in (*MOTORES, "gbm_postos"):
        raise ValueError(f"Motor desconhecido: {motor}")
    cols = gbm.colunas_features(train)
    if motor == "gbm_postos" and not any(c.startswith("posto_") for c in cols):
        raise ValueError("GBM de postos requer features de chuva ANA; reconstrua o pool.")
    if motor != "gbm_postos":
        # Mantém exatamente as entradas dos GBMs já publicados.
        cols = [c for c in cols if not c.startswith("posto_")]
    propria = f"nivel_{baselines.PROPRIA[codigo]}"
    alvo = f"y_{h}h"
    train = train.dropna(subset=[alvo, propria]).copy()
    if motor in ("gbm_delta", "gbm_postos"):
        train[alvo] = train[alvo] - train[propria]
    cfg = load_config("model")
    tr, ev = gbm._split_early_stopping(train, cfg["valid_frac_janelas"])
    if len(tr) < 500 or len(ev) < 50:
        tr, ev = train, None
    modelo = lgb.LGBMRegressor(**(cfg["lgbm"] | {"n_jobs": 4, "random_state": 42}))
    kwargs = {} if ev is None else {
        "eval_set": [(ev[cols], ev[alvo])],
        "callbacks": [lgb.early_stopping(cfg["early_stopping_rounds"], verbose=False)],
    }
    modelo.fit(tr[cols], tr[alvo], **kwargs)
    # Sensores auxiliares podem faltar; o nível do alvo tem de ser atual.
    ok = test[propria].notna()
    pred = pd.Series(float("nan"), index=test.index, name="pred")
    if ok.any():
        pred.loc[ok] = modelo.predict(test.loc[ok, cols])
        if motor in ("gbm_delta", "gbm_postos"):
            pred.loc[ok] += test.loc[ok, propria]
    return pred


def prever_montante(train: pd.DataFrame, test: pd.DataFrame, codigo: int,
                    h: int) -> pd.Series:
    """Ridge da variação de cota com todas as réguas do subconjunto físico.

    Alpha fixo, sem ajuste ao evento corrente. Padronização só no treino.
    Sem fabricar cotas em falhas: usa o linear anterior quando falta uma das
    réguas adicionais. Não mistura réguas a jusante do alvo.
    """
    cols = [c for c in train if c.startswith(("nivel_", "dnivel_1h_", "dnivel_3h_"))]
    propria = f"nivel_{baselines.PROPRIA[codigo]}"
    alvo = f"y_{h}h"
    tr = train.dropna(subset=cols + [alvo])
    pred = baselines.regressao_lags(train, test, codigo, h)
    if len(tr) < 500:
        return pred
    modelo = make_pipeline(StandardScaler(), Ridge(alpha=100.0))
    modelo.fit(tr[cols], tr[alvo] - tr[propria])
    ok = test[cols].notna().all(axis=1)
    if ok.any():
        pred.loc[ok] = test.loc[ok, propria] + modelo.predict(test.loc[ok, cols])
    return pred


def configuracao_validada() -> dict:
    arquivo = ROOT / "reports/12_live_modelos.json"
    if not arquivo.exists():
        arquivo = ROOT / "reports/11_live_modelos.json"
    if not arquivo.exists():
        raise RuntimeError("Rode python -m src.live.evaluate antes de emitir previsões.")
    manifesto = json.loads(arquivo.read_text())
    if manifesto["atrasos_h"] != ATRASOS:
        raise RuntimeError("Latências alteradas: refaça a validação antes de prever.")
    return manifesto


def escolhas_validadas() -> dict[tuple[int, int], str]:
    escolhas = {(int(m["codigo"]), int(m["h"])): m["motor"]
                for m in configuracao_validada()["modelos"]}
    escolhas.update({(codigo, 3): "linear" for codigo in ALVOS})
    return escolhas


def rodada(frame: pd.DataFrame, horas: int = 48) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Previsão por horizonte e replay por janela de TEMPO de validade.

    Cada alvo usa sua última hora com cota, sem prender outras estações à
    régua que parou de transmitir. O replay usa
    48h de observações, com referências até 12h anteriores a essa janela.
    """
    escolhas = escolhas_validadas()
    manifesto = configuracao_validada()
    politicas = {(m["codigo"], m["h"]): m for m in manifesto["modelos"]}
    faixas = {(m["codigo"], m["h"], m["subida_rapida"]): m for m in manifesto.get("faixas", [])}
    disponiveis = features_disponiveis(frame)
    linhas, retrospecto = [], []
    for codigo, (nome, ap) in ALVOS.items():
        fim = frame[f"nivel_{ap}"].last_valid_index()
        if fim is None:
            continue
        inicio = fim - pd.Timedelta(hours=horas)
        inicio_ref = inicio - pd.Timedelta(hours=max(HORIZONTES))
        original = pd.read_parquet(ROOT / f"data/processed/dataset_{codigo}.parquet")
        original = original.set_index("ts_utc")
        ds = dataset_operacional(frame, original, codigo)
        cols = gbm.colunas_features(ds)
        test = disponiveis.loc[inicio_ref:fim, cols]
        for h in HORIZONTES:
            motor = escolhas[(codigo, h)]
            train = treino_antes(ds, inicio_ref, h)
            pred = prever_modelo(train, test, codigo, h, motor)
            politica = politicas.get((codigo, h), {})
            adaptado = corrigir(pred, frame[f"nivel_{ap}"], h,
                               ganho=politica.get("ganho", 0),
                               janela_h=politica.get("janela_h", 6),
                               min_amostras=politica.get("min_amostras", 3))
            valor = adaptado.loc[fim, "previsto_cm"]
            velocidade = frame.loc[fim, f"dnivel_1h_{ap}"]
            p99 = train[f"dnivel_1h_{ap}"].quantile(.99)
            rapido = bool(pd.notna(velocidade) and velocidade > p99)
            faixa = faixa_empirica(valor, velocidade, faixas.get((codigo, h, rapido)))
            margens = pd.Series(float("nan"), index=test.index)
            for t in test.index:
                v = test.loc[t, f"dnivel_1h_{ap}"]
                raro_t = bool(pd.notna(v) and v > p99)
                f = faixa_empirica(adaptado.loc[t, "previsto_cm"], v,
                                  faixas.get((codigo, h, raro_t)))
                if pd.notna(f["superior_cm"]):
                    margens.loc[t] = (f["superior_cm"] - f["inferior_cm"]) / 2
            cobertura = cobertura_recente(adaptado.previsto_cm, margens,
                                          frame[f"nivel_{ap}"], h).loc[fim]
            if (faixa["faixa_status"] == "empirica_sem_garantia"
                    and cobertura.n_faixa_recente >= 3 and cobertura.cobertura_recente < .8):
                faixa.update(inferior_cm=float("nan"), superior_cm=float("nan"),
                             faixa_status="cobertura_recente_baixa")
            linhas.append({"alvo": nome, "codigo": codigo, "motor": motor, "h": h,
                           "t_ref_utc": fim, "nivel_em_t": frame.loc[fim, f"nivel_{ap}"],
                           "previsto_cm": valor, "valido_para_utc": fim + pd.Timedelta(hours=h),
                           "status": "estimativa" if pd.notna(valor) else "dados_insuficientes",
                           "treino_ultima_ref": train.index.max(),
                           "base_cm": pred.loc[fim], "ajuste_cm": adaptado.loc[fim, "ajuste_cm"],
                           "n_ajuste": adaptado.loc[fim, "n_ajuste"],
                           "subida_rapida": rapido, "velocidade_cm_h": velocidade,
                           "idade_cota_h": (frame.index.max() - fim).total_seconds() / 3600,
                           "cobertura_recente": cobertura.cobertura_recente,
                           "n_faixa_recente": int(cobertura.n_faixa_recente),
                           **faixa})
            validade = pred.index + pd.Timedelta(hours=h)
            obs = frame[f"nivel_{ap}"].reindex(validade)
            bt = pd.DataFrame({"t_ref_utc": pred.index, "valido_para": validade,
                               "previsto_cm": adaptado.previsto_cm.to_numpy(),
                               "base_cm": pred.to_numpy(), "ajuste_cm": adaptado.ajuste_cm.to_numpy(),
                               "n_ajuste": adaptado.n_ajuste.to_numpy(), "observado_cm": obs.to_numpy()})
            bt = bt[(bt.valido_para > inicio) & (bt.valido_para <= fim)].dropna()
            bt = bt.assign(alvo=nome, motor=motor, h=h, tipo="replay_latencia_assumida")
            bt["erro_cm"] = bt.previsto_cm - bt.observado_cm
            retrospecto.append(bt)
    if not linhas:
        raise ValueError("Nenhum alvo possui cota observada.")
    return pd.DataFrame(linhas), pd.concat(retrospecto, ignore_index=True)
