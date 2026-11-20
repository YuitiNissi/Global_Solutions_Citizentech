import json

import pytest

from modulos import avaliacao, usabilidade
from modulos.assistente import ResultadoBusca, carregar_base


@pytest.fixture
def base():
    return carregar_base()


def test_conjuntos_de_teste_cumprem_o_minimo(base):
    principais = avaliacao.carregar_perguntas(base=base)
    validacao = avaliacao.carregar_perguntas(avaliacao.ARQUIVO_VALIDACAO, base=base)
    assert len(principais) >= 12
    tipos = {caso["tipo"] for caso in principais}
    assert {"direta", "reformulada", "fora_do_escopo", "vazia", "ambigua"} <= tipos
    assert not {caso["pergunta"] for caso in principais} & {caso["pergunta"] for caso in validacao}


def test_classificacao_de_acertos():
    registro = {"id": "cultivo-01"}
    caso = {"esperado_status": "encontrada", "esperado_ids": ["cultivo-01"]}
    assert avaliacao.classificar(caso, ResultadoBusca("encontrada", registros=(registro,))) == (True, "")
    assert not avaliacao.classificar(caso, ResultadoBusca("ambigua", registros=(registro, {"id": "x"})))[0]
    recusa = {"esperado_status": "fora_do_escopo", "esperado_ids": []}
    acerto, observacao = avaliacao.classificar(recusa, ResultadoBusca("encontrada", registros=(registro,)))
    assert not acerto and observacao.startswith("Resposta indevida")


def test_indicadores_e_relatorio(base, tmp_path):
    perguntas = avaliacao.carregar_perguntas(base=base)
    linhas = avaliacao.executar_testes(base, perguntas, repeticoes=2)
    resumo = avaliacao.resumir(linhas)
    assert resumo["total"] == len(perguntas)
    assert resumo["taxa_acerto"] == pytest.approx(100 * resumo["acertos"] / resumo["total"])
    assert resumo["respostas_indevidas"] == 0
    assert resumo["tempo_medio_ms"] > 0
    comparacao = avaliacao.comparar_modelos(base, perguntas)
    assert comparacao["B"]["taxa_geral"] > comparacao["A"]["taxa_geral"]
    conjunto = {"nome": "Teste", "descricao": "d", "linhas": linhas, "resumo": resumo}
    avaliacao.gerar_relatorio([conjunto], comparacao, pasta=tmp_path)
    assert "Taxa de acerto" in (tmp_path / "resultados_testes.md").read_text(encoding="utf-8")
    assert (tmp_path / "resultados_testes.csv").read_text(encoding="utf-8-sig").startswith("conjunto;id;")


def test_arquivo_de_perguntas_invalido(tmp_path):
    caminho = tmp_path / "perguntas.json"
    caminho.write_text(json.dumps([{"id": "X", "tipo": "direta"}]), encoding="utf-8")
    with pytest.raises(avaliacao.ErroTestes):
        avaliacao.carregar_perguntas(caminho)


def test_roteiro_de_usabilidade(tmp_path):
    resultados = usabilidade.executar_roteiro()
    assert len(resultados) >= 5
    assert all(item["concluida"] for item in resultados)
    usabilidade.gerar_relatorio(resultados, pasta=tmp_path)
    assert "Tarefas concluídas" in (tmp_path / "resultados_usabilidade.md").read_text(encoding="utf-8")
