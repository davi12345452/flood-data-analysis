# Evento de 21/09/2026 — estimativa durante a cheia (rodada 18:00 local)

> **Esta página não é um alerta.** É o registro público de uma rodada do modelo
> feita *durante* um evento, com os erros medidos na hora. Ela existe para ser
> conferida depois contra o que de fato aconteceu. Para decisão operacional:
> [SACE/SGB](https://www.sgb.gov.br/sace/) e Defesa Civil do RS (199).

Primeira rodada em tempo real deste projeto (`src/live/`). Todas as fases
anteriores são retrospectivas: reconstroem o passado com rótulo conhecido.
Aqui não há rótulo — o evento está acontecendo.

## Situação às 18:00 local (21:00 UTC)

Cinco estações do Taquari em alerta; nenhuma acima da cota de inundação ainda.

| Estação | Cota | Situação | Falta p/ inundação |
|---|---|---|---|
| Linha José Julio | 1528 cm | alerta | 922 cm |
| Santa Tereza | 1242 cm | alerta | 258 cm |
| Muçum | 1387 cm | alerta | 413 cm |
| Encantado | 1112 cm | alerta | **88 cm** |
| Estrela (ref. Lajeado) | 1742 cm | alerta | **158 cm** |
| Porto Mariante | 931 cm | atenção | 469 cm |
| Taquari | 460 cm | atenção | 390 cm |

Muçum subiu de **392 cm às 06:00 para 1387 cm às 18:00** — ~10 m em 12 horas.

![Evento em curso](figs/live_20260921_21.png)

## Latência por fonte — o que decide o horizonte utilizável

O achado operacional desta rodada não é uma previsão, é uma tabela de relógios.
Cada fonte tem uma defasagem diferente, e ela define em qual horizonte cada
modelo pode ser rodado:

| Fonte | Variáveis | Defasagem | Última observação |
|---|---|---|---|
| ANA SOAP | cota, chuva de posto | ~15 min | 21:00 UTC |
| ONS (CKAN) | defluência das UHEs CERAN | ~1 h | 20:00 UTC |
| MERGE/CPTEC | chuva em grade | **~5 h** | 16:00 UTC |

Consequência direta: o modelo linear (só lags de cota) roda em `t = 21:00 UTC`;
o GBM, que depende dos acumulados de chuva, roda em `t = 16:00 UTC` — **cinco
horas cego**, justamente as cinco horas em que Muçum subiu 640 cm. Nenhum
relatório anterior mediu isso, porque em modo retrospectivo todas as fontes
parecem igualmente disponíveis. Não parecem.

## Previsões emitidas

Modelo por horizonte conforme o veredito da Fase 7: linear em h≤6, GBM em h≥12.

| Alvo | t de ref. | h | Bruto | Viés medido no evento | Corrigido | Inundação |
|---|---|---|---|---|---|---|
| Muçum | 18:00 | 3 | 1594 | −134 (n=9) | 1728 | 1800 |
| Muçum | 18:00 | 6 | 1727 | −367 (n=6) | **2095** | 1800 |
| Muçum | 13:00 | 12 | 1550 | −739 (n=5) | 2288 | 1800 |
| Muçum | 13:00 | 24 | 1421 | — sem amostra — | — | 1800 |
| Encantado | 18:00 | 3 | **1318** | −98 (n=9) | 1416 | 1200 |
| Encantado | 18:00 | 6 | **1439** | −210 (n=6) | 1649 | 1200 |
| Encantado | 13:00 | 12 | 1500 | −622 (n=5) | 2122 | 1200 |
| Encantado | 13:00 | 24 | 1475 | — sem amostra — | — | 1200 |
| Estrela | 18:00 | 3 | **1967** | −24 (n=9) | 1991 | 1900 |
| Estrela | 18:00 | 6 | **2163** | −97 (n=6) | 2260 | 1900 |
| Estrela | 13:00 | 12 | 2132 | −281 (n=5) | 2413 | 1900 |
| Estrela | 13:00 | 24 | 2225 | — sem amostra — | — | 1900 |

Em negrito, os valores que cruzam a cota de inundação já no número bruto.

## Backtest do próprio evento — a única aferição possível

Durante o evento não existe validação cruzada. O que existe é conferir as
previsões emitidas há *h* horas cujo alvo já foi observado. É essa métrica, e
não o NSE histórico, que qualifica os números acima.

| Alvo | Modelo | h | MAE | Viés | n |
|---|---|---|---|---|---|
| Estrela | linear | 3 | 40 cm | −24 | 9 |
| Estrela | linear | 6 | 97 cm | −97 | 6 |
| Estrela | GBM | 12 | 281 cm | −281 | 5 |
| Encantado | linear | 3 | 114 cm | −98 | 9 |
| Encantado | linear | 6 | 210 cm | −210 | 6 |
| Encantado | GBM | 12 | 622 cm | −622 | 5 |
| Muçum | linear | 3 | 134 cm | −134 | 9 |
| Muçum | linear | 6 | 367 cm | −367 | 6 |
| Muçum | GBM | 12 | 739 cm | −739 | 5 |

**MAE = |viés| em toda linha.** Não há um único erro positivo na tabela: o
modelo subestima em 100% das previsões conferíveis deste evento. Isso não é
ruído, é viés estrutural, e a causa é mensurável — a taxa de subida está no
percentil 99,98–99,99+ da distribuição de treino:

| Alvo | Subida máx. 1h no treino | p99,9 do treino | Pico observado hoje |
|---|---|---|---|
| Muçum | 421 cm/h | 117 cm/h | 195 cm/h |
| Encantado | 171 cm/h | 97 cm/h | **161 cm/h** |

Encantado está a 6% do recorde histórico de velocidade de subida da própria
série. Modelo nenhum extrapola bem onde quase não teve amostra.

## Por que o h=24 desta rodada não deve ser usado

O número existe (Muçum 1421, Encantado 1475, Estrela 2225 cm para 13:00 de
22/09) e três coisas independentes dizem para não usá-lo:

1. **Zero amostras de verificação.** Para conferir um h=24 é preciso ter
   emitido a previsão há 24 h; o evento tem 12 h. A coluna de viés é vazia por
   impossibilidade, não por acaso.
2. **O irmão verificável está errado por 6–7 m.** O GBM h=12, mesmo modelo,
   mesmas features, mesma rodada, erra −622 a −739 cm em Muçum e Encantado.
3. **O número é internamente incoerente.** Para Muçum o GBM prevê 1421 cm em
   h=24, *menos* que os 1550 cm que ele mesmo prevê em h=12 — ou seja, afirma
   que o pico passa durante a madrugada. Enquanto isso a UHE 14 de Julho
   registra afluente (6219 m³/s) **maior** que defluente (5687 m³/s): o
   reservatório ainda está enchendo e a vazão de saída ainda vai subir. E o
   modelo prevê 1421 cm para amanhã às 13:00 quando a régua já marca 1387 cm
   hoje às 18:00 — 19 h antes.

É o modo de falha já documentado na Fase 7 ("árvore não extrapola"), agora
observado ao vivo e com a causa isolada: latência de 5 h na chuva + regime
fora da distribuição de treino.

**Conclusão honesta sobre o h=24: este pipeline não entrega 24 h de
antecedência neste evento.** O teto útil hoje é ~6 h, e mesmo ele com viés
negativo conhecido.

## Dados de barragem

Sim, e desta vez funcionaram. As três UHEs da CERAN transmitiram sem falha:

| UHE | Defluência 06:00 | Defluência 17:00 | Fator |
|---|---|---|---|
| Monte Claro | ~250 m³/s | 8487 m³/s | 34× |
| Castro Alves | ~200 m³/s | 5940 m³/s | 30× |
| 14 de Julho | 391 m³/s | 5687 m³/s | 14,5× |

Contraste com maio/2024, quando essas mesmas usinas transmitiram 9 de 72 horas
no auge. A disponibilidade do dado de barragem, que o projeto trata como
feature e como métrica, hoje está em 100%.

## Limitações desta rodada

- Rodada única, sem redundância, sem validação operacional, feita por uma
  pessoa durante o evento.
- O viés aplicado é aritmética sobre 5–9 amostras, **não um modelo**. Serve
  para dimensionar o erro sistemático, não para substituir a previsão.
- Sem chuva *prevista* (só observada), o teto físico de antecedência da bacia
  (~12 h em Muçum, ~8 h em Estrela) continua valendo e não é contornável aqui.
- As cotas de referência vêm do boletim SACE de 28/07/2026 e podem estar
  desatualizadas.

Reprodução: `uv run python -m src.live.run`.
