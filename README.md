# Horta Viva

Protótipo acadêmico desenvolvido para a Global Solution Citizen Tech da FIAP. O Horta Viva reúne um assistente educativo com fontes verificadas, missões de cultivo em turma e um calendário que mostra às famílias como os alimentos aprendidos na horta podem chegar à merenda e às cestas.

## Por que escolhemos a horta escolar

A Global Solution Citizen Tech propõe usar tecnologia para responder a necessidades concretas das pessoas, entre elas o acesso à alimentação. Escolhemos a escola porque ela oferece um ponto de partida próximo das crianças e das famílias. Uma atividade de colheita pode virar uma conversa sobre a origem dos alimentos, e a família pode acompanhar pelo calendário o que a turma cultivou, o que está previsto no cardápio e o que o produtor confirmou. [Global Solution Citizen Tech — FIAP](https://experience.fiap.com.br/global-solution-citizen-tech)

O protótipo transforma essa ideia em ações concretas. O assistente ajuda a responder dúvidas com referências, as missões orientam a prática com acompanhamento do professor, e o calendário distingue o cultivo da turma, a safra regional e a oferta comunicada pelos produtores. O painel mostra totais mensais de participação, refeições com ingredientes locais e retiradas de cestas, sem expor dados individuais das famílias.

## Relação com políticas públicas

- **Programa Nacional de Alimentação Escolar (PNAE).** O programa apoia a oferta de alimentação na rede pública e promove ações de educação alimentar e nutricional. O FNDE também orienta a compra direta da agricultura familiar com, no mínimo, 45% dos recursos federais que repassa ao PNAE. A horta e as missões exploram a dimensão educativa. No calendário, o exemplo da cenoura mostra como a escola pode comunicar o cultivo pedagógico e o uso confirmado na merenda, com a disponibilidade do produtor registrada separadamente. [PNAE e segurança alimentar — FNDE](https://www.gov.br/fnde/pt-br/assuntos/noticias/pnae-integra-conjunto-de-acoes-voltadas-a-seguranca-alimentar) · [Agricultura Familiar no PNAE — FNDE](https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/pnae/agricultura-familiar-pnae)
- **Programa de Aquisição de Alimentos (PAA).** O programa é uma referência complementar para entender como compras da agricultura familiar podem ampliar o acesso a alimentos. O Horta Viva usa cestas subsidiadas como cenário fictício para demonstrar a comunicação de disponibilidade e retirada. A pontuação das turmas é independente desse cenário. [Programa de Aquisição de Alimentos — MDS](https://www.gov.br/mds/pt-br/acoes-e-programas/acesso-a-alimentos-e-a-agua/programa-de-aquisicao-de-alimentos)

PNAE e PAA são referências para a proposta acadêmica. O aplicativo demonstra o fluxo com dados simulados, e a execução das políticas cabe aos órgãos responsáveis.

## Instalação e execução

Requer Python 3.11 ou superior. Na pasta do projeto, execute no Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abra o endereço local exibido no terminal. Em Linux ou macOS, use `.venv/bin/python` nos dois últimos comandos.

## Como demonstrar

- Consulte “Como regar a horta sem desperdiçar água?” para ver a orientação e sua referência.
- Consulte “Compostagem ou irrigação?” para escolher entre assuntos possíveis.
- Use **Explorar por tema** para selecionar uma área e um subtema.
- Consulte “Qual é a capital da França?” para ver como o assistente trata perguntas fora do escopo.

A busca considera palavras-chave completas, termos em comum e similaridade com perguntas de exemplo. O texto exibido vem da base local. Os links de referência podem ser abertos quando houver acesso à internet.

## Gamificação

- **Ranking** mostra pontos confirmados por turma, com classificações separadas para Educação Infantil, Fundamental I e Fundamental II. A contagem regressiva usa os prazos simulados de 30 de junho e 31 de dezembro, no horário de Brasília.
- **Área da turma** lista cinco missões, seus pontos e a situação de cada uma. Selecione uma missão concluída e envie para confirmação.
- **Área do professor** permite revisar os envios por turma e confirmar a missão e os pontos. A pontuação entra no ranking após a confirmação.

As turmas, missões e o progresso inicial são simulados. As duas áreas são acessíveis pelo menu do protótipo, sem login. A primeira alteração cria `dados/progresso_gamificacao.json` para guardar o progresso local.

## Manutenção da base

Edite `dados/conhecimento.json` mantendo os identificadores únicos e a data de consulta no formato `AAAA-MM-DD`. Para um registro com referência ainda por verificar, use `"fonte": "Pendente de validação"` e `null` em `url_fonte` e `data_consulta`. O assistente sinaliza a pendência na navegação e omite o conteúdo da orientação.

## Testes

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Programa escolar

Em **Programa escolar**, selecione **Novembro de 2026** para ver a colheita de cenoura do 2º ano e as confirmações de merenda e cesta. Compare com **Outubro de 2026**, quando a cenoura ainda estava na etapa de cuidado. **Dezembro de 2026** exemplifica um mês sem registros.

### Cadastro para uso com dados reais

Edite `dados/programa_escolar.json` e substitua os registros fictícios antes de definir `demonstracao` como `false`.

- Preencha `escola.nome` e `escola.regiao`. Em `safras`, use exatamente a região cadastrada como chave e registre os períodos de referência verificados por alimento.
- Em `alimentos`, registre os nomes, as atividades e quais são opções de ciclo curto. Use as mesmas chaves para os alimentos nas demais seções.
- Em `meses`, use chaves `AAAA-MM`. Cadastre a etapa e a próxima atividade em `horta` e, separadamente, a disponibilidade comunicada pelo produtor em `produtor`.
- Em `merenda` e `cestas`, use `Previsto` ou `Confirmado` e informe, quando disponíveis, o preparo e a data da merenda, o prazo de reserva e a data de retirada da cesta. Use datas `AAAA-MM-DD`.
- Para os indicadores, registre as turmas que efetivamente participaram, as refeições efetivamente servidas com alimentos de produtores locais por dia e o total mensal de famílias distintas que retiraram cestas subsidiadas. Conte cada refeição uma vez, mesmo que inclua vários ingredientes locais.

O calendário usa registros agregados para as cestas. Mantenha dados familiares e valores de subsídio individual fora desse arquivo. A pontuação da gamificação é independente desses registros.
