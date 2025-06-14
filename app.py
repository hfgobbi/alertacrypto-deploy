import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Cripto Alerta", layout="wide")

pages = ["Início", "Painel de Alerta"]
icons = ["house", "bar-chart"]

if "menu_escolha" not in st.session_state:
    st.session_state.menu_escolha = "Início"

with st.sidebar:
    escolha = option_menu(
        "Menu",
        pages,
        icons=icons,
        menu_icon="cast",
        default_index=0 if st.session_state.menu_escolha == "Início" else 1
    )
    st.session_state.menu_escolha = escolha

if st.session_state.menu_escolha == "Início":
    st.markdown(
        """
        <div style='text-align: center; margin-top: 60px;'>
            <h1 style='font-size:3em;'>🚀 Alerta Cripto Automatizado</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <div style='text-align: center; font-size: 1.3em; margin-top: 1em; margin-bottom: 2em;'>
            Monitoramento contínuo de rompimentos com inteligência estratégica
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("🔍 Acessar Painel"):
        st.session_state.menu_escolha = "Painel de Alerta"
        st.experimental_rerun()

if st.session_state.menu_escolha == "Painel de Alerta":
    st.markdown("# 📊 Painel de Alerta Cripto")
    st.markdown("Carregando painel...")
    try:
        with open("alertacrypto_parametrizavel.py") as f:
            exec(f.read())
    except Exception as e:
        st.error(f"Erro ao carregar painel: {e}")
