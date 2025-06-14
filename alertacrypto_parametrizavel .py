
import streamlit as st
import requests
import time
import json
import os

# Configurações
api_key = "6039606"
numero_celular = "556781430574"
ARQUIVO_ZONAS = "zonas.json"

# Mapear ativos para CoinGecko
mapa_ids = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "SOLUSDT": "solana"
}

# Carregar zonas salvas
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

def enviar_mensagem(mensagem):
    if not mensagem.strip():
        return
    url = "https://api.callmebot.com/whatsapp.php"
    params = {"phone": numero_celular, "text": mensagem, "apikey": api_key}
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200 and "queued" in r.text.lower():
            print("✅ Enviada:", mensagem)
    except:
        pass

def buscar_dados_coingecko():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        ids = ",".join(mapa_ids.values())
        params = {"ids": ids, "vs_currencies": "usd"}
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            preco_raw = r.json()
            dados = []
            for simbolo, cg_id in mapa_ids.items():
                preco = preco_raw[cg_id]["usd"]
                dados.append({"symbol": simbolo, "price": preco})
            return dados
        else:
            st.error(f"❌ CoinGecko respondeu com status: {r.status_code}")
            return []
    except Exception as e:
        st.error(f"❌ Erro ao conectar à CoinGecko: {e}")
        return []

# Atualização a cada 30 segundos
if "ultima_atualizacao" not in st.session_state:
    st.session_state.ultima_atualizacao = time.time()
elif time.time() - st.session_state.ultima_atualizacao > 30:
    st.session_state.ultima_atualizacao = time.time()
    st.rerun()

st.set_page_config(page_title="Alerta Cripto com CoinGecko", layout="wide")
st.title("📊 Alerta Cripto (CoinGecko) — Atualização a cada 30s")

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

st.subheader("📡 Situação Atual das Criptos")
dados = buscar_dados_coingecko()
if "enviadas" not in st.session_state:
    st.session_state.enviadas = set()

if not dados:
    st.warning("⚠️ Nenhum dado carregado. Verifique conexão com CoinGecko.")

for item in dados:
    simbolo = item["symbol"]
    if simbolo in zonas:
        preco = float(item["price"])
        suporte = zonas[simbolo]["suporte"]
        resistencia = zonas[simbolo]["resistencia"]
        status = "🟡 Dentro da zona"

        if preco > resistencia and (simbolo, "alta") not in st.session_state.enviadas:
            status = "🟢 Rompeu resistência"
            msg = f"🚨 [{simbolo}] ROMPEU A RESISTÊNCIA! Preço: {preco:.2f} USDT | Res: {resistencia} | ⏰ H4"
            enviar_mensagem(msg)
            st.session_state.enviadas.add((simbolo, "alta"))

        elif preco < suporte and (simbolo, "baixa") not in st.session_state.enviadas:
            status = "🔻 Perdeu suporte"
            msg = f"⚠️ [{simbolo}] PERDEU O SUPORTE! Preço: {preco:.2f} USDT | Sup: {suporte} | ⏰ H4"
            enviar_mensagem(msg)
            st.session_state.enviadas.add((simbolo, "baixa"))

        st.markdown(f"**{simbolo}**: {preco:.2f} USDT | Suporte: {suporte} | Resistência: {resistencia} → {status}")

st.info("🔁 CoinGecko com intervalo de 30 segundos para evitar bloqueio.")
