# Limitações

**Este projeto NÃO é um sistema de alerta.** É pesquisa pessoal, sem validação
operacional, sem redundância, sem monitoramento contínuo e sem
responsabilidade institucional. Nenhuma saída deste repositório deve ser usada
para decisão de evacuação ou proteção civil. Para alertas oficiais no Vale do
Taquari, consulte o SACE/SGB (https://www.sgb.gov.br/sace/) e a Defesa Civil
do RS.

## Limitações técnicas medidas (não especulativas)

1. **Teto de horizonte físico.** Com chuva observada, a antecedência útil é
   ~12h (Muçum/Encantado) e ~8h (Estrela/Lajeado). Medido: no regime alto em
   h=24, NSE cai para 0,24–0,58 em todos os modelos testados. Horizontes
   maiores exigem chuva prevista, com incerteza meteorológica dominante.
2. **Subestimação de picos recordes.** O LightGBM errou o valor dos picos dos
   eventos de referência em −160 a −640 cm: árvores não extrapolam além do
   máximo de treino, e cheia recorde é extrapolação por definição.
3. **Censura de sensor nos picos (Armadilha 0).** Cobertura de observação de
   0,65–0,68 nas ±12h dos picos de set/2023, nov/2023 e mai/2024. As métricas
   de pico estão calculadas sobre picos possivelmente truncados — o erro real
   pode ser maior do que o reportado.
4. **Curva-chave extrapolada.** Nos extremos de 2023/2024 as cotas saíram do
   intervalo medido; vazões nesses picos são extrapolação. Todo o projeto
   trabalha em cota, nunca em vazão.
5. **Fontes sem SLA.** A fonte primária de cota é um webservice legado da ANA
   (telemetriaws1) que pode morrer sem aviso; o dado do ONS não é consistido
   (réplica dos agentes, com apagão demonstrado no pico de mai/2024 — 9 de 72
   horas transmitidas); a base horária do MERGE ainda é a versão antiga
   (V06B), diferente da diária (V07B).
6. **Dados de 2024 da UHE 14 de Julho** (rompimento parcial em 02/05/2024)
   estão sinalizados como anômalos (`flag_pos_rompimento`), não corrigidos.
7. **Fuso pré-2019 incerto (±1h)** nas janelas de horário de verão (ANA/ONS
   assumidos em UTC−3 fixo; janelas marcadas com `flag_dst_incerto`). Nenhum
   evento de referência é afetado.
8. **Lajeado é coberto pela régua de Estrela** (não existe estação própria no
   Taquari) — mesma prática do SACE, mas é uma aproximação de margem oposta.
9. **Treinado numa única bacia e num único regime climático** (2018–2026).
   Nada aqui generaliza para outras bacias ou para condições fora do
   histórico amostrado.
