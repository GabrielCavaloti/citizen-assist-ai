# Citizen Assist AI

Projeto da FIAP GS2026.2 para a disciplina Pensamento Computacional e Automação com Python. Esta primeira versão orienta pessoas que usam o SUS pela primeira vez sobre Cartão SUS e cadastro, vacinação e atendimento na UBS.

## Executar no Windows

Abra o PowerShell na pasta do repositório. Com Python 3.10 ou superior disponível, rode:

```powershell
python main.py
```

Nesta máquina, o atalho `python` do Windows não iniciou. O Python 3.12 do Codex funcionou com o seguinte comando:

```powershell
& 'C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1112-737-0_26.1112.737.0_x64__3k8sg7r9htsxt/dependencies/python/python.exe' -X utf8 main.py
```

O programa usa apenas a biblioteca padrão e funciona localmente. As fontes oficiais são exibidas como links para consulta. O sistema usa palavras-chave e títulos para encontrar orientações e funciona como guia acadêmico para procedimentos administrativos.

## Uso e dados

- Faça uma pergunta sem dados pessoais ou navegue pelas categorias. Perguntas com `@` ou oito ou mais dígitos são recusadas antes da busca e do registro.
- A confiança indica o resultado da busca por termos. O sistema considera alta a partir de 6 pontos, média de 3 a 5 e propõe reformulação ou navegação abaixo de 3. Termos repetidos contam uma vez.
- Edite `data/base_conhecimento.json` para atualizar respostas e palavras-chave. Ao atualizar uma orientação, confira a fonte oficial e atualize `verificado_em`.
- O histórico guarda localmente a última pergunta válida de cada atendimento, a orientação exibida e o feedback. A navegação direta grava a pergunta em branco. Cada busca válida conta uma tentativa. Se uma busca sem resultado for resolvida pelas categorias, a escolha soma uma tentativa no mesmo atendimento.
- O tempo mede da abertura da busca ou da navegação até a exibição da orientação avaliada. Em atendimentos sem orientação, mede até o retorno ao menu. O tempo de feedback fica fora da medição.
- A taxa de respostas encontradas usa todos os atendimentos. A taxa de respostas que ajudaram usa as orientações com feedback `s` ou `n`. O tempo médio usa os atendimentos com orientação. Dúvidas sem solução incluem respostas ausentes e orientações avaliadas com `n`. A facilidade é a média das notas coletadas na saída.
- `data/historico.json` persiste atendimentos e notas de facilidade por sessão. Se estiver corrompido, o programa preserva o arquivo e registra em memória durante a sessão. O programa foi projetado para uma sessão por vez.
- A opção de exportação gera `data/atendimentos.csv` com as linhas dos atendimentos. Use dados fictícios nos testes técnicos e evite compartilhar o histórico de uso por conter texto livre.

## Testes

```powershell
python -m unittest discover -s tests -v
```

Se estiver usando o Python do Codex, substitua `python` pelo caminho completo indicado acima, seguido de `-X utf8` e dos argumentos do teste. Os testes usam diretórios temporários. A etapa acadêmica de avaliação com usuários prevê três pessoas reais de fora da dupla e dez atendimentos no total.
