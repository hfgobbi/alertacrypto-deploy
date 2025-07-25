import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import requests

DADOS_ATIVOS_PATH = "ativos_data.json"

def salvar_dados_ativos(dados):
    """Salva dados dos ativos no arquivo JSON"""
    with open(DADOS_ATIVOS_PATH, "w") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def carregar_dados_ativos():
    """Carrega dados dos ativos do arquivo JSON"""
    if os.path.exists(DADOS_ATIVOS_PATH):
        with open(DADOS_ATIVOS_PATH, "r") as f:
            return json.load(f)
    else:
        return {}

def calcular_dias_no_range(data_inicio):
    """Calcula quantos dias se passaram desde a data de início"""
    try:
        if isinstance(data_inicio, str):
            data_inicio_obj = datetime.strptime(data_inicio, "%d/%m/%Y")
        else:
            data_inicio_obj = data_inicio
        
        data_atual = datetime.now()
        diferenca = data_atual - data_inicio_obj
        return round(diferenca.days + diferenca.seconds / 86400, 2)
    except:
        return 0

def calcular_rentabilidade_total(liquidez_inicial, liquidez_final):
    """Calcula rentabilidade total em porcentagem"""
    if liquidez_inicial > 0:
        return round(((liquidez_final - liquidez_inicial) / liquidez_inicial) * 100, 2)
    return 0

def calcular_apr_excel(valor, liquidez_inicial, dias_no_range):
    """Calcula APR conforme Excel: (Valor/Liquidez) * 30 / Dias * 12"""
    if liquidez_inicial > 0 and dias_no_range > 0:
        rentabilidade_mensal = (valor / liquidez_inicial) * 30 / dias_no_range
        return round(rentabilidade_mensal * 12 * 100, 2)
    return 0

def calcular_rentabilidade_mensal_excel(valor, liquidez_inicial, dias_no_range):
    """Calcula Rentabilidade Mensal conforme Excel: (Valor/Liquidez) * 30 / Dias"""
    if liquidez_inicial > 0 and dias_no_range > 0:
        return round(((valor / liquidez_inicial) * 30 / dias_no_range) * 100, 2)
    return 0

def calcular_taxas_somente_apr(taxa_gerada, liquidez_inicial, dias_no_range):
    """Calcula APR apenas das taxas geradas"""
    if liquidez_inicial > 0 and dias_no_range > 0:
        rent_taxas = (taxa_gerada / liquidez_inicial) * 100
        return round((rent_taxas / dias_no_range) * 365, 2)
    return 0

def buscar_preco_do_cache_alertas():
    """Busca preços do cache do sistema de alertas"""
    try:
        if os.path.exists("precos_cache.json"):
            with open("precos_cache.json", "r") as f:
                cache_alertas = json.load(f)
                
            if isinstance(cache_alertas, dict) and "dados" in cache_alertas:
                dados = cache_alertas["dados"]
            else:
                dados = cache_alertas
                
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

# Interface principal
st.set_page_config(page_title="Análise de Ativos - Pool de Liquidez", page_icon="💰", layout="wide")
st.title("💰 Análise de Ativos - Pool de Liquidez")

# Carregar dados existentes
todos_dados = carregar_dados_ativos()

# Sidebar para adicionar novo ativo
st.sidebar.header("➕ Adicionar/Editar Ativo")

# Lista de ativos disponíveis
ativos_existentes = list(todos_dados.keys())
opcoes_ativos = ["Criar Novo"] + ativos_existentes

ativo_selecionado = st.sidebar.selectbox(
    "Selecionar Ativo:",
    opcoes_ativos,
    key="select_ativo"
)

