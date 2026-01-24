import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config(
    page_title="RouteAssist | Apoio Operacional",
    page_icon="🧭",
    layout="centered"
)

# ================= CONFIG LOCAL =================
CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "status_site": "FECHADO",
    "senha_master": "MASTER2026",
    "historico": []
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return DEFAULT_CONFIG.copy()

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

# ================= GOOGLE SHEETS (INTERESSE) =================
SHEET_ID_INTERESSE = "COLE_AQUI_O_ID_DA_PLANILHA"
ABA_INTERESSE = "INTERESSES"
SERVICE_ACCOUNT_FILE = "service_account.json"

def registrar_interesse(dados):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scopes
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID_INTERESSE).worksheet(ABA_INTERESSE)
    sheet.append_row(dados, value_input_option="USER_ENTERED")

# ================= URLs =================
URL_ROTAS = "https://docs.google.com/spreadsheets/d/1F8HC2D8UxRc5R_QBdd-zWu7y6Twqyk3r0NTPN0HCWUI/export?format=csv&gid=1803149397"
URL_DRIVERS = "https://docs.google.com/spreadsheets/d/1F8HC2D8UxRc5R_QBdd-zWu7y6Twqyk3r0NTPN0HCWUI/export?format=csv&gid=36116218"

# ================= FUNÇÕES =================
def limpar_id(valor):
    if pd.isna(valor):
        return ""
    valor = str(valor).strip()
    return "" if valor.lower() in ["nan", "-", "none"] else valor

@st.cache_data(ttl=600)
def carregar_rotas(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df["ID"] = df["ID"].apply(limpar_id)
    df["Data Exp."] = pd.to_datetime(df["Data Exp."], errors="coerce").dt.date
    return df

@st.cache_data(ttl=1800)
def carregar_motoristas(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df["ID"] = df["ID"].apply(limpar_id)
    return df

# ================= SESSION STATE =================
if "interesses" not in st.session_state:
    st.session_state.interesses = set()

if "placas" not in st.session_state:
    st.session_state.placas = {}

if "id_motorista" not in st.session_state:
    st.session_state.id_motorista = ""

if "consultado" not in st.session_state:
    st.session_state.consultado = False

# ================= INTERFACE =================
st.title("🧭 RouteAssist")
st.divider()

df_rotas = carregar_rotas(URL_ROTAS)
df_drivers = carregar_motoristas(URL_DRIVERS)

st.markdown("### 🔍 Consulta Operacional de Rotas")

id_input = st.text_input("Digite seu ID de motorista")

if st.button("🔍 Consultar"):
    st.session_state.id_motorista = id_input.strip()
    st.session_state.consultado = True

if st.session_state.consultado and st.session_state.id_motorista:
    id_motorista = st.session_state.id_motorista

    rotas_disp = df_rotas[df_rotas["ID"] == ""]

    st.markdown("### 📦 Rotas disponíveis")

    for _, row in rotas_disp.iterrows():
        rota_key = f"{row['Rota']}_{row['Bairro']}"

        placa = st.text_input(
            "Digite a placa",
            key=f"placa_{rota_key}"
        )

        if st.button("✋ Tenho interesse nesta rota", key=f"btn_{rota_key}"):
            registrar_interesse([
                id_motorista,
                placa,
                row["Rota"],
                row["Bairro"],
                row["Cidade"],
                row["Tipo Veiculo"],
                datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            ])
            st.success("✔ Interesse registrado com sucesso")

# ================= RODAPÉ =================
st.markdown("""
<hr>
<div style="text-align:center; color:#888; font-size:0.85em;">
<strong>RouteAssist</strong><br>
Concept & Development — Claudiane Vieira<br>
Since Dec/2025
</div>
""", unsafe_allow_html=True)
