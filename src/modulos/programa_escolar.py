import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st


RAIZ = Path(__file__).resolve().parents[2]
ARQUIVO_PROGRAMA = RAIZ / "data" / "programa_escolar.json"
PASTA_IMAGENS = RAIZ / "assets"
MESES = (
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
)
SEM_INFORMACAO = "Sem informação cadastrada"
A_CONFIRMAR = "A confirmar"


def _data_formatada(valor):
    return date.fromisoformat(valor).strftime("%d/%m/%Y") if valor else A_CONFIRMAR


def _exibir_ficha(alimento, horta, safra, produtor, merenda, cesta):
    with st.container(border=True):
        st.subheader(alimento["nome"])
        imagem = alimento.get("imagem")
        if imagem:
            caminho = PASTA_IMAGENS / Path(imagem).name
            if caminho.is_file():
                st.image(str(caminho), width=240)
        if alimento.get("ciclo_curto"):
            st.caption("Opção de ciclo curto para as primeiras atividades")

        st.markdown("**Na horta da escola**")
        st.write(f"Etapa atual: {horta.get('etapa') or SEM_INFORMACAO}")
        st.write(f"Próxima atividade da turma: {horta.get('proxima_atividade') or A_CONFIRMAR}")

        st.markdown("**Na safra local**")
        st.write(f"Período de referência: {safra or SEM_INFORMACAO}")
        st.write(f"Disponibilidade informada pelo produtor: {produtor or SEM_INFORMACAO}")

        st.markdown("**Na merenda**")
        if merenda:
            st.write(f"{merenda['status']} · {merenda.get('uso') or A_CONFIRMAR}")
            st.write(f"Data: {_data_formatada(merenda.get('data'))}")
        else:
            st.write(SEM_INFORMACAO)

        st.markdown("**Na cesta**")
        if cesta:
            detalhe = cesta.get("detalhe") or "Presença na composição da cesta"
            st.write(f"{cesta['status']} · {detalhe}")
            st.write(f"Reserva até: {_data_formatada(cesta.get('reserva_ate'))}")
            st.write(f"Retirada: {_data_formatada(cesta.get('retirada'))}")
        else:
            st.write(SEM_INFORMACAO)

        atividade = alimento.get("atividade")
        if atividade:
            st.markdown("**Atividade para as crianças**")
            st.write(atividade)


def _exibir_indicadores(registro):
    st.subheader("Participação no mês")
    turmas, refeicoes, familias = st.columns(3)
    atividades = registro.get("atividades_realizadas", [] if not registro else None)
    servidas = registro.get("refeicoes_locais_servidas_por_dia", {} if not registro else None)
    retiradas = registro.get("familias_unicas_com_retirada_subsidiada", 0 if not registro else None)
    turmas.metric("Turmas participantes", len(set(atividades)) if atividades is not None else None)
    refeicoes.metric(
        "Refeições servidas com alimentos de produtores locais",
        sum(servidas.values()) if servidas is not None else None,
    )
    familias.metric(
        "Famílias que retiraram cestas com subsídio",
        retiradas,
    )
    if any(valor is None for valor in (atividades, servidas, retiradas)):
        st.caption("Indicadores com traço: sem informação cadastrada.")


def exibir_programa_escolar():
    st.header("Calendário da Horta Viva")
    st.write("Acompanhe o que as turmas cultivam e como os alimentos podem chegar à merenda e às cestas.")
    try:
        dados = json.loads(ARQUIVO_PROGRAMA.read_text(encoding="utf-8"))
        escola, alimentos, safras, meses = (
            dados[campo] for campo in ("escola", "alimentos", "safras", "meses")
        )
        regiao = escola.get("regiao")
        referencia = safras.get(regiao, {})
        hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
        atual = hoje.strftime("%Y-%m")
        inicial = date.fromisoformat(f"{max(meses)}-01") if meses and atual not in meses else hoje
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        st.error("Não foi possível carregar o calendário. Verifique o cadastro do Programa Escolar.")
        return

    if dados.get("demonstracao", True):
        st.info("Demonstração com dados fictícios. Safras, disponibilidade, datas e totais são simulados.")
    st.caption(f"{escola.get('nome') or 'Escola'} · Região de referência: {regiao or SEM_INFORMACAO}")
    coluna_mes, coluna_ano = st.columns(2)
    mes = coluna_mes.selectbox("Mês", MESES, index=inicial.month - 1, key="programa_mes")
    ano = coluna_ano.number_input(
        "Ano", min_value=1, max_value=9999, value=inicial.year, step=1, key="programa_ano"
    )
    registro = meses.get(f"{ano:04d}-{MESES.index(mes) + 1:02d}", {})
    if not registro:
        st.info("Nenhum registro cadastrado para o mês selecionado.")
    else:
        for chave, alimento in alimentos.items():
            _exibir_ficha(
                alimento,
                registro.get("horta", {}).get(chave, {}),
                referencia.get(chave),
                registro.get("produtor", {}).get(chave),
                registro.get("merenda", {}).get(chave),
                registro.get("cestas", {}).get(chave),
            )
    _exibir_indicadores(registro)
