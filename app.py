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

# ================= ARQUIVO DE PERSISTÊNCIA =================
CONFIG_FILE = "config.json"

# ================= CONFIG PADRÃO =================
DEFAULT_CONFIG = {
    "status_site": "FECHADO",
    "senha_master": "MASTER2026",
    "historico": []
}

# ================= LOAD / SAVE =================
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

# ================= FUNÇÃO LOG =================
def registrar_acao(usuario, acao):
    config["historico"].append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "usuario": usuario,
        "acao": acao
    })
    save_config(config)

# ================= REGRA DE HORÁRIO (10:05) =================
agora = datetime.now()
liberar_dobra = (
    agora.hour > 10 or
    (agora.hour == 10 and agora.minute >= 5)
)

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
.card h4 {
    margin-bottom: 12px;
}
.card p {
    margin: 4px 0;
    font-size: 15px;
}
.card a {
    display: inline-block;
    margin-top: 10px;
    color: #ff7a00;
    font-weight: bold;
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

# ================= CABEÇALHO =================
st.title("🧭 RouteAssist")
st.markdown(
    "Ferramenta de **apoio operacional** para alocação e redistribuição de rotas, "
    "atuando de forma complementar ao sistema oficial **SPX**."
)
st.divider()

# ================= SIDEBAR / ADMIN =================
with st.sidebar:
    with st.expander("🔒 Área Administrativa", expanded=False):

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
            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔓 ABRIR"):
                    config["status_site"] = "ABERTO"
                    registrar_acao(nivel, "ABRIU CONSULTA")
                    st.success("Consulta ABERTA")

            with col2:
                if st.button("🔒 FECHAR"):
                    config["status_site"] = "FECHADO"
                    registrar_acao(nivel, "FECHOU CONSULTA")
                    st.warning("Consulta FECHADA")

# ================= STATUS ATUAL =================
st.markdown(f"### 📌 Status atual: **{config['status_site']}**")
st.divider()

# ================= BLOQUEIO =================
if config["status_site"] == "FECHADO":
    st.warning("🚫 Consulta indisponível no momento.")
    st.stop()

# ================= CONSULTA =================
st.markdown("### 🔍 Consulta Operacional de Rotas")
id_motorista = st.text_input("Digite seu ID de motorista")

if id_motorista:
    url_rotas = "https://docs.google.com/spreadsheets/d/1F8HC2D8UxRc5R_QBdd-zWu7y6Twqyk3r0NTPN0HCWUI/export?format=xlsx"
    url_interesse = "https://docs.google.com/spreadsheets/d/1ux9UP_oJ9VTCTB_YMpvHr1VEPpFHdIBY2pudgehtTIE/export?format=xlsx&sheet=Planilha1"  # ajuste se necessário

    # ===== BASE DE ROTAS =====
    df = pd.read_excel(url_rotas)
    df["ID"] = df["ID"].astype(str).str.strip()

    # ===== BASE DE DRIVERS ATIVOS =====
    df_drivers = pd.read_excel(url_rotas, sheet_name="DRIVERS ATIVOS", dtype=str)
    df_drivers["ID"] = df_drivers["ID"].str.strip()
    ids_ativos = set(df_drivers["ID"].dropna())

    id_motorista = id_motorista.strip()

    # ===== VALIDAÇÃO DO ID =====
    if id_motorista not in ids_ativos:
        st.warning(
            "⚠️ ID não encontrado na base de motoristas ativos.\n\n"
            "Verifique se digitou corretamente."
        )
        st.stop()

    # ===== RESULTADOS DO MOTORISTA =====
    resultado = df[df["ID"] == id_motorista]

    # ===== ROTAS DISPONÍVEIS =====
    rotas_disponiveis = df[
        df["ID"].isna() |
        (df["ID"] == "") |
        (df["ID"].str.lower() == "nan") |
        (df["ID"] == "-")
    ]

    # ===== PLANILHA INTERESSE - TRAVA CLIQUE =====
    df_interesse = pd.read_excel(url_interesse)
    df_interesse["ID"] = df_interesse["ID"].astype(str).str.strip()
    df_interesse["Controle 01"] = df_interesse["Controle 01"].astype(str).str.strip()

    # ===== DRIVER COM ROTA =====
    if not resultado.empty:
        for _, row in resultado.iterrows():
            st.markdown(f"""
            <div class="card">
                <h4>🚚 Rota: {row['Rota']}</h4>
                <p>👤 <strong>Motorista:</strong> {row['Nome']}</p>
                <p>🚗 <strong>Placa:</strong> {row['Placa']}</p>
                <p>🏙️ <strong>Cidade:</strong> {row['Cidade']}</p>
                <p>📍 <strong>Bairro:</strong> {row['Bairro']}</p>
            </div>
            """, unsafe_allow_html=True)

        if liberar_dobra and not rotas_disponiveis.empty:
            st.divider()
            st.markdown("### 📦 Rotas disponíveis")
            for cidade in rotas_disponiveis["Cidade"].unique():
                with st.expander(f"🏙️ {cidade}"):
                    for _, row in rotas_disponiveis[rotas_disponiveis["Cidade"] == cidade].iterrows():

                        # ===== VERIFICA SE MOTORISTA JÁ CLICOU =====
                        ja_clicou = not df_interesse[
                            (df_interesse["ID"] == id_motorista) &
                            (df_interesse["Controle 01"] == row["Rota"])
                        ].empty

                        if ja_clicou:
                            st.markdown(f"""
                            <div class="card">
                                <p>📍 <strong>Bairro:</strong> {row['Bairro']}</p>
                                <p>🚗 <strong>Tipo Veículo:</strong> {row.get('Tipo Veiculo', 'Não informado')}</p>
                                <p style="color: green; font-weight:bold;">✅ Você já clicou nesta rota</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            form_url = (
                                "https://docs.google.com/forms/d/e/1FAIpQLSffKb0EPcHCRXv-XiHhgk-w2bTGbt179fJkr879jNdp-AbTxg/viewform"
                                f"?usp=pp_url"
                                f"&entry.392776957={id_motorista}"
                                f"&entry.1682939517={row['Rota']}"
                                f"&entry.2002352354={row['Placa']}"
                                f"&entry.1100254277={row.get('Tipo Veiculo', '')}"
                                f"&entry.625563351={row['Cidade']}"
                                f"&entry.1284288730={row['Bairro']}"
                                f"&entry.1534916252=Tenho+Interesse"
                            )

                            st.markdown(f"""
                            <div class="card">
                                <p>📍 <strong>Bairro:</strong> {row['Bairro']}</p>
                                <p>🚗 <strong>Tipo Veículo:</strong> {row.get('Tipo Veiculo', 'Não informado')}</p>
                                <a href="{form_url}" target="_blank">
                                    👉 Tenho interesse nesta rota
                                </a>
                            </div>
                            """, unsafe_allow_html=True)

    # ===== DRIVER SEM ROTA =====
    else:
        st.info("ℹ️ No momento você não possui rota atribuída.")
        st.markdown("### 📦 Regiões com rotas disponíveis")

        if rotas_disponiveis.empty:
            st.warning("🚫 No momento não há rotas disponíveis.")
        else:
            for cidade in rotas_disponiveis["Cidade"].unique():
                with st.expander(f"🏙️ {cidade}"):
                    for _, row in rotas_disponiveis[rotas_disponiveis["Cidade"] == cidade].iterrows():

                        # ===== VERIFICA SE MOTORISTA JÁ CLICOU =====
                        ja_clicou = not df_interesse[
                            (df_interesse["ID"] == id_motorista) &
                            (df_interesse["Controle 01"] == row["Rota"])
                        ].empty

                        if ja_clicou:
                            st.markdown(f"""
                            <div class="card">
                                <p>📍 <strong>Bairro:</strong> {row['Bairro']}</p>
                                <p>🚗 <strong>Tipo Veículo:</strong> {row.get('Tipo Veiculo', 'Não informado')}</p>
                                <p style="color: green; font-weight:bold;">✅ Você já clicou nesta rota</p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            form_url = (
                                "https://docs.google.com/forms/d/e/1FAIpQLSffKb0EPcHCRXv-XiHhgk-w2bTGbt179fJkr879jNdp-AbTxg/viewform"
                                f"?usp=pp_url"
                                f"&entry.392776957={id_motorista}"
                                f"&entry.1682939517={row['Rota']}"
                                f"&entry.2002352354={row['Placa']}"
                                f"&entry.1100254277={row.get('Tipo Veiculo', '')}"
                                f"&entry.625563351={row['Cidade']}"
                                f"&entry.1284288730={row['Bairro']}"
                                f"&entry.1534916252=Tenho+Interesse"
                            )

                            st.markdown(f"""
                            <div class="card">
                                <p>📍 <strong>Bairro:</strong> {row['Bairro']}</p>
                                <p>🚗 <strong>Tipo Veículo:</strong> {row.get('Tipo Veiculo', 'Não informado')}</p>
                                <a href="{form_url}" target="_blank">
                                    👉 Tenho interesse nesta rota
                                </a>
                            </div>
                            """, unsafe_allow_html=True)

# ================= ASSINATURA =================
st.markdown(
    """
    <hr>
    <div style="text-align: center; color: #888; font-size: 0.85em;">
        <strong>RouteAssist</strong><br>
        Concept & Development — Claudiane Vieira<br>
        Since Dec/2025
    </div>
    """,
    unsafe_allow_html=True
)
