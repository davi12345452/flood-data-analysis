"""Coordenadas e áreas de drenagem oficiais das estações alvo.

Fonte: inventário telemétrico do SOAP legado da ANA (ListaEstacoesTelemetricas),
materializado em data/raw/ana_soap/inventario.parquet com proveniência.
Saída: data/reference/estacoes_coords.csv.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pandas as pd

from ..ingest.common import RAW, REFERENCE, get, is_cached, load_config, make_client, write_parquet

# Campos disponíveis no XML (não há área de drenagem — validação de áreas
# usa o RIGEO e a literatura na Fase 3).
CAMPOS = {
    "CodEstacao": "codigo",
    "NomeEstacao": "nome_ana",
    "Latitude": "lat",
    "Longitude": "lon",
    "Altitude": "altitude_m",
    "NomeRio": "rio_ana",
    "Municipio-UF": "municipio",
    "Operadora": "operadora",
    "StatusEstacao": "status",
}


def baixar_inventario(force: bool = False) -> pd.DataFrame:
    dest = RAW / "ana_soap" / "inventario.parquet"
    if is_cached(dest) and not force:
        return pd.read_parquet(dest)
    cfg = load_config("ingest")["ana_soap"]
    url = f"{cfg['base_url']}/ListaEstacoesTelemetricas"
    with make_client() as client:
        resp = get(client, url, params={"statusEstacoes": "", "origem": ""})
    linhas = []
    for el in ET.fromstring(resp.content).iter():
        if el.tag.endswith("Table"):
            reg = {}
            for filho in el:
                tag = filho.tag.split("}")[-1]
                if tag in CAMPOS:
                    reg[CAMPOS[tag]] = (filho.text or "").strip() or None
            if reg.get("codigo"):
                linhas.append(reg)
    df = pd.DataFrame(linhas)
    for col in ("lat", "lon", "altitude_m"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["codigo"] = df["codigo"].astype(int)
    write_parquet(df, dest, url=url, params={"statusEstacoes": "", "origem": ""})
    return df


def run() -> pd.DataFrame:
    inventario = baixar_inventario()
    estacoes = load_config("stations")["estacoes_fluviometricas"]
    alvo = pd.DataFrame(estacoes)[["nome", "codigo", "rio", "papel"]]
    out = alvo.merge(inventario.drop_duplicates("codigo"), on="codigo", how="left")
    faltando = out[out["lat"].isna()]
    if not faltando.empty:
        # Estação sem coordenada só é aceitável se também não tem nenhum
        # registro no SOAP (caso Bom Retiro do Sul, documentado no config).
        import pyarrow.parquet as pq

        def total_registros(codigo: int) -> int:
            pasta = RAW / "ana_soap" / f"estacao={codigo}"
            return sum(pq.read_metadata(f).num_rows for f in pasta.rglob("*.parquet"))

        problema = [n for n, c in zip(faltando["nome"], faltando["codigo"])
                    if total_registros(c) > 0]
        if problema:
            raise RuntimeError(
                f"Estações COM dado mas sem coordenada: {problema} — resolver."
            )
        print(f"[spatial.stations] AVISO: fora do inventário e sem série: "
              f"{faltando['nome'].tolist()} — excluídas do produto espacial")
        out = out[out["lat"].notna()].reset_index(drop=True)
    # Sanidade geográfica: bacia Taquari-Antas
    fora = out[(out["lat"] < -30.2) | (out["lat"] > -28.0)
               | (out["lon"] < -52.8) | (out["lon"] > -49.4)]
    if not fora.empty:
        raise RuntimeError(f"Coordenadas fora da bacia: {fora[['nome', 'lat', 'lon']].to_dict('records')}")
    REFERENCE.mkdir(parents=True, exist_ok=True)
    out.to_csv(REFERENCE / "estacoes_coords.csv", index=False)
    print(f"[spatial.stations] {len(out)} estações em data/reference/estacoes_coords.csv")
    print(out[["nome", "codigo", "lat", "lon", "altitude_m"]].to_string(index=False))
    return out


if __name__ == "__main__":
    run()
