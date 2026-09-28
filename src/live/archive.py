"""Arquivo completo de uma execução, publicado por rename atômico."""
import hashlib
import json
import shutil

import pandas as pd

from ..core import storage
from ..core.provenance import runtime, sha256
from . import operational


def registrar(frame: pd.DataFrame, prev: pd.DataFrame, bt: pd.DataFrame,
              atualizar: bool, *, root, processed, alvos):
    """Diretório único por execução; mantém entradas e código para auditoria."""
    agora = pd.Timestamp.now(tz="UTC")
    modo = "emissao" if atualizar else "replay"
    pasta = processed / "live_runs" / f"{modo}_{agora:%Y%m%dT%H%M%S%fZ}"
    destino = pasta
    pasta = pasta.with_name(".pending_" + pasta.name)
    pasta.mkdir(parents=True, exist_ok=False)
    prev = prev.copy()
    prev["gerado_em_utc"] = agora
    prev["modo"] = modo
    prev["emitido_em_utc"] = agora if atualizar else pd.NaT
    prev["antecedencia_real_h"] = (
        (prev["valido_para_utc"] - agora).dt.total_seconds() / 3600 if atualizar else float("nan")
    )
    if atualizar:
        prev.loc[prev.antecedencia_real_h <= 0, "status"] = "validade_expirada"
    prev.to_parquet(pasta / "previsoes.parquet", index=False)
    bt.to_parquet(pasta / "replay.parquet", index=False)
    frame.to_parquet(pasta / "features.parquet")
    arquivos = [root / "uv.lock", root / "reports/11_live_modelos.json"]
    if (root / "reports/12_live_modelos.json").exists():
        arquivos.append(root / "reports/12_live_modelos.json")
    arquivos += [processed / f"dataset_{codigo}.parquet" for codigo in alvos]
    arquivos += list((root / "data/reference").glob("*"))
    arquivos += [root / "pyproject.toml"] if (root / "pyproject.toml").exists() else []
    if "modelo_id" in prev:
        arquivos += [processed / "model_cache" / f"{model_id}.pkl"
                     for model_id in prev.modelo_id.dropna().unique()]
    hashes = {}
    for arquivo in arquivos:
        relativo = arquivo.relative_to(root)
        (pasta / relativo).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(arquivo, pasta / relativo)
        hashes[str(arquivo.relative_to(root))] = hashlib.sha256(arquivo.read_bytes()).hexdigest()
    shutil.copytree(root / "src", pasta / "src", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(root / "config", pasta / "config")
    for arquivo in pasta.rglob("*"):
        if arquivo.is_file():
            hashes[str(arquivo.relative_to(pasta))] = sha256(arquivo)
    meta = {"runtime": runtime(), "estado": "completo", "modo": modo, "gerado_em_utc": agora.isoformat(),
            "referencia_utc": prev.t_ref_utc.max().isoformat(),
            "atrasos_assumidos_h": operational.ATRASOS, "sha256": hashes,
            "avaliacao": "replay com latências assumidas; não emissões passadas",
            "sem_correcao_de_vies": bool("ajuste_cm" not in prev or prev.ajuste_cm.eq(0).all())}
    (pasta / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    # Leitores só enxergam a execução depois que todos os artefatos existem.
    pasta.rename(destino)
    pasta = destino
    storage.parquet(prev, processed / "live_v3_previsoes.parquet")
    storage.parquet(bt, processed / "live_v3_replay.parquet")
    return prev, pasta

