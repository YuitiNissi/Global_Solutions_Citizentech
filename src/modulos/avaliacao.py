"""Execução das perguntas de teste, indicadores de desempenho e comparação dos modelos de resposta."""

import csv
import json
import platform
import re
import statistics
from datetime import datetime
from pathlib import Path
from time import perf_counter
from zoneinfo import ZoneInfo

from modulos.assistente import RAIZ, buscar, indexar_por_id, relacionados
from modulos.modelos_resposta import MODELOS, formatar_resultado


ARQUIVO_PERGUNTAS = RAIZ / "data" / "perguntas_teste.json"
ARQUIVO_VALIDACAO = RAIZ / "data" / "perguntas_validacao.json"
PASTA_DOCS = RAIZ / "docs"
TIPOS = ("direta", "reformulada", "ambigua", "fora_do_escopo", "vazia", "erro_digitacao")
STATUS = ("encontrada", "ambigua", "fora_do_escopo", "vazia")
RECUSAS = ("fora_do_escopo", "vazia")
REPETICOES = 200
CRITERIOS = {
    "fonte_completa": "Cita fonte, data de consulta e link",
    "aviso": "Inclui aviso de limitação ou de confirmação",
    "opcoes_numeradas": "Oferece opções numeradas para continuar",
    "orienta_proximo_passo": "Explica o limite e diz o que fazer",
}


class ErroTestes(ValueError):
    """Erro no arquivo de perguntas de teste."""


def carregar_perguntas(caminho=ARQUIVO_PERGUNTAS, base=None):
    try:
        perguntas = json.loads(Path(caminho).read_text(encoding="utf-8"))
    except (OSError, ValueError) as erro:
        raise ErroTestes("Não foi possível ler o arquivo de perguntas de teste.") from erro
    if not isinstance(perguntas, list) or not perguntas:
        raise ErroTestes("O arquivo de perguntas precisa conter uma lista de casos.")
    ids_base = set(indexar_por_id(base)) if base else None
    for caso in perguntas:
        valido = (
            isinstance(caso, dict)
            and isinstance(caso.get("id"), str)
            and caso.get("tipo") in TIPOS
            and isinstance(caso.get("pergunta"), str)
            and caso.get("esperado_status") in STATUS
            and isinstance(caso.get("esperado_ids"), list)
            and (bool(caso["esperado_ids"]) == (caso["esperado_status"] not in RECUSAS))
        )
        if not valido:
            raise ErroTestes(f"Caso de teste inválido: {caso!r}")
        if ids_base is not None and not set(caso["esperado_ids"]) <= ids_base:
            raise ErroTestes(f"Caso {caso['id']} espera um identificador que não existe na base.")
    return perguntas


def classificar(caso, resultado):
    """Retorna (acerto, observação) comparando o resultado com o esperado."""
    esperado = caso["esperado_status"]
    obtidos = [registro["id"] for registro in resultado.registros]
    sugeridos = [registro["id"] for registro in resultado.sugestoes]
    if resultado.status != esperado:
        if esperado == "encontrada" and resultado.status == "ambigua" and caso["esperado_ids"][0] in obtidos:
            return False, "Parcial: o assunto certo aparece entre as opções de desambiguação"
        if esperado != "fora_do_escopo" and resultado.status == "fora_do_escopo" and set(caso["esperado_ids"]) & set(sugeridos):
            return False, "Não respondeu, mas sugeriu o assunto esperado"
        if esperado in RECUSAS and resultado.status == "encontrada":
            return False, "Resposta indevida para pergunta sem base"
        return False, "Comportamento diferente do esperado"
    if esperado == "encontrada" and obtidos[0] != caso["esperado_ids"][0]:
        return False, "Respondeu com outro assunto"
    if esperado == "ambigua" and not set(caso["esperado_ids"]) <= set(obtidos):
        return False, "Desambiguação sem todos os assuntos esperados"
    return True, ""


def descrever(resultado):
    if resultado.status == "encontrada":
        registro = resultado.registros[0]
        return f"{registro['id']} · {registro['subtema']}"
    if resultado.status == "ambigua":
        return "Ambígua: " + ", ".join(registro["id"] for registro in resultado.registros)
    if resultado.status == "vazia":
        return "Aviso de entrada vazia"
    sugeridos = ", ".join(registro["id"] for registro in resultado.sugestoes)
    return "Sem orientação confiável" + (f" · sugeriu {sugeridos}" if sugeridos else "")


def descrever_esperado(caso):
    if caso["esperado_status"] == "encontrada":
        return caso["esperado_ids"][0]
    if caso["esperado_status"] == "ambigua":
        return "Ambígua: " + ", ".join(caso["esperado_ids"])
    return "Aviso de entrada vazia" if caso["esperado_status"] == "vazia" else "Sem orientação confiável"


