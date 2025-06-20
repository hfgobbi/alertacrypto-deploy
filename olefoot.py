import streamlit as st

st.set_page_config(
    page_title="Olefoot Dashboard",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Olefoot • Dashboard Estratégico")
st.markdown("Bem-vindo ao painel inteligente para gestão de portfólio e alertas de criptoativos.")

st.markdown("### 👉 Use o menu lateral para acessar:")

# Aqui estão os links diretos:
st.markdown("- 📈 [Alerta Cripto](./alertacrypto)")
st.markdown("- 💡 [Portfolio Inteligente](./portfolio)")

