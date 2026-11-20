"""Núcleo do assistente: leitura da base, organização dos temas e busca de orientações."""

import json
import math
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from difflib import SequenceMatcher, get_close_matches
from pathlib import Path
from urllib.parse import urlsplit


RAIZ = Path(__file__).resolve().parents[2]
ARQUIVO_BASE = RAIZ / "data" / "conhecimento.json"
CAMPOS_TEXTO = ("id", "tema", "subtema", "resumo", "resposta", "fonte")
CAMPOS_LISTA = ("palavras_chave", "perguntas_exemplo")
PENDENTE = "Pendente de validação"
LIMIAR_RESPOSTA = 0.52
MARGEM_EMPATE = 0.12
LIMITE_SUGESTOES = 3
AVISO_GERAL = (
    "Conteúdo educativo de um protótipo acadêmico, sem vínculo com órgãos públicos. "
    "Confirme informações atualizadas na fonte indicada."
)
PALAVRAS_COMUNS = set(
    "a ao as com como da das de do dos e em eu na nas no nos o os onde "
    "ou para pela pelo por posso pode qual quais que se um uma voce mais "
    "queria quero saber fazer serve sobre".split()
)
# Etapa 2 (correspondência aproximada): palavras vazias mais amplas, radicais e pesos IDF.
PALAVRAS_VAZIAS = PALAVRAS_COMUNS | set(
    "apos aquele aquela aquilo ate bom boa cada certo coisa da dar deve devo dicas ela elas ele eles "
    "essa esse esses essas esta este estes estas estao faz foi ha ir isso isto ja jeito la mas me meu "
    "minha meus minhas muita muitas muito muitos nao nem num numa nos pena quando quanto quem sem ser "
    "seu sua seus suas so tambem te tem ter tipo tudo vai vale vao voces".split()
)
SUFIXOS_VERBAIS = ("arem", "erem", "irem", "ando", "endo", "indo", "ar", "er", "ir")
LIMIAR_APROXIMADO = 0.45
MIN_TERMOS_APROXIMADO = 2
PESO_TEXTO = 0.6
MARGEM_APROXIMADA = 0.1


class ErroBase(ValueError):
    """Erro de leitura ou validação da base educativa."""


@dataclass(frozen=True)
class ResultadoBusca:
    status: str
    mensagem: str = ""
    registros: tuple[dict, ...] = ()
    sugestoes: tuple[dict, ...] = ()
    aproximada: bool = False


def _texto_valido(valor):
    return isinstance(valor, str) and bool(valor.strip())


def _referencia_valida(registro):
    url, consulta = registro["url_fonte"], registro["data_consulta"]
    if registro["fonte"] == PENDENTE:
        return url is None and consulta is None
    if not (_texto_valido(url) and _texto_valido(consulta)):
        return False
    try:
        endereco = urlsplit(url)
        return (
            endereco.scheme in {"http", "https"}
            and bool(endereco.hostname)
            and date.fromisoformat(consulta).isoformat() == consulta
        )
    except ValueError:
        return False


def carregar_base(caminho=ARQUIVO_BASE):
    """Lê o JSON da base e valida os campos obrigatórios de cada orientação."""
    try:
        with Path(caminho).open(encoding="utf-8-sig") as arquivo:
            base = json.load(arquivo)
    except FileNotFoundError as erro:
        raise ErroBase("O arquivo da base de conhecimento não foi encontrado.") from erro
    except (UnicodeError, json.JSONDecodeError) as erro:
        raise ErroBase("O arquivo da base de conhecimento precisa conter JSON válido.") from erro
    except OSError as erro:
        raise ErroBase("Não foi possível ler a base de conhecimento.") from erro

    if not isinstance(base, list) or not base:
        raise ErroBase("A base precisa conter uma lista de orientações.")

    ids = set()
    for indice, registro in enumerate(base, start=1):
        if not isinstance(registro, dict) or not all(
            _texto_valido(registro.get(campo)) for campo in CAMPOS_TEXTO
        ):
            raise ErroBase(f"Orientação {indice} com campos de texto ausentes ou inválidos.")
        for campo in CAMPOS_LISTA:
            valores = registro.get(campo)
            if not isinstance(valores, list) or not valores or not all(
                _texto_valido(valor) and _normalizar(valor) for valor in valores
            ):
                raise ErroBase(f"Orientação {indice} com valores inválidos em {campo}.")
        if not {"url_fonte", "data_consulta"} <= registro.keys() or not _referencia_valida(registro):
            raise ErroBase(f"Orientação {indice} com referência ou data de consulta inválida.")
        if "aviso" in registro and not _texto_valido(registro["aviso"]):
            raise ErroBase(f"Orientação {indice} com aviso vazio.")
        relacionados = registro.get("relacionados", [])
        if not isinstance(relacionados, list) or not all(_texto_valido(item) for item in relacionados):
            raise ErroBase(f"Orientação {indice} com lista de relacionados inválida.")
        if registro["id"] in ids:
            raise ErroBase(f"Orientação {indice} com identificador duplicado.")
        ids.add(registro["id"])

    for indice, registro in enumerate(base, start=1):
        for relacionado in registro.get("relacionados", []):
            if relacionado == registro["id"] or relacionado not in ids:
                raise ErroBase(
                    f"Orientação {indice} relaciona um identificador inexistente: {relacionado}."
                )
    return base


