import streamlit as st
import json
import os

CAMINHO_FORMULARIOS = "data/formularios.json"
CAMINHO_RESPOSTAS = "data/respostas_formularios.json"

def carregar_formularios():
    if os.path.exists(CAMINHO_FORMULARIOS):
        with open(CAMINHO_FORMULARIOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def carregar_respostas():
    if os.path.exists(CAMINHO_RESPOSTAS):
        with open(CAMINHO_RESPOSTAS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def exibir():
    st.title("📋 Respostas dos Formulários")

    formularios = carregar_formularios()
    respostas = carregar_respostas()

    if not formularios:
        st.warning("Nenhum formulário criado ainda.")
        return

    if not respostas:
        st.info("Nenhuma resposta registrada ainda.")
        return

    opcoes_formularios = {f["titulo"]: f["id"] for f in formularios}
    titulo_escolhido = st.selectbox("Escolha o formulário:", list(opcoes_formularios.keys()))

    id_escolhido = opcoes_formularios[titulo_escolhido]

    respostas_filtradas = [r for r in respostas if r["id_formulario"] == id_escolhido]

    if not respostas_filtradas:
        st.info("Nenhuma resposta para este formulário ainda.")
        return

    for r in respostas_filtradas:
        with st.expander(f"🗓️ Enviado em {r['enviado_em']}"):
            for pergunta, resposta in r["respostas"].items():
                st.markdown(f"**{pergunta}**: {resposta}")

if __name__ == "__main__":
    exibir()
