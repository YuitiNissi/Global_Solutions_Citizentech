from datetime import datetime, timedelta
from math import ceil
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from modulos.gamificacao import (
    AGUARDANDO,
    CONFIRMADA,
    DISPONIVEL,
    MISSOES,
    TURMAS,
    ErroGamificacao,
    calcular_pontos,
    carregar_progresso,
    confirmar_missao,
    enviar_missao,
)

PASTA_IMAGENS = Path(__file__).resolve().parents[2] / "assets"


def _prazo_semestre(agora):
    if agora.month <= 6:
        return datetime(agora.year, 7, 1, tzinfo=agora.tzinfo)
    return datetime(agora.year + 1, 1, 1, tzinfo=agora.tzinfo)


@st.fragment(run_every="30s")
def _exibir_timer_semestre():
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    prazo = _prazo_semestre(agora)
    minutos_restantes = ceil((prazo - agora).total_seconds() / 60)
    dias, minutos_do_dia = divmod(minutos_restantes, 24 * 60)
    horas, minutos = divmod(minutos_do_dia, 60)
    ultimo_dia = prazo.date() - timedelta(days=1)

    st.metric("Tempo restante para completar as missões", f"{dias}d {horas:02d}h {minutos:02d}min")
    st.caption(f"Prazo simulado até {ultimo_dia:%d/%m/%Y} às 23h59, horário de Brasília.")


def _exibir_ranking(progresso):
    _exibir_timer_semestre()
    for etapa, turmas in TURMAS.items():
        st.subheader(etapa)
        ranking = pd.DataFrame(
            {"Turma": turmas, "Pontos": [calcular_pontos(progresso.get(turma, {})) for turma in turmas]}
        ).sort_values("Pontos", ascending=False, kind="stable")
        posicoes = ranking["Pontos"].rank(method="min", ascending=False).astype(int)
        ranking.insert(0, "Posição", posicoes)
        st.dataframe(ranking, hide_index=True)


def _selecionar_turma(tela):
    etapa = st.selectbox("Etapa de ensino", list(TURMAS), key=f"etapa-{tela}")
    return st.selectbox("Turma", TURMAS[etapa], key=f"turma-{tela}-{etapa}")


def _exibir_missoes(missoes):
    for chave, missao in MISSOES.items():
        with st.container(border=True):
            icone, detalhes = st.columns([1, 7], gap="small")
            caminho = PASTA_IMAGENS / missao.icone
            if caminho.is_file():
                icone.image(str(caminho), width=48)
            with detalhes:
                st.markdown(f"**{missao.titulo}**")
                st.write(missao.atividade)
                st.caption(f"+{missao.pontos} pontos · {missoes.get(chave, DISPONIVEL)}")


def _exibir_area(progresso, professor=False):
    tela = "professor" if professor else "turma"
    turma = _selecionar_turma(tela)
    missoes = progresso.get(turma, {})
    st.metric("Pontos confirmados", calcular_pontos(missoes))
    concluidas = sum(status == CONFIRMADA for status in missoes.values())
    st.progress(concluidas / len(MISSOES), text=f"{concluidas} de {len(MISSOES)} missões confirmadas")
    _exibir_missoes(missoes)

    status_elegivel = AGUARDANDO if professor else DISPONIVEL
    elegiveis = [chave for chave in MISSOES if missoes.get(chave, DISPONIVEL) == status_elegivel]
    if not elegiveis:
        st.info("Nenhuma missão aguardando confirmação." if professor else "Todas as missões já foram enviadas.")
        return

    chave = st.selectbox(
        "Missão para confirmar" if professor else "Missão concluída pela turma",
        elegiveis,
        format_func=lambda item: f"{MISSOES[item].titulo} · {MISSOES[item].pontos} pontos",
        index=None,
        placeholder="Selecione uma missão",
        key=f"missao-{tela}-{turma}",
    )
    rotulo = "Confirmar missão e pontuação" if professor else "Enviar para confirmação"
    if st.button(rotulo, type="primary", disabled=chave is None):
        if professor:
            confirmar_missao(turma, chave)
            st.session_state["aviso_gamificacao"] = f"Missão confirmada. +{MISSOES[chave].pontos} pontos para {turma}."
        else:
            enviar_missao(turma, chave)
            st.session_state["aviso_gamificacao"] = "Missão enviada para confirmação do professor."
        st.rerun()


def exibir_gamificacao():
    st.header("Gamificação")
    st.caption("Turmas e missões simuladas.")
    tela = st.radio("Área da gamificação", ["Ranking", "Área da turma", "Área do professor"], horizontal=True)
    aviso = st.session_state.pop("aviso_gamificacao", None)
    if aviso:
        st.success(aviso)
    try:
        progresso = carregar_progresso()
        if tela == "Ranking":
            _exibir_ranking(progresso)
        else:
            _exibir_area(progresso, professor=tela == "Área do professor")
    except ErroGamificacao as erro:
        st.error(str(erro))
