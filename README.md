# Citizen Assist AI

Projeto da FIAP GS2026.2 com as contribuições de Pensamento Computacional e Automação com Python e de Soluções em Energias Renováveis e Sustentáveis.

**Integrantes**

- Enrico Marinho de Aquino — RM 569338
- Gabriel Castilla Cavaloti — RM 571643

## Público e problema

Quem usa o SUS pela primeira vez precisa saber onde buscar atendimento, quais documentos levar e onde conferir a informação. O assistente reúne orientações administrativas sobre Cartão SUS e cadastro, vacinação e atendimento na UBS e mostra a fonte de cada resposta.

- **ODS 3 — Saúde e Bem-Estar.** As orientações sobre o primeiro acesso ao SUS se relacionam com a meta 3.8, que trata do acesso a serviços essenciais de saúde. [Nações Unidas](https://brasil.un.org/pt-br/sdgs/03)
- **ODS 10 — Redução das Desigualdades.** A linguagem simples ajuda a reduzir a barreira de informação para quem ainda precisa entender como usar o serviço, em linha com a meta 10.2 sobre inclusão. [Nações Unidas](https://brasil.un.org/pt-br/sdgs/10)

## Soluções em Energias Renováveis e Sustentáveis

O módulo atende famílias que já usam o assistente e querem reduzir o gasto com iluminação. Compara uma referência com incandescentes existentes a LED na rede e a LED com um sistema solar dedicado e bateria. O simulador aceita quantidade de lâmpadas, horas de uso, preço variável do kWh e cenário de sol. As orientações usam os dados preenchidos.

- **Terminal:** execute `python main.py` e escolha **5. Energia e sustentabilidade**.
- **Navegador:** execute `python energia_web.py` e abra `http://127.0.0.1:8765`. Pode usar o cenário inicial ou simular pouco sol e perguntar sobre a bateria.
- [Dados, cálculos, comparação e referências](docs/energia.md)
- [Dados do cenário](data/energia.json) e [série climatológica da NASA POWER](data/nasa-power-sao-paulo.json)
- [Testes técnicos e protocolo de validação com usuários](docs/testes-energia.md)

## Executar no Windows

Abra o PowerShell na pasta do repositório. Com Python 3.10 ou superior disponível, rode:

```powershell
python main.py
```

O programa usa a biblioteca padrão, funciona localmente e usa regras de busca em Python. A aplicação é independente de APIs e de projetos de outras disciplinas.

## Como a busca funciona

O menu inicia um `Assistente` que usa uma `BaseConhecimento` composta por objetos `Orientacao`. A busca compara a pergunta, as palavras-chave e o título em minúsculas, sem acentos ou pontuação. Cada palavra-chave ou expressão completa encontrada soma 3 pontos. Cada palavra distinta da pergunta com quatro letras ou mais que aparece no título soma 1 ponto. A busca devolve as tuplas `(pontos, orientação)` da maior para a menor pontuação.

A melhor pontuação determina a confiança. De 3 a 5 é média e a partir de 6 é alta. Abaixo de 3, o programa indica reformular ou navegar por categorias. A tela oferece até duas alternativas com pontuação de pelo menos 3.

## Uso e dados

- Faça uma pergunta sem dados pessoais ou navegue pelas categorias. Perguntas com `@` ou oito ou mais dígitos são recusadas antes da busca e do registro.
- Edite `data/base_conhecimento.json` para atualizar respostas e palavras-chave. Ao atualizar uma orientação, confira a fonte oficial e atualize `verificado_em`.
- O histórico guarda localmente a última pergunta válida de cada atendimento, a orientação exibida e o feedback. A navegação direta grava a pergunta em branco. Cada busca válida conta uma tentativa. Se uma busca sem resultado for resolvida pelas categorias, a escolha soma uma tentativa no mesmo atendimento.
- O tempo mede da abertura da busca ou da navegação até a exibição da orientação avaliada. Em atendimentos sem orientação, mede até o retorno ao menu. O tempo de feedback fica fora da medição.
- A taxa de respostas encontradas usa todos os atendimentos. A taxa de respostas que ajudaram usa as orientações com feedback `s` ou `n`. O tempo médio usa os atendimentos com orientação. Dúvidas sem solução incluem respostas ausentes e orientações avaliadas com `n`. A facilidade é a média das notas coletadas na saída.
- `data/historico.json` persiste atendimentos e notas de facilidade por sessão. Se estiver corrompido, o programa preserva o arquivo e registra em memória durante a sessão. O programa foi projetado para uma sessão por vez.
- A opção de exportação gera `data/atendimentos.csv` com as linhas dos atendimentos. Use dados fictícios nos testes técnicos e evite compartilhar o histórico de uso por conter texto livre.

## Fontes do SUS

As fontes abaixo foram conferidas em 16/11/2026. Cada registro da base aponta para a página que sustenta a orientação.

- [Ministério da Saúde · Perguntas frequentes do Meu SUS Digital](https://www.gov.br/saude/pt-br/composicao/seidigi/meususdigital/perguntas-e-respostas/cidadao)
- [Ministério da Saúde · Atendimento CadSUS](https://webatendimento.saude.gov.br/faq/cadsus)
- [Ministério da Saúde · Vacinação](https://www.gov.br/saude/pt-br/vacinacao)
- [Ministério da Saúde · Carteira de vacinação digital e correção de registros](https://www.gov.br/saude/pt-br/assuntos/noticias/2026/outubro/quer-consultar-suas-vacinas-saiba-como-acessar-a-carteira-de-vacinacao-pelo-meu-sus-digital)
- [Ministério da Saúde · Calendário Nacional de Vacinação](https://www.gov.br/saude/pt-br/vacinacao/calendario)
- [Ministério da Saúde · Serviços na UBS](https://www.gov.br/saude/pt-br/assuntos/noticias/2025/outubro/ubs-ou-upa-saiba-quando-procurar-a-unidade-mais-proxima-de-voce)
- [Ministério da Saúde · Portaria GM/MS nº 12.263 sobre o CadSUS](https://bvsms.saude.gov.br/bvs/saudelegis/gm/2026/prt12263_05_10_2026.html)

## Testes técnicos

```powershell
python -m unittest discover -s tests -v
python tests/simular_atendimentos.py evidencias/simulacao
```

Em 18/11/2026, os 12 testes automatizados passaram. A simulação executou 10 atendimentos no terminal em três sessões roteirizadas com 4, 3 e 3 atendimentos.

| Indicador exibido | Resultado da simulação |
| --- | --- |
| Respostas encontradas | 90% (9 de 10) |
| Respostas que ajudaram | 100% (9 de 9 avaliações programadas) |
| Tempo médio para encontrar | 0,0 s na precisão de uma casa decimal, com entradas enviadas por script |
| Tentativas por atendimento | 1,1 |
| Facilidade média | 4,3/5, a partir das entradas programadas 4, 5 e 4 |
| Dúvidas sem solução | 1. Transferência de título de eleitor, assunto fora da base SUS |

Na verificação técnica inicial, “Como faço o cartão do SUS?” ficava abaixo da pontuação mínima. Acrescentamos a expressão na orientação sobre o primeiro cartão. A pergunta passou a obter 4 pontos e a apresentar a orientação correta. O caso faz parte dos testes automatizados.

Evidências da simulação. [Histórico JSON](evidencias/simulacao/historico.json) · [CSV exportado](evidencias/simulacao/atendimentos.csv)

## Teste com usuários

Pendente. A avaliação solicitada pela disciplina prevê pelo menos três pessoas de fora da dupla, dez atendimentos no total e uma melhoria baseada nos resultados. Os indicadores da simulação descrevem a execução técnica do roteiro.

## Limitações

- A cobertura se limita aos temas incluídos no JSON. Expressões fora do vocabulário podem exigir reformulação ou navegação.
- A orientação indica canais e procedimentos administrativos. Agenda, horários e disponibilidade de serviços precisam ser conferidos na unidade ou no canal oficial.
- A regra de bloqueio identifica padrões de e-mail e números longos. Evite inserir qualquer dado pessoal em texto livre.

## Vídeo técnico

Link pendente.
