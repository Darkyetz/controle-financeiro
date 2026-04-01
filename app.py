import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from supabase import create_client
import random

# ================== CONFIG ==================
st.set_page_config(page_title="CB Financeiro | HermeX", layout="wide")

# ================== SUPABASE ==================
SUPABASE_URL = "COLE_SUA_URL_AQUI"
SUPABASE_KEY = "COLE_SUA_KEY_AQUI"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================== ANIMAÇÕES ==================
st.markdown("""
<style>

/* Fundo gradient */
.stApp {
    background: linear-gradient(180deg, #000000, #0d001a);
    color: white;
}

/* Corações */
.heart {
    position: fixed;
    top: -10px;
    color: #ff1493;
    font-size: 16px;
    animation: fall linear infinite;
}
@keyframes fall {
    to { transform: translateY(110vh); }
}

/* Logo com glow */
.logo {
    font-size: 80px;
    background: linear-gradient(#ff1493,#ff69b4);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    animation: glow 2s ease-in-out infinite alternate;
}
@keyframes glow {
    from { text-shadow: 0 0 10px #ff1493; }
    to { text-shadow: 0 0 25px #ff69b4; }
}

/* Cards */
.card {
    background:#0a0a0a;
    padding:25px;
    border-radius:20px;
    margin-bottom:20px;
    transition:0.3s;
    border:1px solid #1a1a1a;
}
.card:hover {
    transform: scale(1.03);
    box-shadow: 0 0 20px #ff1493;
}

/* Valores */
.value {
    font-size:30px;
    color:#ff1493;
    font-weight:bold;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0% {opacity:0.8;}
    50% {opacity:1;}
    100% {opacity:0.8;}
}

/* Botões */
.stButton>button {
    background:#ff1493;
    color:white;
    border-radius:10px;
    transition:0.3s;
}
.stButton>button:hover {
    transform:scale(1.05);
}

/* Inputs */
input, select {
    background:#111 !important;
    color:white !important;
}

/* Remove rodapé padrão */
footer {visibility:hidden;}

</style>
""", unsafe_allow_html=True)

# gerar corações
for i in range(20):
    st.markdown(f"""
    <div class="heart" style="
        left:{random.randint(0,100)}%;
        animation-duration:{random.randint(5,12)}s;
        opacity:{random.random()};
    ">❤️</div>
    """, unsafe_allow_html=True)

# ================== DATA ==================
hoje = datetime.now()
dia_atual = hoje.day
data_entrega = datetime(2029,4,30)
dias_restantes = (data_entrega - hoje).days

# ================== DADOS ==================
response = supabase.table("transacoes").select("*").execute()
df = pd.DataFrame(response.data) if response.data else pd.DataFrame()

# ================== HEADER ==================
col1,col2 = st.columns(2)

with col1:
    st.markdown('<div class="logo">CB</div>', unsafe_allow_html=True)
    st.write(f"📅 Hoje: {hoje.strftime('%d/%m/%Y')}")

with col2:
    st.markdown(f"""
    <div style='text-align:right'>
        <div style='font-size:38px;font-weight:800;'>{dias_restantes} dias</div>
        <div style='color:#ff69b4;'>para o nosso apê 🏠💖</div>
    </div>
    """, unsafe_allow_html=True)

# ================== MOTOR ==================
entrada = 0
saida = 0

for _, row in df.iterrows():
    inicio = pd.to_datetime(row['inicio']).date()
    fim = pd.to_datetime(row['fim']).date()

    ativo = inicio <= hoje.date() <= fim

    if row['tipo'] == 'Entrada':
        if ativo:
            entrada += float(row['valor'])
    else:
        if ativo and int(row['vencimento']) <= dia_atual:
            saida += float(row['valor'])

saldo = entrada - saida

# ================== DASH ==================
c1,c2,c3 = st.columns(3)

c1.markdown(f'<div class="card">Entradas<br><span class="value">R$ {entrada:.2f}</span></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card">Saídas<br><span class="value">R$ {saida:.2f}</span></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card">Saldo<br><span class="value">R$ {saldo:.2f}</span></div>', unsafe_allow_html=True)

# ================== FORM ==================
st.subheader("💖 Registrar momento financeiro")

c1,c2,c3,c4 = st.columns([1,2,1,1])

tipo = c1.radio("Tipo", ["Entrada","Saída"])
nome = c2.text_input("Descrição")
categoria = c3.selectbox("Categoria", ["Fixo","Outros","Lazer","Apartamento"])
valor = c4.number_input("Valor", min_value=0.0)

quem = c1.selectbox("Quem", ["Cauã","Beca","Ambos"])

if categoria == "Fixo":
    venc = st.number_input("Vencimento",1,31)
    inicio = st.date_input("Início")
    fim = st.date_input("Fim")
else:
    venc = dia_atual
    inicio = hoje
    fim = hoje

if st.button("Salvar 💕"):
    supabase.table("transacoes").insert({
        "data": hoje.strftime("%Y-%m-%d"),
        "tipo": tipo,
        "nome": nome,
        "categoria": categoria,
        "valor": float(valor),
        "vencimento": int(venc),
        "inicio": str(pd.to_datetime(inicio)),
        "fim": str(pd.to_datetime(fim)),
        "quem": quem
    }).execute()

    st.rerun()

# ================== META ==================
meta = 235000
total = df[df['tipo']=="Entrada"]['valor'].sum() if not df.empty else 0

st.subheader("🏠 Nosso sonho ganhando forma 💕")

progress = total/meta if meta > 0 else 0
st.progress(min(progress,1.0))

st.write(f"💰 Guardado: R$ {total:,.2f}")
st.write(f"🎯 Meta: R$ {meta:,.2f}")
st.write(f"📊 {progress*100:.1f}% concluído")

# ================== GRÁFICO ==================
if not df.empty:
    fig = px.bar(df, x='quem', y='valor', color='tipo')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    st.plotly_chart(fig, use_container_width=True)

# ================== FOOTER ==================
st.markdown("""
<div style="text-align:center;margin-top:50px;padding:20px;border-top:1px solid #111;">
<p style="color:#ff1493;font-size:18px;">Juntos construindo nosso futuro 💑✨</p>
<p style="color:#666;font-size:12px;">HERMEX SOLUTIONS © 2026</p>
</div>
""", unsafe_allow_html=True)
