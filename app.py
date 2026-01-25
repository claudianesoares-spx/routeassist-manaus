import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config(
    page_title="RouteAssist | Apoio Operacional",
    page_icon="🧭",
    layout="centered"
)

# ================= ESTADO GLOBAL SEGURO =================
if "status_site" not in st.session_state:
    st.session_state.status_site = "FECHADO"

if "historico" not in st.session_state:
    st.session_state.historico = []

# ================= FUNÇÕES =================
def registrar_acao(usuario, acao):
    st.session_state.historico.append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "usuario": usuario,
        "acao": acao
    })

def limpar_id(valor):
    if pd.isna(valor):
        return ""
    valor = str(valor).strip()
    return "" if valor.lower() in ["nan", "-", "none"] else valor

@st.cache_data(ttl=120)
def carregar_rotas(url):
    try:
        df = pd.read_csv(url)
        if df.empty:
            raise ValueError("Planilha de rotas vazia")
        df.columns = df.columns.str.strip()
        df["ID"] = df["ID"].apply(limpar_id)
        df["Data Exp."] = pd.to_datetime(df["Data Exp."], errors="coerce").dt.date
        return df
    except Exception as e:
        st.error("❌ Erro ao carregar ROTAS")
        st.exception(e)
        st.stop()

@st.cache_data(ttl=300)
def carregar_motoristas(url):
    try:
        df = pd.read_csv(url)
        if df.empty:
            raise ValueError("Planilha de motoristas vazia")
        df.columns = df.columns.str.strip()
        df["ID"] = df["ID"].apply(limpar_id)
        return df
    except Exception as e:
        st.error("❌ Erro ao carregar MOTORISTAS")
        st.exception(e)
        st.stop()

# ================= URLs =================
URL_ROTAS = "https://docs.google.com/spreadsheets/d/1F8HC2D8UxRc5R_QBdd-zWu7y6Twqyk3r0NTPN0HCWUI/export?format=csv&gid=1803149397"
URL_DRIVERS = "https://docs.google.com/spreadsheets/d/1F8HC2D8UxRc5R_QBdd-zWu7y6Twqyk3r0NTPN0HCWUI/export?format=csv&gid=36116218"

GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSffKb0EPcHCRXv-XiHhgk-w2bTGbt179fJkr879jNdp-AbTxg/viewform"

# ================= INTERFACE =================
st.title("🧭 RouteAssist")
st.markdown("Ferramenta de apoio operacional para alocação e redistribuição de rotas.")
st.divider()

# ================= ADMIN =================
with st.sidebar:
    with st.expander("🔒 Área Administrativa"):
        senha = st.text_input("Senha", type="password")

        nivel = None
        if senha == "MASTER2026":
            nivel = "MASTER"
            st.success("Acesso MASTER liberado")
        elif senha == "LPA2026":
            nivel = "ADMIN"
            st.success("Acesso ADMIN liberado")
        elif senha:
            st.error("Senha incorreta")

        if nivel:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔓 ABRIR"):
                    st.session_state.status_site = "ABERTO"
                    registrar_acao(nivel, "ABRIU CONSULTA")
            with col2:
                if st.button("🔒 FECHAR"):
                    st.session_state.status_site = "FECHADO"
                    registrar_acao(nivel, "FECHOU CONSULTA")

            if st.button("🔄 Limpar cache agora"):
                st.cache_data.clear()
                st.success("Cache limpo")

st.markdown(f"### 📌 Status atual: **{st.session_state.status_site}**")
st.divider()

if st.session_state.status_site == "FECHADO":
    st.warning("🚫 Consulta indisponível no momento.")
    st.stop()

# ================= CONSULTA =================
st.markdown("### 🔍 Consulta Operacional de Rotas")

id_motorista = st.text_input("Digite seu ID de motorista")

if st.button("🔍 Consultar") and id_motorista.strip():

    df_rotas = carregar_rotas(URL_ROTAS)
    df_drivers = carregar_motoristas(URL_DRIVERS)

    if id_motorista not in set(df_drivers["ID"]):
        st.warning("⚠️ ID não encontrado.")
        st.stop()

    # ===== ROTAS DO MOTORISTA =====
    rotas_motorista = df_rotas[df_rotas["ID"] == id_motorista]

    if not rotas_motorista.empty:
        st.markdown("### 🚚 Suas rotas atribuídas")
        for _, row in rotas_motorista.iterrows():
            data_fmt = row["Data Exp."].strftime("%d/%m/%Y") if pd.notna(row["Data Exp."]) else "-"
            st.markdown(f"""
            <div class="card">
                <strong>ROTA:</strong> {row['Rota']}<br>
                <strong>PLACA:</strong> {row['Placa']}<br>
                <strong>BAIRRO:</strong> {row['Bairro']}<br>
                <strong>CIDADE:</strong> {row['Cidade']}<br>
                <strong>DATA:</strong> {data_fmt}
            </div>
            """, unsafe_allow_html=True)

    # ===== ROTAS DISPONÍVEIS =====
    rotas_disp = df_rotas[df_rotas["ID"] == ""]

    if not rotas_disp.empty:
        st.markdown("### 📦 Rotas disponíveis")

        for cidade, df_cidade in rotas_disp.groupby("Cidade"):
            with st.expander(f"🏙️ {cidade}", expanded=False):
                for _, row in df_cidade.iterrows():
                    data_fmt = row["Data Exp."].strftime("%d/%m/%Y") if pd.notna(row["Data Exp."]) else "-"

                    form_url = (
                        f"{GOOGLE_FORM_URL}?usp=pp_url"
                        f"&entry.392776957={id_motorista}"
                        f"&entry.1682939517={row['Rota']}"
                        f"&entry.625563351={row['Cidade']}"
                        f"&entry.1284288730={row['Bairro']}"
                        f"&entry.1534916252=Tenho+Interesse"
                    )

                    st.markdown(f"""
                    <div class="card">
                        📍 {row['Bairro']} — {row['Tipo Veiculo']}<br>
                        📅 {data_fmt}
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"[👉 Abrir formulário]({form_url})")

# ================= RODAPÉ =================
st.markdown("""
<hr>
<div style="text-align:center; color:#888; font-size:0.85em;">
<strong>RouteAssist</strong><br>
Concept & Development — Claudiane Vieira<br>
Since Dec/2025
</div>
""", unsafe_allow_html=True)
