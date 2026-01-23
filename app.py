import streamlit as st
import pandas as pd
from datetime import datetime

# ================= CONFIG =================
st.set_page_config(
    page_title="RouteAssist | Apoio Operacional",
    page_icon="🧭",
    layout="centered"
)

GOOGLE_FORM_URL = "https://docs.google.com/forms/d/e/SEU_FORM_ID/viewform"

# ================= SESSION STATE =================
if "interesses" not in st.session_state:
    st.session_state.interesses = set()

# ================= DADOS (EXEMPLO / JÁ EXISTENTE) =================
# Substitua apenas pelo seu carregamento real
df_rotas = pd.DataFrame([
    {"Rota": "A12", "Cidade": "Belém", "Bairro": "Marco", "Data Exp.": datetime(2026,1,24), "ID": ""},
    {"Rota": "B07", "Cidade": "Belém", "Bairro": "Pedreira", "Data Exp.": datetime(2026,1,24), "ID": ""},
    {"Rota": "D03", "Cidade": "Ananindeua", "Bairro": "Cidade Nova", "Data Exp.": datetime(2026,1,24), "ID": ""},
])

id_motorista = st.text_input("Informe seu ID:")

st.markdown("---")

# ================= ROTAS DISPONÍVEIS =================
rotas_disp = df_rotas[df_rotas["ID"] == ""]

if not rotas_disp.empty:
    st.markdown("### 📦 Rotas disponíveis")

    # 🔹 AGRUPAMENTO POR CIDADE (ÚNICA ALTERAÇÃO)
    for cidade, grupo in rotas_disp.groupby("Cidade"):
        st.markdown(f"#### 📍 {cidade}")

        for _, row in grupo.iterrows():
            data_fmt = (
                row["Data Exp."].strftime("%d/%m/%Y")
                if pd.notna(row["Data Exp."])
                else "-"
            )

            rota_key = f"{row['Rota']}_{row['Bairro']}_{data_fmt}"
            btn_key = f"btn_{rota_key}"

            if btn_key not in st.session_state:
                st.session_state[btn_key] = False

            form_url = (
                f"{GOOGLE_FORM_URL}?usp=pp_url"
                f"&entry.392776957={id_motorista}"
                f"&entry.1682939517={row['Rota']}"
                f"&entry.625563351={row['Cidade']}"
                f"&entry.1284288730={row['Bairro']}"
                f"&entry.1534916252=Tenho+Interesse"
            )

            # ===== CARD (NÃO ALTERADO) =====
            st.markdown(f"""
            <div class="card" style="
                background:#ffffff;
                padding:15px;
                border-radius:10px;
                box-shadow:0 2px 6px rgba(0,0,0,0.1);
                margin-bottom:10px;
            ">
                <p><strong>Rota:</strong> {row['Rota']}</p>
                <p>📍 Bairro: {row['Bairro']}</p>
                <p>📅 Data: {data_fmt}</p>
            </div>
            """, unsafe_allow_html=True)

            # ===== BOTÃO / STATUS =====
            if rota_key in st.session_state.interesses:
                st.success("✔ Interesse registrado")
                st.markdown(f"[👉 Abrir formulário]({form_url})")
            else:
                if st.button("✋ Tenho interesse nesta rota", key=btn_key):
                    st.session_state.interesses.add(rota_key)
                    st.success("✔ Interesse registrado")
                    st.markdown(f"[👉 Abrir formulário]({form_url})")

else:
    st.info("Nenhuma rota disponível no momento.")