def organizar_por_tema(base):
    """Hierarquia tema -> subtema -> lista de orientações (dicionário de dicionários)."""
    temas = {}
    for registro in base:
        subtemas = temas.setdefault(registro["tema"], {})
        subtemas.setdefault(registro["subtema"], []).append(registro)
    return temas


def indexar_por_id(base):
    """Dicionário identificador -> orientação, para consultas diretas em tempo constante."""
    return {registro["id"]: registro for registro in base}


def validado(registro):
    return registro["fonte"] != PENDENTE


def relacionados(registro, indice):
    """Vizinhos do registro no grafo de assuntos relacionados (lista de adjacência)."""
    return [
        indice[identificador]
        for identificador in registro.get("relacionados", [])
        if identificador in indice and validado(indice[identificador])
    ]


def buscar_por_id(identificador, base):
    texto = identificador.strip().casefold() if isinstance(identificador, str) else ""
    if not texto:
        return ResultadoBusca("vazia", "Digite um identificador, por exemplo: cultivo-02.")
    registro = indexar_por_id(base).get(texto)
    if registro is None or not validado(registro):
        return ResultadoBusca(
            "inexistente",
            "Identificador não encontrado. Use o formato tema-número, como cultivo-02.",
            sugestoes=_sugestoes_padrao(base),
        )
    return ResultadoBusca("encontrada", registros=(registro,))


def _normalizar(texto):
    decomposicao = unicodedata.normalize("NFKD", texto.casefold())
    sem_acentos = "".join(letra for letra in decomposicao if not unicodedata.combining(letra))
    return " ".join(re.findall(r"[^\W_]+", sem_acentos))


def _termos(texto):
    return set(texto.split()) - PALAVRAS_COMUNS


def _pontuar(pergunta, termos, registro):
    termos_chave = set()
    for chave in registro["palavras_chave"]:
        chave = _normalizar(chave)
        if f" {chave} " in f" {pergunta} ":
            termos_chave.update(_termos(chave))

    melhor = 0.0
    for exemplo in registro["perguntas_exemplo"]:
        exemplo = _normalizar(exemplo)
        termos_exemplo = _termos(exemplo)
        comuns = termos & termos_exemplo
        cobertura = len(termos_chave | comuns) / len(termos)
        similaridade = SequenceMatcher(None, pergunta, exemplo).ratio()

        if pergunta == exemplo:
            return 1.0
        if termos_chave and cobertura >= 0.5:
            melhor = max(melhor, 0.3 + 0.5 * cobertura + 0.15 * similaridade)
        elif len(comuns) >= 2 and cobertura >= 0.6 and similaridade >= LIMIAR_RESPOSTA:
            melhor = max(melhor, 0.65 * cobertura + 0.25 * similaridade)
    return melhor


def _vocabulario(registro):
    textos = [registro["tema"], registro["subtema"], *registro["palavras_chave"], *registro["perguntas_exemplo"]]
    return set().union(*(_termos(_normalizar(texto)) for texto in textos))


def _sugestoes_padrao(base):
    """Um assunto de cada tema, para quando a pergunta não tem nenhuma relação com a base."""
    escolhidos = {}
    for registro in base:
        if validado(registro):
            escolhidos.setdefault(registro["tema"], registro)
    return tuple(escolhidos.values())


def sugerir(pergunta, base, limite=LIMITE_SUGESTOES):
    """Assuntos próximos para continuar a consulta quando não há resposta confiável.

    Cada termo da pergunta que aparece no vocabulário de um registro vale 1 ponto;
    termos parecidos (erros de digitação) valem 0,5. Sem pontos, sugere um assunto por tema.
    """
    termos = _termos(_normalizar(pergunta))
    pontuados = []
    for registro in filter(validado, base):
        vocabulario = _vocabulario(registro)
        pontos = 0.0
        for termo in termos:
            if termo in vocabulario:
                pontos += 1
            elif len(termo) >= 5 and get_close_matches(termo, vocabulario, n=1, cutoff=0.8):
                pontos += 0.5
        if pontos:
            pontuados.append((pontos, registro))
    if not pontuados:
        return _sugestoes_padrao(base)
    pontuados.sort(key=lambda item: item[0], reverse=True)
    return tuple(registro for _, registro in pontuados[:limite])