# Formulário para criar/editar ativo
with st.sidebar.form("form_ativo"):
    if ativo_selecionado == "Criar Novo":
        nome_ativo = st.text_input("Nome do Ativo (ex: SOL/USDC):", key="nome_ativo")
        dados_ativo = {}
    else:
        nome_ativo = ativo_selecionado
        dados_ativo = todos_dados.get(ativo_selecionado, {})
    
    st.subheader("📅 Dados Iniciais")
    data_inicio = st.date_input(
        "Data de Início:",
        value=datetime.strptime(dados_ativo.get("data_inicio", datetime.now().strftime("%d/%m/%Y")), "%d/%m/%Y").date() if dados_ativo.get("data_inicio") else datetime.now().date(),
        key="data_inicio"
    )
    
    hora_inicio = st.time_input(
        "Hora de Início:",
        value=datetime.strptime(dados_ativo.get("hora_inicio", "09:00"), "%H:%M").time() if dados_ativo.get("hora_inicio") else datetime.now().time(),
        key="hora_inicio"
    )
    
    st.subheader("🪙 Tokens")
    col1, col2 = st.columns(2)
    with col1:
        token_a = st.text_input("Token A:", value=dados_ativo.get("token_a", "SOL"), key="token_a")
        quantidade_a = st.number_input("Quantidade Token A:", value=dados_ativo.get("quantidade_a", 0.0), format="%.4f", key="qtd_a")
        usd_a = st.number_input("Valor USD Token A:", value=dados_ativo.get("usd_a", 0.0), format="%.2f", key="usd_a")
    
    with col2:
        token_b = st.text_input("Token B:", value=dados_ativo.get("token_b", "USDC"), key="token_b")
        quantidade_b = st.number_input("Quantidade Token B:", value=dados_ativo.get("quantidade_b", 0.0), format="%.4f", key="qtd_b")
        usd_b = st.number_input("Valor USD Token B:", value=dados_ativo.get("usd_b", 0.0), format="%.2f", key="usd_b")
    
    st.subheader("💰 Liquidez")
    liquidez_inicial = st.number_input("Liquidez Inicial (USD):", value=dados_ativo.get("liquidez_inicial", 0.0), format="%.2f", key="liq_inicial")
    liquidez_final = st.number_input("Liquidez Final (USD):", value=dados_ativo.get("liquidez_final", 0.0), format="%.2f", key="liq_final")
    taxa_gerada = st.number_input("Taxa Gerada (USD):", value=dados_ativo.get("taxa_gerada", 0.0), format="%.2f", key="taxa_gerada")
    
    # Calcular valores em tempo real para exibir
    if liquidez_inicial > 0 and liquidez_final > 0:
        impermanent_loss_calc = liquidez_final - liquidez_inicial
        lucro_prejuizo_calc = (liquidez_final + taxa_gerada) - liquidez_inicial
        valor_total_atual = liquidez_final + taxa_gerada
        rent_total_calc = calcular_rentabilidade_total(liquidez_inicial, valor_total_atual)
        
        # Mostrar cálculo da composição também
        total_a = quantidade_a * usd_a
        total_b = quantidade_b * usd_b
        
        st.info(f"📊 **Cálculo Automático**: Impermanent Loss: ${impermanent_loss_calc:.2f} | Lucro/Prejuízo: ${lucro_prejuizo_calc:.2f} | Rentabilidade: {rent_total_calc:.2f}%")
        st.info(f"🪙 **Composição**: {token_a}: ${total_a:.2f} | {token_b}: ${total_b:.2f} | Total: ${total_a + total_b:.2f}")
    
    st.subheader("📊 Range de Preço")
    range_inicio = st.number_input("Range Início:", value=dados_ativo.get("range_inicio", 0.0), format="%.2f", key="range_inicio")
    range_fim = st.number_input("Range Fim:", value=dados_ativo.get("range_fim", 0.0), format="%.2f", key="range_fim")
    
    # Botão de salvar
    salvar_ativo = st.form_submit_button("💾 Salvar Ativo", use_container_width=True, type="primary")

# BOTÃO DE EXCLUSÃO - VISÍVEL E FUNCIONAL
if ativo_selecionado != "Criar Novo":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🗑️ Excluir Ativo")
    
    # Usar session_state para controlar o estado
    if "mostrar_confirmacao" not in st.session_state:
        st.session_state.mostrar_confirmacao = False
    
    if not st.session_state.mostrar_confirmacao:
        # Botão principal de exclusão
        if st.sidebar.button(
            f"🗑️ EXCLUIR {ativo_selecionado}", 
            key="btn_excluir_principal",
            use_container_width=True,
            type="secondary"
        ):
            st.session_state.mostrar_confirmacao = True
            st.rerun()
    
    else:
        # Mostrar confirmação
        st.sidebar.error(f"⚠️ CONFIRMAR EXCLUSÃO DE '{ativo_selecionado}'?")
        
        # Botões de confirmação em colunas
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.sidebar.button("✅ SIM", key="confirmar_sim", type="primary", use_container_width=True):
                # Executar exclusão
                if ativo_selecionado in todos_dados:
                    del todos_dados[ativo_selecionado]
                    salvar_dados_ativos(todos_dados)
                    st.session_state.mostrar_confirmacao = False
                    st.sidebar.success(f"✅ {ativo_selecionado} foi excluído!")
                    st.rerun()
        
        with col2:
            if st.sidebar.button("❌ NÃO", key="cancelar_nao", use_container_width=True):
                st.session_state.mostrar_confirmacao = False
                st.rerun()

