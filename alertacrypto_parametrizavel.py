
import streamlit as st
import requests
import time
import json
import os

# Configurações principais
api_key = "6039606"
numero_celular = "556781430574"
ARQUIVO_ZONAS = "zonas.json"

# Carregar ou inicializar zonas
def carregar_zonas():
    if os.path.exists(ARQUIVO_ZONAS):
        with open(ARQUIVO_ZONAS, "r") as f:
            return json.load(f)
    return {
        "BTCUSDT": {"suporte": 103000, "resistencia": 109000},
        "ETHUSDT": {"suporte": 2500, "resistencia": 2700},
        "SOLUSDT": {"suporte": 144, "resistencia": 155}
    }

def salvar_zonas(zonas):
    with open(ARQUIVO_ZONAS, "w") as f:
        json.dump(zonas, f, indent=4)

# Enviar mensagem WhatsApp
def enviar_mensagem(mensagem):
    if not mensagem.strip():
        print("⚠️ Mensagem vazia — não enviada.")
        return
    print(">>> Enviando mensagem:", mensagem)
    url = "https://api.callmebot.com/whatsapp.php"
    params = {"phone": numero_celular, "text": mensagem, "apikey": api_key}
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200 and "queued" in r.text.lower():
            print("✅ Mensagem enviada com sucesso!")
        else:
            print("❌ Erro ao enviar:", r.status_code, r.text)
    except Exception as e:
        print("❌ Erro:", e)

# Interface Streamlit
st.set_page_config(page_title="Alerta Cripto - Parametrização", layout="wide")
st.title("📊 Alerta Cripto com Parametrização de Zonas")

zonas = carregar_zonas()

with st.expander("⚙️ Parâmetros de Zonas"):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        for ativo in zonas:
            zonas[ativo]["suporte"] = st.number_input(f"{ativo} - Suporte", value=zonas[ativo]["suporte"], key=f"{ativo}_s")
    with col2:
        for ativo in zonas:
            zonas[ativo]["resistencia"] = st.number_input(f"{ativo} - Resistência", value=zonas[ativo]["resistencia"], key=f"{ativo}_r")
    with col3:
        if st.button("💾 Salvar configurações"):
            salvar_zonas(zonas)
            st.success("Zonas salvas com sucesso!")

st.divider()
st.subheader("📡 Monitoramento de Rompimentos")

placeholder = st.empty()
enviadas = set()

def buscar_dados():
    try:
        r = requests.get('https://api.binance.com/api/v3/ticker/price', timeout=10)
        return r.json() if r.status_code == 200 else []
    except:
        return []

while True:
    dados = buscar_dados()
    exibicao = []
    for item in dados:
        simbolo = item["symbol"]
        if simbolo in zonas:
            preco = float(item["price"])
            suporte = zonas[simbolo]["suporte"]
            resistencia = zonas[simbolo]["resistencia"]
            status = "🟡 Dentro da zona"

            if preco > resistencia and (simbolo, "alta") not in enviadas:
                status = "🟢 Rompeu resistência"
                msg = f"🚨 [{simbolo}] ROMPEU A RESISTÊNCIA! Preço atual: {preco:.2f} USDT | Res: {resistencia} | ⏰ H4"
                enviar_mensagem(msg)
                enviadas.add((simbolo, "alta"))
            elif preco < suporte and (simbolo, "baixa") not in enviadas:
                status = "🔻 Perdeu suporte"
                msg = f"⚠️ [{simbolo}] PERDEU O SUPORTE! Preço atual: {preco:.2f} USDT | Sup: {suporte} | ⏰ H4"
                enviar_mensagem(msg)
                enviadas.add((simbolo, "baixa"))

            exibicao.append((simbolo, preco, suporte, resistencia, status))

    with placeholder.container():
        st.markdown("### Situação Atual das Criptos")
        for s, p, sup, res, stat in exibicao:
            st.markdown(f"**{s}**: {p:.2f} USDT | Suporte: {sup} | Resistência: {res} → {stat}")
        st.info("Atualizando a cada 10 segundos com base nas zonas definidas acima.")
    time.sleep(10)
