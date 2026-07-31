# Fase 3 — Delineamento e agregação espacial

Executada em 2026-07-31. Saídas: `data/reference/subbacias.gpkg`,
`data/reference/estacoes_coords.csv`, `data/reference/subbacias_areas.csv`,
`data/interim/merge/diaria/ano=*.parquet` (1998→hoje) e
`data/interim/merge/horaria/evento=*.parquet` (janelas dos 3 eventos).

## Método de delineamento (e por que não MDE nem ottobacias da ANA)

O idea.md pedia MDE ou ottobacias. O geoserviço ArcGIS da ANA expõe a
hidrografia ottocodificada como **trechos (linhas)**, não os polígonos de
ottobacia; e delinear do MDE seria retrabalho pesado para o uso real — agregar
chuva em células de 0,1° (~90 km²). Usei **HydroBASINS nível 8** (WWF, derivado
de SRTM, ~130 km²/polígono, topologia `NEXT_DOWN`): bacias de contribuição por
BFS reversa a partir do polígono que contém cada estação.

**Validação contra área oficial** (critério de adequação, erro fatal se >10%):

| Estação | Calculada (km²) | Oficial (km²) | Erro |
|---|---|---|---|
| Muçum | 15.983 | 16.000 (RIGEO doc/24429) | **+0,1%** |

## Sub-bacias incrementais (unidades de agregação de chuva)

| Estação | Montante direta | Incremental (km²) | Total (km²) |
|---|---|---|---|
| Linha José Julio (Antas) | cabeceira | 12.918 | 12.918 |
| Santa Tereza / Muçum | Linha José Julio | 3.065 | 15.983 |
| Encantado | Santa Tereza, Muçum | 3.700 | 19.683 |
| Estrela | Encantado | 4.289 | 23.972 |
| Porto Mariante | Estrela | 691 | 24.663 |
| Taquari | Porto Mariante | 1.295 | 25.958 |

Limitação de resolução: **Santa Tereza e Muçum caem no mesmo polígono lev08**
(estão a ~13 km uma da outra) e compartilham a mesma bacia — a chuva agregada
delas é idêntica. Irrelevante para o modelo (a unidade incremental é a mesma).

A cascata CERAN fica inteira dentro da unidade "Linha José Julio" (12.918 km²,
metade da bacia): a chuva dessa unidade é o preditor da defluência/onda do
Antas.

## Agregação do MERGE

- Média ponderada por fração de área da célula na sub-bacia (interseção em
  EPSG:6933, equivalente; pesos somam 1, testado). 426 pares célula-sub-bacia.
- **Pesos por assinatura de grade**: cada arquivo tem a grade verificada
  (origem, resolução, dimensões) e ganha pesos próprios se divergir — protege
  contra mudanças silenciosas de domínio entre bases do MERGE. No
  reprocessamento completo (13,8k arquivos) só uma grade apareceu
  (701×493, 0,1°, América do Sul) e nenhum arquivo foi ilegível.

## Convenção temporal do MERGE (verificada empiricamente)

O GRIB não declara o período de acumulação. Assumido: **rótulo do arquivo =
fim da acumulação** (diário AAAAMMDD = 24h terminando 12 UTC; horário
AAAAMMDDHH = 1h terminando HH UTC), com rótulos de saída deslocados para o
início do período, como no resto do projeto.

Verificação: correlação entre chuva horária MERGE (sub-bacia) e pluviômetro
ANA (estação, rótulo=início) em set/2023, por defasagem:

| Estação | Melhor lag | r no melhor | r em lag 0 |
|---|---|---|---|
| Muçum | 0 | 0,661 | 0,661 |
| Encantado | 0 | 0,710 | 0,710 |
| Linha José Julio | 0 | 0,673 | 0,673 |
| Estrela | −1 | 0,615 | 0,544 |

3 de 4 estações com máximo em lag 0 confirmam a convenção (magnitudes de
r são as esperadas para ponto vs média espacial). Estrela, com a sub-bacia
mais extensa da comparação e menos horas válidas, fica a 1h — dentro do ruído.

## Correções de premissa (regra 8)

1. **O arquivo histórico único do MERGE existe** — o README aponta
   `DAILY/MERGE_NEW_1998_2024.tar.gz` (4,1 GB). Minha nota da Fase 1 dizendo o
   contrário estava errada (o listing do FTP foi truncado na leitura). Baixado
   e usado: o diário agregado agora cobre **1998→hoje** (29 anos).
2. **A base horária do MERGE ainda é a antiga (V06B)**: o README afirma que a
   atualização V07B dos horários "está em andamento". Ou seja, diário (V07B,
   com dados ONS) e horário (V06B) **não são a mesma base** — consistência
   entre eles deve ser tratada com cuidado nas features.
3. Bom Retiro do Sul está fora do inventário telemétrico da ANA (além de sem
   série no SOAP) — excluída do produto espacial, permanece documentada.
