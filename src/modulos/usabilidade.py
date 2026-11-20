"""Roteiro de tarefas de facilidade de uso, executado sobre a interface textual real.

Cada tarefa abre uma sessão nova, envia as entradas do roteiro e verifica o resultado na
transcrição. Mede se a tarefa foi concluída, quantas interações foram usadas em relação ao
caminho mínimo e quantas mensagens de erro apareceram.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Callable
from zoneinfo import ZoneInfo

from modulos.assistente import RAIZ
from modulos.interface_texto import executar


PASTA_DOCS = RAIZ / "docs"
MENSAGENS_DE_ERRO = ("Opção inexistente", "Entrada vazia", "Digite uma pergunta", "Não encontrei")


@dataclass(frozen=True)
class Tarefa:
    codigo: str
    objetivo: str
    entradas: tuple[str, ...]
    passos_minimos: int
    concluida: Callable[[str], bool]


TAREFAS = (
    Tarefa(
        "U1", "Fazer uma pergunta e localizar a fonte da resposta",
        ("1", "Como regar a horta sem desperdiçar água?", "", "0"), 3,
        lambda texto: "== Irrigação" in texto and "Link: https://" in texto,
    ),
    Tarefa(
        "U2", "Encontrar a orientação sobre rotação de culturas pelo menu de temas",
        ("2", "2", "6", "", "0"), 4,
        lambda texto: "== Rotação de culturas" in texto,
    ),
    Tarefa(
        "U3", "Navegar por três assuntos relacionados a partir de compostagem",
        ("1", "Como fazer compostagem?", "1", "1", "", "0"), 5,
        lambda texto: "Caminho: Compostagem > Cobertura do solo > Irrigação" in texto,
    ),
    Tarefa(
        "U4", "Resolver uma pergunta ambígua escolhendo o assunto desejado",
        ("1", "Compostagem ou irrigação?", "2", "", "0"), 4,
        lambda texto: "mais de um assunto" in texto and texto.count("== ") >= 1,
    ),
    Tarefa(
        "U5", "Recuperar-se de entrada vazia, opção inexistente e pergunta em branco",
        ("", "9", "1", "", "0"), 4,
        lambda texto: all(aviso in texto for aviso in ("Entrada vazia", "Opção inexistente", "Digite uma pergunta"))
        and "Até logo" in texto,
    ),
    Tarefa(
        "U6", "Receber o aviso de limite para pergunta sem base e seguir uma sugestão",
        ("1", "Como tirar a segunda via do RG?", "1", "", "0"), 4,
        lambda texto: "Não encontrei uma orientação confiável" in texto and "== " in texto,
    ),
    Tarefa(
        "U7", "Consultar uma orientação pelo identificador cultivo-03",
        ("3", "cultivo-03", "", "0"), 3,
        lambda texto: "== Cobertura do solo" in texto,
    ),
    Tarefa(
        "U8", "Trocar para o modelo A e comparar a resposta sobre compostagem",
        ("4", "1", "Como fazer compostagem?", "0"), 3,
        lambda texto: "Modelo A" in texto and "Fonte: Embrapa" in texto,
    ),
)


def executar_tarefa(tarefa):
    entradas = iter(tarefa.entradas)
    consumidas = []
    linhas = []

    def entrada(rotulo):
        valor = next(entradas, None)
        if valor is None:
            raise EOFError
        consumidas.append(valor)
        linhas.append(f"{rotulo}{valor}")
        return valor

    inicio = perf_counter()
    codigo = executar(entrada=entrada, saida=lambda texto="": linhas.append(str(texto)))
    tempo = (perf_counter() - inicio) * 1000
    transcricao = "\n".join(linhas)
    interacoes = len(consumidas) - (consumidas[-1:] == ["0"])
    return {
        "codigo": tarefa.codigo,
        "objetivo": tarefa.objetivo,
        "concluida": codigo == 0 and tarefa.concluida(transcricao),
        "interacoes": interacoes,
        "passos_minimos": tarefa.passos_minimos,
        "mensagens_erro": sum(transcricao.count(mensagem) for mensagem in MENSAGENS_DE_ERRO),
        "tempo_ms": tempo,
        "transcricao": transcricao,
    }


def executar_roteiro(tarefas=TAREFAS):
    return [executar_tarefa(tarefa) for tarefa in tarefas]


def gerar_relatorio(resultados, pasta=PASTA_DOCS):
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    concluidas = sum(item["concluida"] for item in resultados)
    excesso = sum(item["interacoes"] - item["passos_minimos"] for item in resultados)
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    md = [
        "# Resultados do roteiro de facilidade de uso",
        "",
        "> Arquivo gerado por `python src/avaliar.py`. Método e análise em [teste_usabilidade.md](teste_usabilidade.md).",
        "",
        f"- Execução: {agora:%d/%m/%Y %H:%M} (horário de Brasília)",
        f"- Tarefas concluídas: **{concluidas}/{len(resultados)} ({100 * concluidas / len(resultados):.0f}%)**",
        f"- Interações além do caminho mínimo: {excesso}",
        "",
        "| Tarefa | Objetivo | Concluída | Interações / mínimo | Mensagens de erro ou limite | Processamento (ms) |",
        "|---|---|---|---|---|---|",
    ]
    for item in resultados:
        md.append(
            f"| {item['codigo']} | {item['objetivo']} | {'✅' if item['concluida'] else '❌'} | "
            f"{item['interacoes']} / {item['passos_minimos']} | {item['mensagens_erro']} | {item['tempo_ms']:.1f} |"
        )
    md += ["", "## Transcrições", ""]
    for item in resultados:
        md += [
            f"<details><summary>{item['codigo']} · {item['objetivo']}</summary>",
            "",
            "```text",
            item["transcricao"],
            "```",
            "",
            "</details>",
            "",
        ]
    (pasta / "resultados_usabilidade.md").write_text("\n".join(md), encoding="utf-8")
