
import streamlit as st
import pandas as pd
import json
import os

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

def portfolio_inteligente():
    st.title("💡 Portfolio Inteligente - Pool de Liquidez Multiativo")

    ativo = st.sidebar.radio(
        "Selecione o ativo para análise:",
        ("BTC", "ETH", "SOL")
    )

    ativos_data = {
        "BTC": {
            "label": "BTC/USD",
            "saldo1_label": "BTC (USD)",
            "saldo2_label": "USDC (USD)",
            "saldo1_default": 1000.0,
            "saldo2_default": 1500.0,
            "ranges_default": {
                140000: 10,
                130000: 30,
                120000: 40,
                110000: 55,
                100000: 75,
                90000: 90
            }
        },
        "ETH": {
            "label": "ETH/USD",
            "saldo1_label": "ETH (USD)",
            "saldo2_label": "USDC (USD)",
            "saldo1_default": 6109.0,
            "saldo2_default": 0.0,
            "ranges_default": {
                4000: 30,
                3500: 30,
                3100: 40,
                2900: 55,
                2700: 75,
                2400: 100,
                2000: 100
            }
        },
        "SOL": {
            "label": "SOL/USD",
            "saldo1_label": "SOL (USD)",
            "saldo2_label": "USDC (USD)",
            "saldo1_default": 4999.0,
            "saldo2_default": 0.0,
            "ranges_default": {
                300: 40,
                260: 55,
                220: 75,
                200: 90,
                170: 100,
                140: 100,
                110: 100
            }
        }
    }

    all_data = carregar_dados_portfolio()
    data = all_data.get(ativo, {})
    data_cfg = ativos_data[ativo]

    st.header(f"Tabela 1 - Valor disponível na Pool [{data_cfg['label']}]")
    saldo1 = st.number_input(data_cfg['saldo1_label'], value=data.get("saldo1", data_cfg['saldo1_default']), min_value=0.0, format="%.2f", key=f"saldo1_{ativo}")
    saldo2 = st.number_input(data_cfg['saldo2_label'], value=data.get("saldo2", data_cfg['saldo2_default']), min_value=0.0, format="%.2f", key=f"saldo2_{ativo}")

    total = saldo1 + saldo2
    saldo1_perc = saldo1 / total * 100 if total else 0
    saldo2_perc = saldo2 / total * 100 if total else 0

    st.dataframe(pd.DataFrame({
        "POOL ATIVA": [ativo, "USDC", "TOTAL"],
        "VALOR $$$ DISPONÍVEL NA POOL": [saldo1, saldo2, total],
        "%": [saldo1_perc, saldo2_perc, 100]
    }), hide_index=True, use_container_width=True)

    st.header("Tabela 4 - Estratégia por Range de Preço")
    ranges = data.get("ranges", data_cfg["ranges_default"])
    new_ranges = {}
    for price in sorted(ranges.keys(), reverse=True):
        col1, col2 = st.columns([2,1])
        with col1:
            price_input = st.number_input(f"Preço {ativo}", key=f"preco_{ativo}_{price}", value=float(price))
        with col2:
            perc_input = st.number_input(f"% {ativo}", key=f"perc_{ativo}_{price}", value=float(ranges[price]))
        new_ranges[price_input] = perc_input

    range_selecionado = st.selectbox(f"Preço atual {ativo}", options=sorted(new_ranges.keys(), reverse=True))
    perc_ativo_sug = new_ranges[range_selecionado]
    perc_usdc_sug = 100 - perc_ativo_sug

    st.header("Tabela 2 - Próxima Estratégia Sugerida")
    st.dataframe(pd.DataFrame({
        "ALOCACAO ATUAL": [ativo, "USDC"],
        "PRÓXIMA ESTRATÉGIA (%)": [perc_ativo_sug, perc_usdc_sug]
    }), hide_index=True, use_container_width=True)

    st.header("Tabela 3 - Sugestão de Nova Alocação")
    st.markdown("> Valores calculados automaticamente com base no percentual de risco da Tabela 4.")
    st.dataframe(pd.DataFrame({
        "USD": [total*perc_ativo_sug/100, total*perc_usdc_sug/100, total],
        "%": [perc_ativo_sug, perc_usdc_sug, 100]
    }, index=[ativo, "USDC", "TOTAL"]), use_container_width=True)

    all_data[ativo] = {"saldo1": saldo1, "saldo2": saldo2, "ranges": new_ranges}
    salvar_dados_portfolio(all_data)

st.sidebar.title("Menu Principal")
menu = st.sidebar.selectbox("Navegação", ["Alerta Cripto", "Portfolio Inteligente"])

if menu == "Alerta Cripto":
    st.title("🚨 Alerta Cripto")
    st.info("Integrar seu sistema aqui.")
else:
    portfolio_inteligente()
