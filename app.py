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

# ================== DATA ==================
hoje = datetime.now()
dia_atual = hoje.day

# ================== SALÁRIOS ==================
salarios = {
    "Cauã": {"v1": 3000, "d1": 5, "v2": 3000, "d2": 20},
    "Beca": {"v1": 2000, "d1": 5, "v2": 2000, "d2": 20}
}

# ================== BUSCAR DADOS ==================
try:
    response = supabase.table("transacoes").select("*").execute()
    df = pd.DataFrame(response.data) if response.data else pd.DataFrame()
except:
    df = pd.DataFrame()

# ================== ANIMAÇÃO CORAÇÕES ==================
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

for _ in range(12):
    st.markdown(f"<div class='heart' style='left:{random.randint(0,100)}%; animation-duration:{random.randint(6,12)}s;'>❤️</div>", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown("## 💖 CB Financeiro")
st.write(f"📅 {hoje.strftime('%d/%m/%Y')}")
# ================== MOTOR FINANCEIRO ==================
entrada = 0
saida = 0

# salário automático
for p, s in salarios.items():
    if dia_atual >= s["d1"]:
        entrada += s["v1"]
    if dia_atual >= s["d2"]:
        entrada += s["v2"]

# transações
for _, row in df.iterrows():
    try:
        inicio = pd.to_datetime(row['inicio']).date()
        fim = pd.to_datetime(row['fim']).date()

        if inicio <= hoje.date() <= fim:
            if row['tipo'] == 'Entrada':
                entrada += float(row['valor'])

            if row['tipo'] == 'Saída':
                if int(row['vencimento']) <= dia_atual:
                    saida += float(row['valor'])
    except:
        pass

saldo = entrada - saida

# ================== DASH ==================
c1,c2,c3 = st.columns(3)
c1.metric("Entradas", f"R$ {entrada:.2f}")
c2.metric("Saídas", f"R$ {saida:.2f}")
c3.metric("Saldo", f"R$ {saldo:.2f}")

# ================== ALERTA ==================
if saldo < 0:
    st.error("⚠️ saldo negativo")
elif saldo < 1000:
    st.warning("⚠️ saldo baixo")
else:
    st.success("💖 tudo sob controle")

# ================== FORM ==================
st.subheader("💸 Registrar movimentação")

tipo = st.radio("Tipo", ["Entrada","Saída"])
nome = st.text_input("Descrição")
categoria = st.selectbox("Categoria", ["Fixo","Outros","Lazer","Apartamento"])
valor = st.number_input("Valor", min_value=0.0)
quem = st.selectbox("Quem", ["Cauã","Beca","Ambos"])
data_real = st.date_input("Data real")

if categoria == "Fixo":
    venc = st.number_input("Dia vencimento",1,31)
    inicio = st.date_input("Início")
    fim = st.date_input("Fim")
else:
    venc = dia_atual
    inicio = hoje
    fim = hoje

pago = st.checkbox("Já foi pago?")

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
        "pago": pago
    }).execute()

    st.rerun()

# ================== PAGAR CONTAS ==================
st.subheader("📌 Contas Pendentes")

if not df.empty and "pago" in df.columns:
    pendentes = df[df["pago"] == False]

    for i, row in pendentes.iterrows():
        col1,col2 = st.columns([3,1])

        col1.write(f"{row['nome']} - R$ {row['valor']}")

        if col2.button(f"Pagar {i}"):
            supabase.table("transacoes").update({
                "pago": True
            }).eq("id", row["id"]).execute()

            st.rerun()

# ================== PREVISÃO ==================
st.subheader("📊 Previsão do Mês")

saldo_temp = saldo
dia_negativo = None

for d in range(dia_atual, 32):
    for _, row in df.iterrows():
        if row['tipo']=="Saída" and int(row['vencimento']) == d:
            saldo_temp -= float(row['valor'])
            if saldo_temp < 0 and not dia_negativo:
                dia_negativo = d

if dia_negativo:
    st.error(f"⚠️ saldo ficará negativo no dia {dia_negativo}")
else:
    st.success("💖 mês fecha positivo")

# ================== META APÊ ==================
st.subheader("🏠 Nosso Apê")

meta = 235000

ap_pago = df[
    (df["categoria"] == "Apartamento") &
    (df["pago"] == True)
]["valor"].sum() if not df.empty else 0

st.progress(min(ap_pago/meta,1.0))
st.write(f"R$ {ap_pago:,.2f} / R$ {meta:,.2f}")

# ================== CALENDÁRIO ==================
st.subheader("📆 Calendário")

if not df.empty:
    df["data_real"] = pd.to_datetime(df["data_real"], errors="coerce")
    calendario = df.sort_values("data_real")

    st.dataframe(
        calendario[["data_real","nome","valor","pago"]],
        use_container_width=True
    )

# ================== EXTRATO ==================
st.subheader("📑 Extrato")

if not df.empty:
    def cor(row):
        if row["tipo"] == "Entrada":
            return ["background-color: rgba(0,255,0,0.1)"]*len(row)
        else:
            return ["background-color: rgba(255,0,0,0.1)"]*len(row)

    st.dataframe(df.style.apply(cor, axis=1), use_container_width=True)

# ================== GRÁFICO ==================
if not df.empty:
    fig = px.bar(
        df,
        x='quem',
        y='valor',
        color='tipo',
        color_discrete_map={
            "Entrada": "#ff69b4",
            "Saída": "#ff1493"
        }
    )

    fig.update_layout(
        paper_bgcolor='black',
        plot_bgcolor='black',
        font_color='white'
    )

    st.plotly_chart(fig, use_container_width=True)
