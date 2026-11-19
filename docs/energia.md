# Soluções em Energias Renováveis e Sustentáveis

## Público e necessidade

O módulo de energia atende famílias que já usam o Citizen Assist AI e querem entender o gasto com a iluminação de casa. O estudo considera uma residência em São Paulo (SP) com seis lâmpadas incandescentes de 60 W. A quantidade de lâmpadas e o tempo de uso foram estimados para o exemplo. Famílias que já usam LED precisam conferir a potência e o brilho dos produtos que possuem antes de aplicar a comparação.

O serviço comparado é manter cerca de 800 lúmens por ponto em seis pontos por cinco horas diárias, durante 30 dias. A referência de 60 W e a alternativa LED de 9 W entregam fluxo luminoso semelhante. Distribuição da luz, temperatura de cor, encaixe e tensão precisam ser confirmados no produto e no ambiente.

## Dados e premissas

| Dado | Valor utilizado | Origem |
| --- | ---: | --- |
| Pontos de luz e tempo de uso | 6 pontos, 5 h/dia, 30 dias | Perfil hipotético editável, com iluminação ao fim do dia |
| Incandescente existente | 60 W, aproximadamente 800 lm | Tabela de equivalência do DOE |
| LED | 9 W, 803 lm no produto de referência | Registro Inmetro 001887/2024 |
| Preço variável da energia | R$ 1,00/kWh | Premissa editável. Use a parcela variável da fatura, com tributos e bandeira quando aplicáveis; exclua itens fixos |
| Irradiação de junho em São Paulo | 3,2578 kWh/m²/dia | NASA POWER, parâmetro ALLSKY_SFC_SW_DWN, ponto de consulta −23,55°, −46,63°, climatologia de 2001–2025 |
| Cenário com pouco sol | 1,50 kWh/m²/dia | Hipótese de sensibilidade, aplicada aos mesmos 30 dias |
| Kit fotovoltaico independente | Painel de 200 Wp, bateria de 12,8 V e 50 Ah, controlador e inversor | Especificações hipotéticas. O inversor deve comportar a carga e sua partida, sob verificação profissional |
| Perdas e reserva | Rendimento de carga de 75%, bateria útil de 80%, inversor de 90% e autoconsumo de 10 Wh/dia | Valores adotados para a simulação, com inversor desligado fora do uso. Devem ser conferidos nas fichas técnicas e no perfil real |
| Fator de emissão da rede | 0,0385 kg de CO₂/kWh | MCTI, fator médio histórico do SIN em 2023. Conversão de 0,0385 t/MWh |
| Investimento em LED | R$ 12 por unidade | Preço estimado para o exercício, sem cotação comercial |
| Investimento adicional em solar | R$ 2.000 | Orçamento estimado para o exercício, detalhado abaixo |

Valores e links usados pelo código estão em [dados de energia](../data/energia.json). A [resposta original da NASA](../data/nasa-power-sao-paulo.json) registra a série, unidade e período. Irradiação diária média em superfície horizontal serve aqui de aproximação para horas de sol pico (HSP), a quantidade equivalente de horas a 1 kW/m². A geração real depende de inclinação, orientação, temperatura, perdas e sombra.

O investimento solar ilustrativo soma R$ 350 de painel, R$ 700 de bateria, R$ 150 de controlador, R$ 250 de inversor e R$ 550 de estrutura, proteção e instalação. O valor da alimentação de reserva deve ser cotado quando precisar ser instalada. O LED usa os pontos existentes em condições adequadas. A referência tem investimento inicial zero porque as lâmpadas já existem.

## Cálculos reproduzíveis

