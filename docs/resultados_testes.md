# Rodada 2 · versão atual (etapas 1 e 2)

> Arquivo gerado por `python src/avaliar.py`. Não edite à mão: execute o script novamente.

- Execução: 19/11/2026 22:28 (horário de Brasília)
- Ambiente: Python 3.14.3 · Windows 11
- Tempo de consulta: média de 200 execuções da função `buscar` para cada pergunta

## Resumo

| Conjunto | Perguntas | Acertos | Taxa de acerto | Tempo médio (ms) | Respostas indevidas |
|---|---|---|---|---|---|
| Conjunto principal | 22 | 18 | 81.8% | 3.683 | 0 |
| Conjunto de validação | 14 | 10 | 71.4% | 5.200 | 0 |

## Conjunto principal

22 perguntas: diretas, reformuladas, ambíguas, fora do escopo, vazias e com erro de digitação.

### Indicadores

| Indicador | Valor |
|---|---|
| Perguntas testadas | 22 |
| Acertos | 18 |
| Erros | 4 |
| **Taxa de acerto** | **81.8%** |
| **Tempo médio de consulta** | **3.683 ms** |
| Tempo mediano | 2.817 ms |
| Tempo máximo | 7.881 ms |
| Respostas indevidas (respondeu sem ter base) | 0 |

| Tipo | Acertos | Total | Taxa |
|---|---|---|---|
| direta | 6 | 6 | 100.0% |
| reformulada | 5 | 7 | 71.4% |
| ambigua | 1 | 2 | 50.0% |
| fora_do_escopo | 4 | 4 | 100.0% |
| vazia | 2 | 2 | 100.0% |
| erro_digitacao | 0 | 1 | 0.0% |

### Registro dos testes

| ID | Tipo | Pergunta | Esperado | Obtido | Resultado | Tempo (ms) | Observação |
|---|---|---|---|---|---|---|---|
| T01 | direta | Como fazer compostagem? | cultivo-01 | cultivo-01 · Compostagem | ✅ acerto | 1.942 |  |
| T02 | direta | O que são alimentos in natura? | alimentacao-01 | alimentacao-01 · Alimentos in natura | ✅ acerto | 2.476 |  |
| T03 | direta | Como ensinar matemática na horta? | escola-01 | escola-01 · Matemática na horta | ✅ acerto | 2.447 |  |
| T04 | direta | Como planejar as refeições da semana? | alimentacao-03 | alimentacao-03 · Planejamento de refeições | ✅ acerto | 2.763 |  |
| T05 | direta | Como melhorar a drenagem do canteiro? | cultivo-05 | cultivo-05 · Drenagem dos canteiros | ✅ acerto | 2.585 |  |
| T06 | direta | Quem cuida da horta nas férias escolares? | escola-04 | escola-04 · Cuidados durante as férias | ✅ acerto | 2.517 |  |
| T07 | reformulada | Qual o jeito certo de regar as plantas sem gastar muita água? | cultivo-02 | cultivo-02 · Irrigação | ✅ acerto | 5.555 |  |
| T08 | reformulada | Refrigerante faz parte dos ultraprocessados? | alimentacao-02 | alimentacao-02 · Ultraprocessados | ✅ acerto | 2.774 |  |
| T09 | reformulada | Dicas para os pais participarem da horta da escola | escola-03 | escola-03 · Participação das famílias | ✅ acerto | 4.684 |  |
| T10 | reformulada | Vale a pena colocar palha em cima da terra do canteiro? | cultivo-03 | Sem orientação confiável · sugeriu cultivo-03, cultivo-01, cultivo-05 | ❌ erro | 6.841 | Não respondeu, mas sugeriu o assunto esperado |
| T11 | reformulada | Quero aprender a cozinhar, por onde começo? | alimentacao-06 | alimentacao-06 · Habilidades culinárias | ✅ acerto | 4.512 |  |
| T12 | reformulada | Em que lugar devo montar a horta da escola? | cultivo-04 | cultivo-04 · Local da horta | ✅ acerto | 4.768 |  |
| T13 | reformulada | Por que trocar a família das plantas a cada ciclo no canteiro? | cultivo-06 | Sem orientação confiável · sugeriu cultivo-03, cultivo-05, cultivo-06 | ❌ erro | 7.881 | Não respondeu, mas sugeriu o assunto esperado |
| T14 | ambigua | Compostagem ou irrigação? | Ambígua: cultivo-01, cultivo-02 | Ambígua: cultivo-02, cultivo-01 | ✅ acerto | 2.173 |  |
| T15 | ambigua | Feira ou cardápio semanal? | Ambígua: alimentacao-05, alimentacao-03 | alimentacao-03 · Planejamento de refeições | ❌ erro | 2.031 | Comportamento diferente do esperado |
| T16 | fora_do_escopo | Qual é a capital da França? | Sem orientação confiável | Sem orientação confiável · sugeriu alimentacao-01, cultivo-01, escola-01 | ✅ acerto | 5.178 |  |
| T17 | fora_do_escopo | Como tirar a segunda via do RG? | Sem orientação confiável | Sem orientação confiável · sugeriu alimentacao-01, cultivo-01, escola-01 | ✅ acerto | 5.196 |  |
| T18 | fora_do_escopo | Qual remédio tomar para dor de cabeça? | Sem orientação confiável | Sem orientação confiável · sugeriu alimentacao-01, cultivo-01, escola-01 | ✅ acerto | 6.018 |  |
| T19 | fora_do_escopo | Como investir na bolsa de valores? | Sem orientação confiável | Sem orientação confiável · sugeriu alimentacao-01, cultivo-01, escola-01 | ✅ acerto | 5.831 |  |
| T20 | vazia | (vazia) | Aviso de entrada vazia | Aviso de entrada vazia | ✅ acerto | 0.001 |  |
| T21 | vazia | ??? | Aviso de entrada vazia | Aviso de entrada vazia | ✅ acerto | 0.002 |  |
| T22 | erro_digitacao | como fazer compostajem | cultivo-01 | Sem orientação confiável · sugeriu cultivo-01 | ❌ erro | 2.860 | Não respondeu, mas sugeriu o assunto esperado |

