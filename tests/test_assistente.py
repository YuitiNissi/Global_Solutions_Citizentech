import json

import pytest

from modulos.assistente import ErroBase, buscar, carregar_base, organizar_por_tema


@pytest.fixture
def base():
    return carregar_base()


def test_carrega_e_organiza_as_18_orientacoes(base):
    temas = organizar_por_tema(base)
    assert len(base) == 18
    assert set(temas) == {
        "Alimentação consciente",
        "Cultivo sustentável",
        "Educação comunitária e hortas escolares",
    }
    assert all(len(subtemas) == 6 for subtemas in temas.values())
    assert all(registro["url_fonte"].startswith("https://") for registro in base)


def test_busca_palavra_chave_sem_acentos(base):
    resultado = buscar("IRRIGACAO!", base)
    assert resultado.status == "encontrada"
    assert resultado.registros[0]["id"] == "cultivo-02"


def test_todas_as_perguntas_de_exemplo_retornam_a_orientacao(base):
    for registro in base:
        for pergunta in registro["perguntas_exemplo"]:
            resultado = buscar(pergunta, base)
            assert resultado.status == "encontrada", pergunta
            assert resultado.registros[0]["id"] == registro["id"], pergunta


@pytest.mark.parametrize(
    ("pergunta", "identificador"),
    [
        ("De que jeito eu posso regar a horta?", "cultivo-02"),
        ("Onde eu posso comprar verduras e frutas da época?", "alimentacao-05"),
        ("Como posso manter a horta no recesso?", "escola-04"),
    ],
)
def test_perguntas_reformuladas(base, pergunta, identificador):
    resultado = buscar(pergunta, base)
    assert resultado.status == "encontrada"
    assert resultado.registros[0]["id"] == identificador


@pytest.mark.parametrize("pergunta", ["", "  \t ", "?!"])
def test_perguntas_vazias(base, pergunta):
    assert buscar(pergunta, base).status == "vazia"


@pytest.mark.parametrize("pergunta", ["Qual é a capital da França?", "Como investir na bolsa?", "cirrigacao"])
def test_perguntas_fora_do_escopo(base, pergunta):
    resultado = buscar(pergunta, base)
    assert resultado.status == "fora_do_escopo"
    assert not resultado.registros


def test_pergunta_ambigua(base):
    resultado = buscar("Compostagem ou irrigação?", base)
    assert resultado.status == "ambigua"
    assert {registro["id"] for registro in resultado.registros} == {"cultivo-01", "cultivo-02"}


def test_arquivo_inexistente(tmp_path):
    with pytest.raises(ErroBase, match="não foi encontrado"):
        carregar_base(tmp_path / "ausente.json")


@pytest.mark.parametrize(
    ("conteudo", "erro"),
    [(b"{", "JSON válido"), (b"\xff", "JSON válido"), (b"{}", "lista"), (b"[{}]", "campos de texto")],
)
def test_arquivo_invalido(tmp_path, conteudo, erro):
    caminho = tmp_path / "base.json"
    caminho.write_bytes(conteudo)
    with pytest.raises(ErroBase, match=erro):
        carregar_base(caminho)


def test_rejeita_identificadores_duplicados(tmp_path, base):
    caminho = tmp_path / "base.json"
    caminho.write_text(json.dumps([base[0], base[0]]), encoding="utf-8")
    with pytest.raises(ErroBase, match="duplicado"):
        carregar_base(caminho)


def test_aceita_pendencia_mas_exclui_da_busca(tmp_path, base):
    registro = base[0] | {
        "fonte": "Pendente de validação",
        "url_fonte": None,
        "data_consulta": None,
    }
    caminho = tmp_path / "base.json"
    caminho.write_text(json.dumps([registro]), encoding="utf-8")
    assert buscar("in natura", carregar_base(caminho)).status == "fora_do_escopo"
