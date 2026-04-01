import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import random

# CONFIG
st.set_page_config(page_title="CB Financeiro | HermeX", layout="wide")

# ================== CORAÇÕES CAINDO ❤️ ==================
st.markdown("""
<style>
.heart {
    position: fixed;
    top: -10px;
    color: #ff1493;
    font-size: 18px;
    animation: fall linear infinite;
    z-index: 999;
}

@keyframes fall {
    to {
        transform: translateY(110vh);
    }
}
</style>
""", unsafe_allow_html=True)

for i in range(15):
    st.markdown(f"""
    <div class="heart" style="
        left: {random.randint(0,100)}%;
        animation-duration: {random.randint(6,12)}s;
        opacity: {random.random()};
    ">❤️</div>
    """, unsafe_allow_html=True)

# ================== CSS ==================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@100;400;900&family=Playfair+Display:ital,wght@1,900&display=swap');

header, footer {
    visibility: hidden;
}

.block-container {
    padding-top: 1rem;
}

.stApp {
    background-color: #000;
    color: #fff;
    font-family: 'Montserrat', sans-serif;
}

@keyframes fadeIn {
    from {opacity: 0; transform: translateY(20px);}
    to {opacity: 1; transform: translateY(0);}
}

.logo {
    font-family: 'Playfair Display', serif;
    font-size: 80px;
    background: linear-gradient(180deg, #ff1493, #3d001f);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: fadeIn 1s;
}

.card {
    background: #0a0a0a;
    padding: 25px;
    border-radius: 20px;
    margin-bottom: 20px;
    animation: fadeIn 0.8s;
    transition: 0.3s;
}

.card:hover {
    transform: scale(1.02);
    box-shadow: 0 0 20px #ff1493;
}

.value {
    font-size: 28px;
    font-weight: bold;
    color: #ff1493;
}
</style>
""", unsafe_allow_html=True)

# ================== DATA ==================
hoje = datetime.now()
dia_atual = hoje.day

data_entrega = datetime(2029, 4, 30)
dias_restantes = (data_entrega - hoje).days

# ================== SESSION ==================
if 'transacoes' not in st.session_state:
    st.session_state.transacoes = pd.DataFrame(
        columns=['Data','Tipo','Nome','Categoria','Valor','Vencimento','Inicio','Fim','Quem']
    )

df = st.session_state.transacoes

# ================== HEADER ==================
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="logo">CB</div>', unsafe_allow_html=True)
    st.write(f"📅 Hoje: {hoje.strftime('%d/%m/%Y')}")

with col2:
    st.markdown(f"""
    <div style='text-align:right'>
        <div style='font-size:40px; font-weight:800;'>{dias_restantes} dias</div>
        <div style='color:#ff69b4; font-size:14px;'>para o nosso apê 🏠</div>
    </div>
    """, unsafe_allow_html=True)

# ================== MOTOR ==================
entrada = 0
saida = 0

for _, row in df.iterrows():
    inicio = pd.to_datetime(row['Inicio'])
    fim = pd.to_datetime(row['Fim'])

    ativo = inicio <= hoje <= fim

    if row['Tipo'] == 'Entrada':
        if ativo:
            entrada += row['Valor']
    else:
        if ativo and row['Vencimento'] <= dia_atual:
            saida += row['Valor']

saldo = entrada - saida

# ================== DASH ==================
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f'<div class="card">Entradas<br><span class="value">R$ {entrada:.2f}</span></div>', unsafe_allow_html=True)

with c2:
    st.markdown(f'<div class="card">Saídas<br><span class="value">R$ {saida:.2f}</span></div>', unsafe_allow_html=True)

with c3:
    st.markdown(f'<div class="card">Saldo Atual<br><span class="value">R$ {saldo:.2f}</span></div>', unsafe_allow_html=True)

# ================== FORM ==================
st.subheader("🚀 Registrar movimentação")

c1, c2, c3, c4 = st.columns([1,2,1,1])

tipo = c1.radio("Tipo", ["Entrada", "Saída"])
nome = c2.text_input("Descrição")
categoria = c3.selectbox("Categoria", ["Fixo", "Outros", "Lazer", "Apartamento"])
valor = c4.number_input("Valor", min_value=0.0)

dono = c1.selectbox("Quem", ["Cauã", "Beca", "Ambos"])

extra = st.container()

if categoria == "Fixo":
    with extra:
        venc = st.number_input("Dia vencimento", 1, 31)
        inicio = st.date_input("Data início")
        fim = st.date_input("Data fim")
else:
    venc = dia_atual
    inicio = hoje
    fim = hoje

if st.button("Salvar"):
    if nome and valor > 0:
        nova = pd.DataFrame({
            'Data':[hoje],
            'Tipo':[tipo],
            'Nome':[nome],
            'Categoria':[categoria],
            'Valor':[valor],
            'Vencimento':[venc],
            'Inicio':[inicio],
            'Fim':[fim],
            'Quem':[dono]
        })

        st.session_state.transacoes = pd.concat(
            [st.session_state.transacoes, nova],
            ignore_index=True
        )

        st.rerun()

# ================== GRÁFICOS ==================
g1, g2 = st.columns(2)

with g1:
    df_saida = df[df['Tipo']=="Saída"]
    if not df_saida.empty:
        fig = px.pie(df_saida, values='Valor', names='Categoria')
        st.plotly_chart(fig, use_container_width=True)

with g2:
    if not df.empty:
        fig2 = px.bar(df, x='Quem', y='Valor', color='Tipo')
        st.plotly_chart(fig2, use_container_width=True)

# ================== TABELA ==================
st.subheader("📑 Histórico")

def color_rows(row):
    if row.Tipo == 'Entrada':
        return ['background-color: rgba(144,238,144,0.15)']*len(row)
    else:
        return ['background-color: rgba(255,182,193,0.15)']*len(row)

if not df.empty:
    st.dataframe(df.style.apply(color_rows, axis=1), use_container_width=True)
else:
    st.write("Sem dados ainda...")

# ================== FOOTER ==================
st.markdown("""
<div style="
    text-align:center;
    margin-top:50px;
    padding:20px;
    border-top:1px solid #111;
">
    <p style="color:#ff1493; font-size:14px;">
        Construindo juntos nosso futuro 💕 | Rumo ao apê de 235k 🏠
    </p>
    <p style="color:#666; font-size:12px; letter-spacing:2px;">
        DESENVOLVIDO POR HERMEX SOLUTIONS © 2026
    </p>
</div>
""", unsafe_allow_html=True)