def medir_tempo_ms(pergunta, base, repeticoes=REPETICOES, etapa_aproximada=True):
    inicio = perf_counter()
    for _ in range(repeticoes):
        buscar(pergunta, base, etapa_aproximada)
    return (perf_counter() - inicio) * 1000 / repeticoes


def executar_testes(base, perguntas, repeticoes=REPETICOES, etapa_aproximada=True):
    linhas = []
    for caso in perguntas:
        resultado = buscar(caso["pergunta"], base, etapa_aproximada)
        acerto, observacao = classificar(caso, resultado)
        linhas.append({
            "id": caso["id"],
            "tipo": caso["tipo"],
            "pergunta": caso["pergunta"],
            "esperado": descrever_esperado(caso),
            "obtido": descrever(resultado),
            "acerto": acerto,
            "observacao": observacao,
            "tempo_ms": medir_tempo_ms(caso["pergunta"], base, repeticoes, etapa_aproximada),
        })
    return linhas


def resumir(linhas):
    tempos = [linha["tempo_ms"] for linha in linhas]
    por_tipo = {}
    for linha in linhas:
        acertos, total = por_tipo.get(linha["tipo"], (0, 0))
        por_tipo[linha["tipo"]] = (acertos + linha["acerto"], total + 1)
    acertos = sum(linha["acerto"] for linha in linhas)
    indevidas = sum(linha["observacao"] == "Resposta indevida para pergunta sem base" for linha in linhas)
    return {
        "total": len(linhas),
        "acertos": acertos,
        "erros": len(linhas) - acertos,
        "taxa_acerto": 100 * acertos / len(linhas),
        "tempo_medio_ms": statistics.mean(tempos),
        "tempo_mediano_ms": statistics.median(tempos),
        "tempo_maximo_ms": max(tempos),
        "respostas_indevidas": indevidas,
        "por_tipo": por_tipo,
    }


def avaliar_saida(texto, resultado, opcoes, registro=None):
    """Critérios objetivos verificados no texto produzido por um modelo. None = não se aplica."""
    status = resultado.status
    return {
        "fonte_completa": (
            registro["fonte"] in texto
            and registro["url_fonte"] in texto
            and bool(re.search(r"\d{2}/\d{2}/\d{4}", texto))
        ) if status == "encontrada" else None,
        "aviso": ("Aviso:" in texto) if status in ("encontrada", "fora_do_escopo") else None,
        "opcoes_numeradas": bool(re.search(r"^\s+1\. ", texto, re.MULTILINE)) if opcoes else None,
        "orienta_proximo_passo": (
            any(palavra in texto.casefold() for palavra in ("digite", "reformule", "escolha"))
        ) if status in ("ambigua", "fora_do_escopo", "vazia") else None,
    }


def comparar_modelos(base, perguntas):
    indice = indexar_por_id(base)
    comparacao = {}
    for codigo in MODELOS:
        contagem = {criterio: [0, 0] for criterio in CRITERIOS}
        palavras = []
        for caso in perguntas:
            resultado = buscar(caso["pergunta"], base)
            registro = resultado.registros[0] if resultado.status == "encontrada" else None
            vizinhos = relacionados(registro, indice) if registro and codigo == "B" else []
            opcoes = vizinhos or resultado.sugestoes or (resultado.registros if resultado.status == "ambigua" else ())
            texto = formatar_resultado(resultado, codigo, vizinhos)
            if registro:
                palavras.append(len(texto.split()))
            for criterio, atendido in avaliar_saida(texto, resultado, opcoes, registro).items():
                if atendido is not None:
                    contagem[criterio][0] += atendido
                    contagem[criterio][1] += 1
        atendidos = sum(valor[0] for valor in contagem.values())
        aplicaveis = sum(valor[1] for valor in contagem.values())
        comparacao[codigo] = {
            "criterios": {criterio: tuple(valor) for criterio, valor in contagem.items()},
            "taxa_geral": 100 * atendidos / aplicaveis,
            "palavras_media": statistics.mean(palavras) if palavras else 0,
        }
    return comparacao


def _celula(texto):
    return str(texto).replace("|", "\\|") or "(vazia)"


