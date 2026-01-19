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
.card p { margin: 4px 0; font-size: 15px; }
.card a { margin-top: 10px; color: #ff7a00; font-weight: bold; }
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
                        <p>📅 Data: {data_fmt}</p>
                        <p style="color:green;font-weight:bold;">✅ Você já clicou nesta rota</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    form_url = (
                        "https://docs.google.com/forms/d/e/1FAIpQLSffKb0EPcHCRXv-XiHhgk-w2bTGbt179fJkr879jNdp-AbTxg/viewform"
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
                        <p>📅 Data: {data_fmt}</p>
