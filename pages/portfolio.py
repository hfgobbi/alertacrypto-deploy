import streamlit as st
import pandas as pd
import json
import os
import requests

DADOS_PATH = "portfolio_data.json"

def salvar_dados_portfolio(dados):
    with open(DADOS_PATH, "w") as f:
        json.dump(dados, f, indent=4)

def carregar_dados_portfolio():
    if os.path.exists(DADOS_PATH):
        with open(DADOS_PATH, "r") as f:
            return json.load(f)
    else:
        return {}

def obter_percentual_por_range(preco_atual, ranges):
    ranges_ordenados = sorted(ranges.items(), key=lambda x: float(x[0]), reverse=True)
    for preco_range, percentual in ranges_ordenados:
        if preco_atual >= float(preco_range):
            return float(percentual)
    # Se preço for menor que todos os ranges, retorna o menor percentual
    return float(ranges_ordenados[-1][1]) if ranges_ordenados else 50.0

def buscar_preco_do_cache_alertas():
    """Busca preços do cache do sistema de alertas"""
    try:
        # Tentar ler do cache do alerta cripto
        if os.path.exists("precos_cache.json"):
            with open("precos_cache.json", "r") as f:
                cache_alertas = json.load(f)
                
            # Se tem dados recentes (estrutura com timestamp)
            if isinstance(cache_alertas, dict) and "dados" in cache_alertas:
                dados = cache_alertas["dados"]
            else:
                dados = cache_alertas
                
            # Extrair preços
            precos = {}
            for item in dados:
                if item["symbol"] == "BTCUSDT":
                    precos["BTC"] = item["price"]
                elif item["symbol"] == "ETHUSDT":
                    precos["ETH"] = item["price"]
                elif item["symbol"] == "SOLUSDT":
                    precos["SOL"] = item["price"]
                    
            return precos
    except:
        pass
    return {}

def buscar_preco_mercado(ativo):
    """Primeiro tenta API, depois usa cache do alerta cripto"""
    
    # Tentar API direta (caso funcione)
    try:
        mapa_ids = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana"}
        url = "https://api.coingecko.com/api/v3/simple/price"
        cg_id = mapa_ids[ativo]
        params = {"ids": cg_id, "vs_currencies": "usd"}
        
        r = requests.get(url, params=params, timeout=10)
        
        if r.status_code == 200:
            preco_raw = r.json()
            if cg_id in preco_raw and "usd" in preco_raw[cg_id]:
                return preco_raw[cg_id]["usd"]
    except:
        pass
    
    # Se API falhou, tentar cache do alerta cripto
    precos_cache = buscar_preco_do_cache_alertas()
    if ativo in precos_cache:
        return precos_cache[ativo]
    
    return None

st.title("💡 Portfolio Inteligente - Pool de Liquidez Multiativo")

ativo = st.radio(
    "Selecione o ativo para análise:",
    ("BTC", "ETH", "SOL")
)

# Carregar dados do ativo selecionado
all_data = carregar_dados_portfolio()
data = all_data.get(ativo, {})

st.header(f"💰 Valor disponível na Pool [{ativo}/USD]")
saldo1 = st.number_input(f"{ativo} (USD)", value=data.get("saldo1", 1000.0), format="%.2f")
saldo2 = st.number_input("USDC (USD)", value=data.get("saldo2", 1500.0), format="%.2f")
total = saldo1 + saldo2

st.dataframe(pd.DataFrame({"Ativo": [ativo, "USDC", "TOTAL"], "USD": [saldo1, saldo2, total]}), hide_index=True)

st.header("🎯 Estratégia por Range de Preço")
st.markdown("**Configure 5 faixas de preço e o percentual do ativo para cada uma:**")

# Carregar ranges existentes ou criar padrão
ranges_existentes = data.get("ranges", {})

# Se não há ranges ou tem formato antigo, criar 5 ranges padrão
if len(ranges_existentes) != 5:
    if ativo == "BTC":
        ranges_existentes = {"140000": 10, "120000": 30, "100000": 50, "80000": 70, "60000": 90}
    elif ativo == "ETH":
        ranges_existentes = {"4000": 20, "3500": 40, "3000": 60, "2500": 80, "2000": 95}
    elif ativo == "SOL":
        ranges_existentes = {"300": 25, "250": 45, "200": 65, "150": 85, "100": 100}

# Converter para lista ordenada para interface
ranges_lista = sorted(ranges_existentes.items(), key=lambda x: float(x[0]), reverse=True)

# Interface para 5 ranges fixos
novos_ranges = {}
for i in range(5):
    col1, col2 = st.columns(2)
    
    preco_default = float(ranges_lista[i][0]) if i < len(ranges_lista) else 0.0
    perc_default = float(ranges_lista[i][1]) if i < len(ranges_lista) else 50.0
    
    with col1:
        preco = st.number_input(
            f"Preço Range {i+1}:", 
            value=preco_default, 
            format="%.2f",
            key=f"preco_{ativo}_{i}",
            help=f"Quando {ativo} atingir este preço ou mais"
        )
    
    with col2:
        perc = st.number_input(
            f"% {ativo}:", 
            value=perc_default, 
            min_value=0.0, 
            max_value=100.0, 
            format="%.1f",
            key=f"perc_{ativo}_{i}",
            help=f"Percentual de {ativo} na pool neste range"
        )
    
    if preco > 0:
        novos_ranges[str(preco)] = perc

