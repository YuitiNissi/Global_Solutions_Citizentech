from base64 import b64encode
from datetime import date
from mimetypes import guess_type
from pathlib import Path

import streamlit as st

from modulos.assistente import ErroBase, buscar, carregar_base, organizar_por_tema
from modulos.gamificacao_ui import exibir_gamificacao
from modulos.programa_escolar import exibir_programa_escolar


IMAGENS_DE_FUNDO = {
    "Assistente educativo": "horta1.webp",
    "Gamificação": "horta2.jpeg",
    "Programa escolar": "horta3.webp",
}
ICONES_DOS_MODULOS = {
    "Assistente educativo": "💬",
    "Gamificação": "🏆",
    "Programa escolar": "🏫",
}


def selecionar_modulo():
    st.html("""
        <style>
        [data-testid="stSidebar"] {
            background-color: #e0f2df;
            color: #183c27;
        }
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
        [data-testid="stSidebar"] [data-testid="stHeading"] {
            color: #183c27;
            text-align: center;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] {
            display: flex;
            justify-content: center;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button {
            width: 100%;
            min-height: 3.5rem;
            padding: 0.65rem 1rem;
            border-radius: 999px;
            border: 2px solid #78a784;
            background-color: #f1faee;
            color: #183c27;
            text-align: center;
            white-space: normal;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button p {
            font-size: 1.1rem;
            font-weight: 700;
            line-height: 1.2;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
            background-color: #c8e8c8;
            border-color: #39704a;
        }
        [data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
            background-color: #b2dfb5;
            border-color: #255a37;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] button:focus-visible {
            outline: 3px solid #255a37;
            outline-offset: 3px;
        }
        </style>
    """)
    st.sidebar.caption("Protótipo acadêmico")
    st.sidebar.subheader("Módulos")
    ativo = st.session_state.setdefault("modulo_ativo", "Assistente educativo")
    for modulo in IMAGENS_DE_FUNDO:
        st.sidebar.button(
            f"{ICONES_DOS_MODULOS[modulo]} {modulo}",
            key=f"navegacao-{modulo}",
            type="primary" if modulo == ativo else "secondary",
            on_click=st.session_state.update,
            args=({"modulo_ativo": modulo},),
        )
    return ativo


@st.cache_data(show_spinner=False)
def carregar_imagem_de_fundo(nome):
    caminho = Path(__file__).resolve().parent / "imagens" / nome
    tipo, _ = guess_type(caminho.name)
    imagem = b64encode(caminho.read_bytes()).decode("ascii")
    return f"data:{tipo};base64,{imagem}"


def aplicar_fundo(modulo):
    try:
        imagem = carregar_imagem_de_fundo(IMAGENS_DE_FUNDO[modulo])
    except OSError:
        return

    st.html(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            --foto-horta: url("{imagem}");
            --fundo-legivel: color-mix(in srgb, var(--st-background-color, white) 94%, transparent);
            --fundo-lateral: color-mix(in srgb, var(--st-background-color, white) 24%, transparent);
            background-image: linear-gradient(
                90deg, var(--fundo-lateral), var(--fundo-legivel) 22%,
                var(--fundo-legivel) 78%, var(--fundo-lateral)
            ), var(--foto-horta);
            background-size: cover;
            background-position: center;
        }}
        @media (max-width: 1200px) {{
            [data-testid="stAppViewContainer"] {{
                --fundo-legivel: color-mix(in srgb, var(--st-background-color, white) 88%, transparent);
                background-image: linear-gradient(
                    var(--fundo-legivel), var(--fundo-legivel)
                ), var(--foto-horta);
            }}
        }}
        </style>
        """
    )


def exibir_orientacao(registro):
    st.subheader(registro["subtema"])
    if registro["fonte"] == "Pendente de validação":
        st.warning("Orientação pendente de validação.")
        return
    st.caption(registro["tema"])
    st.write(registro["resumo"])
    st.write(registro["resposta"])
    consulta = date.fromisoformat(registro["data_consulta"])
    st.caption(f"Fonte consultada em {consulta:%d/%m/%Y}")
    st.link_button(registro["fonte"], registro["url_fonte"])


def exibir_assistente(base):
    pergunta, explorar = st.tabs(["Fazer uma pergunta", "Explorar por tema"])
    with pergunta:
        with st.form("formulario_assistente"):
            texto = st.text_input(
                "O que você quer aprender?",
                placeholder="Exemplo: Como economizar água na irrigação?",
                max_chars=300,
            )
            if st.form_submit_button("Consultar", type="primary"):
                st.session_state["consulta"] = texto

        if "consulta" in st.session_state:
            resultado = buscar(st.session_state["consulta"], base)
            if resultado.status == "encontrada":
                exibir_orientacao(resultado.registros[0])
            elif resultado.status == "ambigua":
                st.info(resultado.mensagem)
                opcoes = {registro["id"]: registro for registro in resultado.registros}
                escolhido = st.selectbox(
                    "Qual era o assunto da pergunta?",
                    options=list(opcoes),
                    format_func=lambda item: f'{opcoes[item]["subtema"]} · {opcoes[item]["tema"]}',
                    index=None,
                    placeholder="Selecione um assunto",
                    key=f'ambiguidade-{st.session_state["consulta"]}',
                )
                if escolhido is not None:
                    exibir_orientacao(opcoes[escolhido])
            else:
                st.info(resultado.mensagem)

    with explorar:
        temas = organizar_por_tema(base)
        tema = st.selectbox("Tema", list(temas))
        subtema = st.selectbox("Subtema", list(temas[tema]), key=f"subtema-{tema}")
        for registro in temas[tema][subtema]:
            exibir_orientacao(registro)


def main():
    st.set_page_config(page_title="Horta Viva", page_icon="🌱")
    st.title("🌱 Horta Viva")
    st.write("Aprenda sobre alimentação consciente, cultivo sustentável e hortas escolares.")
    modulo = selecionar_modulo()
    aplicar_fundo(modulo)
    if modulo == "Gamificação":
        exibir_gamificacao()
        return
    if modulo == "Programa escolar":
        exibir_programa_escolar()
        return

    try:
        base = carregar_base()
    except ErroBase as erro:
        st.error(str(erro))
        return
    exibir_assistente(base)


if __name__ == "__main__":
    main()