# Processar salvamento do formulário
if salvar_ativo and nome_ativo:
    # Calcular valores automaticamente
    data_inicio_str = data_inicio.strftime("%d/%m/%Y")
    hora_inicio_str = hora_inicio.strftime("%H:%M")
    timestamp = f"{data_inicio_str} {hora_inicio_str}"
    
    # Garantir que liquidez_inicial seja calculada se não foi inserida
    if liquidez_inicial == 0:
        liquidez_inicial = usd_a + usd_b
    
    dias_no_range = calcular_dias_no_range(data_inicio_str)
    
    # FÓRMULAS CORRETAS:
    # Impermanent Loss = liquidez final - liquidez inicial
    impermanent_loss = liquidez_final - liquidez_inicial
    
    # Lucro/Prejuízo = (liquidez final + taxa gerada) - liquidez inicial
    lucro_prejuizo = (liquidez_final + taxa_gerada) - liquidez_inicial
    
    # Calcular rentabilidade total (incluindo taxas)
    valor_total_atual = liquidez_final + taxa_gerada
    rentabilidade_total = calcular_rentabilidade_total(liquidez_inicial, valor_total_atual)
    
    # Calcular APRs conforme Excel
    apr_total = calcular_apr_excel(lucro_prejuizo, liquidez_inicial, dias_no_range)
    taxas_somente_apr = calcular_apr_excel(taxa_gerada, liquidez_inicial, dias_no_range)
    
    # Calcular rentabilidades mensais conforme Excel
    rent_mensal_total = calcular_rentabilidade_mensal_excel(lucro_prejuizo, liquidez_inicial, dias_no_range)
    rent_mensal_taxas = calcular_rentabilidade_mensal_excel(taxa_gerada, liquidez_inicial, dias_no_range)
    
    # Calcular proporções CORRETAS baseadas no total USD de cada token
    total_usd_token_a = quantidade_a * usd_a  # Quantidade × Valor USD
    total_usd_token_b = quantidade_b * usd_b  # Quantidade × Valor USD
    total_usd_geral = total_usd_token_a + total_usd_token_b
    
    proporcao_a = f"{(total_usd_token_a / total_usd_geral * 100):.2f}%" if total_usd_geral > 0 else "0%"
    proporcao_b = f"{(total_usd_token_b / total_usd_geral * 100):.2f}%" if total_usd_geral > 0 else "0%"
    
    # Salvar dados
    novo_ativo = {
        "data_inicio": data_inicio_str,
        "hora_inicio": hora_inicio_str,
        "timestamp": timestamp,
        "dias_no_range": dias_no_range,
        "token_a": token_a,
        "token_b": token_b,
        "quantidade_a": quantidade_a,
        "usd_a": usd_a,
        "total_usd_token_a": total_usd_token_a,
        "usd_b": usd_b,
        "total_usd_token_b": total_usd_token_b,
        "proporcao_a": proporcao_a,
        "quantidade_b": quantidade_b,
        "proporcao_b": proporcao_b,
        "liquidez_inicial": liquidez_inicial,
        "liquidez_final": liquidez_final,
        "taxa_gerada": taxa_gerada,
        "lucro_prejuizo": lucro_prejuizo,
        "impermanent_loss": impermanent_loss,
        "rentabilidade_total": f"{rentabilidade_total:.2f}%",
        "apr_total": f"{apr_total:.2f}%",
        "taxas_somente": f"{taxas_somente_apr:.2f}%",
        "rent_mensal_total": f"{rent_mensal_total:.2f}%",
        "rent_mensal_taxas": f"{rent_mensal_taxas:.2f}%",
        "range_inicio": range_inicio,
        "range_fim": range_fim,
        "ultima_atualizacao": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    
    todos_dados[nome_ativo] = novo_ativo
    salvar_dados_ativos(todos_dados)
    st.sidebar.success(f"✅ Ativo '{nome_ativo}' salvo com sucesso!")
    st.rerun()

# Exibir ativos existentes
if todos_dados:
    st.header("📊 Análise dos Ativos")
    
    # Criar abas para cada ativo
    abas = st.tabs(list(todos_dados.keys()))
    
    for i, (nome_ativo, dados) in enumerate(todos_dados.items()):
        with abas[i]:
            # Recalcular dados em tempo real
            dias_atuais = calcular_dias_no_range(dados["data_inicio"])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("📅 Informações Iniciais")
                st.metric("Data de Início", dados["data_inicio"])
                st.metric("Hora de Início", dados["hora_inicio"])
                st.metric("Dias no Range", f"{dias_atuais:.2f} dias")
                st.metric("Token A", dados["token_a"])
                st.metric("Token B", dados["token_b"])
                st.metric("Range de Preço", f"${dados['range_inicio']:.2f} - ${dados['range_fim']:.2f}")
            
            with col2:
                st.subheader("💰 Valores Financeiros")
                st.metric("Liquidez Inicial", f"${dados['liquidez_inicial']:.2f}")
                st.metric("Liquidez Final", f"${dados['liquidez_final']:.2f}")
                st.metric("Taxa Gerada", f"${dados['taxa_gerada']:.2f}")
                
                # FÓRMULAS CORRETAS:
                # Lucro/Prejuízo = (liquidez final + taxa gerada) - liquidez inicial
                lucro_prejuizo_atual = (dados['liquidez_final'] + dados['taxa_gerada']) - dados['liquidez_inicial']
                st.metric("Lucro/Prejuízo", f"${lucro_prejuizo_atual:.2f}")
                
                # Impermanent Loss = liquidez final - liquidez inicial
                impermanent_loss = dados['liquidez_final'] - dados['liquidez_inicial']
                st.metric("Impermanent Loss", f"${impermanent_loss:.2f}")
            
            with col3:
                st.subheader("📈 Rentabilidade")
                
                # Recalcular rentabilidades com fórmulas corretas do Excel
                valor_total_atual = dados['liquidez_final'] + dados['taxa_gerada']
                rent_total_atual = calcular_rentabilidade_total(dados['liquidez_inicial'], valor_total_atual)
                lucro_prejuizo_atual = (dados['liquidez_final'] + dados['taxa_gerada']) - dados['liquidez_inicial']
                
                apr_atual = calcular_apr_excel(lucro_prejuizo_atual, dados['liquidez_inicial'], dias_atuais)
                taxas_apr_atual = calcular_apr_excel(dados['taxa_gerada'], dados['liquidez_inicial'], dias_atuais)
                rent_mensal_atual = calcular_rentabilidade_mensal_excel(lucro_prejuizo_atual, dados['liquidez_inicial'], dias_atuais)
                rent_mensal_taxas_atual = calcular_rentabilidade_mensal_excel(dados['taxa_gerada'], dados['liquidez_inicial'], dias_atuais)
                
                st.metric("Rentabilidade Total", f"{rent_total_atual:.2f}%")
                st.metric("APR Total", f"{apr_atual:.2f}%")
                st.metric("APR Taxas Somente", f"{taxas_apr_atual:.2f}%")
                st.metric("Rent. Mensal Total", f"{rent_mensal_atual:.2f}%")
                st.metric("Rent. Mensal Taxas", f"{rent_mensal_taxas_atual:.2f}%")
            
            # Tabela resumo como na planilha Excel
            st.subheader("📋 Resumo Completo (Formato Planilha)")
            
            # Dados básicos
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📅 DADOS BÁSICOS**")
                dados_basicos = pd.DataFrame({
                    "Item": ["Data", "Hora", "Timestamp", "Dias no Range"],
                    "Valor": [dados["data_inicio"], dados["hora_inicio"], dados["timestamp"], f"{dias_atuais:.2f} dias"]
                })
                st.dataframe(dados_basicos, hide_index=True, use_container_width=True)
            
            with col2:
                st.markdown("**🪙 COMPOSIÇÃO**")
                
                # Calcular totais USD corretos para cada token
                total_usd_a = dados['quantidade_a'] * dados.get('usd_a', 0)
                total_usd_b = dados['quantidade_b'] * dados.get('usd_b', 0)
                
                composicao_df = pd.DataFrame({
                    "Token": [dados["token_a"], dados["token_b"]],
                    "Quantidade": [f"{dados['quantidade_a']:.4f}", f"{dados['quantidade_b']:.4f}"],
                    "Valor USD Unitário": [f"${dados.get('usd_a', 0):.2f}", f"${dados.get('usd_b', 0):.2f}"],
                    "Total USD": [f"${total_usd_a:.2f}", f"${total_usd_b:.2f}"],
                    "Proporção": [dados["proporcao_a"], dados["proporcao_b"]]
                })
                st.dataframe(composicao_df, hide_index=True, use_container_width=True)
            
            # Tabela principal de análise
            st.markdown("**💰 ANÁLISE FINANCEIRA COMPLETA**")
            
            # Recalcular todos os valores com as fórmulas corretas do Excel
            valor_total_atual = dados['liquidez_final'] + dados['taxa_gerada']
            rent_total_atual = calcular_rentabilidade_total(dados['liquidez_inicial'], valor_total_atual)
            lucro_prejuizo_atual = (dados['liquidez_final'] + dados['taxa_gerada']) - dados['liquidez_inicial']
            
            apr_atual = calcular_apr_excel(lucro_prejuizo_atual, dados['liquidez_inicial'], dias_atuais)
            taxas_apr_atual = calcular_apr_excel(dados['taxa_gerada'], dados['liquidez_inicial'], dias_atuais)
            rent_mensal_atual = calcular_rentabilidade_mensal_excel(lucro_prejuizo_atual, dados['liquidez_inicial'], dias_atuais)
            rent_mensal_taxas_atual = calcular_rentabilidade_mensal_excel(dados['taxa_gerada'], dados['liquidez_inicial'], dias_atuais)
            
            # FÓRMULAS CORRETAS:
            impermanent_loss = dados['liquidez_final'] - dados['liquidez_inicial']
            
            analise_completa = pd.DataFrame({
                "Métrica": [
                    "Liquidez Inicial",
                    "Liquidez Final", 
                    "Taxa Gerada",
                    "Impermanent Loss",
                    "Lucro/Prejuízo Total",
                    "Rentabilidade Total",
                    "APR Total",
                    "APR Taxas Somente",
                    "Rent. Mensal Total",
                    "Rent. Mensal Taxas",
                    "Range de Preço"
                ],
                "Valor": [
                    f"${dados['liquidez_inicial']:.2f}",
                    f"${dados['liquidez_final']:.2f}",
                    f"${dados['taxa_gerada']:.2f}",
                    f"${impermanent_loss:.2f}",
                    f"${lucro_prejuizo_atual:.2f}",
                    f"{rent_total_atual:.2f}%",
                    f"{apr_atual:.2f}%",
                    f"{taxas_apr_atual:.2f}%",
                    f"{rent_mensal_atual:.2f}%",
                    f"{rent_mensal_taxas_atual:.2f}%",
                    f"${dados['range_inicio']:.2f} - ${dados['range_fim']:.2f}"
                ]
            })
            
            st.dataframe(analise_completa, hide_index=True, use_container_width=True)
            
            # Observações importantes
            st.subheader("📝 Observações")
            st.warning(
                "🔄 **Impermanent Loss**: Lembre-se que quando o preço do ativo voltar ao range ideal, "
                "o lucro pode se tornar 100% novamente. O Impermanent Loss é temporário enquanto os ativos "
                "estão fora do range de preço configurado."
            )
            
            # Mostrar última atualização
            if "ultima_atualizacao" in dados:
                st.caption(f"📅 Última atualização: {dados['ultima_atualizacao']}")

else:
    st.info("👆 Use a barra lateral para adicionar seu primeiro ativo para análise!")

# Mostrar preços atuais do cache (se disponível)
if os.path.exists("precos_cache.json"):
    precos_disponiveis = buscar_preco_do_cache_alertas()
    if precos_disponiveis:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Preços Atuais")
        for ativo, preco in precos_disponiveis.items():
            st.sidebar.metric(ativo, f"${preco:.2f}")

# Status geral no sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("📈 Status Geral")
if todos_dados:
    total_investido = sum(ativo.get("liquidez_inicial", 0) for ativo in todos_dados.values())
    total_atual = sum(ativo.get("liquidez_final", 0) + ativo.get("taxa_gerada", 0) for ativo in todos_dados.values())
    total_taxas = sum(ativo.get("taxa_gerada", 0) for ativo in todos_dados.values())
    
    st.sidebar.metric("💰 Total Investido", f"${total_investido:.2f}")
    st.sidebar.metric("💵 Valor Atual", f"${total_atual:.2f}")
    st.sidebar.metric("🎯 Total em Taxas", f"${total_taxas:.2f}")
    
    if total_investido > 0:
        rentabilidade_geral = ((total_atual - total_investido) / total_investido) * 100
        st.sidebar.metric("📈 Rentabilidade Geral", f"{rentabilidade_geral:.2f}%")

st.sidebar.markdown("---")
st.sidebar.caption("💡 Sistema de Análise de Pool de Liquidez v2.0")