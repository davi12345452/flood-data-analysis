# Fase 0 — Reconhecimento de fontes de dados

Data do teste: **2026-07-28** (rede local, macOS). Cada fonte recebeu uma requisição mínima real.
Legenda: ✅ funciona | 🔑 precisa credencial | ⚠️ mudou / requer atenção | ❌ inacessível

## Resumo

| # | Fonte | Status | Acesso programático |
|---|-------|--------|---------------------|
| 1 | ANA HidroWebService (oficial) | 🔑 precisa credencial | Sim, após credencial por e-mail |
| 2 | ANA API legada (HidroWeb REST) | ❌ **endpoint agora exige token** | Não (premissa do idea.md quebrada) |
| 3 | ANA HidroWeb portal (séries históricas) | ✅ portal no ar | A investigar (download por interface) |
| 4 | CEMADEN | ⚠️ portal no ar, fluxo semi-manual | Download via link por e-mail |
| 5 | INMET (portal, API, BDMEP) | ❌ **connection reset desta rede** | Bloqueado (WAF ou rede) |
| 6 | MERGE / CPTEC | ✅ | Sim, HTTP direto (GRIB2) |
| 7 | ONS Dados Abertos | ✅ **melhor fonte confirmada** | Sim, CKAN + S3, Parquet |
| 8 | CERAN | ⚠️ site no ar, sem endpoint conhecido | Investigar na Fase 1 (scraping) |
| 9 | SACE boletins (SGB/CPRM) | ✅ via `boletins.php?idbacia=9` | Sim, scraping de PDFs |
| 10 | RIGEO (PDF cotas de referência) | ✅ | Sim, download direto |
| 11 | Ottobacias / metadados SNIRH | ✅ | Sim (geoserviços a mapear) |

## Detalhes por fonte

### 1. ANA HidroWebService (API oficial) — 🔑
- `swagger-ui.html` responde (HTTP 302 → página no ar).
- `GET /EstacoesTelemetricas/OAUth/v1` com credencial de teste devolve `401 — Usuário sem permissão de acesso ao módulo`, ou seja, a API está viva e o fluxo de autenticação descrito no idea.md continua válido.
- **Bloqueio: não há credencial configurada.** É preciso solicitar por e-mail à ANA conforme o manual. Sem isso, não há acesso programático à série telemétrica oficial.

### 2. ANA API legada — ❌ premissa quebrada
- `GET /hidroweb/rest/api/estacaotelemetrica?id=86510000` → `401 Unauthorized — "Token de Autenticação da API Inexistente ou mal Formatado"`.
- O mesmo para `gerarTelemetricas` e variações de rota. **A API legada não é mais aberta**: toda a árvore `/hidroweb/rest/api/` passou a exigir token.
- Conforme a regra 8 do projeto: reportando em vez de contornar. O caminho de prototipagem sem credencial descrito no idea.md **não existe mais**.

### 3. ANA HidroWeb portal — ✅ (manual)
- `https://www.snirh.gov.br/hidroweb/serieshistoricas` responde 200. O download em lote (zip por estação) pela interface continua como alternativa manual para séries convencionais históricas.

### 4. CEMADEN — ⚠️
- `mapainterativo.cemaden.gov.br` responde 200. O fluxo oficial de download entrega o arquivo por link no e-mail (semi-manual).
- Endpoints REST antigos testados (`sws.cemaden.gov.br/PED/rest/...`, `mapainterativo/graficorec/...`) devolvem 400/404 — não há API pública óbvia. Fase 1: usar o fluxo por e-mail ou investigar endpoints internos do mapa interativo.

### 5. INMET — ❌ desta rede
- `portal.inmet.gov.br`, `apitempo.inmet.gov.br` e o zip de dados históricos: **connection reset** em todas as tentativas (curl, Python/urllib, IPv4 forçado, user-agent de navegador). DNS resolve normalmente (201.57.198.188).
- Diagnóstico: bloqueio no nível de rede/WAF (possivelmente fingerprinting TLS ou bloqueio do IP/ASN desta conexão), não um problema de rota. **Testar de outra rede ou via navegador antes de descartar a fonte.**

