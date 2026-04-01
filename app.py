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

# ================== CORAÇÕES ==================
st.markdown("""
<style>
.heart {
    position: fixed;
    top: -10px;
    color: #ff1493;
    font-size: 18px;
    animation: fall linear infinite;
}
@keyframes fall {
    to { transform: translateY(110vh); }
}
</style>
""", unsafe_allow_html=True)

for i in range(15):
    st.markdown(f"""
    <div class="heart" style="
        left:{random.randint(0,100)}%;
        animation-duration:{random.randint(6,12)}s;
        opacity:{random.random()};
    ">❤️</div>
    """, unsafe_allow_html=True)

# ================== CSS ==================
st.markdown("""
<style>
header, footer {visibility:hidden;}
.stApp {background:#000;color:#fff;font-family:Montserrat;}
.logo {font-size:80px;background:linear-gradient(#ff1493,#3d001f);
-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.card {background:#0a0a0a;padding:25px;border-radius:20px;margin-bottom:20px;}
.value {font-size:28px;color:#ff1493;font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# ================== DATA ==================
hoje = datetime.now()
dia_atual = hoje.day

data_entrega = datetime(2029,4,30)
dias_restantes = (data_entrega - hoje).days

# ================== BUSCAR DADOS ==================
response = supabase.table("transacoes").select("*").execute()
df = pd.DataFrame(response.data)

if df.empty:
    df = pd.DataFrame(columns=['data','tipo','nome','categoria','valor','vencimento','inicio','fim','quem'])

# ================== HEADER ==================
col1,col2 = st.columns(2)

with col1:
    st.markdown('<div class="logo">CB</div>', unsafe_allow_html=True)
    st.write(f"📅 Hoje: {hoje.strftime('%d/%m/%Y')}")

with col2:
    st.markdown(f"""
    <div style='text-align:right'>
        <div style='font-size:40px;font-weight:800;'>{dias_restantes} dias</div>
        <div style='color:#ff69b4;'>para o apê 🏠</div>
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
st.subheader("🚀 Registrar")

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

if st.button("Salvar"):
    supabase.table("transacoes").insert({
        "data": hoje.strftime("%Y-%m-%d"),
        "tipo": tipo,
        "nome": nome,
        "categoria": categoria,
        "valor": float(valor),
        "vencimento": int(venc),
        "inicio": str(inicio),
        "fim": str(fim),
        "quem": quem
    }).execute()

    st.rerun()

# ================== META ==================
meta = 235000
total = df[df['tipo']=="Entrada"]['valor'].sum() if not df.empty else 0

st.subheader("🏠 Progresso do Apê")
st.progress(min(total/meta if meta>0 else 0,1.0))
st.write(f"R$ {total:,.2f} / R$ {meta:,.2f}")

# ================== GRÁFICO ==================
if not df.empty:
    fig = px.bar(df, x='quem', y='valor', color='tipo')
    st.plotly_chart(fig, use_container_width=True)

# ================== FOOTER ==================
st.markdown("""
<div style="text-align:center;margin-top:50px;padding:20px;border-top:1px solid #111;">
<p style="color:#ff1493;">Construindo nosso futuro juntos 💕</p>
<p style="color:#666;font-size:12px;">HERMEX SOLUTIONS © 2026</p>
</div>
""", unsafe_allow_html=True)
