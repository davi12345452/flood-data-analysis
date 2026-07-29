# Fase 0.5 — Desbloqueio

Executada em **2026-07-28**, mesma rede da Fase 0. Resultado das quatro tarefas e recomendação
de fonte primária de cota para a Fase 1.

## TL;DR

| Tarefa | Resultado |
|---|---|
| 1. E-mail à ANA | ✍️ Rascunho pronto em `reports/email_ana_credencial.md` — **exige seu CPF, você precisa enviar** |
| 2. `curl_cffi` × INMET | ✅ **Desbloqueou.** `impersonate="chrome"` → HTTP 200 no portal e na apitempo |
| 3. XHR do CEMADEN | ❌ Endpoints do frontend mortos; extensão do Chrome indisponível para capturar XHR ao vivo. **Assumir fluxo por e-mail** |
| 4. Rotas alternativas de cota | 🏆 **Achado maior: o webservice SOAP legado da ANA está vivo e aberto.** Rede estadual RS está fora do ar |

**Recomendação de fonte primária de cota: `telemetriaws1.ana.gov.br/ServiceANA.asmx` (SOAP legado, sem credencial).** Detalhes abaixo.

---

## Tarefa 1 — Credencial da ANA

O manual oficial (baixado e lido) instrui enviar e-mail a **hidro@ana.gov.br** com assunto
`"[CPF] - Solicitação de acesso à API HidroWebService para consumo de dados"`, incluindo nome
completo, CPF e e-mail para receber a senha. Como exige CPF, o envio é seu: rascunho pronto em
`reports/email_ana_credencial.md`. Nada bloqueia esperando a resposta (ver Tarefa 4).

## Tarefa 2 — INMET via curl_cffi

Confirmado o diagnóstico de fingerprinting TLS. Com `curl_cffi` e `impersonate="chrome"`:

- `https://portal.inmet.gov.br/dadoshistoricos` → **200** (61.887 bytes)
- `https://apitempo.inmet.gov.br/estacoes/T` → **200** (262.243 bytes, catálogo de automáticas)

INMET está disponível para a Fase 1 usando `curl_cffi` como transporte. Prioridade continua
baixa (CEMADEN + MERGE cobrem chuva), mas a porta está aberta.

## Tarefa 3 — CEMADEN

Sem navegador disponível nesta sessão (extensão do Chrome desconectada), fiz análise estática
do frontend:

- `js/script.js` do mapa interativo referencia `/dados/*.json`, `/graficos/interativo/grafico_CEMADEN.php?idpcd=`
  e `sjc.salvar.cemaden.gov.br/...` — **todos devolvem 404 ou redirecionam para o WordPress
  institucional**. São restos de uma versão antiga do app.
- Conclusão: não há endpoint público óbvio recuperável por análise estática. Duas opções:
  (a) capturar a XHR com DevTools quando houver navegador disponível (custo: 10 min, incerto), ou
  (b) **assumir o fluxo por e-mail** — ~150 requisições mensais RS 2014→2026, custo único, vira
  Parquet para sempre. **Recomendo (b)**, começando pelos meses dos eventos de referência.

## Tarefa 4 — Rotas alternativas de cota

### 🏆 SOAP legado da ANA (telemetriaws1) — VIVO, ABERTO, VALIDADO

`http://telemetriaws1.ana.gov.br/ServiceANA.asmx/DadosHidrometeorologicos?codEstacao={cod}&dataInicio={dd/MM/yyyy}&dataFim={dd/MM/yyyy}`

