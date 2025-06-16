
import streamlit as st

st.set_page_config(page_title="Blog Olefoot", layout="centered")
st.title("📚 Blog Olefoot – DeFi e Liquidez")

# Lista de posts prontos
posts = [
    {
        "title": "🔟 Como escolher a melhor pool de liquidez – 10 critérios essenciais",
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
        "title": "💧 DCA em Liquidez? Sim, dá! Veja como usar DCA em Pools DeFi",
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
        "title": "⚖️ Altcoin com BTC ou USDC? Como se posicionar e lucrar com LPs",
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

# Exibir posts com botões de expandir
for i, post in enumerate(posts):
    with st.expander(post["title"], expanded=False):
        st.markdown(post["content"])
