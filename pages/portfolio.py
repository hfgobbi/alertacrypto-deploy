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

def buscar_preco_mercado(ativo):
    ids = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana"}
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids[ativo]}&vs_currencies=usd"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()[ids[ativo]]["usd"]
    except:
        pass
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
preco_mercado = data.get("preco_mercado", 0.0)

col1, col2 = st.columns([2, 1])
with col1:
    preco_atual = st.number_input(f"Preço atual de mercado ({ativo})", value=preco_mercado, format="%.2f")

with col2:
    if st.button("🔄 Atualizar preço"):
        novo_preco = buscar_preco_mercado(ativo)
        if novo_preco:
            preco_atual = float(novo_preco)
            st.success(f"Preço atualizado: ${preco_atual}")
            st.rerun()

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