import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlsplit


ARQUIVO_BASE = Path(__file__).resolve().parents[1] / "dados" / "conhecimento.json"
CAMPOS_TEXTO = ("id", "tema", "subtema", "resumo", "resposta", "fonte")
CAMPOS_LISTA = ("palavras_chave", "perguntas_exemplo")
PALAVRAS_COMUNS = set(
    "a ao as com como da das de do dos e em eu na nas no nos o os onde "
    "ou para pela pelo por posso pode qual quais que se um uma voce mais "
    "queria quero saber fazer serve sobre".split()
)


class ErroBase(ValueError):
    """Erro de leitura ou validação da base educativa."""


@dataclass(frozen=True)
class ResultadoBusca:
    status: str
    mensagem: str = ""
    registros: tuple[dict, ...] = ()


def _texto_valido(valor):
    return isinstance(valor, str) and bool(valor.strip())


def _referencia_valida(registro):
    url, consulta = registro["url_fonte"], registro["data_consulta"]
    if registro["fonte"] == "Pendente de validação":
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
        if registro["id"] in ids:
            raise ErroBase(f"Orientação {indice} com identificador duplicado.")
        ids.add(registro["id"])
    return base


def organizar_por_tema(base):
    temas = {}
    for registro in base:
        subtemas = temas.setdefault(registro["tema"], {})
        subtemas.setdefault(registro["subtema"], []).append(registro)
    return temas


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
        elif len(comuns) >= 2 and cobertura >= 0.6 and similaridade >= 0.52:
            melhor = max(melhor, 0.65 * cobertura + 0.25 * similaridade)
    return melhor


def buscar(pergunta, base):
    pergunta = _normalizar(pergunta)
    if not pergunta:
        return ResultadoBusca("vazia", "Digite uma pergunta para consultar o assistente.")

    termos = _termos(pergunta)
    melhores = []
    if termos:
        for registro in base:
            if registro["fonte"] != "Pendente de validação":
                pontos = _pontuar(pergunta, termos, registro)
                if pontos >= 0.52:
                    melhores.append((pontos, registro))

    if not melhores:
        return ResultadoBusca(
            "fora_do_escopo",
            "Não encontrei uma orientação confiável na base. Reformule a pergunta "
            "ou explore os temas do assistente.",
        )

    melhores.sort(key=lambda item: item[0], reverse=True)
    maior_pontuacao = melhores[0][0]
    proximos = tuple(registro for pontos, registro in melhores if maior_pontuacao - pontos <= 0.12)
    if len(proximos) > 1:
        return ResultadoBusca(
            "ambigua", "Encontrei mais de um assunto possível. Escolha um deles.", proximos
        )
    return ResultadoBusca("encontrada", registros=proximos)
