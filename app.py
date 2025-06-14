
import streamlit as st
from streamlit_option_menu import option_menu
import base64

st.set_page_config(page_title="Cripto Alerta", layout="wide")

with st.sidebar:
    escolha = option_menu("Menu", ["🏠 Início", "📊 Painel de Alerta"],
                          icons=["house", "bar-chart"], menu_icon="cast", default_index=0)

# 🔧 FUNDO FUNCIONAL COM OVERLAY ESCURO
def carregar_fundo(caminho):
    with open(caminho, "rb") as img_file:
        b64_img = base64.b64encode(img_file.read()).decode()
    return f"""
        <style>
        html, body, [class*="css"]  {{
            height: 100%;
            margin: 0;
        }}
        .background {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-image: url("data:image/png;base64,{b64_img}");
            background-size: cover;
            background-position: center;
            z-index: -2;
        }}
        .overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0,0,0,0.75);
            z-index: -1;
        }}
        .conteudo {{
            position: relative;
            top: 25vh;
            text-align: center;
            color: white;
        }}
        .conteudo h1 {{
            font-size: 3.5em;
            font-weight: bold;
            margin-bottom: 0.2em;
        }}
        .conteudo p {{
            font-size: 1.2em;
            color: #cccccc;
            margin-bottom: 2em;
        }}
        .botao {{
            font-size: 1.1em;
            padding: 12px 30px;
            background-color: #10a37f;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: 0.3s ease-in-out;
        }}
        .botao:hover {{
            background-color: #0e8e6b;
            transform: scale(1.05);
        }}
        </style>
        <div class="background"></div>
        <div class="overlay"></div>
    """

# Página HOME
if escolha == "🏠 Início":
    st.markdown(carregar_fundo("fundo_inicio.png"), unsafe_allow_html=True)
    st.markdown("""
        <div class="conteudo">
            <h1>🚀 Alerta Cripto Automatizado</h1>
            <p>Monitoramento contínuo de rompimentos com inteligência estratégica</p>
            <a href="?page=📊 Painel de Alerta">
                <button class="botao">🔍 Acessar Painel</button>
            </a>
        </div>
    """, unsafe_allow_html=True)

# Painel operacional
elif escolha == "📊 Painel de Alerta":
    st.markdown("# 📊 Painel de Alerta Cripto")
    st.markdown("Carregando painel...")
    try:
        with open("alertacrypto_parametrizavel.py") as f:
            exec(f.read())
    except Exception as e:
        st.error(f"Erro ao carregar painel: {e}")
