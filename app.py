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

# ================= CACHE POR CAMADA =================
@st.cache_data(ttl=120)
def carregar_rotas(url_rotas: str) -> pd.DataFrame:
    df = pd.read_csv(url_rotas)
    df.columns = df.columns.str.strip()
    df["ID"] = df["ID"].fillna("").astype(str).str.strip().replace({"nan": "", "-": ""})
    df["Data Exp."] = pd.to_datetime(df["Data Exp."], errors="coerce").dt.date
    return df


@st.cache_data(ttl=300)
def carregar_motoristas(url_drivers: str) -> pd.DataFrame:
    df = pd.read_csv(url_drivers)
    df.columns = df.columns.str.strip()
    df["ID"] = df["ID"].fillna("").astype(str).str.strip()
    return df


@st.cache_data(ttl=60)
def carregar_interesse(url_interesse: str) -> pd.DataFrame:
    df = pd.read_csv(url_interesse)
    df.columns = df.columns.str.strip()
    df["ID"] = df["ID"].fillna("").astype(str).str.strip()
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
</style>
""", unsafe_allow_html=True)

# ================= FUNÇÃO ROTAS DISPONÍVEIS =================
def mostrar_rotas_disponiveis(rotas_disponiveis, df_interesse, id_motorista):
    if rotas_disponiveis.empty:
        st.warning("🚫 No momento não há rotas disponíveis.")
        return

    st.markdown("### 📦 Regiões com rotas disponíveis")

    for cidade in rotas_disponiveis["Cidade"].unique():
        with st.expander(f"🏙️ {cidade}"):
            df_cidade = rotas_disponiveis[rotas_disponiveis["Cidade"] == cidade]

            for _, row in df_cidade.iterrows():
                ja_clicou = not df_interesse[
                    (df_interesse["ID"] == id_motorista) &
                    (df_interesse["Controle 01"] == row["Rota"]) &
                    (df_interesse["Data Exp."] == row["Data Exp."])
                ].empty

                data_fmt = row["Data Exp."].strftime("%d/%m/%Y") if pd.notna(row["Data Exp."]) else "-"

                if ja_clicou:
                    st.markdown(f"""
                    <div class="card">
                        <p>📍 Bairro: {row['Bairro']}</p>
                        <p>🚗 Tipo Veículo: {row.get('Tipo Veiculo','Não informado')}</p>
                        <p>📅 Data da Expedição: {data_fmt}</p>
                        <p style="color: green; font-weight:bold;">✅ Você já clicou nesta rota</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    form_url = (
                        "https://docs.google.com/forms/d/e/1FAIpQLSffKb0EPcHCRXv-XiHhgk-w2bTGbt179fJkr879jNdp-AbTxg/viewform"
                        f"?usp=pp_url"
                        f"&entry.392776957={id_motorista}"
                        f"&entry.1682939517={row['Rota']}"
                        f"&entry.2002352354={row.get('Placa','')}"
                        f"&entry.1100254277={row.get('Tipo Veiculo','')}"
                        f"&entry.625563351={row['Cidade']}"
                        f"&entry.1284288730={row['Bairro']}"
                        f"&entry.1534916252=Tenho+Interesse"
                    )

                    st.markdown(f"""
                    <div class="card">
                        <p>📍 Bairro: {row['Bairro']}</p>
                        <p>🚗 Tipo Veículo: {row.get('Tipo Veiculo','Não informado')}</p>
                        <p>📅 Data da Expedição: {data_fmt}</p>
                        <a href="{form_url}" target="_blank">👉 Tenho interesse nesta rota</a>
                    </div>
                    """, unsafe_allow_html=True)

# ================= INTERFACE =================
st.title("🧭 RouteAssist")
st.markdown("Ferramenta de apoio operacional para alocação e redistribuição de rotas.")
st.divider()

# ================= SIDEBAR =================
with st.sidebar:
    with st.expander("🔒 Área Administrativa"):
        senha = st.text_input("Senha", type="password")
        nivel = None

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

st.markdown(f"### 📌 Status atual: {config['status_site']}")
st.divider()

# ================= CONSULTA =================
if config["status_site"] == "FECHADO":
    st.warning("🚫 Consulta indisponível no momento.")
    st.stop()

st.markdown("### 🔍 Consulta Operacional de Rotas")
id_motorista = st.text_input("Digite seu ID de motorista")

if id_motorista:
    df_rotas = carregar_rotas(URL_ROTAS)
    df_drivers = carregar_motoristas(URL_DRIVERS)
    df_interesse = carregar_interesse(URL_INTERESSE)

    ids_ativos = set(df_drivers["ID"].dropna())
    id_motorista = id_motorista.strip()

    if id_motorista not in ids_ativos:
        st.warning("⚠️ ID não encontrado na base de motoristas ativos.")
        st.stop()

    st.info("🔄 Após clicar em 'Tenho interesse', atualize a página para visualizar a confirmação.")

    resultado = df_rotas[df_rotas["ID"] == id_motorista]
    rotas_disponiveis = df_rotas[df_rotas["ID"] == ""]

    if not resultado.empty:
        for _, row in resultado.iterrows():
            data_fmt = row["Data Exp."].strftime("%d/%m/%Y") if pd.notna(row["Data Exp."]) else "-"
            st.markdown(f"""
            <div class="card">
                <h4>🚚 Rota: {row['Rota']}</h4>
                <p>👤 Motorista: {row['Nome']}</p>
                <p>🚗 Placa: {row['Placa']}</p>
                <p>🏙️ Cidade: {row['Cidade']}</p>
                <p>📍 Bairro: {row['Bairro']}</p>
                <p>📅 Data: {data_fmt}</p>
            </div>
            """, unsafe_allow_html=True)

    mostrar_rotas_disponiveis(rotas_disponiveis, df_interesse, id_motorista)

# ================= RODAPÉ =================
st.markdown("""
<hr>
<div style="text-align: center; color: #888; font-size: 0.85em;">
<strong>RouteAssist</strong><br>
Concept & Development — Claudiane Vieira<br>
Since Dec/2025
</div>
""", unsafe_allow_html=True)
