import json

from modulos.interface_texto import executar


def sessao(*entradas, **opcoes):
    fila = iter(entradas)
    linhas = []

    def entrada(rotulo):
        valor = next(fila, None)
        if valor is None:
            raise EOFError
        linhas.append(f"{rotulo}{valor}")
        return valor

    codigo = executar(entrada=entrada, saida=lambda texto="": linhas.append(str(texto)), **opcoes)
    return codigo, "\n".join(linhas)


def test_pergunta_mostra_fonte_aviso_e_relacionados():
    codigo, texto = sessao("1", "Como regar a horta sem desperdiçar água?", "", "0")
    assert codigo == 0
    assert "== Irrigação · Cultivo sustentável · cultivo-02 ==" in texto
    assert "Link: https://www.infoteca.cnptia.embrapa.br" in texto
    assert "consultada em 17/11/2026" in texto
    assert "Aviso: Conteúdo educativo" in texto
    assert "Continue explorando:\n  1. Cobertura do solo" in texto


def test_navega_por_tres_assuntos_relacionados():
    _, texto = sessao("1", "Como fazer compostagem?", "1", "1", "", "0")
    assert "Caminho: Compostagem > Cobertura do solo > Irrigação" in texto


def test_explorar_por_tema_e_aviso_especifico():
    _, texto = sessao("2", "1", "6", "", "0")
    assert "Temas disponíveis:" in texto
    assert "6. Habilidades culinárias (alimentacao-06)" in texto
    assert "Atenção: Atividades de crianças na cozinha precisam de supervisão de um adulto." in texto


def test_entradas_invalidas_tem_mensagens_compreensiveis():
    _, texto = sessao("", "7", "abc", "2", "9", "", "1", "   ", "0")
    assert "Entrada vazia. Digite o número de uma opção do menu." in texto
    assert texto.count("Opção inexistente. Digite um número de 0 a 5.") == 2
    assert "Opção inexistente. Digite um número de 1 a 3 ou Enter para voltar." in texto
    assert "Digite uma pergunta para consultar o assistente." in texto


def test_pergunta_ambigua_permite_escolher():
    _, texto = sessao("1", "Compostagem ou irrigação?", "2", "", "0")
    assert "Encontrei mais de um assunto possível" in texto
    assert texto.count("== ") == 1


def test_fora_do_escopo_explica_limite_e_sugere():
    _, texto = sessao("1", "Qual remédio tomar para dor de cabeça?", "", "0")
    assert "Não encontrei uma orientação confiável na base" in texto
    assert "Assuntos que você pode consultar:" in texto
    assert "== " not in texto


def test_consulta_por_identificador_e_troca_de_modelo():
    _, texto = sessao("3", "escola-05", "", "4", "1", "Como fazer compostagem?", "0")
    assert "Atenção: Mudanças no cardápio da merenda" in texto
    assert "Modelo de resposta: Modelo A · resposta direta." in texto
    assert "\nFonte: Embrapa — Hortas Pedagógicas: Manual prático para instalação\n" in texto


def test_indicadores_no_menu():
    _, texto = sessao("5", "0")
    assert "Perguntas de teste: 22" in texto
    assert "taxa de acerto:" in texto


def test_fim_de_entrada_encerra_sem_erro():
    codigo, texto = sessao("1")
    assert codigo == 0
    assert "Até logo!" in texto


def test_base_invalida_encerra_com_mensagem(tmp_path):
    caminho = tmp_path / "base.json"
    caminho.write_text(json.dumps([]), encoding="utf-8")
    codigo, texto = sessao(caminho_base=caminho)
    assert codigo == 1
    assert "Erro: A base precisa conter uma lista de orientações." in texto