st.subheader("📌 Preço atual de mercado")

# Inicializar session state para preço atual
if f"preco_atual_{ativo}" not in st.session_state:
    st.session_state[f"preco_atual_{ativo}"] = data.get("preco_mercado", 0.0)

col1, col2 = st.columns([2, 1])

with col1:
    preco_atual = st.number_input(
        f"Preço atual de mercado ({ativo})", 
        value=st.session_state[f"preco_atual_{ativo}"], 
        format="%.2f",
        key=f"input_preco_{ativo}"
    )
    # Atualizar session state quando input muda
    st.session_state[f"preco_atual_{ativo}"] = preco_atual

with col2:
    if st.button("🔄 Atualizar preço", key=f"btn_atualizar_{ativo}"):
        with st.spinner("Buscando preço..."):
            novo_preco = buscar_preco_mercado(ativo)
            if novo_preco:
                st.session_state[f"preco_atual_{ativo}"] = float(novo_preco)
                st.success(f"✅ Preço atualizado: ${novo_preco:.2f}")
                st.rerun()
            else:
                st.error("❌ Erro ao buscar preço. Verifique se o alerta cripto está rodando.")
                
# Mostrar preços disponíveis do cache de alertas
if os.path.exists("precos_cache.json"):
    precos_disponiveis = buscar_preco_do_cache_alertas()
    if precos_disponiveis:
        st.info(f"💡 **Preços do sistema de alertas:** BTC: ${precos_disponiveis.get('BTC', 'N/A'):.2f} | ETH: ${precos_disponiveis.get('ETH', 'N/A'):.2f} | SOL: ${precos_disponiveis.get('SOL', 'N/A'):.2f}")
        
        # Botão para usar preço do cache
        if ativo in precos_disponiveis:
            if st.button(f"📋 Usar preço do alerta cripto (${precos_disponiveis[ativo]:.2f})", key=f"btn_cache_{ativo}"):
                st.session_state[f"preco_atual_{ativo}"] = float(precos_disponiveis[ativo])
                st.success(f"✅ Preço importado do sistema de alertas!")
                st.rerun()

# Usar o preço do session state
preco_atual = st.session_state[f"preco_atual_{ativo}"]

# Calcular estratégia atual
if preco_atual > 0 and novos_ranges:
    perc_ativo_sug = obter_percentual_por_range(preco_atual, novos_ranges)
    perc_usdc_sug = 100 - perc_ativo_sug

    st.success(
        f"✅ **Estratégia Atual**: {perc_ativo_sug:.1f}% {ativo} e "
        f"{perc_usdc_sug:.1f}% USDC (Preço: ${preco_atual:.2f})"
    )

    st.header("📊 Sugestão de Nova Alocação (%) e USD")
    valor_ativo_sugerido = total * perc_ativo_sug / 100
    valor_usdc_sugerido = total * perc_usdc_sug / 100
    
    df_alocacao = pd.DataFrame({
        "Ativo": [ativo, "USDC", "TOTAL"],
        "% Alocação": [f"{perc_ativo_sug:.1f}%", f"{perc_usdc_sug:.1f}%", "100.0%"],
        "USD Sugerido": [f"${valor_ativo_sugerido:.2f}", f"${valor_usdc_sugerido:.2f}", f"${total:.2f}"],
        "USD Atual": [f"${saldo1:.2f}", f"${saldo2:.2f}", f"${total:.2f}"]
    })
    
    st.dataframe(df_alocacao, hide_index=True)
    
    # Mostrar diferença para rebalanceamento
    diff_ativo = valor_ativo_sugerido - saldo1
    diff_usdc = valor_usdc_sugerido - saldo2
    
    if abs(diff_ativo) > 10:  # Só mostra se diferença > $10
        if diff_ativo > 0:
            st.info(f"📈 **Ação sugerida**: Comprar ${diff_ativo:.2f} em {ativo}")
        else:
            st.info(f"📉 **Ação sugerida**: Vender ${abs(diff_ativo):.2f} em {ativo}")
else:
    st.warning("⚠️ Configure os ranges e preço atual para ver a estratégia.")

# Sempre salvar os dados
all_data[ativo] = {
    "saldo1": saldo1,
    "saldo2": saldo2,
    "ranges": novos_ranges,
    "preco_mercado": preco_atual
}
salvar_dados_portfolio(all_data)

# Mostrar ranges configurados
if novos_ranges:
    st.subheader("📋 Ranges Configurados")
    ranges_df = pd.DataFrame([
        {"Preço": f"${float(k):.2f}", "% Ativo": f"{v:.1f}%", "% USDC": f"{100-v:.1f}%"} 
        for k, v in sorted(novos_ranges.items(), key=lambda x: float(x[0]), reverse=True)
    ])
    st.dataframe(ranges_df, hide_index=True)

# Status da última atualização
st.sidebar.markdown("### 📊 Status")
st.sidebar.info(f"💰 Portfolio: ${total:.2f}")
st.sidebar.info(f"📈 {ativo}: ${preco_atual:.2f}")
if novos_ranges:
    perc_atual = obter_percentual_por_range(preco_atual, novos_ranges) if preco_atual > 0 else 0
    st.sidebar.info(f"🎯 Estratégia: {perc_atual:.1f}% {ativo}")
