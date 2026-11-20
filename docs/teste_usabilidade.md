# Teste de facilidade de uso

## Método

O desafio aceita um teste com usuário ou com **roteiro de tarefas**. Usamos um roteiro de 8 tarefas, executado sobre a interface textual real (`src/modulos/interface_texto.py`) pelo script [`src/avaliar.py`](../src/avaliar.py). Cada tarefa abre uma sessão nova, envia as entradas previstas e confere o resultado na transcrição.

- **Participantes:** nenhum participante externo. O roteiro roda automaticamente e as dificuldades vêm de uma avaliação heurística das transcrições, guiada pelas heurísticas de Nielsen e feita com apoio de IA (registrada em [uso_ia.md](uso_ia.md)).
- **Métricas:** tarefa concluída ou não, interações usadas em relação ao caminho mínimo e mensagens de erro ou de limite exibidas.
- **Resultados detalhados e transcrições:** [resultados_usabilidade.md](resultados_usabilidade.md).

## Roteiro

| Tarefa | Objetivo | Caminho mínimo |
|---|---|---|
| U1 | Fazer uma pergunta e localizar a fonte da resposta | 3 interações |
| U2 | Encontrar a orientação sobre rotação de culturas pelo menu de temas | 4 |
| U3 | Navegar por três assuntos relacionados a partir de compostagem | 5 |
| U4 | Resolver uma pergunta ambígua escolhendo o assunto desejado | 4 |
| U5 | Recuperar-se de entrada vazia, opção inexistente e pergunta em branco | 4 |
| U6 | Receber o aviso de limite para pergunta sem base e seguir uma sugestão | 4 |
| U7 | Consultar uma orientação pelo identificador cultivo-03 | 3 |
| U8 | Trocar para o modelo A e comparar a resposta sobre compostagem | 3 |

## Resultados

- **Tarefas concluídas:** 8 de 8 (100%).
- **Interações além do caminho mínimo:** 0. Era esperado, porque o roteiro segue o caminho ideal. O número mostra que nenhuma tarefa exige passos extras, mas não mede hesitação humana.
- **Recuperação de erros:** em U5 apareceram as três mensagens de erro esperadas e a sessão voltou ao menu sem travar.

## Dificuldades encontradas nas transcrições

| # | Dificuldade | Gravidade | Situação |
|---|---|---|---|
| 1 | A opção "Consultar por identificador" pedia um código que não aparecia em nenhuma tela. | Alta | **Corrigida:** o identificador agora aparece no título de cada orientação e na lista de assuntos do menu de temas. |
| 2 | Na pergunta ambígua "Compostagem ou irrigação?", as opções saem na ordem da pontuação (Irrigação primeiro). Quem digita "2" pensando na ordem da frase recebe outro assunto. | Média | Melhoria proposta |
| 3 | As respostas do modelo B têm cerca de 118 palavras e o link longo quebra a linha em terminais estreitos. | Média | Mitigada pelo resumo de uma frase no início; melhoria proposta |
| 4 | O menu completo é reimpresso depois de cada ação e empurra a orientação para cima da tela. | Baixa | Melhoria proposta |
| 5 | Para perguntas sem nenhuma relação com a base, as sugestões são genéricas (um assunto por tema) e podem parecer aleatórias. | Baixa | A mensagem explica que não há resposta confiável |
| 6 | Com o modelo A, a navegação por relacionados some. É uma escolha de projeto, mas pode surpreender quem troca de modelo. | Informativa | Registrada na comparação de modelos |

## Melhorias propostas

1. Ordenar as opções de uma pergunta ambígua pela ordem em que os assuntos aparecem na frase.
2. Oferecer um modo compacto que mostre só resumo e fonte, com a opção "ver mais".
3. Mostrar um menu curto depois de uma resposta ("1 nova pergunta · 0 sair") em vez do menu completo.

## Limitações

- Sem participante externo, o teste não mede tempo humano, compreensão do texto nem satisfação.
- O roteiro testa o caminho previsto. Pessoas reais erram de formas que o roteiro não antecipa.
- Não foi feito teste com leitor de tela.

## Como repetir com um usuário real

Peça a uma pessoa que não conhece o projeto para executar `python src/sistema.py` e cumprir as tarefas U1 a U7 sem ajuda. Anote o tempo, os erros e os comentários:

| Tarefa | Concluiu? | Tempo (s) | Erros | Comentários |
|---|---|---|---|---|
| U1 a U7 | | | | |
