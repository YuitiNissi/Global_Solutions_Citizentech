"""Dois modelos de instrução de resposta, aplicados como regras de formatação.

O protótipo não chama um modelo de linguagem: cada modelo é uma instrução documentada
(papel, formato, fonte e limites) que o código cumpre ao montar a resposta a partir da base.
"""

from dataclasses import dataclass
from datetime import date

from modulos.assistente import AVISO_GERAL


@dataclass(frozen=True)
class ModeloResposta:
    codigo: str
    nome: str
    instrucao: str


MODELOS = {
    "A": ModeloResposta(
        codigo="A",
        nome="Modelo A · resposta direta",
        instrucao=(
            "Responda com a orientação encontrada na base, em texto corrido, e informe o nome da fonte. "
            "Se não houver orientação, diga que não encontrou a resposta."
        ),
    ),
    "B": ModeloResposta(
        codigo="B",
        nome="Modelo B · assistente educativo estruturado",
        instrucao=(
            "Papel: você é um assistente educativo de um protótipo acadêmico sobre alimentação e hortas "
            "escolares, sem vínculo com órgãos públicos. "
            "Formato: título com o assunto e o tema, resumo em uma frase, orientação, fonte com data de "
            "consulta e link, avisos e até três assuntos relacionados para continuar. "
            "Fonte: toda orientação deve citar a referência da base; sem referência, não responda. "
            "Limites: use apenas o texto da base, não invente instruções, avise quando for preciso "
            "confirmar a informação e, sem resposta confiável, explique o limite e sugira assuntos."
        ),
    ),
}
MODELO_PADRAO = "B"


def _data(valor):
    return f"{date.fromisoformat(valor):%d/%m/%Y}"


def _lista_numerada(registros):
    return [f"  {numero}. {item['subtema']} ({item['tema']})" for numero, item in enumerate(registros, start=1)]


def formatar_orientacao(registro, codigo=MODELO_PADRAO, relacionados=()):
    if codigo == "A":
        return f"{registro['resposta']}\nFonte: {registro['fonte']}"

    linhas = [
        f"== {registro['subtema']} · {registro['tema']} · {registro['id']} ==",
        f"Resumo: {registro['resumo']}",
        f"Orientação: {registro['resposta']}",
        f"Fonte: {registro['fonte']} (consultada em {_data(registro['data_consulta'])})",
        f"Link: {registro['url_fonte']}",
    ]
    if registro.get("aviso"):
        linhas.append(f"Atenção: {registro['aviso']}")
    linhas.append(f"Aviso: {AVISO_GERAL}")
    if relacionados:
        linhas.append("Continue explorando:")
        linhas.extend(_lista_numerada(relacionados))
    return "\n".join(linhas)


def nota_aproximada(registro):
    return (
        f"Entendi que sua dúvida é sobre \"{registro['subtema']}\". "
        "Se não for isso, reformule a pergunta ou explore os temas."
    )


def formatar_resultado(resultado, codigo=MODELO_PADRAO, relacionados=()):
    """Texto completo para um ResultadoBusca, segundo o modelo escolhido."""
    if resultado.status == "encontrada":
        texto = formatar_orientacao(resultado.registros[0], codigo, relacionados)
        if resultado.aproximada and codigo == "B":
            return f"{nota_aproximada(resultado.registros[0])}\n{texto}"
        return texto

    if codigo == "A":
        if resultado.status == "ambigua":
            return "Mais de um assunto: " + ", ".join(item["subtema"] for item in resultado.registros) + "."
        if resultado.status == "vazia":
            return "Pergunta vazia."
        return "Não encontrei a resposta."

    if resultado.status == "ambigua":
        return "\n".join([resultado.mensagem, *_lista_numerada(resultado.registros)])
    if resultado.status == "vazia":
        return resultado.mensagem
    linhas = [resultado.mensagem]
    if resultado.sugestoes:
        linhas.append("Assuntos que você pode consultar:")
        linhas.extend(_lista_numerada(resultado.sugestoes))
    linhas.append(f"Aviso: {AVISO_GERAL}")
    return "\n".join(linhas)
