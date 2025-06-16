import streamlit as st
import requests
import time
import json
import os

# Configurações
api_key_whatsapp = "6039606"
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
    dados_cache = {
        "timestamp": time.time(),
        "dados": dados
    }
    with open(ARQUIVO_CACHE, "w") as f:
        json.dump(dados_cache, f)

def carregar_cache():
    if os.path.exists(ARQUIVO_CACHE):
        with open(ARQUIVO_CACHE, "r") as f:
            cache = json.load(f)
            return cache.get("dados", []), cache.get("timestamp", 0)
    return [], 0

def enviar_mensagem(mensagem):
    if not mensagem.strip():
        return False
    url = "https://api.callmebot.com/whatsapp.php"
    params = {"phone": numero_celular, "text": mensagem, "apikey": api_key_whatsapp}
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200 and "queued" in r.text.lower():
            print("✅ Enviada:", mensagem)
            return True
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")
    return False

def buscar_dados_coingecko():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        ids = ",".join(mapa_ids.values())
        params = {"ids": ids, "vs_currencies": "usd"}
        
        r = requests.get(url, params=params, timeout=15)
        
        if r.status_code == 200:
            preco_raw = r.json()
            dados = []
            
            for simbolo, cg_id in mapa_ids.items():
                if cg_id in preco_raw and "usd" in preco_raw[cg_id]:
                    preco = preco_raw[cg_id]["usd"]
                    dados.append({"symbol": simbolo, "price": preco})
            
            salvar_cache(dados)
            return dados, True
        else:
            st.warning(f"⚠️ CoinGecko API status {r.status_code}. Usando dados em cache.")
            dados_cache, _ = carregar_cache()
            return dados_cache, False
            
    except Exception as e:
        st.warning(f"⚠️ Erro ao conectar à CoinGecko: {e}. Usando dados em cache.")
        dados_cache, _ = carregar_cache()
        return dados_cache, False

def verificar_necessidade_atualizacao():
    """Verifica se precisa atualizar os dados (5 minutos = 300 segundos)"""
    _, timestamp_cache = carregar_cache()
    return time.time() - timestamp_cache > 300

def calcular_tempo_restante():
    """Calcula tempo restante para próxima atualização"""
    _, timestamp_cache = carregar_cache()
    tempo_passado = time.time() - timestamp_cache
    tempo_restante = max(0, 300 - tempo_passado)
    return int(tempo_restante)

# Configuração da página
st.set_page_config(page_title="Alerta Cripto - CoinGecko", layout="wide")
st.title("📊 Alerta Cripto (CoinGecko Free) — Atualização a cada 5 minutos")

# Inicializar session state
if "ultima_atualizacao" not in st.session_state:
    st.session_state.ultima_atualizacao = 0
if "enviadas" not in st.session_state:
    st.session_state.enviadas = set()
if "dados_atuais" not in st.session_state:
    st.session_state.dados_atuais = []
if "api_funcionando" not in st.session_state:
    st.session_state.api_funcionando = True

# Carregar zonas
zonas = carregar_zonas()

# Botões de controle principais
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([2, 1, 1, 1])

with col_btn1:
    if st.button("🔄 Atualizar Preços Agora", type="primary", use_container_width=True):
        with st.spinner("Buscando preços na CoinGecko..."):
            dados, api_ok = buscar_dados_coingecko()
            st.session_state.dados_atuais = dados
            st.session_state.ultima_atualizacao = time.time()
            st.session_state.api_funcionando = api_ok
            if api_ok:
                st.success("✅ Preços atualizados com sucesso!")
            else:
                st.warning("⚠️ Usando dados em cache")
            time.sleep(1)
            st.rerun()

with col_btn2:
    if st.button("🗑️ Limpar Alertas", use_container_width=True):
        st.session_state.enviadas.clear()
        st.success("✅ Histórico limpo!")

with col_btn3:
    tempo_restante = calcular_tempo_restante()
    if tempo_restante > 0:
        st.info(f"⏱️ Próxima: {tempo_restante//60}:{tempo_restante%60:02d}")
    else:
        st.info("⏱️ Atualizando...")

with col_btn4:
    # Status da API
    if st.session_state.api_funcionando:
        st.success("🟢 Online")
    else:
        st.error("🔴 Cache")

# Verificação automática a cada 5 minutos
if verificar_necessidade_atualizacao():
    with st.spinner("Atualizando automaticamente..."):
        dados, api_ok = buscar_dados_coingecko()
        st.session_state.dados_atuais = dados
        st.session_state.ultima_atualizacao = time.time()
        st.session_state.api_funcionando = api_ok
        if api_ok and dados:
            st.success("🔄 Atualização automática realizada!")

# Se não tem dados, carregar do cache
if not st.session_state.dados_atuais:
    dados_cache, timestamp_cache = carregar_cache()
    st.session_state.dados_atuais = dados_cache
    st.session_state.ultima_atualizacao = timestamp_cache

# Mostrar última atualização
if st.session_state.ultima_atualizacao > 0:
    tempo_atualizacao = time.strftime("%d/%m %H:%M:%S", time.localtime(st.session_state.ultima_atualizacao))
    st.caption(f"🕒 Última atualização: {tempo_atualizacao}")

