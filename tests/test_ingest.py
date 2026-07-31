"""Testes da infraestrutura de ingestão: parsers e idempotência de cache."""

import datetime as dt

import pandas as pd
import pytest

from src.ingest.ana_soap import parse_dados_xml
from src.ingest.common import is_cached, is_partial, month_ranges, write_parquet
from src.ingest.merge import url_daily, url_hourly
from src.ingest.sace import parse_index

XML_AMOSTRA = """<?xml version="1.0" encoding="utf-8"?>
<DataTable xmlns="http://MRCS/">
  <diffgr:diffgram xmlns:msdata="urn:schemas-microsoft-com:xml-msdata"
                   xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1">
    <DocumentElement xmlns="">
      <DadosHidrometereologicos diffgr:id="d1" msdata:rowOrder="0">
        <CodEstacao>86510000</CodEstacao>
        <DataHora>2024-05-02 23:45:00 </DataHora>
        <Vazao>12201.30</Vazao>
        <Nivel>2301.00</Nivel>
        <Chuva>0.20</Chuva>
      </DadosHidrometereologicos>
      <DadosHidrometereologicos diffgr:id="d2" msdata:rowOrder="1">
        <CodEstacao>86510000</CodEstacao>
        <DataHora>2024-05-02 23:30:00 </DataHora>
        <Vazao></Vazao>
        <Nivel>0</Nivel>
        <Chuva/>
      </DadosHidrometereologicos>
    </DocumentElement>
  </diffgr:diffgram>
</DataTable>"""


class TestParseAnaSoap:
    def test_extrai_registros_e_tipos(self):
        df = parse_dados_xml(XML_AMOSTRA)
        assert len(df) == 2
        assert df.loc[0, "Nivel"] == 2301.0
        assert df.loc[0, "DataHora"] == "2024-05-02 23:45:00"

    def test_vazio_vira_nan_mas_zero_permanece(self):
        # Raw fica raw: o zero (falha de sensor) só vira NaN na Fase 2 (QC).
        df = parse_dados_xml(XML_AMOSTRA)
        assert pd.isna(df.loc[1, "Vazao"])
        assert pd.isna(df.loc[1, "Chuva"])
        assert df.loc[1, "Nivel"] == 0.0

    def test_xml_sem_registros(self):
        df = parse_dados_xml("<DataTable xmlns='http://MRCS/'></DataTable>")
        assert df.empty
        assert list(df.columns) == ["CodEstacao", "DataHora", "Vazao", "Nivel", "Chuva"]


class TestCache:
    def test_write_parquet_gera_meta_e_cache(self, tmp_path):
        dest = tmp_path / "x.parquet"
        write_parquet(pd.DataFrame({"a": [1, 2]}), dest, url="http://origem", params={"q": 1})
        assert is_cached(dest)
        assert not is_partial(dest)

    def test_partial_forca_rebaixa(self, tmp_path):
        dest = tmp_path / "x.parquet"
        write_parquet(pd.DataFrame({"a": [1]}), dest, url="u", partial=True)
        assert is_cached(dest)
        assert is_partial(dest)

    def test_arquivo_sem_meta_nao_conta_como_cache(self, tmp_path):
        dest = tmp_path / "x.parquet"
        pd.DataFrame({"a": [1]}).to_parquet(dest)
        assert not is_cached(dest)


class TestMonthRanges:
    def test_meses_completos_e_bordas(self):
        faixas = month_ranges(dt.date(2024, 1, 15), dt.date(2024, 3, 10))
        assert faixas == [
            (dt.date(2024, 1, 15), dt.date(2024, 1, 31)),
            (dt.date(2024, 2, 1), dt.date(2024, 2, 29)),
            (dt.date(2024, 3, 1), dt.date(2024, 3, 10)),
        ]


class TestMergeUrls:
    def test_daily(self):
        url = url_daily("https://ftp/x", dt.date(2024, 5, 2))
        assert url == "https://ftp/x/DAILY/2024/05/MERGE_CPTEC_20240502.grib2"

    def test_hourly(self):
        url = url_hourly("https://ftp/x", dt.datetime(2024, 5, 2, 7))
        assert url == "https://ftp/x/HOURLY/2024/05/02/MERGE_CPTEC_2024050207.grib2"


class TestSaceIndex:
    HTML = """
    <a href='boletins/Taquari/20240502_10-20240502 - 113045.pdf'>Boletim</a>
    <a href='boletins/Taquari/20240502_10-20240502 - 113045.pdf'>duplicado</a>
    <a href='boletins/Taquari/nome_estranho.pdf'>fora do padrão</a>
    """

    def test_parse_dedup_e_emissao(self):
        df = parse_index(self.HTML)
        assert len(df) == 2
        boletim = df[df["arquivo"].str.startswith("20240502")].iloc[0]
        assert boletim["emissao"] == pd.Timestamp("2024-05-02 10:00")

    def test_nome_fora_do_padrao_tem_emissao_nula(self):
        df = parse_index(self.HTML)
        assert df[df["arquivo"] == "nome_estranho.pdf"]["emissao"].isna().all()

    def test_indice_vazio(self):
        assert parse_index("<html></html>").empty
