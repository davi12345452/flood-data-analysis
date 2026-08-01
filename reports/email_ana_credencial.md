# Modelo — solicitação de credencial à ANA (HidroWebService)

Template para quem quiser reproduzir o projeto com a API oficial. Envie do seu
e-mail pessoal (a senha chega no endereço informado), preenchendo os campos.

---

**Para:** hidro@ana.gov.br

**Assunto:** [SEU CPF ou CNPJ] - Solicitação de acesso à API HidroWebService para consumo de dados

**Corpo:**

Prezados,

Solicito credencial de acesso à API HidroWebService para consumo automatizado de dados.

Motivação: projeto de pesquisa em modelagem hidrológica na bacia Taquari-Antas (RS),
com uso de séries telemétricas de cota, vazão e chuva das estações fluviométricas do rio
Taquari (Muçum, Encantado, Estrela e vizinhas) para estudo de previsão de nível em eventos
de cheia. Uso estritamente não comercial e de pesquisa.

Dados para cadastro:

- Nome completo: [SEU NOME]
- CPF: [SEU CPF]
- E-mail: [SEU E-MAIL]

Atenciosamente,
[SEU NOME]

---

Fonte do procedimento: manual oficial do HidroWebService (link no README).
Com a credencial, configure `ANA_IDENTIFICADOR` e `ANA_SENHA` no `.env`.
