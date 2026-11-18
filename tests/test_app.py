from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from streamlit.testing.v1 import AppTest

import pytest

from modulos import gamificacao
from modulos.gamificacao_ui import _prazo_semestre


APP = Path(__file__).resolve().parents[1] / "app.py"


def test_fluxo_do_assistente():
    app = AppTest.from_file(APP).run()
    assert not app.exception
    app.text_input[0].input("Compostagem ou irrigação?")
    app.button[0].click().run()
    assert "mais de um assunto" in app.info[0].value
    app.selectbox[0].select("cultivo-02").run()
    assert app.subheader[0].value == "Irrigação"
    assert "Embrapa" in app.get("link_button")[0].proto.label

    app.selectbox[1].select("Cultivo sustentável").run()
    app.selectbox[2].select("Rotação de culturas").run()
    assert any(item.value == "Rotação de culturas" for item in app.subheader)

    assert not app.exception


def test_calendario_da_horta_atualiza_fichas_e_totais():
    app = AppTest.from_file(APP).run()
    app.sidebar.button(key="navegacao-Programa escolar").click().run()
    app.number_input(key="programa_ano").set_value(2026)
    app.selectbox(key="programa_mes").select("Novembro").run()

    textos = [item.value for item in app.markdown]
    assert "dados fictícios" in app.info[0].value
    assert [item.value for item in app.subheader][:6] == [
        "Cenoura", "Tomate", "Alface", "Hortelã", "Rabanete", "Rúcula",
    ]
    assert len(app.get("image")) == 6
    assert "Etapa atual: Colheita" in textos
    assert "Confirmado · Equipe de alimentação confirmou cenoura no arroz com legumes." in textos
    assert "Confirmado · Produtor confirmou cenoura na composição da cesta." in textos
    assert "Reserva até: 23/11/2026" in textos
    assert "Retirada: 27/11/2026" in textos
    assert [item.value for item in app.metric] == ["3", "175", "12"]

    app.selectbox(key="programa_mes").select("Outubro").run()
    textos = [item.value for item in app.markdown]
    assert "Etapa atual: Cuidado" in textos
    assert "Previsto · Cenoura ralada na salada." in textos
    assert "Retirada: A confirmar" in textos
    assert [item.value for item in app.metric] == ["2", "120", "8"]

    app.number_input(key="programa_ano").set_value(2027).run()
    assert any("Nenhum registro cadastrado" in item.value for item in app.info)
    assert "Cenoura" not in [item.value for item in app.subheader]
    assert [item.value for item in app.metric] == ["0", "0", "0"]
    assert not app.exception


def test_missao_enviada_confirmada_e_contabilizada_no_ranking(monkeypatch, tmp_path):
    arquivo = tmp_path / "progresso.json"
    monkeypatch.setattr(gamificacao, "ARQUIVO_PROGRESSO", arquivo)
    app = AppTest.from_file(APP).run()
    app.sidebar.button(key="navegacao-Gamificação").click().run()
    assert app.metric[0].label == "Tempo restante para completar as missões"
    assert [len(tabela.value) for tabela in app.dataframe] == [3, 5, 4]

    app.radio[0].set_value("Área da turma").run()
    app.selectbox[0].select("Ensino Fundamental I").run()
    assert app.selectbox[1].value == "1º ano"
    assert [item.value for item in app.markdown if item.value.startswith("**")] == [
        "**Plantar uma muda**",
        "**Cuidar do canteiro**",
        "**Missão Composteira**",
        "**Da semente ao prato**",
        "**Aula dos sentidos**",
    ]
    assert [item.value.split(" · ")[0] for item in app.caption if item.value.startswith("+")] == [
        "+10 pontos", "+5 pontos", "+5 pontos", "+10 pontos", "+20 pontos",
    ]
    assert len(app.get("image")) == 5
    app.selectbox[2].select("compostagem").run()
    app.button[0].click().run()
    assert app.metric[0].value == "10"
    assert gamificacao.carregar_progresso()["1º ano"]["compostagem"] == gamificacao.AGUARDANDO

    app.radio[0].set_value("Área do professor").run()
    app.selectbox[0].select("Ensino Fundamental I").run()
    app.selectbox[2].select("compostagem").run()
    app.button[0].click().run()
    assert app.metric[0].value == "15"
    assert arquivo.exists()
    with pytest.raises(gamificacao.ErroGamificacao):
        gamificacao.confirmar_missao("1º ano", "compostagem")

    app.radio[0].set_value("Ranking").run()
    assert app.dataframe[1].value.iloc[0].to_dict() == {"Posição": 1, "Turma": "1º ano", "Pontos": 15}
    assert not app.exception


def test_prazo_do_semestre_muda_na_virada_do_calendario():
    fuso = ZoneInfo("America/Sao_Paulo")
    antes = datetime(2026, 6, 30, 23, 59, tzinfo=fuso)
    inicio_segundo = datetime(2026, 7, 1, tzinfo=fuso)
    inicio_ano_seguinte = datetime(2027, 1, 1, tzinfo=fuso)
    assert _prazo_semestre(antes) == inicio_segundo
    assert _prazo_semestre(inicio_segundo) == inicio_ano_seguinte
    assert _prazo_semestre(inicio_ano_seguinte) == datetime(2027, 7, 1, tzinfo=fuso)