### 6. MERGE / CPTEC — ✅
- Diretório `DAILY/` responde 200; GRIB2 horário de teste (`MERGE_CPTEC_2024050112.grib2`) existe e responde 200.
- Fase 1: procurar o arquivo histórico único 1998–2024 mencionado no idea.md antes de fazer loop de downloads.

### 7. ONS Dados Abertos — ✅ melhor fonte confirmada
- CKAN funcional (82 datasets). Dataset **`dados_hidrologicos_ho`** ("Dados Hidráulicos por Reservatório – Base horária"): 602 recursos em Parquet/CSV/XLSX no S3, cobertura desde **2019-01**, dados *não consistidos* (réplica do que os agentes enviam).
- **Verificado no Parquet de maio/2024**: as três usinas da CERAN estão presentes — `MONTE CLARO`, `CASTRO ALVES`, `14 DE JULHO` — com colunas `val_vazaoafluente`, `val_vazaodefluente`, `val_vazaoturbinada`, `val_vazaovertida`, `val_nivelmontante` etc., em passo horário, incluindo o período do evento (01/05/2024 já mostra defluência de ~4.000 m³/s na 14 de Julho, subindo).
- Existe também `dados-hidrologicos-res` (base diária, histórico possivelmente mais longo) para complementar.
- Limitação: horário só desde 2019 — antes disso, só passo diário.

### 8. CERAN — ⚠️
- `ceran.com.br` responde 200. Não foi identificado endpoint de dados nesta fase; Fase 1 decide entre scraping educado das páginas de operação ou depender só do ONS (que já entrega defluência horária das três usinas — provavelmente suficiente).

### 9. SACE boletins — ✅ (rota corrigida)
- O diretório `boletins/Taquari/` devolve 403 (listagem bloqueada), mas a página **`https://www.sgb.gov.br/sace/boletins.php?idbacia=9`** lista todos os boletins com links diretos para os PDFs em `boletins/Taquari/<YYYYMMDD_HH...>.pdf` (testado, 200, boletim mais recente de 28/07/2026).
- Scraping viável: paginação via tablesorter, PDFs com data/hora no nome. Baseline externo garantido.

### 10. RIGEO — ✅
- PDF das cotas de referência (`cotas_sace_taquari_mucum_artigo.pdf`) responde 200. Fase 1: baixar, extrair a tabela e versionar em `data/reference/cotas_referencia.csv`.

### 11. Ottobacias / metadados SNIRH — ✅
- `metadados.snirh.gov.br` responde 200. Mapeamento dos geoserviços (WFS/download da base ottocodificada) fica para a Fase 3.

## Lista de bloqueios (decisões suas)

1. **Credencial da ANA (crítico).** A API legada morreu; sem credencial do HidroWebService **não há acesso programático a cota telemétrica**, que é o alvo do modelo. Ação: solicitar credencial à ANA por e-mail (manual no idea.md). Alternativas parciais enquanto isso: download manual pelo portal HidroWeb e/ou dados do SACE.
2. **INMET bloqueado nesta rede.** Testar de outra rede/VPN ou navegador. Se persistir, seguimos sem INMET (CEMADEN + MERGE cobrem chuva).
3. **CEMADEN é semi-manual** (arquivo por e-mail). Aceitável? Ou investigo os endpoints internos do mapa interativo na Fase 1?
4. **CERAN sem endpoint conhecido** — mas o ONS já entrega a defluência horária das três UHEs desde 2019, o que cobre a necessidade do modelo. Proposta: usar ONS como fonte primária e só voltar à CERAN se houver lacunas.

## Ambiente

- Python 3.12 (pinado via `uv`), venv em `.venv/`, dependências em `pyproject.toml` (base: httpx, pandas, pyarrow, pyyaml, tenacity; extras `geo`, `ml`, `dev`).
- Estrutura de diretórios criada conforme o idea.md (`data/{raw,interim,processed,reference}`, `src/{ingest,qc,features,models,eval}`, `notebooks/`, `tests/`, `reports/`, `config/`).
