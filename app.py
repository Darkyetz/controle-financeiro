import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from supabase import create_client
import random

# ================== CONFIG ==================
st.set_page_config(page_title="CB Financeiro | HermeX", layout="wide")

# ================== SUPABASE ==================
SUPABASE_URL = "https://dqxkorlftspzadevawge.supabase.co"
SUPABASE_KEY = "SUA_KEY_AQUI"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================== CSS ==================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Montserrat:wght@300;600&display=swap');

.stApp {
    background: radial-gradient(circle at top, #0a0014, #000);
    color: white;
    font-family: 'Montserrat', sans-serif;
}

input, select {
    background-color: #111 !important;
    color: white !important;
    border-radius: 10px !important;
}

button {
    background: #ff1493 !important;
    color: white !important;
    border-radius: 10px !important;
}

.logo {
    font-family: 'Playfair Display', serif;
    font-size: 90px;
    background: linear-gradient(#ff1493,#ff69b4);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}

.frase {
    color: #ff69b4;
    font-size: 14px;
    margin-top: -20px;
}

.card {
    background:#0a0a0a;
    padding:25px;
    border-radius:20px;
    margin-bottom:15px;
    transition:0.3s;
}

.value {
    font-size:28px;
    color:#ff1493;
    font-weight:bold;
}

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
</style>
""", unsafe_allow_html=True)

# ================== CORAÇÕES ==================
for _ in range(15):
    st.markdown(f"""
    <div class="heart" style="
        left:{random.randint(0,100)}%;
        animation-duration:{random.randint(6,12)}s;
        opacity:{random.random()};
    ">❤️</div>
    """, unsafe_allow_html=True)

# ================== DATA ==================
hoje = datetime.now()
dia_atual = hoje.day

# ================== SALÁRIOS ==================
salarios = {
    "Cauã": {"v1": 3000, "d1": 5, "v2": 3000, "d2": 20},
    "Beca": {"v1": 2000, "d1": 5, "v2": 2000, "d2": 20}
}

# ================== DADOS ==================
response = supabase.table("transacoes").select("*").execute()
df = pd.DataFrame(response.data) if response.data else pd.DataFrame()

# ================== HEADER ==================
st.markdown('<div class="logo">CB 💖</div>', unsafe_allow_html=True)
st.markdown('<div class="frase">cada centavo mais perto do nosso cantinho 🏠💕</div>', unsafe_allow_html=True)
st.write(f"📅 {hoje.strftime('%d/%m/%Y')}")

# ================== MOTOR ==================
entrada = 0
saida = 0

for s in salarios.values():
    if dia_atual >= s["d1"]: entrada += s["v1"]
    if dia_atual >= s["d2"]: entrada += s["v2"]

for _, row in df.iterrows():
    try:
        inicio = pd.to_datetime(row['inicio']).date()
        fim = pd.to_datetime(row['fim']).date()

        if inicio <= hoje.date() <= fim:
            if row['tipo'] == 'Entrada':
                entrada += float(row['valor'])
            else:
                if int(row['vencimento']) <= dia_atual:
                    saida += float(row['valor'])
    except:
        pass

saldo = entrada - saida

# ================== DASH ==================
c1,c2,c3 = st.columns(3)
c1.markdown(f'<div class="card">Entradas<br><span class="value">R$ {entrada:.2f}</span></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card">Saídas<br><span class="value">R$ {saida:.2f}</span></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card">Saldo<br><span class="value">R$ {saldo:.2f}</span></div>', unsafe_allow_html=True)

# ================== FORM ==================
st.subheader("💖 Registrar")

tipo = st.radio("Tipo", ["Entrada","Saída"])
nome = st.text_input("Descrição")
categoria = st.selectbox("Categoria", ["Fixo","Outros","Lazer","Apartamento"])
valor = st.number_input("Valor", min_value=0.0)
quem = st.selectbox("Quem", ["Cauã","Beca","Ambos"])
data_real = st.date_input("Data real")

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
        "quem": quem,
        "data_real": str(data_real),
        "pago": False
    }).execute()
    st.rerun()

# ================== HISTÓRICO ==================
st.subheader("📊 Histórico")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📌 Contas Fixas")
    if not df.empty:
        fixos = df[df["categoria"] == "Fixo"]
        for i, row in fixos.iterrows():
            status = "✅ Pago" if row.get("pago") else "❌ Pendente"
            c1, c2 = st.columns([3,1])
            c1.write(f"{row['nome']} - R$ {row['valor']} ({status})")
            if not row.get("pago"):
                if c2.button(f"Pagar {i}"):
                    supabase.table("transacoes").update({"pago": True}).eq("id", row["id"]).execute()
                    st.rerun()

with col2:
    st.markdown("### 📑 Extrato Diário")
    if not df.empty:
        df["data_real"] = pd.to_datetime(df["data_real"], errors="coerce")
        extrato = df.sort_values("data_real", ascending=False)
        st.dataframe(extrato[["data_real","nome","tipo","valor","pago"]], use_container_width=True)

# ================== META ==================
st.subheader("🏠 Apê")

meta = 235000
ap_pago = df[(df["categoria"]=="Apartamento") & (df["pago"]==True)]["valor"].sum() if not df.empty else 0

st.progress(min(ap_pago/meta,1.0))
st.write(f"R$ {ap_pago:,.2f} / R$ {meta:,.2f}")

# ================== GRÁFICO ==================
if not df.empty:
    fig = px.bar(df, x='quem', y='valor', color='tipo',
                 color_discrete_map={"Entrada":"#ff69b4","Saída":"#ff1493"})
    fig.update_layout(paper_bgcolor='black', plot_bgcolor='black', font_color='white')
    st.plotly_chart(fig, use_container_width=True)
