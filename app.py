import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config(
    page_title="RouteAssist | Apoio Operacional",
    page_icon="🧭",
    layout="centered"
)

# ================= CONFIGURAÇÃO =================
CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "status_site": "FECHADO",
    "senha_master": "MASTER2026",
    "historico": []
}

# ================= FUNÇÕES DE CONFIG =================
def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)

config = load_config()

def registrar_acao(usuario, acao):
    config["historico"].append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "usuario": usuario,
        "acao": acao
    })
    save_config(config)

# ================= URLs =================
URL_ROTAS = "https://docs.google.com/spreadsheets/d/1F8HC2D8UxRc5R_QBdd-zWu7y6Twqyk3r0NTPN0HCWUI/export?format=csv&gid=1803149397"
URL_DRIVERS = "https://docs.google.com/spreadsheets/d/1F8HC2D8UxRc5R_QBdd-zWu7y6Twqyk3r0NTPN0HCWUI/export?format=csv&gid=36116218"
URL_INTERESSE = "https://docs.google.com/spreadsheets/d/1ux9UP_oJ9VTCTB_YMpvHr1VEPpFHdIBY2pudgehtTIE/export?format=csv&gid=1442170550"

GOOGLE_FORM_URL = (
    "https://docs.google.com/forms/d/e/1FAIpQLSffKb0EPcHCRXv-XiHhgk-w2bTGbt179fJkr879jNdp-AbTxg/viewform"
)

# ================= CACHE ANTI-PICO =================
@st.cache_data(ttl=120)
def carregar_rotas(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df["ID"] = df["ID"].fillna("").astype(str).str.strip().replace({"nan": "", "-": ""})
    df["Data Exp."] = pd.to_datetime(df["Data Exp."], errors="coerce").dt.date
    return df

@st.cache_data(ttl=300)
def carregar_motoristas(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df["ID"] = df["ID"].fillna("").astype(str).str.strip()
    return df

@st.cache_data(ttl=60)
def carregar_interesse(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df["ID"] = df["ID"].astype(str).str.strip()
    df["Controle 01"] = df["Controle 01"].astype(str).str.strip()
    df["Data Exp."] = pd.to_datetime(df["Data Exp."], errors="coerce").dt.date
    return df

# ================= ESTILO =================
st.markdown("""
<style>
.card {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border-left: 6px solid #ff7a00;
    margin-bottom: 16px;
}
a {
    font-weight: bold;
    color: #ff7a00;
}
</style>
""", unsafe_allow_html=True)

# ================= INTERFACE =================
st.title("🧭 RouteAssist")
st.markdown("Ferramenta de apoio operacional para alocação e redistribuição de rotas.")
st.divider()

# ================= SIDEBAR ADMIN =================
nivel = None

with st.sidebar:
    with st.expander("🔒 Área Administrativa"):
        senha = st.text_input("Senha", type="password")

        if senha == config["senha_master"]:
            nivel = "MASTER"
            st.success("Acesso MASTER liberado")
        elif senha == "LPA2026":
            nivel = "ADMIN"
            st.success("Acesso ADMIN liberado")
        elif senha:
            st.error("Senha incorreta")

        if nivel in ["ADMIN", "MASTER"]:
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔓 ABRIR"):
                    config["status_site"] = "ABERTO"
                    registrar_acao(nivel, "ABRIU CONSULTA")

            with col2:
                if st.button("🔒 FECHAR"):
                    config["status_site"] = "FECHADO"
                    registrar_acao(nivel, "FECHOU CONSULTA")

            st.divider()

            if st.button("🔄 Atualizar dados agora"):
                st.cache_data.clear()
                st.success("Dados atualizados com sucesso!")

st.markdown(f"### 📌 Status atual: {config['status_site']}")
st.divider()

# ================= CONSULTA =================
if config["status_site"] == "FECHADO":
    st.warning("🚫 Consulta indisponível no momento.")
    st.stop()

st.markdown("### 🔍 Consulta Operacional de Rotas")

id_motorista = st.text_input("Digite seu ID de motorista").strip()

consultar = st.button("🔍 Consultar rotas disponíveis")

if consultar:
    if not id_motorista:
        st.warning("⚠️ Informe seu ID de motorista.")
        st.stop()

    df_rotas = carregar_rotas(URL_ROTAS)
    df_drivers = carregar_motoristas(URL_DRIVERS)
    df_interesse = carregar_interesse(URL_INTERESSE)

    if id_motorista not in set(df_drivers["ID"]):
        st.warning("⚠️ ID não encontrado na base de motoristas ativos.")
        st.stop()

    resultado = df_rotas[df_rotas["ID"] == id_motorista]
    rotas_disponiveis = df_rotas[df_rotas["ID"] == ""]

    if not resultado.empty:
        for _, row in resultado.iterrows():
            data_fmt = row["Data Exp."].strftime("%d/%m/%Y") if pd.notna(row["Data Exp."]) else "-"
            st.markdown(f"""
            <div class="card">
                <h4>🚚 Rota: {row['Rota']}</h4>
                <p>🏙️ Cidade: {row['Cidade']}</p>
                <p>📍 Bairro: {row['Bairro']}</p>
                <p>📅 Data: {data_fmt}</p>
            </div>
            """, unsafe_allow_html=True)

    if not rotas_disponiveis.empty:
        st.markdown("### 📦 Rotas disponíveis")

        for _, row in rotas_disponiveis.iterrows():
            data_fmt = row["Data Exp."].strftime("%d/%m/%Y") if pd.notna(row["Data Exp."]) else "-"

            form_url = (
                f"{GOOGLE_FORM_URL}"
                f"?usp=pp_url"
                f"&entry.392776957={id_motorista}"
                f"&entry.1682939517={row['Rota']}"
                f"&entry.625563351={row['Cidade']}"
                f"&entry.1284288730={row['Bairro']}"
                f"&entry.1534916252=Tenho+Interesse"
            )

            st.markdown(f"""
            <div class="card">
                <p>📍 Bairro: {row['Bairro']}</p>
                <p>🚗 Tipo Veículo: {row.get('Tipo Veiculo','Não informado')}</p>
                <p>📅 Data da Expedição: {data_fmt}</p>
                <a href="{form_url}" target="_blank">✋ Tenho interesse nesta rota</a>
            </div>
            """, unsafe_allow_html=True)

# ================= RODAPÉ =================
st.markdown("""
<hr>
<div style="text-align:center; color:#888; font-size:0.85em;">
<strong>RouteAssist</strong><br>
Concept & Development — Claudiane Vieira<br>
Since Dec/2025
</div>
""", unsafe_allow_html=True)
