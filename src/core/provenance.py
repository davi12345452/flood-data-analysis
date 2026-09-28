"""Vínculo verificável entre validação, dados de treino, features e código."""
import hashlib
import json
import platform
from importlib.metadata import version
from pathlib import Path

import pandas as pd

from .paths import ROOT
from .storage import text

VERSION = 1


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def frame_hash(frame: pd.DataFrame) -> str:
    digest = hashlib.sha256()
    digest.update(json.dumps([(str(c), str(d)) for c, d in frame.dtypes.items()]).encode())
    digest.update(pd.util.hash_pandas_object(frame, index=True).values.tobytes())
    return digest.hexdigest()


def runtime() -> dict:
    return {"python": platform.python_version(), "packages": {
        name: version(name) for name in ("numpy", "pandas", "pyarrow", "scikit-learn", "lightgbm")}}


def contract(frame: pd.DataFrame, root: Path = ROOT) -> dict:
    # Relatórios e código de apresentação não entram: alterar um gráfico não
    # invalida modelos. Toda transformação, split e política científica entra.
    dirs = ('core', 'ingest', 'qc', 'spatial', 'features', 'dataset', 'models')
    files = [p for d in dirs for p in (root / 'src' / d).glob('*.py')]
    files += [root / 'src/eval/cv.py']
    files += [root / 'src/live' / f'{n}.py' for n in
              ('operational', 'adaptation', 'uncertainty', 'evaluate', 'improve')]
    files += list((root / 'config').glob('*.yaml'))
    files += [root / 'uv.lock']
    files += list((root / 'data/reference').glob('*'))
    datasets = sorted((root / 'data/processed').glob('dataset_*.parquet'))
    if not datasets:
        raise RuntimeError('Sem datasets para vincular à validação.')
    files += datasets
    cutoff = max(pd.read_parquet(path, columns=['ts_utc']).ts_utc.max()
                 for path in datasets) + pd.Timedelta(hours=24)
    # Inclui toda a história anterior: as features operacionais também leem
    # t-1/t-5/t-24 nas bordas das janelas. Append posterior ao corte é livre.
    history = frame.loc[:cutoff]
    return {'version': VERSION, 'runtime': runtime(),
            'files': {str(p.relative_to(root)): sha256(p) for p in sorted(files) if p.is_file()},
            'feature_schema': [(str(c), str(d)) for c, d in frame.dtypes.items()],
            'training_features_until_utc': cutoff.isoformat(),
            'training_features_sha256': frame_hash(history)}


def validate(expected: dict | None, frame: pd.DataFrame, root: Path = ROOT) -> None:
    if expected is None:
        raise RuntimeError('Manifesto sem contrato de validação; execute src.live.evaluate e improve.')
    current = contract(frame, root)
    # Roundtrip converte tuplas em listas, sem alterar a identidade.
    if json.dumps(current, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise RuntimeError('Dados, features, configuração ou código mudaram desde a validação. '
                           'Execute src.live.evaluate e src.live.improve antes de prever.')


def publish_manifest(value: dict, path: Path) -> None:
    """Guarda versão imutável por conteúdo e atualiza ponteiro de conveniência."""
    content = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    identifier = hashlib.sha256(content.encode()).hexdigest()
    text(content, path.parent / 'model_versions' / f'{identifier}.json')
    text(content, path)
