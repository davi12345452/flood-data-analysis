# Fase 1 — Relatório de cobertura

Gerado em 2026-07-31T20:02:37+00:00 a partir do cache local (`data/raw/`). Reexecutável com
`make coverage`.

## ANA — SOAP legado (telemetriaws1), grade nominal de 15 min

Percentual de "nível zero ou ausente" reportado à parte: pela Armadilha 0,
zero de nível é falha de sensor, não medição.

| estacao           |   codigo | inicio              | fim                 |   registros |   lacunas_grade_15min_pct |   nivel_zero_ou_nan_pct |   resolucao_mediana_min |
|:------------------|---------:|:--------------------|:--------------------|------------:|--------------------------:|------------------------:|------------------------:|
| Santa Tereza      | 86472600 | 2023-09-30 20:00:00 | 2026-07-31 16:45:00 |       97259 |                       2.1 |                     0.4 |                      15 |
| Linha José Julio  | 86472000 | 2018-01-01 00:00:00 | 2026-07-31 16:30:00 |      292142 |                       2.9 |                    13   |                      15 |
| Muçum             | 86510000 | 2018-04-30 00:00:00 | 2026-07-31 16:30:00 |      274001 |                       5.3 |                     1.6 |                      15 |
| Encantado         | 86720000 | 2018-04-30 00:00:00 | 2026-07-31 16:30:00 |      270086 |                       6.7 |                     4.8 |                      15 |
| Estrela           | 86879300 | 2020-07-09 04:00:00 | 2026-07-31 16:30:00 |      191036 |                      10.1 |                     5.8 |                      15 |
| Bom Retiro do Sul | 86882000 | NaT                 | NaT                 |           0 |                     nan   |                   nan   |                     nan |
| Porto Mariante    | 86895000 | 2018-01-01 07:00:00 | 2026-07-31 16:30:00 |      155790 |                      48.2 |                     8.7 |                      15 |
| Taquari           | 86950000 | 2021-11-26 10:00:00 | 2026-07-31 16:45:00 |      153910 |                       6.2 |                     0.4 |                      15 |

## ONS — dados_hidrologicos_ho (usinas CERAN), grade horária

| usina        | inicio              | fim                 |   registros |   lacunas_grade_horaria_pct |   defluente_nan_pct |   resolucao_mediana_min |
|:-------------|:--------------------|:--------------------|------------:|----------------------------:|--------------------:|------------------------:|
| 14 DE JULHO  | 2010-01-01 01:00:00 | 2026-07-28 21:00:00 |      142520 |                         1.9 |                 0.1 |                      60 |
| CASTRO ALVES | 2010-01-01 01:00:00 | 2026-07-28 21:00:00 |      142563 |                         1.9 |                 0.1 |                      60 |
| MONTE CLARO  | 2010-01-01 01:00:00 | 2026-07-28 21:00:00 |      142548 |                         1.9 |                 0.1 |                      60 |

## MERGE/CPTEC (GRIB2)

- Diários: 3130 de 3133 esperados no período de modelagem
- Horários (janelas de eventos): 3383 de ~3384 esperados

## SACE — boletins por ano de emissão

|   ano |   boletins |   baixados |
|------:|-----------:|-----------:|
|  2016 |         16 |         16 |
|  2017 |         38 |         38 |
|  2018 |         13 |         13 |
|  2020 |         54 |         54 |
|  2021 |          3 |          3 |
|  2022 |         24 |         24 |
|  2023 |         57 |         57 |
|  2024 |         54 |         54 |
|  2025 |         34 |         34 |
|  2026 |         12 |         12 |