# Configuração das zonas
with st.expander("⚙️ Configurar Zonas de Suporte e Resistência"):
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.subheader("💚 Suporte")
        for ativo in zonas:
            nome_limpo = ativo.replace("USDT", "")
            zonas[ativo]["suporte"] = st.number_input(
                f"{nome_limpo}", 
                value=float(zonas[ativo]["suporte"]), 
                key=f"{ativo}_suporte",
                format="%.2f"
            )
    
    with col2:
        st.subheader("🔴 Resistência")
        for ativo in zonas:
            nome_limpo = ativo.replace("USDT", "")
            zonas[ativo]["resistencia"] = st.number_input(
                f"{nome_limpo}", 
                value=float(zonas[ativo]["resistencia"]), 
                key=f"{ativo}_resistencia",
                format="%.2f"
            )
    
    with col3:
        st.subheader("🔧 Ações")
        if st.button("💾 Salvar Configurações", use_container_width=True):
            salvar_zonas(zonas)
            st.success("✅ Zonas salvas!")
        
        if st.button("🔄 Restaurar Padrão", use_container_width=True):
            zonas_padrao = {
                "BTCUSDT": {"suporte": 103000, "resistencia": 109000},
                "ETHUSDT": {"suporte": 2500, "resistencia": 2700},
                "SOLUSDT": {"suporte": 144, "resistencia": 155}
            }
            salvar_zonas(zonas_padrao)
            st.success("✅ Restaurado!")
            time.sleep(1)
            st.rerun()

# Análise dos preços
st.subheader("📈 Monitoramento em Tempo Real")

if not st.session_state.dados_atuais:
    st.warning("⚠️ Nenhum dado disponível. Clique em 'Atualizar Preços Agora'.")
else:
    # Criar cards para cada crypto
    for item in st.session_state.dados_atuais:
        simbolo = item["symbol"]
        if simbolo in zonas:
            preco = float(item["price"])
            suporte = zonas[simbolo]["suporte"]
            resistencia = zonas[simbolo]["resistencia"]
            nome_limpo = simbolo.replace("USDT", "")
            
            # Calcular percentuais
            distancia_suporte = ((preco - suporte) / suporte) * 100
            distancia_resistencia = ((resistencia - preco) / preco) * 100
            
            # Determinar status e cor
            if preco > resistencia:
                status = "🚀 ROMPEU RESISTÊNCIA"
                cor = "success"
                emoji_status = "🟢"
                # Verificar se deve enviar alerta
                if (simbolo, "alta") not in st.session_state.enviadas:
                    msg = f"🚨 [{nome_limpo}] ROMPEU A RESISTÊNCIA!\n💰 Preço: ${preco:,.2f}\n🎯 Resistência: ${resistencia:,.2f}\n📈 +{distancia_suporte:.1f}% do suporte\n⏰ {time.strftime('%H:%M:%S')}"
                    if enviar_mensagem(msg):
                        st.session_state.enviadas.add((simbolo, "alta"))
                        st.balloons()
            
            elif preco < suporte:
                status = "📉 PERDEU SUPORTE"
                cor = "error"
                emoji_status = "🔴"
                # Verificar se deve enviar alerta
                if (simbolo, "baixa") not in st.session_state.enviadas:
                    msg = f"⚠️ [{nome_limpo}] PERDEU O SUPORTE!\n💰 Preço: ${preco:,.2f}\n🎯 Suporte: ${suporte:,.2f}\n📉 {distancia_suporte:.1f}% abaixo\n⏰ {time.strftime('%H:%M:%S')}"
                    if enviar_mensagem(msg):
                        st.session_state.enviadas.add((simbolo, "baixa"))
            
            else:
                status = "⚖️ DENTRO DA ZONA"
                cor = "info"
                emoji_status = "🟡"
                # Limpar alertas quando volta para a zona
                st.session_state.enviadas.discard((simbolo, "alta"))
                st.session_state.enviadas.discard((simbolo, "baixa"))
            
            # Card visual para cada crypto
            with st.container():
                st.markdown(f"### {emoji_status} {nome_limpo} - {status}")
                
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.metric(
                        label="💰 Preço Atual",
                        value=f"${preco:,.2f}",
                        delta=f"{distancia_suporte:+.1f}% do suporte"
                    )
                
                with col2:
                    st.metric(
                        label="💚 Suporte",
                        value=f"${suporte:,.2f}",
                        delta=f"{abs(distancia_suporte):.1f}%" if preco >= suporte else f"-{abs(distancia_suporte):.1f}%"
                    )
                
                with col3:
                    st.metric(
                        label="🔴 Resistência", 
                        value=f"${resistencia:,.2f}",
                        delta=f"+{distancia_resistencia:.1f}%" if preco <= resistencia else f"Rompida!"
                    )
                
                with col4:
                    # Barra de progresso visual
                    if preco <= resistencia and preco >= suporte:
                        progresso = (preco - suporte) / (resistencia - suporte)
                        st.progress(progresso)
                        st.caption(f"📊 {progresso*100:.1f}% da zona")
                    elif preco > resistencia:
                        st.progress(1.0)
                        st.caption("🚀 Acima da zona")
                    else:
                        st.progress(0.0)
                        st.caption("📉 Abaixo da zona")
                
                # Status colorido
                if cor == "success":
                    st.success(f"✅ {status} - Alerta enviado!" if (simbolo, "alta") in st.session_state.enviadas else f"✅ {status}")
                elif cor == "error":
                    st.error(f"❌ {status} - Alerta enviado!" if (simbolo, "baixa") in st.session_state.enviadas else f"❌ {status}")
                else:
                    st.info(f"ℹ️ {status}")
                
                st.divider()

# Rodapé informativo
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.info("🔄 **Atualização:** A cada 5 minutos\n📱 **Alertas:** WhatsApp configurado")

with col2:
    st.info("🆓 **API:** CoinGecko (100% Gratuita)\n💾 **Cache:** Dados salvos localmente")

with col3:
    total_alertas = len(st.session_state.enviadas)
    st.info(f"📊 **Alertas Enviados:** {total_alertas}\n🎯 **Moedas:** {len(mapa_ids)} monitoradas")

# Auto-refresh a cada 30 segundos para atualizar o contador
time.sleep(1)
st.rerun()