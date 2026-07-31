"""Cotas de referência (atenção/alerta/inundação) por estação.

Fontes, em ordem:
1. PDF do RIGEO (cotas_sace_taquari_mucum_artigo.pdf) — tabula APENAS Muçum
   (500/900/1800 cm). A premissa do idea.md de que ele cobria todas as
   estações estava errada.
2. Boletim mais recente do SACE — a legenda do gráfico de cada estação declara
   as três cotas. É de onde saem as demais estações.

Muçum é validado nas duas fontes: divergência é erro fatal, não warning.
Saída: data/reference/cotas_referencia.csv (versionada no git).
"""

from __future__ import annotations

import re
import unicodedata

import pandas as pd
import pdfplumber

from .common import RAW, REFERENCE, download_binary, load_config, make_client

RE_ESTACAO = re.compile(r"(\d{8})\s*-\s*([A-ZÀ-Ü][A-ZÀ-Ü\s./]+?):")
RE_INUNDACAO = re.compile(r"Cota de Inunda[çc][ãa]o \((\d+)\s*cm\)")
RE_ALERTA = re.compile(r"Cota de Alerta \((\d+)\s*cm\)")
RE_ATENCAO = re.compile(r"Cota de Aten[çc][ãa]o \((\d+)\s*cm\)")

MUCUM_RIGEO = {"atencao_cm": 500, "alerta_cm": 900, "inundacao_cm": 1800}


def _norm(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().strip()


def extrair_cotas_boletim(caminho_pdf) -> pd.DataFrame:
    """Uma linha por estação. Páginas trazem vários blocos de gráfico; o texto
    é segmentado pelos cabeçalhos "########  - NOME:" e as três cotas são
    procuradas dentro de cada segmento."""
    linhas = []
    with pdfplumber.open(caminho_pdf) as pdf:
        for page in pdf.pages:
            texto = page.extract_text() or ""
            cabecalhos = list(RE_ESTACAO.finditer(texto))
            for i, m_est in enumerate(cabecalhos):
                fim = cabecalhos[i + 1].start() if i + 1 < len(cabecalhos) else len(texto)
                segmento = texto[m_est.start():fim]
                m_inu = RE_INUNDACAO.search(segmento)
                m_ale = RE_ALERTA.search(segmento)
                m_ate = RE_ATENCAO.search(segmento)
                linhas.append({
                    "codigo": int(m_est.group(1)),
                    "nome": _norm(m_est.group(2)).title(),
                    "atencao_cm": int(m_ate.group(1)) if m_ate else None,
                    "alerta_cm": int(m_ale.group(1)) if m_ale else None,
                    "inundacao_cm": int(m_inu.group(1)) if m_inu else None,
                })
    return pd.DataFrame(linhas).drop_duplicates(subset="codigo").reset_index(drop=True)


def run() -> None:
    cfg = load_config("ingest")
    with make_client() as client:
        # 1. RIGEO (proveniência: mantido bruto em data/raw/)
        rigeo_dest = RAW / "rigeo" / "cotas_sace_taquari_mucum_artigo.pdf"
        download_binary(client, cfg["rigeo"]["cotas_pdf_url"], rigeo_dest)

    # 2. Boletim mais recente já baixado pelo módulo sace
    indice_path = RAW / "sace" / "index.parquet"
    if not indice_path.exists():
        raise RuntimeError("Rode a ingestão do SACE antes (src.ingest.sace).")
    indice = pd.read_parquet(indice_path).dropna(subset=["emissao"])
    mais_recente = indice.sort_values("emissao").iloc[-1]
    ano = mais_recente["emissao"].year
    pdf_path = RAW / "sace" / "boletins" / str(ano) / mais_recente["arquivo"]
    if not pdf_path.exists():
        raise RuntimeError(f"Boletim mais recente não baixado: {pdf_path}")

    cotas = extrair_cotas_boletim(pdf_path)
    if cotas.empty:
        raise RuntimeError(f"Nenhuma cota extraída de {pdf_path} — layout mudou?")

    # Validação cruzada de Muçum contra o RIGEO
    mucum = cotas[cotas["codigo"] == 86510000]
    if mucum.empty:
        raise RuntimeError("Muçum ausente no boletim — extração suspeita.")
    for campo, esperado in MUCUM_RIGEO.items():
        obtido = mucum.iloc[0][campo]
        if obtido != esperado:
            raise RuntimeError(
                f"Divergência em Muçum ({campo}): boletim={obtido}, RIGEO={esperado}. "
                "Investigar antes de usar."
            )

    cotas["fonte"] = f"SACE boletim {mais_recente['arquivo']}"
    cotas.loc[cotas["codigo"] == 86510000, "fonte"] += " + RIGEO doc/24429 (validado)"
    REFERENCE.mkdir(parents=True, exist_ok=True)
    out = REFERENCE / "cotas_referencia.csv"
    cotas.to_csv(out, index=False)
    print(f"[reference] {len(cotas)} estações em {out}")
    print(cotas.to_string(index=False))


if __name__ == "__main__":
    run()
