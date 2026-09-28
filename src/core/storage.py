"""Publicação atômica de arquivos e exclusão mútua entre escritores locais."""
import fcntl
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path


def atomic_write(dest: Path, writer) -> None:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f'.{dest.name}.', dir=dest.parent)
    os.close(fd)
    tmp = Path(name)
    try:
        writer(tmp)
        with tmp.open('rb') as handle:
            os.fsync(handle.fileno())
        tmp.replace(dest)
    finally:
        tmp.unlink(missing_ok=True)


def parquet(df, dest: Path, *, index=False) -> None:
    atomic_write(dest, lambda tmp: df.to_parquet(tmp, index=index))


def text(value: str, dest: Path) -> None:
    atomic_write(dest, lambda tmp: tmp.write_text(value, encoding='utf-8'))


@contextmanager
def exclusive(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f'Outra execução está alterando os dados: {path}') from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)
