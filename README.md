# 🌊 Cheias do Taquari — dados, modelo e registro de eventos

**Pipeline aberto e reprodutível de dados e previsão de cota do rio Taquari
(Vale do Taquari, RS)** — da ingestão de fontes públicas ao modelo validado
evento a evento, com todos os erros medidos e publicados.

> ## ⚠️ Isto NÃO é um sistema de alerta
> Este é um projeto independente de pesquisa, sem validação operacional, sem
> redundância e sem responsabilidade institucional. **Nenhum número daqui deve
> orientar decisão de evacuação.** Para alertas oficiais: boletins do
> [SACE/SGB](https://www.sgb.gov.br/sace/) e Defesa Civil do RS.
> Limitações medidas (não especulativas): [`LIMITACOES.md`](LIMITACOES.md).

---

## Por que este projeto existe

Setembro/2023, novembro/2023 e maio/2024 produziram as maiores cheias já
registradas no Vale do Taquari. Os dados para entendê-las e antecipá-las são
públicos, mas espalhados em meia dúzia de órgãos, formatos e convenções não
documentadas — e alguns morrem em silêncio exatamente durante os eventos.
Este repositório junta tudo em um pipeline auditável e responde, com números:
**quanto dá para antecipar do nível do rio usando só dado observado?**

## A resposta curta

Resultados da validação retrospectiva original (Fases 6–8). Para estimativas
com latência de fontes, consulte a revisão de setembro abaixo.

| Horizonte | Melhor modelo | Qualidade (Muçum, NSE) | Observação |
|---|---|---|---|
| **3–6h** | regressão linear com lags de montante | 0,99 / 0,98 | **bate a previsão oficial pareada nas mesmas horas** (MAE 17,6 vs 46,8 cm) |
| **12–24h** | LightGBM raso | 0,94 / 0,78 | mas subestima picos *recordes* em até 6 m — árvore não extrapola |
| **24h, em cheia** | LightGBM | NSE 0,24–0,58 | desempenho baixo nesta validação; não estabelece um teto físico universal |

E o detalhe que mais importa e menos aparece em papers: **os sensores falham
preferencialmente nos picos**. Nos três grandes eventos, só 65–68% das horas
em torno do pico têm observação válida — a régua de Estrela perdeu o máximo
histórico, e as usinas do rio das Antas transmitiram 9 de 72 horas no auge de
maio/2024. Aqui a disponibilidade de sensor é flag, feature e denominador de
métrica.

## Estudo de caso: as duas cheias de julho/2026 em Lajeado

Previsões **fora-de-amostra** (o modelo nunca viu o evento), régua de Estrela:

![Julho/2026 em Lajeado](reports/figs/hidrograma_ev20260722_lajeado.png)

| Onda | Pico observado | Linear h=3 | Erro |
|---|---|---|---|
| 21–23/07 | 2.475 cm | 2.459 cm | **−16 cm** |
| 28–30/07 | 2.398 cm | 2.405 cm | **+7 cm** |

Análise completa em [`reports/09_julho2026.md`](reports/09_julho2026.md).
**Este é o formato do que vem a seguir: cada nova cheia ganha uma página como
esta — previsto × ocorrido, publicado.**

## Rodada ao vivo: 21/09/2026

Primeira estimativa emitida *durante* um evento, com os erros medidos na hora
em vez de depois: [`reports/10_setembro2026.md`](reports/10_setembro2026.md).
O replay das horas anteriores subestimou **55 de 60 pares (91,7%)**, com viés
médio de −24 a −739 cm por estação/horizonte. A subida ficou no percentil
99,98+ do treino, mas sua contribuição para o erro não foi isolada. A versão
original recuava também as cotas para acompanhar o MERGE atrasado em 5h;
o h=12 tinha só 7h de antecedência restante às 18h. Não havia evidência para
declarar um teto útil de 6h.

A revisão prevê **3, 6, 9 e 12h desde a mesma referência de cota**, com
atrasos por fonte também no treino. A escolha entre linear, GBM nível e GBM
de variação usa eventos de 2023–2025; eventos de 2026 ficam separados para
teste. Resultados e limitações: [`reports/11_validacao_live.md`](reports/11_validacao_live.md).
Estimativas revisadas da referência das 18h e erros no evento:
[`reports/live_ultima_rodada.md`](reports/live_ultima_rodada.md).

Na rodada seguinte de desenvolvimento, o modelo com mais réguas a montante
reduziu o MAE de Encantado em 6h de **46,1 para 28,9 cm** no conjunto de
aceitação de 2026, em regime alto. Chuva de postos ANA e correção por erros
recentes foram testadas, mas não promovidas onde pioraram a comparação.
O sistema agora calcula faixas empíricas, suspende sua publicação quando
faltam exemplos ou a cobertura recente cai, e confere emissões reais
arquivadas separadamente de replays. Resultados completos e candidatos
rejeitados: [`reports/12_melhoria_live.md`](reports/12_melhoria_live.md).

### Previsto × observado (conferido em 22/09 às 07h)

Os três alvos cruzaram a cota de inundação: Encantado e Estrela às 20h de
21/09, Muçum à 01h de 22/09. Picos observados até 07h: Muçum 1871 cm (04h,
já em recessão), Encantado 1643 cm (05h), Estrela 2400 cm (07h, ainda
subindo). Cada número publicado durante o evento foi casado com a cota que a
ANA mediu na validade: [`reports/13_verificacao_setembro2026.md`](reports/13_verificacao_setembro2026.md).

| Emissão | h | MAE | Viés | n |
|---|---|---|---|---|
| 18h original (bruto) | 3 | 12 cm | −3 | 3 |
| 18h original (bruto) | 6 | 22 cm | −22 | 3 |
| 18h original (bruto) | 12 | 127 cm | −127 | 3 |
| 21h | 3 | 28 cm | −9 | 2 |
| 21h | 6 | 136 cm | −113 | 3 |
| 21h | 9 | 202 cm | −168 | 3 |

O que os números mostram, escrito depois de vê-los:

- **O linear bruto de 3 e 6h acertou dentro de 5 a 32 cm** nas três estações,
  em plena subida recorde. O replay das horas anteriores havia medido viés
  de −24 a −367 cm nesses horizontes; a partir das 18h o erro caiu porque a
  subida desacelerou, não porque o modelo mudou.
- **A "correção de viés" errou em todas as nove linhas conferidas**, de +2 a
  +594 cm, sempre para cima. Era aritmética sobre as horas de aceleração,
  aplicada quando a aceleração acabou. Fica registrado como o erro
  metodológico desta cheia: não corrigir viés com a própria fase que está
  terminando.
- **O GBM de variação da emissão das 21h previu recessão cedo demais** em
  Muçum e Encantado: os rios subiram mais 4 a 5 horas e o erro em 6–9h ficou
  entre −133 e −285 cm. Em Estrela, o linear errou para cima (+19 a +51 cm)
  quando a subida perdeu força.
- **O h=24 das 18h ainda não venceu** (13h de 22/09). Estrela já está 175 cm
  acima do valor previsto para essa hora, então ele será subestimativa, como
  a própria página das 18h antecipava.

A emissão das 07h de 22/09 (referência 07:00, cotas até 07:00) projeta
recessão em Muçum e Encantado e pico em Estrela por volta das 10h. Pela
primeira vez as faixas empíricas de 6h foram publicadas nos três alvos, com
cobertura recente de 83% ou mais. Segue em
[`reports/live_ultima_rodada.md`](reports/live_ultima_rodada.md) e será
conferida da mesma forma.

## O que tem aqui

```
📥 Ingestão      8 estações fluviométricas (ANA, 15 min, 2018+) · defluência das
                 3 UHEs da CERAN (ONS, horário, 2010+) · chuva em grade MERGE/CPTEC
                 (diária 1998+, horária por evento) · 305 boletins do SACE (2016+)
                 — tudo com cache idempotente e proveniência (.meta.json)
🔬 QC            fusos determinados EMPIRICAMENTE (ANA/ONS em UTC-3 fixo, validados
                 contra boletim e por cross-correlação física) · zero-de-nível = NaN
                 com flag · nenhuma interpolação de lacuna, nunca
🗺️  Espacial      bacias de contribuição por estação (HydroBASINS lev8; Muçum
                 validada a +0,1% da área oficial) · chuva média por sub-bacia
🧮 Features      77 features de base + 35 acumulados de chuva de postos ANA
                 (horas completas, sem preencher lacunas) — causalidade TESTADA
🎯 Dataset       59 eventos (2018-2026) + janelas normais · rótulos em 3/6/12/24h
                 para Muçum, Encantado e Estrela/Lajeado
📊 Avaliação     validação cruzada POR EVENTO (o extremo avaliado nunca está no
                 treino) · 4 baselines obrigatórios · POD/FAR/CSI · erro de valor
                 e tempo de pico · confronto pareado com a previsão oficial
```

Trilha completa de decisões e premissas corrigidas: `reports/00_fontes.md` →
`09_julho2026.md` (um relatório por fase) e a síntese em
[`reports/final.md`](reports/final.md).

## Rodando

Requisitos: [uv](https://docs.astral.sh/uv/); no macOS, `brew install libomp eccodes`.

```bash
uv sync --all-extras
make all    # reconstrói tudo do cache (~12 GB no primeiro make ingest)
make test   # QC, fusos, causalidade, latências e registro de previsões
```

Cada alvo é idempotente e cache-first; após `make ingest`, nada depende de
rede. Alvos individuais: `ingest → reference → qc → spatial → features →
dataset → baselines → model → evaluation` (ver `Makefile`).

Para a revisão de 6–12h:

```bash
uv run python -m src.live.evaluate          # valida e escolhe por evento passado
uv run python -m src.live.improve           # compara candidatos e calibra faixas
uv run python -m src.live.run --sem-atualizar # replay com o cache existente
uv run python -m src.live.run               # atualiza ANA/ONS e baixa MERGE recente
uv run python -m src.live.evento            # confere o publicado contra a cota observada
```

Cada execução guarda entradas, configuração, código e resultados em
`data/processed/live_runs/`. Replay não recebe horário de emissão; execução
com atualização registra emissão real e antecedência restante. O MERGE recente
é baixado antes da agregação; arquivos ainda não publicados ficam registrados
como ausentes, sem preenchimento.
`reports/12_live_modelos.json`, quando presente, define a política mais recente;
reexecute `src.live.improve` após refazer a validação base. Nenhuma rotina
promove um candidato apenas por melhorar o evento de setembro.

### Credencial da ANA (opcional)

O projeto funciona sem credencial (fonte primária: webservice SOAP legado da
ANA, aberto). Para a API oficial HidroWebService, solicite credencial por
e-mail ([manual](https://www.gov.br/ana/pt-br/assuntos/monitoramento-e-eventos-criticos/monitoramento-hidrologico/orientacoes-manuais/manuais/manual-hidrowebservice_publica.pdf);
modelo de e-mail em `reports/email_ana_credencial.md`) e crie um `.env`:

```
ANA_IDENTIFICADOR=...
ANA_SENHA=...
```

## Achados que podem servir a outros projetos

1. **`telemetriaws1.ana.gov.br/ServiceANA.asmx` está vivo e aberto** (série
   telemétrica de 15 min sem credencial) — a API REST legada do HidroWeb
   morreu (401 em toda a árvore desde ~2026).
2. **INMET bloqueia por fingerprinting TLS** — `curl_cffi` com
   `impersonate="chrome"` resolve.
3. **ANA e ONS publicam em UTC−3 fixo** (sem DST) — verificado empiricamente,
   não documentado em lugar nenhum.
4. **O ONS mudou o schema em 2026-02** (espaços em `nom_reservatorio`;
   filtre por `cod_usina`).
5. **O MERGE horário ainda é a base antiga (V06B)**; o diário é V07B — e o
   histórico único de 1998–2024 existe:
   `DAILY/MERGE_NEW_1998_2024.tar.gz` (4,1 GB).
6. **Treinar só no regime alto (≥ atenção) piorou** os resultados com
   amostragem por evento — na contramão da literatura recente da bacia.

## Roadmap — o registro público de cheias

- [ ] **Página de eventos**: a cada nova cheia, publicar previsto × ocorrido
      no formato do estudo de julho/2026 (hidrograma + tabela de erros)
- [ ] Atualização contínua da ingestão (o pipeline já é incremental)
- [ ] Chuva prevista (ETA/BRAMS ou GFS/ECMWF) — avaliar ganho em horizontes longos
- [ ] Modelo híbrido para picos (GBM sobre resíduo do linear) — ataca o viés em recordes
- [ ] Previsão por quantis (banda de incerteza em vez de número seco)
- [ ] CEMADEN (pluviômetros de 10 min) via fluxo de e-mail

## Fontes e créditos

| Fonte | Dado | Órgão |
|---|---|---|
| [HidroWeb/telemetria](https://www.snirh.gov.br/hidroweb/) | cota, vazão, chuva (15 min) | ANA |
| [Dados Abertos ONS](https://dados.ons.org.br) | defluência das UHEs (horário) | ONS |
| [MERGE/GPM](https://ftp.cptec.inpe.br/modelos/tempo/MERGE/GPM/) | chuva em grade 0,1° | INPE/CPTEC |
| [SACE Taquari](https://www.sgb.gov.br/sace/) | boletins e previsões oficiais | SGB/CPRM |
| [RIGEO](https://rigeo.sgb.gov.br) | cotas de referência (Muçum) | SGB/CPRM |
| [HydroBASINS](https://www.hydrosheds.org/products/hydrobasins) | polígonos de sub-bacias | WWF/HydroSHEDS © |

Os dados brutos pertencem aos respectivos órgãos. HydroSHEDS é usado sob sua
licença de atribuição. As usinas da CERAN são a fio d'água e a defluência é
tratada como observação de vazão, nunca como variável de controle.

---

*Projeto pessoal de Davi Janisch Maia. Contribuições e correções são
bem-vindas via issues e pull requests — especialmente de quem conhece a bacia.*