def _tabela_indicadores(resumo):
    md = [
        "| Indicador | Valor |",
        "|---|---|",
        f"| Perguntas testadas | {resumo['total']} |",
        f"| Acertos | {resumo['acertos']} |",
        f"| Erros | {resumo['erros']} |",
        f"| **Taxa de acerto** | **{resumo['taxa_acerto']:.1f}%** |",
        f"| **Tempo médio de consulta** | **{resumo['tempo_medio_ms']:.3f} ms** |",
        f"| Tempo mediano | {resumo['tempo_mediano_ms']:.3f} ms |",
        f"| Tempo máximo | {resumo['tempo_maximo_ms']:.3f} ms |",
        f"| Respostas indevidas (respondeu sem ter base) | {resumo['respostas_indevidas']} |",
        "",
        "| Tipo | Acertos | Total | Taxa |",
        "|---|---|---|---|",
    ]
    for tipo, (acertos, total) in resumo["por_tipo"].items():
        md.append(f"| {tipo} | {acertos} | {total} | {100 * acertos / total:.1f}% |")
    return md


def _tabela_registro(linhas):
    md = [
        "| ID | Tipo | Pergunta | Esperado | Obtido | Resultado | Tempo (ms) | Observação |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for linha in linhas:
        md.append(
            f"| {linha['id']} | {linha['tipo']} | {_celula(linha['pergunta'])} | {linha['esperado']} | "
            f"{linha['obtido']} | {'✅ acerto' if linha['acerto'] else '❌ erro'} | "
            f"{linha['tempo_ms']:.3f} | {_celula(linha['observacao']) if linha['observacao'] else ''} |"
        )
    return md


def gerar_relatorio(conjuntos, comparacao, pasta=PASTA_DOCS, nome="resultados_testes", titulo=None):
    """conjuntos: lista de dicionários com nome, descricao, linhas e resumo."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    with (pasta / f"{nome}.csv").open("w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(["conjunto", "id", "tipo", "pergunta", "esperado", "obtido", "acerto", "observacao", "tempo_ms"])
        for conjunto in conjuntos:
            for linha in conjunto["linhas"]:
                escritor.writerow([
                    conjunto["nome"], linha["id"], linha["tipo"], linha["pergunta"], linha["esperado"],
                    linha["obtido"], "acerto" if linha["acerto"] else "erro", linha["observacao"],
                    f"{linha['tempo_ms']:.3f}",
                ])

    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    md = [
        f"# {titulo or 'Resultados das perguntas de teste'}",
        "",
        "> Arquivo gerado por `python src/avaliar.py`. Não edite à mão: execute o script novamente.",
        "",
        f"- Execução: {agora:%d/%m/%Y %H:%M} (horário de Brasília)",
        f"- Ambiente: Python {platform.python_version()} · {platform.system()} {platform.release()}",
        f"- Tempo de consulta: média de {REPETICOES} execuções da função `buscar` para cada pergunta",
        "",
        "## Resumo",
        "",
        "| Conjunto | Perguntas | Acertos | Taxa de acerto | Tempo médio (ms) | Respostas indevidas |",
        "|---|---|---|---|---|---|",
    ]
    for conjunto in conjuntos:
        resumo = conjunto["resumo"]
        md.append(
            f"| {conjunto['nome']} | {resumo['total']} | {resumo['acertos']} | {resumo['taxa_acerto']:.1f}% | "
            f"{resumo['tempo_medio_ms']:.3f} | {resumo['respostas_indevidas']} |"
        )
    for conjunto in conjuntos:
        md += ["", f"## {conjunto['nome']}", "", conjunto["descricao"], "", "### Indicadores", ""]
        md += _tabela_indicadores(conjunto["resumo"])
        md += ["", "### Registro dos testes", ""]
        md += _tabela_registro(conjunto["linhas"])
    if comparacao:
        md += [
            "",
            "## Comparação dos modelos de resposta",
            "",
            "Os dois modelos recebem os mesmos resultados de busca das perguntas do conjunto principal. "
            "Cada critério é verificado no texto produzido; a coluna mostra atendidos/aplicáveis.",
            "",
            "| Critério | " + " | ".join(MODELOS[codigo].nome for codigo in comparacao) + " |",
            "|---|" + "---|" * len(comparacao),
        ]
        for criterio, descricao in CRITERIOS.items():
            valores = []
            for dados in comparacao.values():
                atendidos, aplicaveis = dados["criterios"][criterio]
                valores.append(f"{atendidos}/{aplicaveis}")
            md.append(f"| {descricao} | " + " | ".join(valores) + " |")
        md.append("| **Critérios atendidos** | " + " | ".join(
            f"**{dados['taxa_geral']:.1f}%**" for dados in comparacao.values()) + " |")
        md.append("| Palavras por resposta encontrada (média) | " + " | ".join(
            f"{dados['palavras_media']:.0f}" for dados in comparacao.values()) + " |")
    md.append("")
    (pasta / f"{nome}.md").write_text("\n".join(md), encoding="utf-8")
