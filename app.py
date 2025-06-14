import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Cripto Alerta", layout="wide")

with st.sidebar:
    escolha = option_menu("Menu", ["🏠 Início", "📊 Painel de Alerta"],
                          icons=["house", "bar-chart"], menu_icon="cast", default_index=0)

if escolha == "🏠 Início":
    st.markdown(
        """
        <div style='text-align: center; margin-top: 60px;'>
            <h1 style='font-size:3em;'>🚀 Alerta Cripto Automatizado</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )


    img_path = "fundo_inicio.png"

    col_text, col_img = st.columns([2, 1])
    with col_text:
        st.markdown(
            """
            <div style='text-align: center; font-size: 1.3em; margin-top: 1em; margin-bottom: 2em;'>
                Monitoramento contínuo de rompimentos com inteligência estratégica
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div style='display: flex; justify-content: center;'>
                <a href='/?page=📊 Painel de Alerta'><button style='font-size:1.2em; padding:12px 32px; border-radius:10px; background:#22c55e; color:white; border:none; cursor:pointer;'>🔍 Acessar Painel</button></a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_img:
        st.image(img_path, use_column_width=True, caption=None)

elif escolha == "📊 Painel de Alerta":
    st.markdown("# 📊 Painel de Alerta Cripto")
    st.markdown("Carregando painel...")
    try:
        with open("alertacrypto_parametrizavel.py") as f:
            exec(f.read())
    except Exception as e:
        st.error(f"Erro ao carregar painel: {e}")
