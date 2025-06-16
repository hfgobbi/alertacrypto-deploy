import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Blog Olefoot", 
    layout="wide",
    page_icon="🚀"
)

# CSS moderno e elegante
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset e base */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
        min-height: 100vh;
    }
    
    .block-container {
        padding: 4rem 2rem;
        max-width: 900px;
        margin: 0 auto;
    }
    
    /* Header moderno */
    .header-container {
        text-align: center;
        margin-bottom: 4rem;
        padding: 2rem 0;
    }
    
    .logo-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        display: block;
        filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.3));
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .subtitle {
        font-size: 1.2rem;
        color: #a0a0a0;
        font-weight: 300;
        margin-bottom: 3rem;
    }
    
    /* Expander customizado moderno */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        margin: 2rem 0 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.3rem !important;
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .streamlit-expanderHeader::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        transform: translateY(-8px) !important;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        background: rgba(255, 255, 255, 0.08) !important;
    }
    
    .streamlit-expanderHeader:hover::before {
        opacity: 1;
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-top: none !important;
        border-radius: 0 0 20px 20px !important;
        padding: 2rem !important;
        margin-top: -1rem !important;
        color: #e0e0e0 !important;
        line-height: 1.7 !important;
    }
    
    /* Ícones dos posts */
    .post-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 12px;
        font-size: 2rem;
        margin-right: 1rem;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        vertical-align: middle;
    }
    
    /* Estilização do conteúdo dos posts */
    .streamlit-expanderContent h1, 
    .streamlit-expanderContent h2, 
    .streamlit-expanderContent h3 {
        color: #ffffff !important;
        margin: 2rem 0 1rem 0 !important;
        font-weight: 600 !important;
    }
    
    .streamlit-expanderContent h3 {
        font-size: 1.3rem !important;
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
    
    .streamlit-expanderContent strong {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    .streamlit-expanderContent ul, 
    .streamlit-expanderContent ol {
        margin: 1rem 0 !important;
        padding-left: 1.5rem !important;
    }
    
    .streamlit-expanderContent li {
        margin: 0.5rem 0 !important;
        color: #d0d0d0 !important;
    }
    
    .streamlit-expanderContent p {
        margin: 1rem 0 !important;
        color: #e0e0e0 !important;
    }
    
    /* Divisórias */
    .streamlit-expanderContent hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent) !important;
        margin: 2rem 0 !important;
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 4px;
    }
    
    /* Ocultar elementos do Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Animação para quando expander abre */
    .streamlit-expanderContent {
        animation: slideDown 0.3s ease-out;
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('''
<div class="header-container">
    <span class="logo-icon">📚</span>
    <h1 class="main-title">Blog Olefoot</h1>
    <p class="subtitle">Estratégias avançadas em DeFi e Pools de Liquidez</p>
</div>
''', unsafe_allow_html=True)

# Lista de posts
posts = [
    {
        "emoji": "🔟",
        "title": "Como escolher a melhor pool de liquidez – 10 critérios essenciais",
        "content": """
**1. Objetivo financeiro**  
Defina se quer segurança, rendimento passivo ou retorno agressivo.

**2. Risco de impermanent loss**  
Evite pares com alta volatilidade relativa (ex: ETH/PEPE) se não for trader.

**3. Tipo de ativo**  
Pools com stablecoins (ex: USDC/DAI) são mais seguros; pares voláteis têm mais risco e potencial.

**4. Recompensas e farming**  
Prefira pools com incentivo adicional em tokens (APR mais alto).

**5. Volume e liquidez da pool**  
Pools com alto volume têm menos slippage e mais recompensas por taxa.

**6. TVL (Total Value Locked)**  
Quanto maior o TVL, maior a confiança do mercado naquela pool.

**7. Plataforma (DEX)**  
Use DEXs auditadas e com boa reputação: Uniswap, Curve, Balancer, Velodrome.

**8. Rede blockchain**  
Avalie taxas da rede: Ethereum (caro), Arbitrum/Optimism (barato), BSC (rápido).

**9. Ferramentas de automação**  
Use gerenciadores como Gamma, Beefy, ou AutoFarm para auto-compounding e rebalanceamento.

**10. Tempo de exposição**  
Se o LP for curto prazo, foque em pools com menos volatilidade e mais liquidez imediata.
"""
    },
    {
        "emoji": "💧",
        "title": "DCA em Liquidez? Sim, dá! Veja como usar DCA em Pools DeFi",
        "content": """
📌 **O que é DCA?**  
Dollar-Cost Averaging (DCA) é uma estratégia onde você compra um ativo em partes iguais ao longo do tempo, reduzindo o impacto da volatilidade.

🔥 **Mas dá pra usar DCA em liquidity pools?**  
Sim — e pode ser poderoso!

### 🚀 Como aplicar DCA em pools de liquidez

1. **Escolha uma pool com fundamentos sólidos**  
Ex: ETH/USDC na Uniswap ou Curve. Priorize ativos que você já quer manter.

2. **Divida sua entrada em etapas**  
Ex: R$10.000 → R$2.000 por semana → menos risco de entrar no topo.

3. **Evite IL desnecessário**  
DCA suaviza o risco de impermanent loss ao longo do tempo.

4. **Automatize com bots ou scripts**  
Use DeFiSaver, Gelato, ou scripts próprios via API.

5. **Reinvista as recompensas**  
Combine com auto-compound para potencializar ganhos.

🎯 **Benefícios:**
- ✅ Menor exposição inicial ao IL  
- ✅ Reduz impacto da volatilidade  
- ✅ Boa estratégia para mercados incertos  
- ✅ Ideal para pools novas ou tokens voláteis

⚠️ **Dica final:**  
DCA não elimina riscos. Em Uniswap v3, ajuste as faixas a cada entrada.
"""
    },
    {
        "emoji": "⚖️",
        "title": "Altcoin com BTC ou USDC? Como se posicionar e lucrar com LPs",
        "content": """
🔁 **Opção 1: Altcoin + USDC**  
📈 Estratégia:
- Proteção contra queda
- Geração de yield constante
- Ideal para mercados laterais ou de baixa

💰 Como lucrar:
- Farming + recompensas
- Auto-compound
- Se a altcoin subir, você perde parte da valorização, mas recebe taxas

🎯 Perfil ideal: Investidor mais conservador

---

🔁 **Opção 2: Altcoin + BTC**  
📊 Estratégia:
- Aposta dupla em alta
- Ganhos se ambos subirem
- Mais risco e mais potencial

💰 Como lucrar:
- Ideal para bull market
- Recompensas de farming + valorização

🎯 Perfil ideal: Investidor agressivo

---

🧠 **Como se posicionar:**
1. Mercado lateral? Altcoin/USDC  
2. Mercado de alta? Altcoin/BTC  
3. Reduzir risco? Faça DCA  
4. Travar lucro? Retire parcial

💡 **Dica Ninja:**  
Combine ambas LPs:
- 70% altcoin/USDC (defesa)
- 30% altcoin/BTC (ataque)
"""
    }
]

# Exibir posts usando expanders nativos do Streamlit com design moderno
for post in posts:
    # Criar o título com ícone (sem HTML, apenas texto)
    titulo_com_icone = f'{post["emoji"]} {post["title"]}'
    
    with st.expander(titulo_com_icone, expanded=False):
        st.markdown(post["content"])