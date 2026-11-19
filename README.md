# Citizen Assist AI

FIAP GS2026.2 — Pensamento Computacional e Automação com Python

- Enrico Marinho de Aquino — RM 569338
- Gabriel Castilla Cavaloti — RM 571643

## Proposta

Orientar pessoas que usam o SUS pela primeira vez sobre Cartão SUS, vacinação e atendimento na UBS. A base reúne 12 orientações com documentos, local de atendimento, fonte oficial e data de conferência.

O projeto se relaciona ao ODS 3, pelo acesso à informação sobre saúde, e ao ODS 10, pela linguagem acessível.

## Como executar

Com Python 3.10 ou superior, abra o terminal nesta pasta e rode:

```
python main.py
```

O menu permite perguntar, navegar pelas categorias, consultar indicadores e exportar o CSV. O zero volta à tela anterior. O projeto usa a biblioteca padrão do Python.

## Como funciona

`Orientacao` guarda e exibe os dados. `BaseConhecimento` lê o JSON e busca as orientações. `Assistente` recebe as entradas e registra os atendimentos. O Assistente contém a base, que contém uma lista de orientações.

A busca compara os textos em minúsculas, sem acentos ou pontuação. Cada palavra-chave completa encontrada soma 3 pontos. Cada palavra distinta da pergunta com quatro letras ou mais que aparece no título soma 1 ponto. Os resultados são tuplas ordenadas por pontuação.

A partir de 6 pontos, a confiança é alta. De 3 a 5, é média. Abaixo de 3, o programa sugere reformular ou navegar. São exibidas até duas alternativas.

O histórico fica em `data/historico.json`. O CSV é gerado pelo menu. A taxa de ajuda considera as respostas avaliadas, e o tempo médio considera os atendimentos com orientação. A facilidade é a média das notas dadas na saída.

## Verificação

Os 12 testes técnicos passaram, cobrindo busca, navegação, entradas inválidas, bloqueio de dados pessoais, histórico e CSV.

A expressão “faço o cartão do SUS” foi acrescentada após uma falha na busca. A pergunta passou a receber 4 pontos e a exibir a orientação correta.

## Teste com usuários

A dupla informou ter realizado dez atendimentos com três participantes e forneceu os resultados agregados abaixo.

| Participante | Atendimentos | Orientações encontradas | Facilidade de uso |
| --- | ---: | ---: | ---: |
| Pessoa 1 | 4 | 4 | 4/5 |
| Pessoa 2 | 3 | 3 | 5/5 |
| Pessoa 3 | 3 | 2 | 4/5 |
| Total / média | 10 | 9 | 4,3/5 |

Foram encontradas orientações em 90% dos atendimentos. Um atendimento ficou sem orientação.

Tempo médio, tentativas por atendimento, porcentagem de respostas que ajudaram, descrição da dúvida sem solução e melhoria decorrente dessa avaliação aguardam os registros complementares da dupla. A melhoria técnica descrita acima foi feita durante a verificação do sistema.

## Fontes e limites

As informações foram conferidas em 16/11/2026. Cada registro do JSON informa seu link oficial.

- [Meu SUS Digital](https://www.gov.br/saude/pt-br/composicao/seidigi/meususdigital/perguntas-e-respostas/cidadao)
- [CadSUS](https://webatendimento.saude.gov.br/faq/cadsus)
- [Vacinação](https://www.gov.br/saude/pt-br/vacinacao)
- [Carteira digital de vacinação](https://www.gov.br/saude/pt-br/assuntos/noticias/2026/outubro/quer-consultar-suas-vacinas-saiba-como-acessar-a-carteira-de-vacinacao-pelo-meu-sus-digital)
- [Calendário de vacinação](https://www.gov.br/saude/pt-br/vacinacao/calendario)
- [Atendimento na UBS](https://www.gov.br/saude/pt-br/assuntos/noticias/2025/outubro/ubs-ou-upa-saiba-quando-procurar-a-unidade-mais-proxima-de-voce)
- [Cadastro e documentação](https://bvsms.saude.gov.br/bvs/saudelegis/gm/2026/prt12263_05_10_2026.html)

O assistente é acadêmico. Horários, agendamento e documentos devem ser confirmados no serviço oficial. A busca depende das expressões cadastradas. Evite digitar dados pessoais. Perguntas com arroba ou oito ou mais dígitos são bloqueadas.

## Vídeo

[Apresentação técnica no YouTube](https://youtu.be/8QYd1CMBlys)
