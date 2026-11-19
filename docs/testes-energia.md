# Validação do módulo de energia

## Testes técnicos — 18/11/2026

| Situação | Evidência observada |
| --- | --- |
| Cenário inicial | 54,00 kWh/mês na referência, 8,10 kWh/mês com LED e 45,90 kWh/mês de redução |
| Pergunta sobre economia | A resposta usa a mesma economia da comparação e apresenta investimento de R$ 72 e retorno simples de 1,6 mês |
| Cenário com pouco sol | O simulador apresenta 71,7% de cobertura solar e 2,30 kWh de rede. A resposta sobre bateria acompanha a mudança |
| Pergunta sobre impacto | São exibidos os valores de CO₂ da rede e o escopo operacional do indicador |
| Tarifa com vírgula | Para R$ 0,85/kWh, a resposta recalcula a economia para R$ 39,02 |
| Uso zero e entradas inválidas | A cobertura fica sem valor quando não há consumo. Horas acima de 24 e cenário desconhecido são recusados |
| Interface móvel | A largura de 390 px foi testada sem rolagem horizontal, com seleção de pergunta e retorno da resposta |
| Referências | Os cinco links de origem são exibidos no simulador |
| Menu do terminal | A opção 5 carrega o cenário com pouco sol, retorna 2,30 kWh de rede na resposta e volta ao menu após Enter |
| Regressão do assistente | A suíte com 18 testes passou, incluindo os 12 do módulo original |

Para repetir a suíte com Python 3.10 ou superior:

```pwsh
python -m unittest discover -s tests -v
```

Para reproduzir as verificações da interface, execute `python energia_web.py` e abra `http://127.0.0.1:8765`. Faça as ações descritas na tabela usando o cenário inicial, exceto quando a linha pedir uma alteração. Os testes do navegador foram feitos no Microsoft Edge com automação, sem participação de usuários.

### Mudanças feitas durante a verificação técnica

- O comparativo e a resposta textual aplicam o mesmo arredondamento à parcela de rede de 2,295 kWh no cenário de pouco sol. A tela abrevia 2,30 kWh para 2,3 kWh. Os cálculos de custo e cobertura usam os valores antes da formatação.
- O indicador de cobertura exibe “Sem uso informado” quando o tempo de uso é zero. A entrada “25” no campo de horas recebe uma mensagem com a faixa válida.

## Teste com usuários

A coleta com pessoas do público-alvo está pendente. Este protocolo é para verificar compreensão e utilidade, com registro anônimo e sem coletar faturas, endereços, documentos ou nomes dos participantes.

1. Abra o cenário inicial. Peça à pessoa que descubra quanto economizaria trocando as seis lâmpadas e explique se a estimativa vale para toda a conta.
2. Peça para mudar o cenário para **Pouco sol (hipotético)** e perguntar sobre a bateria. A pessoa deve conseguir explicar o que significam a cobertura e a parcela de rede.
3. Peça para indicar o primeiro passo que faria em casa e explicar se a orientação ajuda a decidir. Registre a dificuldade e uma sugestão de melhoria com palavras da própria pessoa, sem dados pessoais.
4. Ajuste a interface ou o texto a partir de uma dificuldade observada. Repita a tarefa afetada e registre o resultado obtido.

| Código | Tarefa | Conseguiu explicar? | Comentário recebido | Ajuste aplicado e resultado do reteste |
| --- | --- | --- | --- | --- |
| — | — | — | Coleta pendente | — |
