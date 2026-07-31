"""Extração das previsões oficiais dos boletins do SACE (baseline externo).

Formatos por época:
- 2023+ : prosa "Em Muçum, o nível ... atingirá a cota de 1222cm nas próximas
  4h." + timestamp de referência no cabeçalho da tabela. Extração completa.
- 2016-2022: "Muçum: O nível, provavelmente, atingirá valores entre: 5,7 e
  6,7 m", sem horizonte explícito no texto. Registrado com o ponto médio da
  faixa e horizonte NaN — fica FORA do score por horizonte (documentado).

A avaliação compara a previsão com a cota observada (interim ANA) no
timestamp de referência + horizonte, ambos em hora local UTC-3 fixa
(mesma convenção validada na Fase 2).
"""

from __future__ import annotations

import re
import unicodedata

import pandas as pd
import pdfplumber

from .common import RAW, ROOT

INTERIM = ROOT / "data" / "interim"

CIDADE_PARA_CODIGO = {
    "mucum": 86510000,
    "encantado": 86720000,
    "estrela": 86879300,       # "Estrela/Lajeado", "Estrela e Lajeado"
    "lajeado": 86879300,
    "taquari": 86950000,
}

RE_REF = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2})")
RE_PROSA = re.compile(
    r"(?:Em|No município de|Nos municípios de)\s+([A-Za-zÀ-ÿ/ e]+?),?\s*o nível do rio Taquari"
    r"[^.]*?cota de\s*(\d+)\s*cm\s*nas próximas\s*(\d+)\s*h",
    re.IGNORECASE,
)
RE_FAIXA = re.compile(
    r"([A-Za-zÀ-ÿ/ ]+?):\s*O nível,?\s*provavelmente,?\s*atingirá valores entre:\s*"
    r"([\d.,]+)\s*e\s*([\d.,]+)\s*m",
    re.IGNORECASE,
)


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return s.strip().lower()


def _cidade_codigo(texto: str) -> int | None:
    chave = _norm(texto)
    for cidade, codigo in CIDADE_PARA_CODIGO.items():
        if cidade in chave:
            return codigo
    return None


def extrair_boletim(caminho) -> list[dict]:
    with pdfplumber.open(caminho) as pdf:
        texto = pdf.pages[0].extract_text() or ""
        if len(pdf.pages) > 1 and "atingir" not in texto:
            texto += "\n" + (pdf.pages[1].extract_text() or "")

    m_ref = RE_REF.search(texto)
    ref = (pd.to_datetime(f"{m_ref.group(1)} {m_ref.group(2)}", format="%d/%m/%Y %H:%M")
           if m_ref else None)

    linhas = []
    for m in RE_PROSA.finditer(texto):
        codigo = _cidade_codigo(m.group(1))
        if codigo is None:
            continue
        linhas.append({
            "codigo": codigo,
            "prevista_cm": float(m.group(2)),
            "horizonte_h": int(m.group(3)),
            "referencia_local": ref,
            "formato": "prosa",
        })
    if not linhas:
        for m in RE_FAIXA.finditer(texto):
            codigo = _cidade_codigo(m.group(1))
            if codigo is None:
                continue
            lo = float(m.group(2).replace(",", "."))
            hi = float(m.group(3).replace(",", "."))
            linhas.append({
                "codigo": codigo,
                "prevista_cm": (lo + hi) / 2 * 100,
                "horizonte_h": None,
                "referencia_local": ref,
                "formato": "faixa",
            })
    return linhas


def run() -> None:
    indice = pd.read_parquet(RAW / "sace" / "index.parquet").dropna(subset=["emissao"])
    registros = []
    sem_extracao = 0
    for _, b in indice.iterrows():
        pdf = RAW / "sace" / "boletins" / str(b["emissao"].year) / b["arquivo"]
        if not pdf.exists():
            continue
        try:
            linhas = extrair_boletim(pdf)
        except Exception as exc:
            print(f"[sace_forecasts] ERRO {b['arquivo']}: {type(exc).__name__}")
            sem_extracao += 1
            continue
        if not linhas:
            sem_extracao += 1
            continue
        for linha in linhas:
            linha["boletim"] = b["arquivo"]
            linha["emissao"] = b["emissao"]
            if linha["referencia_local"] is None:
                linha["referencia_local"] = b["emissao"]  # aproximação: hora de emissão
                linha["formato"] += "+ref_emissao"
            registros.append(linha)

    df = pd.DataFrame(registros)
    df["referencia_utc"] = (
        df["referencia_local"].dt.tz_localize("Etc/GMT+3").dt.tz_convert("UTC")
    )
    df["alvo_utc"] = df["referencia_utc"] + pd.to_timedelta(df["horizonte_h"], unit="h")
    INTERIM.mkdir(parents=True, exist_ok=True)
    df.to_parquet(INTERIM / "sace_previsoes.parquet", index=False)
    total = indice["arquivo"].nunique()
    print(f"[sace_forecasts] {len(df)} previsões de {total - sem_extracao}/{total} "
          f"boletins ({sem_extracao} sem extração)")
    print(df.groupby([df["emissao"].dt.year, "formato"]).size().to_string())


if __name__ == "__main__":
    run()
