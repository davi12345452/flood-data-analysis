# Fase 1 — Notas de ingestão

Complementa `01_cobertura.md` (que é gerado automaticamente por `make coverage`).
Registra decisões, premissas corrigidas e particularidades descobertas na ingestão,
executada em 2026-07-28/31.

## Premissas do idea.md corrigidas (regra 8)

1. **ONS horário desde 2010, não 2019.** A leitura da Fase 0 olhou só os primeiros
   recursos do catálogo CKAN (que não é cronológico). O dataset completo
   `dados_hidrologicos_ho` cobre 2010-01 → hoje, com 1,9% de lacunas para as três
   UHEs da CERAN. A janela de treino é maior que o previsto — a restrição
   vinculante passa a ser a cota da ANA (2018+).
2. **O "arquivo histórico único 1998-2024" do MERGE não existe** no FTP do CPTEC.
   A raiz de `GPM/` tem apenas DAILY/, HOURLY/, CLIMATOLOGY/ etc. Loop de
   downloads foi inevitável (3.130 diários + 3.383 horários, com rate limit).
3. **O PDF do RIGEO tabula cotas de referência apenas de Muçum** (500/900/1800 cm),
   não de todas as estações. As demais vieram do boletim SACE mais recente
   (legendas dos gráficos), com Muçum validada nas duas fontes.
4. **Linha José Júlio tem cota de inundação** (2450 cm) no boletim SACE atual,
   contrariando a Armadilha 7 ("só atenção e alerta"). Fica registrado; o limiar
   existe e será usado como os demais.
5. **Linha José Júlio fica no rio das Antas**, não no Taquari — é a estação que
   recebe a onda das UHEs CERAN antes da confluência. Corrigido no config.

## Descobertas

- **Estrela cobre Lajeado oficialmente**: o boletim descreve a estação 86879300
  como "Rio Taquari nos municípios de Estrela e Lajeado". A decisão de tratar
  Lajeado via Estrela está alinhada com a prática do SACE.
- **Duas estações extras no trecho**: Bom Retiro do Sul (86882000) e Porto
  Mariante (86895000) aparecem nos boletins e foram adicionadas como
  intermediárias (redundância para a Armadilha 0). Porém: Bom Retiro devolve
  **0 registros** no SOAP legado, e Porto Mariante tem **48% de lacunas**.
- **ONS mudou o schema em 2026-02**: `nom_reservatorio` passou a vir com espaços
  de preenchimento e `cod_usina` mudou de float para int. Filtros devem usar
  `str.strip()` ou `cod_usina` (97=Castro Alves, 98=Monte Claro, 99=14 de Julho).
- **Início real das séries de cota (SOAP)**: José Júlio e Porto Mariante 2018-01;
  Muçum e Encantado 2018-04; Estrela **2020-07**; Taquari **2021-11**; Santa
  Tereza **2023-09** (instalada após o primeiro evento de 2023). Ou seja: para os
  eventos de set/2023, Estrela e Taquari têm dado, mas Santa Tereza praticamente não.
- **MERGE**: 3 diários faltantes de 3.133 (dias recentes ainda não publicados) e
  1 horário de 3.384 (04h de 24/04/2024, lacuna real da fonte, registrada em
  `data/raw/merge/faltantes_hourly_eventos.txt`).
- **Instabilidade do SOAP legado**: o serviço devolveu 504 em rajada durante a
  ingestão (e ficou fora por ~1h). O ingestor tolera falha por mês (registra em
  `falhas_ultimo_run.txt` e retenta na próxima execução) e não roda em paralelo.

## Volumes em cache (`data/raw/`)

| Fonte | Volume | Conteúdo |
|---|---|---|
| ana_soap | 18 MB | 824 parquets (8 estações × ~103 meses, 15 min) |
| ons | 267 MB | 199 parquets horários (2010+) + 27 diários (2000+) |
| merge | 1,6 GB | 3.130 GRIB2 diários (2018+) + 3.383 horários (eventos) |
| sace | 176 MB | 305 boletins PDF (2016+) + índice parquet |
| rigeo | 1,4 MB | PDF das cotas de referência de Muçum |

Total: ~2,1 GB, tudo com `.meta.json` de proveniência. Reexecutar `make ingest`
não rebaixa nada (idempotente); apenas meses/recursos marcados como parciais são
atualizados.
