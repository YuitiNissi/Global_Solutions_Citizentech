# Uso de inteligência artificial

## Ferramenta

A equipe usou o **Claude** (Anthropic), pelo Claude Code, como assistente de programação, revisão e documentação.

## O protótipo não usa IA em execução

O Horta Viva não chama nenhum modelo de linguagem nem API externa. Todas as orientações exibidas são o texto de [`data/conhecimento.json`](../data/conhecimento.json), selecionado por regras de busca e formatado pelos modelos de instrução descritos em [modelos_resposta.md](modelos_resposta.md). Nenhum texto exibido como orientação é gerado no momento da consulta.

## Onde a IA apoiou o trabalho

Na etapa final (19/11/2026), a IA apoiou:

- a conferência do projeto contra os requisitos do enunciado e a lista do que faltava;
- a reorganização do repositório no modelo da coordenação (`src/`, `data/`, `docs/`, `assets/`);
- a interface textual `src/sistema.py`, a busca por identificador, o grafo de assuntos relacionados e as sugestões quando não há resposta;
- a etapa 2 da busca (cobertura ponderada por IDF);
- os dois modelos de instrução de resposta e os critérios usados para compará-los;
- as perguntas de teste e de validação, os scripts de avaliação e o roteiro de usabilidade;
- a análise heurística das transcrições do roteiro;
- a redação do README e destes documentos.

Os campos `relacionados` e `aviso` da base foram propostos nessa etapa. Os avisos são frases de cautela gerais (supervisão de crianças, nutricionista responsável, profissional de saúde) e não acrescentam instruções novas às orientações das fontes.

## Validação crítica

| Verificação | Como foi feita | Resultado |
|---|---|---|
| Código funciona | 48 testes automatizados (`python -m pytest -q`) cobrindo base, busca, interface textual, app web, avaliação e roteiro | 48 aprovados |
| Respostas não inventadas | O texto exibido é copiado da base; o indicador "respostas indevidas" conta respostas dadas a perguntas sem base | 0 em 36 perguntas, inclusive perguntas fora do escopo com palavras do domínio, como "merenda" e "Bolsa Família" |
| Melhoria sem viés de ajuste | As perguntas de validação foram escritas antes da etapa 2, e o limiar foi fixado olhando só o conjunto principal. A rodada 1 (sem a etapa 2) é regenerada a cada avaliação | O conjunto de validação teve desempenho menor (71,4% contra 81,8%), e o relatório mostra isso |
| Fontes acessíveis | Os links da base foram testados por requisição HTTP em 19/11/2026 | 3 de 4 responderam com o PDF. O link do FNDE ("Hortas escolares") retornou **HTTP 401** para acesso automatizado. A equipe deve abri-lo no navegador e, se não abrir, atualizar a referência dos seis registros `escola-*` |
| Facilidade de uso | O roteiro de 8 tarefas rodou na interface real | 8/8 concluídas, com a limitação declarada de não ter havido participante externo |

## Responsabilidade da equipe

A IA acelerou a escrita do código e dos documentos, mas a equipe é responsável por entender, testar e saber explicar cada parte da solução: as regras de busca, os limiares, os critérios de acerto e as limitações da avaliação. Os resultados registrados vêm de execuções reais dos scripts, sem números escritos à mão.