## Conjunto de validação

14 perguntas novas, escritas antes da melhoria da busca e nunca usadas para ajustá-la. Inclui perguntas fora do escopo com palavras do domínio, como merenda e família.

### Indicadores

| Indicador | Valor |
|---|---|
| Perguntas testadas | 14 |
| Acertos | 10 |
| Erros | 4 |
| **Taxa de acerto** | **71.4%** |
| **Tempo médio de consulta** | **5.200 ms** |
| Tempo mediano | 5.241 ms |
| Tempo máximo | 8.260 ms |
| Respostas indevidas (respondeu sem ter base) | 0 |

| Tipo | Acertos | Total | Taxa |
|---|---|---|---|
| reformulada | 5 | 9 | 55.6% |
| direta | 1 | 1 | 100.0% |
| ambigua | 1 | 1 | 100.0% |
| fora_do_escopo | 3 | 3 | 100.0% |

### Registro dos testes

| ID | Tipo | Pergunta | Esperado | Obtido | Resultado | Tempo (ms) | Observação |
|---|---|---|---|---|---|---|---|
| V01 | reformulada | Que tipo de lixo da cozinha pode ir para a composteira? | cultivo-01 | Sem orientação confiável · sugeriu cultivo-01, alimentacao-06 | ❌ erro | 6.644 | Não respondeu, mas sugeriu o assunto esperado |
| V02 | reformulada | Como usar menos água para molhar os canteiros? | cultivo-02 | cultivo-02 · Irrigação | ✅ acerto | 5.130 |  |
| V03 | reformulada | Biscoito recheado é saudável? | alimentacao-02 | alimentacao-02 · Ultraprocessados | ✅ acerto | 2.237 |  |
| V04 | reformulada | Como fazer a lista de compras do mês? | alimentacao-03 | alimentacao-03 · Planejamento de refeições | ✅ acerto | 2.914 |  |
| V05 | reformulada | Comer vendo celular faz mal? | alimentacao-04 | Sem orientação confiável · sugeriu alimentacao-04, alimentacao-06 | ❌ erro | 5.351 | Não respondeu, mas sugeriu o assunto esperado |
| V06 | reformulada | Que atividades de ciências dá para fazer com as plantas da escola? | escola-02 | escola-02 · Ciências na horta | ✅ acerto | 3.677 |  |
| V07 | reformulada | Como trazer a comunidade para ajudar na horta? | escola-03 | Sem orientação confiável · sugeriu escola-03, cultivo-02, cultivo-03 | ❌ erro | 6.820 | Não respondeu, mas sugeriu o assunto esperado |
| V08 | reformulada | Como juntar várias matérias num projeto sobre a horta? | escola-06 | Sem orientação confiável · sugeriu escola-06, cultivo-02, cultivo-03 | ❌ erro | 8.260 | Não respondeu, mas sugeriu o assunto esperado |
| V09 | reformulada | O que é comida minimamente processada? | alimentacao-01 | alimentacao-01 · Alimentos in natura | ✅ acerto | 4.905 |  |
| V10 | direta | Como organizar a horta durante o recesso escolar? | escola-04 | escola-04 · Cuidados durante as férias | ✅ acerto | 3.216 |  |
| V11 | ambigua | Rotação de culturas ou cobertura morta? | Ambígua: cultivo-06, cultivo-03 | Ambígua: cultivo-03, cultivo-06 | ✅ acerto | 2.819 |  |
| V12 | fora_do_escopo | Qual o horário da merenda na escola do meu filho? | Sem orientação confiável | Sem orientação confiável · sugeriu escola-05, escola-01, escola-02 | ✅ acerto | 7.730 |  |
| V13 | fora_do_escopo | Como fazer o cadastro no Bolsa Família? | Sem orientação confiável | Sem orientação confiável · sugeriu escola-03 | ✅ acerto | 7.522 |  |
| V14 | fora_do_escopo | Quanto custa um saco de adubo? | Sem orientação confiável | Sem orientação confiável · sugeriu cultivo-05 | ✅ acerto | 5.574 |  |

## Comparação dos modelos de resposta

Os dois modelos recebem os mesmos resultados de busca das perguntas do conjunto principal. Cada critério é verificado no texto produzido; a coluna mostra atendidos/aplicáveis.

| Critério | Modelo A · resposta direta | Modelo B · assistente educativo estruturado |
|---|---|---|
| Cita fonte, data de consulta e link | 0/12 | 12/12 |
| Inclui aviso de limitação ou de confirmação | 0/19 | 19/19 |
| Oferece opções numeradas para continuar | 0/8 | 20/20 |
| Explica o limite e diz o que fazer | 0/10 | 10/10 |
| **Critérios atendidos** | **0.0%** | **100.0%** |
| Palavras por resposta encontrada (média) | 41 | 118 |
