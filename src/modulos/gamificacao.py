import json
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock


ARQUIVO_PROGRESSO = Path(__file__).resolve().parents[2] / "data" / "progresso_gamificacao.json"
TURMAS = {
    "Educação Infantil": ("Maternal", "Pré I", "Pré II"),
    "Ensino Fundamental I": tuple(f"{ano}º ano" for ano in range(1, 6)),
    "Ensino Fundamental II": tuple(f"{ano}º ano" for ano in range(6, 10)),
}
AGUARDANDO = "Aguardando confirmação"
CONFIRMADA = "Confirmada"
DISPONIVEL = "Não concluída"
_trava = Lock()


@dataclass(frozen=True)
class Missao:
    titulo: str
    atividade: str
    pontos: int
    icone: str


MISSOES = {
    "plantio": Missao(
        "Plantar uma muda",
        "Planta ou transplanta uma muda em grupo e coloca uma plaquinha com o nome da planta.",
        10,
        "gardening_mission1.png",
    ),
    "rega": Missao(
        "Cuidar do canteiro",
        "Verifica se a terra precisa de água, rega se necessário ou ajuda em outro cuidado orientado pelo professor.",
        5,
        "watering_plants_mission2.png",
    ),
    "compostagem": Missao(
        "Missão Composteira",
        "Separa cascas e sobras de frutas ou verduras, coloca o material na composteira "
        "com orientação do professor e cobre com folhas secas.",
        5,
        "fertilizer_mission3.png",
    ),
    "safra": Missao(
        "Da semente ao prato",
        "Escolhe uma planta da horta e monta, com desenhos ou cartões, a sequência do plantio "
        "até uma comida que leva aquele ingrediente.",
        10,
        "food_mission4.png",
    ),
    "diario": Missao(
        "Aula dos sentidos",
        "Explora dois ou três alimentos naturais pela cor, pelo cheiro, pela textura e, para quem quiser e puder, "
        "pelo sabor. Para concluir, a turma compartilha uma descoberta sobre o alimento e como ele é cultivado "
        "ou usado nas refeições.",
        20,
        "seeds_mission5.png",
    ),
}


class ErroGamificacao(ValueError):
    """Erro ao consultar ou atualizar o progresso."""


def carregar_progresso():
    try:
        with ARQUIVO_PROGRESSO.open(encoding="utf-8") as arquivo:
            progresso = json.load(arquivo)
    except FileNotFoundError:
        return {
            "Pré II": {"plantio": CONFIRMADA},
            "1º ano": {"plantio": CONFIRMADA, "rega": AGUARDANDO},
            "3º ano": {"rega": CONFIRMADA, "compostagem": CONFIRMADA},
            "6º ano": {"safra": AGUARDANDO},
            "8º ano": {"diario": CONFIRMADA},
        }
    except (OSError, ValueError) as erro:
        raise ErroGamificacao("Não foi possível ler o progresso das turmas.") from erro

    turmas_validas = {turma for turmas in TURMAS.values() for turma in turmas}
    if not isinstance(progresso, dict) or any(
        turma not in turmas_validas
        or not isinstance(missoes, dict)
        or any(
            chave not in MISSOES or status not in (AGUARDANDO, CONFIRMADA)
            for chave, status in missoes.items()
        )
        for turma, missoes in progresso.items()
    ):
        raise ErroGamificacao("O arquivo de progresso contém dados inválidos.")
    return progresso


def _salvar(progresso):
    temporario = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=ARQUIVO_PROGRESSO.parent, delete=False
        ) as arquivo:
            temporario = Path(arquivo.name)
            json.dump(progresso, arquivo, ensure_ascii=False, indent=2)
        temporario.replace(ARQUIVO_PROGRESSO)
    except OSError as erro:
        if temporario is not None:
            with suppress(OSError):
                temporario.unlink(missing_ok=True)
        raise ErroGamificacao("Não foi possível salvar o progresso da turma.") from erro


def _transicao(turma, chave, anterior, novo):
    if chave not in MISSOES or not any(turma in turmas for turmas in TURMAS.values()):
        raise ErroGamificacao("Selecione uma turma e uma missão válidas.")
    with _trava:
        progresso = carregar_progresso()
        missoes = progresso.setdefault(turma, {})
        if missoes.get(chave, DISPONIVEL) != anterior:
            raise ErroGamificacao("A situação da missão mudou. Atualize a tela e confira o progresso.")
        missoes[chave] = novo
        _salvar(progresso)


def enviar_missao(turma, chave):
    _transicao(turma, chave, DISPONIVEL, AGUARDANDO)


def confirmar_missao(turma, chave):
    _transicao(turma, chave, AGUARDANDO, CONFIRMADA)


def calcular_pontos(missoes_da_turma):
    return sum(MISSOES[chave].pontos for chave, status in missoes_da_turma.items() if status == CONFIRMADA)
