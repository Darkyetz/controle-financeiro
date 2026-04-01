import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from supabase import create_client
import random

# ================== CONFIG ==================
st.set_page_config(page_title="CB Financeiro | HermeX", layout="wide")

# ================== SUPABASE ==================
SUPABASE_URL = "https://dqckorlftspzadevawge.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRxY2tvcmxmdHNwemFkZXZhd2dlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUwNzMwNTksImV4cCI6MjA5MDY0OTA1OX0.OZz8Mt_oS4t57FxVmWsXsdhSg59Sb57B0V9BofQIrkQ"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================== ANIMAÇÕES ==================
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #0a0014, #000);
    color: white;
}

/* partículas */
.particle {
    position: fixed;
    width: 4px;
    height: 4px;
    background: #ff69b4;
    border-radius: 50%;
    animation: float 10s linear infinite;
}
@keyframes float {
    to { transform: translateY(-120vh); }
}

/* corações */
.heart {
    position: fixed;
    top: -10px;
    font-size: 16px;
    color: #ff1493;
    animation: fall linear infinite;
}
@keyframes fall {
    to { transform: translateY(110vh); }
}

/* dinheiro subindo */
.money {
    position: fixed;
    bottom: 0;
    color: #00ff88;
    font-size: 20px;
    animation: rise 2s ease-out;
}
@keyframes rise {
    to { transform: translateY(-200px); opacity:0; }
}

/* logo glow */
.logo {
    font-size: 80px;
    background: linear-gradient(#ff1493,#ff69b4);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    animation: glow 2s infinite alternate;
}
@keyframes glow {
    from { text-shadow:0 0 10px #ff1493; }
    to { text-shadow:0 0 30px #ff69b4; }
}

/* cards */
.card {
    background:#0a0a0a;
    padding:25px;
    border-radius:20px;
    transition:0.3s;
}
.card:hover {
    transform:scale(1.04);
    box-shadow:0 0 25px #ff1493;
}

.value {
    font-size:30px;
    color:#ff1493;
    font-weight:bold;
}

button {
    background:#ff1493 !important;
    color:white !important;
}
</style>
""", unsafe_allow_html=True)

# partículas
for _ in range(25):
    st.markdown(f"<div class='particle' style='left:{random.randint(0,100)}%; animation-duration:{random.randint(5,15)}s'></div>", unsafe_allow_html=True)

# corações
for _ in range(10):
    st.markdown(f"<div class='heart' style='left:{random.randint(0,100)}%; animation-duration:{random.randint(5,12)}s'>❤️</div>", unsafe_allow_html=True)

# ================== DATA ==================
hoje = datetime.now()
dia_atual = hoje.day
data_entrega = datetime(2029,4,30)
dias_restantes = (data_entrega - hoje).days

# ================== DADOS ==================
response = supabase.table("transacoes").select("*").execute()
df = pd.DataFrame(response.data) if response.data else pd.DataFrame()

# ================== HEADER ==================
c1,c2 = st.columns(2)

with c1:
    st.markdown('<div class="logo">CB</div>', unsafe_allow_html=True)
    st.write(f"📅 {hoje.strftime('%d/%m/%Y')}")

with c2:
    st.markdown(f"<h2 style='text-align:right'>{dias_restantes} dias 💕</h2>", unsafe_allow_html=True)

# ================== MOTOR ==================
entrada = 0
saida = 0

for _, row in df.iterrows():
    inicio = pd.to_datetime(row['inicio']).date()
    fim = pd.to_datetime(row['fim']).date()

    if inicio <= hoje.date() <= fim:
        if row['tipo'] == 'Entrada':
            entrada += float(row['valor'])
        else:
            if int(row['vencimento']) <= dia_atual:
                saida += float(row['valor'])

saldo = entrada - saida

# ================== DASH ==================
c1,c2,c3 = st.columns(3)

c1.markdown(f"<div class='card'>Entradas<br><span class='value'>R$ {entrada:.2f}</span></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='card'>Saídas<br><span class='value'>R$ {saida:.2f}</span></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='card'>Saldo<br><span class='value'>R$ {saldo:.2f}</span></div>", unsafe_allow_html=True)

# ================== FORM ==================
st.subheader("💖 Registrar")

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

if st.button("Salvar 💸"):
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

    # animação dinheiro
    for _ in range(5):
        st.markdown(f"<div class='money' style='left:{random.randint(10,90)}%'>💸</div>", unsafe_allow_html=True)

    st.success("Salvo com sucesso 💕")
    st.rerun()

# ================== PREVISÃO ==================
st.subheader("📊 Previsão Inteligente")

saldo_temp = saldo
dia_negativo = None

for d in range(dia_atual, 32):
    for _, row in df.iterrows():
        if row['tipo']=="Saída" and int(row['vencimento']) == d:
            saldo_temp -= float(row['valor'])
            if saldo_temp < 0 and not dia_negativo:
                dia_negativo = d

if dia_negativo:
    st.error(f"⚠️ Atenção: saldo negativo no dia {dia_negativo}")
else:
    st.success("✅ Você vai fechar o mês positivo 💖")

# ================== META ==================
meta = 235000
total = df[df['tipo']=="Entrada"]['valor'].sum() if not df.empty else 0

st.subheader("🏠 Nosso Apê 💕")
st.progress(min(total/meta if meta>0 else 0,1.0))
st.write(f"R$ {total:,.2f} / R$ {meta:,.2f}")

# ================== FOOTER ==================
st.markdown("""
<div style="text-align:center;margin-top:50px">
<p style="color:#ff1493;font-size:18px;">Construindo nosso futuro juntos 💑✨</p>
<p style="color:#666;">HERMEX SOLUTIONS</p>
</div>
""", unsafe_allow_html=True)
