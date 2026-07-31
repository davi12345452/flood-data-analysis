"""Dataset supervisionado — Fase 5.

Uma tabela por estação alvo em data/processed/dataset_{codigo}.parquet:
- linhas: horas dentro das janelas amostradas (eventos + normais)
- colunas: subconjunto de features do pool (só montante físico da estação),
  rótulos y_{3,6,12,24}h = cota da estação em t+h, e metadados de amostragem
  (janela_id, tipo, evento_id) para a validação cruzada por evento.

Regras anti-vazamento:
- rótulo NaN (sensor caído em t+h) permanece NaN — a linha vale para outros
  horizontes; a Fase 8 reporta cobertura de rótulo nos picos (Armadilha 0).
- nenhuma normalização/imputação aqui: fit de scaler é responsabilidade do
  treino (Fase 6/7), dentro do fold.
- split é por evento (evento_id), nunca aleatório por linha.
"""

from __future__ import annotations

import json

import pandas as pd

from ..ingest.common import ROOT, load_config

PROCESSED = ROOT / "data" / "processed"

APELIDO = {86472000: "jj", 86472600: "st", 86510000: "mu", 86720000: "en",
           86879300: "es", 86895000: "pm", 86950000: "tq"}


def colunas_do_subconjunto(frame: pd.DataFrame, sub: dict) -> list[str]:
    cols: list[str] = []
    for macro in sub["chuva"]:
        cols += [c for c in frame.columns if c.startswith(f"chuva_{macro}_")]
        cols += [c for c in frame.columns if c.startswith(f"api_{macro}_")]
    for ap in sub["estacoes"]:
        cols += [c for c in frame.columns if c.endswith(f"_{ap}")]
    if sub.get("uhes"):
        cols += [c for c in frame.columns if "defluente" in c]
    return cols


def montar_alvo(frame: pd.DataFrame, codigo: int, horizontes: list[int],
                janelas: list[dict], sub: dict) -> pd.DataFrame:
    ap = APELIDO[codigo]
    nivel = frame[f"nivel_{ap}"]

    cols = colunas_do_subconjunto(frame, sub)
    partes = []
    for j in janelas:
        ini, fim = pd.Timestamp(j["inicio"]), pd.Timestamp(j["fim"])
        bloco = frame.loc[ini:fim, cols].copy()
        for h in horizontes:
            bloco[f"y_{h}h"] = nivel.shift(-h).loc[ini:fim]
        bloco["janela_id"] = j["nome"]
        bloco["tipo"] = "evento" if j["nome"].startswith("ev") else "normal"
        partes.append(bloco)
    out = pd.concat(partes)
    # janelas de eventos podem se sobrepor às caudas das vizinhas
    out = out[~out.index.duplicated(keep="first")]
    # linha inútil se não há NENHUM rótulo (ex.: sensor morto o tempo todo)
    tem_rotulo = out[[f"y_{h}h" for h in horizontes]].notna().any(axis=1)
    return out[tem_rotulo].sort_index()


def run() -> None:
    cfg = load_config("dataset")
    frame = pd.read_parquet(PROCESSED / "features_hourly.parquet").set_index("ts_utc")
    janelas = json.loads((PROCESSED / "janelas_amostradas.json").read_text())

    for codigo in cfg["alvos"]:
        sub = cfg["subconjuntos"][codigo]
        ds = montar_alvo(frame, codigo, cfg["horizontes_h"], janelas, sub)
        out = PROCESSED / f"dataset_{codigo}.parquet"
        ds.reset_index().to_parquet(out, index=False)
        n_ev = (ds["tipo"] == "evento").sum()
        cobertura_chuva = ds.filter(like="chuva_").notna().all(axis=1).mean()
        print(f"[dataset] {codigo}: {len(ds)} linhas ({n_ev} evento / "
              f"{len(ds) - n_ev} normal), {ds.shape[1]} colunas, "
              f"chuva horária completa em {cobertura_chuva:.0%} das linhas")


if __name__ == "__main__":
    run()
