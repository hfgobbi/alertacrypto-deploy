
import streamlit as st
import requests
import time
import json
import os

# Configurações
api_key = "6039606"
numero_celular = "556781430574"
ARQUIVO_ZONAS = "zonas.json"
ARQUIVO_CACHE = "precos_cache.json"

# Mapear ativos para CoinGecko
mapa_ids = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT": "ethereum",
    "SOLUSDT": "solana"
}

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

def salvar_cache(dados):
    with open(ARQUIVO_CACHE, "w") as f:
        json.dump(dados, f)

def carregar_cache():
    if os.path.exists(ARQUIVO_CACHE):
        with open(ARQUIVO_CACHE, "r") as f:
            return json.load(f)
    return []

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
            salvar_cache(dados)
            return dados
        else:
            st.warning(f"⚠️ CoinGecko status {r.status_code}. Usando dados em cache.")
            return carregar_cache()
    except Exception as e:
        st.warning(f"⚠️ Erro ao conectar à CoinGecko: {e}. Usando dados em cache.")
        return carregar_cache()

# Atualização a cada 30 segundos
if "ultima_atualizacao" not in st.session_state:
    st.session_state.ultima_atualizacao = time.time()
elif time.time() - st.session_state.ultima_atualizacao > 30:
    st.session_state.ultima_atualizacao = time.time()
    st.rerun()

st.title("📊 Alerta Cripto (CoinGecko + Cache) — Atualização a cada 30s")

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
    st.warning("⚠️ Nenhum dado carregado (nem mesmo cache).")
else:
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

st.info("🔁 CoinGecko com cache ativado. Atualização a cada 30s.")