def _radical(termo):
    """Radical simplificado: retira plural, terminações verbais comuns e vogal final."""
    if len(termo) > 4 and termo.endswith("s"):
        termo = termo[:-1]
    for sufixo in SUFIXOS_VERBAIS:
        if termo.endswith(sufixo) and len(termo) - len(sufixo) >= 3:
            return termo[: -len(sufixo)]
    if len(termo) > 3 and termo[-1] in "aeo":
        return termo[:-1]
    return termo


def _radicais(texto):
    return {_radical(termo) for termo in _normalizar(texto).split() if termo not in PALAVRAS_VAZIAS and len(termo) > 1}


def _busca_aproximada(pergunta, base):
    """Etapa 2: cobertura da pergunta pelo vocabulário de cada orientação, ponderada por IDF.

    Termos que aparecem em poucas orientações pesam mais; termos desconhecidos da base pesam o
    máximo e derrubam a cobertura, o que protege contra perguntas fora do escopo.
    """
    termos = _radicais(pergunta)
    if len(termos) < MIN_TERMOS_APROXIMADO:
        return []
    documentos = []
    for registro in filter(validado, base):
        indexados = set().union(*(
            _radicais(texto)
            for texto in (registro["tema"], registro["subtema"], *registro["palavras_chave"], *registro["perguntas_exemplo"])
        ))
        documentos.append((registro, indexados, _radicais(f"{registro['resumo']} {registro['resposta']}") - indexados))
    frequencia = {}
    for _, indexados, texto in documentos:
        for termo in indexados | texto:
            frequencia[termo] = frequencia.get(termo, 0) + 1
    total_documentos = len(documentos)

    def idf(termo):
        return math.log((total_documentos + 1) / (frequencia.get(termo, 0) + 1)) + 1

    peso_total = sum(idf(termo) for termo in termos)
    pontuados = []
    for registro, indexados, texto in documentos:
        casados = termos & indexados
        pontos = sum(idf(termo) for termo in casados) + PESO_TEXTO * sum(idf(termo) for termo in termos & texto)
        cobertura = pontos / peso_total
        if len(casados) >= MIN_TERMOS_APROXIMADO and cobertura >= LIMIAR_APROXIMADO:
            pontuados.append((cobertura, registro))
    pontuados.sort(key=lambda item: item[0], reverse=True)
    return pontuados


def buscar(pergunta, base, etapa_aproximada=True):
    """Busca por pergunta livre em duas etapas.

    Etapa 1: palavras-chave completas e semelhança com perguntas de exemplo (alta precisão).
    Etapa 2: só quando a etapa 1 não encontra nada, cobertura ponderada por IDF (correspondência
    aproximada, sinalizada ao usuário).
    Retorna "vazia", "fora_do_escopo", "ambigua" (empate entre assuntos) ou "encontrada".
    etapa_aproximada=False reproduz a busca original (linha de base da rodada 1 de testes).
    """
    pergunta = _normalizar(pergunta) if isinstance(pergunta, str) else ""
    if not pergunta:
        return ResultadoBusca("vazia", "Digite uma pergunta para consultar o assistente.")

    termos = _termos(pergunta)
    melhores = []
    if termos:
        for registro in filter(validado, base):
            pontos = _pontuar(pergunta, termos, registro)
            if pontos >= LIMIAR_RESPOSTA:
                melhores.append((pontos, registro))

    if not melhores:
        aproximados = _busca_aproximada(pergunta, base) if etapa_aproximada else []
        if aproximados:
            topo = aproximados[0][0]
            proximos = tuple(registro for pontos, registro in aproximados if topo - pontos <= MARGEM_APROXIMADA)
            if len(proximos) > 1:
                return ResultadoBusca(
                    "ambigua", "Encontrei mais de um assunto possível. Escolha um deles.", proximos, aproximada=True
                )
            return ResultadoBusca("encontrada", registros=proximos, aproximada=True)
        return ResultadoBusca(
            "fora_do_escopo",
            "Não encontrei uma orientação confiável na base para essa pergunta. "
            "Reformule a pergunta ou escolha um dos assuntos sugeridos.",
            sugestoes=sugerir(pergunta, base),
        )

    melhores.sort(key=lambda item: item[0], reverse=True)
    maior_pontuacao = melhores[0][0]
    proximos = tuple(registro for pontos, registro in melhores if maior_pontuacao - pontos <= MARGEM_EMPATE)
    if len(proximos) > 1:
        return ResultadoBusca(
            "ambigua", "Encontrei mais de um assunto possível. Escolha um deles.", proximos
        )
    return ResultadoBusca("encontrada", registros=proximos)
