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
    for preco_range in sorted(ranges.keys(), reverse=True):
        if preco_atual >= preco_range:
            return ranges[preco_range]
    return list(ranges.values())[-1]

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

ativos_data = {
    "BTC": {"saldo1_default": 1000.0, "saldo2_default": 1500.0, "ranges_default": {140000: 10, 130000: 30, 120000: 40, 110000: 55, 100000: 75, 90000: 90}},
    "ETH": {"saldo1_default": 6109.0, "saldo2_default": 0.0, "ranges_default": {4000: 30, 3500: 30, 3100: 40, 2900: 55, 2700: 75, 2400: 100, 2000: 100}},
    "SOL": {"saldo1_default": 4999.0, "saldo2_default": 0.0, "ranges_default": {300: 40, 260: 55, 220: 75, 200: 90, 170: 100, 140: 100, 110: 100}}
}

all_data = carregar_dados_portfolio()
data = all_data.get(ativo, {})
data_cfg = ativos_data[ativo]

st.header(f"💰 Valor disponível na Pool [{ativo}/USD]")
saldo1 = st.number_input(f"{ativo} (USD)", value=data.get("saldo1", data_cfg['saldo1_default']), format="%.2f")
saldo2 = st.number_input("USDC (USD)", value=data.get("saldo2", data_cfg['saldo2_default']), format="%.2f")
total = saldo1 + saldo2

st.dataframe(pd.DataFrame({"Ativo": [ativo, "USDC", "TOTAL"], "USD": [saldo1, saldo2, total]}), hide_index=True)

st.header("🎯 Estratégia por Range de Preço")
ranges = data.get("ranges", data_cfg["ranges_default"])
novos_ranges = {}

for price in sorted(ranges.keys(), reverse=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        price_input = st.number_input(f"Preço do range para {ativo}", value=float(price), key=f"preco_{ativo}_{price}")
    with col2:
        perc_input = st.number_input(f"% {ativo}", value=float(ranges[price]), key=f"perc_{ativo}_{price}")
    novos_ranges[price_input] = perc_input


preco_mercado = data.get("preco_mercado")
if not preco_mercado:
    preco_mercado = sorted(novos_ranges.keys())[0]
st.subheader("📌 Preço atual de mercado")

col1, col2 = st.columns([2, 1])
with col2:
    if st.button("🔄 Atualizar preço"):
        preco_mercado = buscar_preco_mercado(ativo)
        if preco_mercado:
            preco_mercado = float(preco_mercado)
            st.success(f"Preço atualizado: ${preco_mercado}")
            all_data[ativo]["preco_mercado"] = preco_mercado
            salvar_dados_portfolio(all_data)

with col1:
    preco_atual = st.number_input(f"Preço atual de mercado ({ativo})", value=preco_mercado, format="%.2f")

perc_ativo_sug = obter_percentual_por_range(preco_atual, novos_ranges)
perc_usdc_sug = 100 - perc_ativo_sug

st.success(
    f"✅ Melhor estratégia atual para {ativo} é: {perc_ativo_sug}% {ativo} e "
    f"{perc_usdc_sug}% USDC (Preço atual: ${preco_atual:.2f})"
)

st.header("📊 Sugestão de Nova Alocação (%) e USD")
st.dataframe(pd.DataFrame({
    "Ativo": [ativo, "USDC", "TOTAL"],
    "% Alocação": [perc_ativo_sug, perc_usdc_sug, 100],
    "USD": [total * perc_ativo_sug / 100, total * perc_usdc_sug / 100, total]
}), hide_index=True)

all_data[ativo] = {
    "saldo1": saldo1,
    "saldo2": saldo2,
    "ranges": novos_ranges,
    "preco_mercado": preco_atual
}
salvar_dados_portfolio(all_data)
