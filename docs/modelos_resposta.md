# Modelos de instrução de resposta

O Horta Viva não chama um modelo de linguagem. Cada modelo abaixo é uma **instrução documentada** (papel, formato, obrigação de citar a fonte e limites) que o código cumpre ao montar a resposta a partir do texto da base. As instruções estão em [`src/modulos/modelos_resposta.py`](../src/modulos/modelos_resposta.py) e podem ser trocadas na interface textual pela opção **4** do menu.

## Modelo A · resposta direta

**Instrução**

> Responda com a orientação encontrada na base, em texto corrido, e informe o nome da fonte. Se não houver orientação, diga que não encontrou a resposta.

**Exemplo** (pergunta: "Como fazer compostagem?")

```text
Cascas de frutas, talos e borra de café podem ser combinados com folhas secas ou palha. Mantenha a mistura úmida e arejada. Evite carnes, óleos, sobras cozidas e fezes de animais.
Fonte: Embrapa — Hortas Pedagógicas: Manual prático para instalação
```

## Modelo B · assistente educativo estruturado (padrão)

**Instrução**

> **Papel:** você é um assistente educativo de um protótipo acadêmico sobre alimentação e hortas escolares, sem vínculo com órgãos públicos.
> **Formato:** título com o assunto e o tema, resumo em uma frase, orientação, fonte com data de consulta e link, avisos e até três assuntos relacionados para continuar.
> **Fonte:** toda orientação deve citar a referência da base; sem referência, não responda.
> **Limites:** use apenas o texto da base, não invente instruções, avise quando for preciso confirmar a informação e, sem resposta confiável, explique o limite e sugira assuntos.

**Exemplo** (mesma pergunta)

```text
== Compostagem · Cultivo sustentável · cultivo-01 ==
Resumo: Combine resíduos vegetais crus com material seco.
Orientação: Cascas de frutas, talos e borra de café podem ser combinados com folhas secas ou palha. Mantenha a mistura úmida e arejada. Evite carnes, óleos, sobras cozidas e fezes de animais.
Fonte: Embrapa — Hortas Pedagógicas: Manual prático para instalação (consultada em 17/11/2026)
Link: https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1120149/1/manual-pratico-instalacao.pdf
Aviso: Conteúdo educativo de um protótipo acadêmico, sem vínculo com órgãos públicos. Confirme informações atualizadas na fonte indicada.
Continue explorando:
  1. Cobertura do solo (Cultivo sustentável)
  2. Rotação de culturas (Cultivo sustentável)
  3. Ciências na horta (Educação comunitária e hortas escolares)
```

Quando a pergunta não tem resposta confiável, o modelo A diz apenas "Não encontrei a resposta." O modelo B explica o limite, sugere até três assuntos numerados e repete o aviso.

## Comparação nas perguntas de teste

**Método.** Os dois modelos formataram os mesmos resultados de busca das 22 perguntas do conjunto principal. O script [`src/avaliar.py`](../src/avaliar.py) verifica no texto produzido quatro critérios objetivos, tirados dos requisitos do desafio:

| Critério | Modelo A | Modelo B |
|---|---|---|
| Cita fonte, data de consulta e link (respostas encontradas) | 0/12 | 12/12 |
| Inclui aviso de limitação ou de confirmação | 0/19 | 19/19 |
| Oferece opções numeradas para continuar | 0/8 | 20/20 |
| Explica o limite e diz o que fazer (vazia, ambígua, sem base) | 0/10 | 10/10 |
| **Critérios atendidos** | **0%** | **100%** |
| Palavras por resposta encontrada (média) | 41 | 118 |

Os números da última execução ficam em [resultados_testes.md](resultados_testes.md#comparação-dos-modelos-de-resposta). O denominador do terceiro critério muda entre os modelos porque só o modelo B oferece assuntos relacionados depois de uma resposta encontrada.

**Justificativa da escolha.** O modelo B virou o padrão porque é o único que cumpre as obrigações do desafio: citar a fonte de forma verificável, avisar sobre os limites e oferecer caminhos quando não há resposta. O custo é o tamanho: as respostas do B têm em média 118 palavras, contra 41 do A. Para não perder clareza, o B usa rótulos fixos ("Resumo", "Orientação", "Fonte", "Aviso") e põe o resumo de uma frase logo no começo, então quem tem pressa pode parar ali. O modelo A continua disponível para comparação e como base para canais curtos no futuro, desde que ganhe pelo menos o link da fonte.

**Limitações da comparação.** Os critérios verificam se os elementos estão presentes, não se a pessoa entendeu a resposta. Como foram tirados dos requisitos que o modelo B foi escrito para cumprir, a comparação mostra que o A não basta, mas não prova que o B seja o formato mais claro possível. Isso pede um teste com leitores reais (ver [teste_usabilidade.md](teste_usabilidade.md)).

## Uso futuro com um modelo de linguagem

Se um LLM for integrado, o modelo B serve de instrução de sistema. A pergunta do usuário e o registro encontrado pela busca entram como contexto:

```text
[sistema] <instrução do Modelo B>
[contexto] id, subtema, resumo, resposta, fonte, url_fonte e data_consulta do registro encontrado
[usuário] <pergunta>
```

A resposta gerada só seria exibida se contivesse o `url_fonte` do registro e não trouxesse instruções ausentes do campo `resposta`. Caso contrário, o sistema mostraria o texto da base formatado pelas regras atuais. Essa checagem segue a orientação do desafio de confrontar respostas de modelos externos com a base verificada.