1. **Potência e energia.** Incandescente: 6 × 60 W = 360 W. Em 30 dias: 0,360 kW × 5 h/dia × 30 dias = **54,00 kWh**. LED: 6 × 9 W = 54 W. No mesmo período: 0,054 × 5 × 30 = **8,10 kWh**. A redução é de 45,90 kWh, ou 85% da energia das lâmpadas.
2. **Geração do painel e energia útil.** A potência de pico em kWp, multiplicada pelas horas de sol pico e pelo rendimento de 75%, estima a energia de carga em corrente contínua. Em junho, 0,2 × 3,2578 × 0,75 = 0,48867 kWh/dia. Esse valor cabe na capacidade útil de 0,512 kWh da bateria. Descontando o consumo auxiliar e a perda do inversor, (0,48867 − 0,010) × 0,90 = 0,430803 kWh/dia disponíveis na saída. Como as lâmpadas precisam de 0,270 kWh/dia, o aproveitamento solar fica limitado a essa demanda.
3. **Pouco sol.** 0,2 × 1,50 × 0,75 = 0,225 kWh/dia na carga. Após o consumo auxiliar e o inversor, restam 0,1935 kWh/dia úteis. Em 30 dias, cerca de **5,81 kWh solares** e **2,30 kWh da rede** mantêm o mesmo serviço, com cobertura solar de 71,7%. Os valores arredondados separadamente podem somar um centésimo a mais.
4. **Autonomia sem geração.** A bateria fornece nominalmente 12,8 × 50 × 0,80 = 512 Wh úteis em corrente contínua. As lâmpadas pedem 270 Wh/dia em corrente alternada, equivalentes a 270/0,90 + 10 = 310 Wh/dia da bateria. Com carga cheia, 512/310 ≈ **1,65 dia de uso**.
5. **Custo e CO₂.** Energia comprada da rede × tarifa variável estima a despesa de iluminação. Energia da rede × 0,0385 estima o CO₂ operacional associado ao consumo. A pegada de ciclo de vida inclui fabricação, transporte, reposição e destinação, que ficam fora do indicador.
6. **Retorno simples do investimento.** Dividindo o custo dos seis LEDs pela economia estimada, R$ 72 ÷ R$ 45,90 ≈ 1,6 mês. Já o acréscimo de R$ 2.000 do sistema solar economizaria até R$ 8,10 por período em relação ao LED ligado à rede. Se essa cobertura se repetisse, o retorno simples seria de aproximadamente 246,9 meses. No cenário de pouco sol, seriam 344,5 meses. São comparações ilustrativas que excluem substituições, financiamento, degradação e manutenção.

## Comparação para 30 dias

| Opção | Consumo das lâmpadas (kWh) | Rede (kWh) | Solar usado (kWh) | Investimento | Custo variável | CO₂ da rede (kg) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Incandescente + rede | 54,00 | 54,00 | 0 | R$ 0 | R$ 54,00 | 2,08 |
| LED + rede | 8,10 | 8,10 | 0 | R$ 72 | R$ 8,10 | 0,31 |
| LED + solar com bateria, junho médio | 8,10 | 0 | 8,10 | R$ 2.072 | R$ 0,00 | 0,00 |
| LED + solar com bateria, pouco sol | 8,10 | 2,30 | 5,81 | R$ 2.072 | R$ 2,30 | 0,09 |

**Recomendação.** Para uma casa que ainda usa incandescentes, a troca por LED de brilho equivalente é o primeiro passo. No exemplo, ela reduz o consumo em 85% com investimento estimado de R$ 72. O kit solar pode atender quem dá mais valor à autonomia da iluminação e tem local sem sombra, orçamento e instalação viável. Com apenas essa carga, a economia mensal adicional é pequena em relação ao custo do kit. Também é preciso considerar manutenção, reposição da bateria e descarte de lâmpadas e componentes nos canais adequados.

**Limites do solar.** A estimativa usa um dia típico repetido, carga diurna e uso predominantemente após o pôr do sol. O modelo limita a energia solar diária à capacidade útil da bateria e ao consumo. Ele não acompanha o estado de carga dia a dia nem prevê dias nublados consecutivos. O kit é dedicado e separado do fornecimento da distribuidora. A parcela de rede é a energia necessária para manter o serviço com uma alimentação de reserva projetada por profissional, com isolamento apropriado e sem injeção de energia. Sem reserva, essa parcela representa iluminação que pode ficar sem atendimento. Os custos variáveis podem ser zero apenas para a iluminação modelada. A fatura residencial inclui os outros consumos e as cobranças fixas.

## Integração

A opção **5. Energia e sustentabilidade** no menu do Citizen Assist AI abre o mesmo modelo Python usado pelo simulador web. O assistente monta as respostas a partir dos resultados atuais. Perguntas sobre economia, consumo, solar e impacto ambiental usam métricas do cenário selecionado. A interface web e o módulo de energia do terminal não armazenam as perguntas.

## Referências

- [DOE · Potência e lúmens em lâmpadas equivalentes](https://www.energy.gov/cmei/femp/purchasing-energy-efficient-light-bulbs)
- [Inmetro · Registro do LED de 9 W e 803 lm](https://registro.inmetro.gov.br/consulta/detalhe.aspx?NumeroRegistro=001887%2F2024&pag=1)
- [NASA POWER · Documentação do serviço de climatologia](https://power.larc.nasa.gov/docs/services/api/temporal/climatology/)
- [NASA POWER · Consulta usada para São Paulo](https://power.larc.nasa.gov/api/temporal/climatology/point?parameters=ALLSKY_SFC_SW_DWN&community=RE&longitude=-46.63&latitude=-23.55&format=JSON)
- [ANEEL · Composição do custo da energia na fatura](https://www.gov.br/aneel/pt-br/assuntos/tarifas/entenda-a-tarifa/custo-da-energia-que-chega-aos-consumidores)
- [MCTI · Fator médio de emissão do SIN de 2023](https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/noticias/2024/02/fator-de-emissao-de-co2-na-geracao-de-energia-eletrica-no-brasil-em-2023-e-o-menor-em-12-anos)
