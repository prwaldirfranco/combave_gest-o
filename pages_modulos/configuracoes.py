import streamlit as st
import os
import json
from PIL import Image

CAMINHO_CONFIG = "data/config.json"
CAMINHO_LOGO = "data/logo_igreja.png"

def carregar_config():
    if os.path.exists(CAMINHO_CONFIG):
        with open(CAMINHO_CONFIG, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def salvar_config(config):
    with open(CAMINHO_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def exibir():
    st.title("⚙️ Configurações do Sistema")

    config = carregar_config()

    nome_atual = config.get("nome_igreja", "")
    email_atual = config.get("email_igreja", "")
    tema_atual = config.get("tema", "Claro")
    cor_primaria = config.get("cor_primaria", "#0E76A8")
    logo_existente = os.path.exists(CAMINHO_LOGO)

    with st.form("form_config"):
        st.subheader("🏷️ Identidade da Igreja")
        nome_igreja = st.text_input("Nome da Igreja", value=nome_atual)
        email_igreja = st.text_input("E-mail da Igreja", value=email_atual)

        st.subheader("🎨 Tema e Aparência")
        tema = st.selectbox("Tema do Sistema", ["Claro", "Escuro"], index=0 if tema_atual == "Claro" else 1)
        cor = st.color_picker("Cor Primária", value=cor_primaria)

        st.markdown("---")
        st.subheader("🖼️ Logo da Igreja")

        if logo_existente:
            st.image(CAMINHO_LOGO, width=200, caption="Logo atual")

        nova_logo = st.file_uploader("Atualizar Logo (PNG ou JPG)", type=["png", "jpg", "jpeg"])

        st.markdown("---")
        st.subheader("🔐 Segurança")
        senha_admin = st.text_input("Nova senha do administrador (deixe em branco para não alterar)", type="password")

        salvar = st.form_submit_button("💾 Salvar Configurações")

        if salvar:
            config["nome_igreja"] = nome_igreja.strip()
            config["email_igreja"] = email_igreja.strip()
            config["tema"] = tema
            config["cor_primaria"] = cor

            if senha_admin.strip():
                config["senha_admin"] = senha_admin.strip()

            salvar_config(config)

            if nova_logo:
                with open(CAMINHO_LOGO, "wb") as f:
                    f.write(nova_logo.read())

            st.success("✅ Configurações atualizadas com sucesso!")
            st.rerun()