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

# ================= FUNÇÃO ROTAS DISPONÍVEIS =================
def mostrar_rotas_disponiveis(rotas_disponiveis, df_interesse, id_motorista):
    if rotas_disponiveis.empty:
        st.warning("🚫 No momento não há rotas disponíveis.")
        return

    st.markdown("### 📦 Regiões com rotas disponíveis")

    for cidade in rotas_disponiveis["Cidade"].unique():
        with st.expander(f"🏙️ {cidade}"):
            for _, row in rotas_disponiveis[rotas_disponiveis["Cidade"] == cidade].iterrows():

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
                        <p style="color: green; font-weight:bold;">
                            ✅ Você já clicou nesta rota nesta data
                        </p>
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
                        <a href="{form_url}" target="_blank">
                            👉 Tenho interesse nesta rota
                        </a>
                    </div>
                    """, unsafe_allow_html=True)

# ================= STATUS =================
st.markdown(f"### 📌 Status atual: **{config['status_site']}**")
st.divider()

if config["status_site"] == "FECHADO":
    st.warning("🚫 Consulta indisponível no momento.")
    st.stop()

# ================= CONSULTA MOTORISTA =================
st.markdown("### 🔍 Consulta Operacional de Rotas")
id_motorista = st.text_input("Digite seu ID de motorista")

if id_motorista:
    hora_atual = datetime.now().hour  # 👈 ÚNICA REGRA ADICIONADA

    url_rotas = "https://docs.google.com/spreadsheets/d/1F8HC2D8UxRc5R_QBdd-zWu7y6Twqyk3r0NTPN0HCWUI/export?format=xlsx"
    url_interesse = "https://docs.google.com/spreadsheets/d/1ux9UP_oJ9VTCTB_YMpvHr1VEPpFHdIBY2pudgehtTIE/export?format=xlsx"

    df = pd.read_excel(url_rotas)
    df["ID"] = df["ID"].astype(str).str.strip()
    df["Data Exp."] = pd.to_datetime(df["Data Exp."], errors="coerce").dt.date

    resultado = df[df["ID"] == id_motorista]

    rotas_disponiveis = df[df["ID"].isna() | (df["ID"] == "") | (df["ID"] == "-")]

    df_interesse = pd.read_excel(url_interesse)
    df_interesse["ID"] = df_interesse["ID"].astype(str).str.strip()
    df_interesse["Controle 01"] = df_interesse["Controle 01"].astype(str).str.strip()
    df_interesse["Data Exp."] = pd.to_datetime(df_interesse["Data Exp."], errors="coerce").dt.date

    # ===== DRIVER COM ROTA =====
    if not resultado.empty:
        for _, row in resultado.iterrows():
            st.markdown(f"""
            <div class="card">
                <h4>🚚 Rota: {row['Rota']}</h4>
                <p>👤 Motorista: {row['Nome']}</p>
            </div>
            """, unsafe_allow_html=True)

        if 9 <= hora_atual < 15:
            mostrar_rotas_disponiveis(rotas_disponiveis, df_interesse, id_motorista)
        else:
            st.info("⏰ Motoristas com rota atribuída podem visualizar novas rotas apenas das **09h às 15h**.")

    # ===== DRIVER SEM ROTA =====
    else:
        mostrar_rotas_disponiveis(rotas_disponiveis, df_interesse, id_motorista)
# ================= ASSINATURA =================
st.markdown("""
<hr>
<div style="text-align: center; color: #888; font-size: 0.85em;">
    <strong>RouteAssist</strong><br>
    Concept & Development — Claudiane Vieira<br>
    Since Dec/2025
</div>
""", unsafe_allow_html=True)