- **Sem token.** XML (DataSet .NET) com `CodEstacao, DataHora, Vazao, Nivel, Chuva`, passo de **15 minutos**.
- Validado no pico do evento: Muçum em 02/05/2024 23:30 → Nivel 2310 cm, Vazao 12.281 m³/s. Dados reais do maior evento registrado.
- **Profundidade do histórico (Muçum):** 2018 parcial, 2019+ completo, 2010–2017 vazio. Janela utilizável ≈ **2018/2019 → hoje**, compatível com a janela do ONS horário (2019+).
- `ListaEstacoesTelemetricas` também funciona (inventário completo, 5.244 estações) — foi como confirmei os códigos abaixo.
- Riscos: serviço legado sem SLA (pode morrer sem aviso — mitigado pelo cache Parquet agressivo); fuso do `DataHora` precisa ser verificado na Fase 2 (provavelmente hora local, confirmar contra evento conhecido).

### Códigos confirmados no inventário telemétrico

| Estação | Código | Registros em 01–03/05/2024 (288 possíveis) |
|---|---|---|
| Santa Tereza | 86472600 ✅ | 288 |
| Linha José Julio | 86472000 ✅ (grafia oficial: LINHA JOSÉ JÚLIO) | 288 |
| Muçum | 86510000 ✅ | 288 |
| **Encantado** | **86720000** (novo, confirmado, Rio Taquari) | 288 |
| **Estrela** | **86879300** (novo, confirmado, Rio Taquari) | **163 ⚠️** |
| Lajeado | **não existe estação "Lajeado" no rio Taquari** | — |
| Taquari | 86950000 ✅ | **132 ⚠️** |

Duas observações importantes:

1. **Armadilha 0 já visível:** Estrela (57%) e Taquari (46%) têm lacunas exatamente durante o
   evento de maio/2024. A censura não aleatória é real e mensurável desde já.
2. **Lajeado:** o mais próximo no inventário é `86878700 ARROIO DO MEIO/LAJEADO`, mas fica no
   **rio Forqueta** (afluente) e devolveu **0 registros** no período testado. Na prática, a régua
   de Estrela é a referência do trecho Estrela/Lajeado (cidades em margens opostas). **Proposta:
   tratar Lajeado via estação Estrela e remover "Lajeado" como alvo separado — preciso do seu ok.**

### HIDRO-Telemetria ASP.NET (Mapa.aspx / gerarGrafico.aspx)

Responde 200, mas é frontend da **mesma base** que o SOAP expõe. Com o SOAP funcionando, não há
motivo para raspar postbacks ASP.NET. Descartado.

### Rede estadual RS — fora do ar

- `saladesituacao.rs.gov.br`: **DNS não resolve** nem em resolvedores públicos (8.8.8.8, 1.1.1.1). O domínio morreu, embora a Sema ainda o linke.
- `www.smad.rs.gov.br`: DNS resolve (200.198.133.119) mas **não conecta** em 80/443, nem via IP direto.
- A premissa A.2 do idea.md v2 está quebrada (regra 8: avisando em vez de contornar). A rede
  estadual sai do plano por ora; se os portais voltarem, reavaliamo-la como redundância para a Armadilha 0.

---

## Recomendação para a Fase 1

**Fonte primária de cota: SOAP legado (`telemetriaws1`)** — programático, 15 min, cobre todas as
estações alvo, valida contra o evento de maio/2024. Ordem de ingestão:

1. **ONS** (`dados_hidrologicos_ho`) — defluência das UHEs, Parquet limpo
2. **SOAP legado ANA** — cota/vazão/chuva 15 min das 6 estações confirmadas
3. **MERGE** — chuva em grade
4. **SACE** — boletins (benchmark externo + cota observada de backup)
5. INMET via `curl_cffi` e CEMADEN por e-mail — segunda leva
6. Cliente HidroWebService pronto por trás de flag, aguardando credencial

## Decisões que preciso de você

1. **Enviar o e-mail à ANA** (`reports/email_ana_credencial.md` — falta só o CPF).
2. **Lajeado via estação Estrela** (não existe estação própria no Taquari) — ok?
3. **CEMADEN pelo fluxo de e-mail** (custo único, ~150 arquivos) — ok, ou prefere que eu tente a captura de XHR quando o navegador estiver disponível?
