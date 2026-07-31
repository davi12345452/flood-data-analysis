# Fase 5 — Dataset supervisionado

Executada em 2026-07-31. Saídas: `data/processed/dataset_{86510000,86720000,86879300}.parquet`,
`eventos.parquet`, `janelas_normais.parquet`, `janelas_amostradas.json`.

## Alvos e horizontes

Cota (cm) em **Muçum**, **Encantado** e **Estrela** (que cobre Lajeado — decisão
da Fase 0.5, alinhada à prática do SACE: não existe estação "Lajeado" no
Taquari), em horizontes de **3, 6, 12 e 24h**. Rótulo `y_h` = nível da própria
estação em t+h; rótulo NaN (sensor caído no futuro) permanece NaN e a linha
sobrevive se tiver outro horizonte válido.

## Amostragem por evento

- **Evento** = bloco contíguo com qualquer alvo ≥ cota de atenção; blocos a
  menos de 72h um do outro são fundidos. Janela amostrada = bloco com **168h de
  antecedência** (features de chuva de 120h + contexto pré-evento) e **72h de
  cauda** (recessão).
- **59 eventos** detectados em 2018–2026, incluindo os três de referência
  (set/2023, nov/2023, mai/2024 — este com 591 horas acima da atenção e pico
  de 2.551 cm em Muçum) e um **evento em curso** no fechamento da fase
  (ev20260722, pico 1.986 cm).
- **36 janelas normais** de 240h, 4/ano, sorteadas com semente fixa (42) fora
  dos eventos (buffer de 48h), sem sobreposição.

### Proporção evento/normal e justificativa

| Alvo | Linhas | Evento | Normal | ≥ atenção | ≥ inundação |
|---|---|---|---|---|---|
| Muçum | 26.217 | 69% | 31% | 20,1% | 0,5% |
| Encantado | 24.038 | 67% | 33% | 11,0% | 1,1% |
| Estrela | 16.229 | 66% | 34% | 8,9% | 3,0% |

Justificativa: as janelas de evento já contêm muito regime baixo (antecedência
de 7 dias + cauda), então ~1/3 de janelas normais adicionais basta para
ancorar o regime base sem afogar o sinal de cheia — que é o que importa
(Armadilha 2: estudo de 2025 na bacia melhorou ~86% restringindo o treino a
≥ atenção). A Fase 7 testará adicionalmente o treino restrito a ≥ atenção como
variante.

## Chuva horária por janela amostrada (anti-vazamento)

O MERGE horário foi baixado para **todas** as 95 janelas (com margem de 120h
antes do início, para os acumulados longos): ~35,7 mil horas agregadas por
sub-bacia. Sem isso, features de chuva presentes só em eventos vazariam
"isto é um evento" pela máscara de NaN. Cobertura final: **95–97%** das linhas
com chuva horária completa (o resto são 166 horas inexistentes no FTP do
CPTEC — lacunas da fonte, registradas, não imputadas).

Acumulados ≥24h toleram até 2% de horas faltantes na janela (soma usa só o
observado — subconta marginalmente, não fabrica). Janelas ≤12h exigem
completude.

## Features por alvo (só montante físico)

- **Muçum** (49 col.): chuva antas+medio, API, blocos jj/st/mu, UHEs
- **Encantado** (55): + bloco próprio
- **Estrela** (71): bacia inteira até aqui (chuva baixo, blocos até es)

## Split (decisão fixada com o usuário)

- **Validação cruzada por evento** (`janela_id` é a chave de fold): treino
  nunca contém horas do evento validado. Split **cronológico dentro do
  possível e nunca aleatório por linha** — a autocorrelação horária vazaria.
- **Extremos incluídos no treino** quando não são o fold validado; relatório
  separado para set/2023, nov/2023 e mai/2024 na Fase 8.
- Nenhuma normalização/imputação foi feita aqui: fit de scaler (se houver) é
  dentro do fold, no treino (Armadilha 3).

## Cobertura de rótulo

`y_24h` válido em 97,7–98,9% das linhas — mas a Fase 8 reportará a cobertura
especificamente **nas horas de pico** por evento (Armadilha 0: em mai/2024,
Estrela teve só ~50% de horas válidas; o rótulo some exatamente onde o erro
custa caro).
