import streamlit as st
import json
import uuid
from datetime import datetime

CAMINHO_DADOS = "data/usuarios.json"

PAGINAS_DISPONIVEIS = [
    "🏠 Início",
    "👥 Membros",
    "📅 Eventos",
    "💒 Ministérios",
    "💰 Financeiro",
    "📈 Relatórios",
    "📝 Formulários",
    "📧 Avisos",
    "⚙️ Configurações"
]

def carregar_usuarios():
    try:
        with open(CAMINHO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def salvar_usuarios(usuarios):
    with open(CAMINHO_DADOS, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)

def exibir():
    st.title("👤 Gerenciar Usuários")

    aba = st.radio("Escolha uma opção:", ["➕ Cadastrar Usuário", "📋 Lista de Usuários"])

    if aba == "➕ Cadastrar Usuário":
        with st.form("form_usuario", clear_on_submit=True):
            nome = st.text_input("Nome")
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            email = st.text_input("Email")
            nivel = st.selectbox("Nível de Acesso", ["admin", "comum", "liderança"])
            permissoes = st.multiselect("Páginas Permitidas", PAGINAS_DISPONIVEIS, default=["🏠 Início"])

            enviado = st.form_submit_button("💾 Salvar")

            if enviado:
                usuarios = carregar_usuarios()
                novo_usuario = {
                    "id": str(uuid.uuid4()),
                    "nome": nome,
                    "usuario": usuario,
                    "senha": senha,
                    "email": email,
                    "nivel": nivel,
                    "permissoes": permissoes,  # 👈 Aqui é o nome correto
                    "criado_em": str(datetime.now())
                }
                usuarios.append(novo_usuario)
                salvar_usuarios(usuarios)
                st.success("✅ Usuário cadastrado com sucesso!")

    else:
        usuarios = carregar_usuarios()
        if not usuarios:
            st.info("Nenhum usuário cadastrado.")
            return

        for u in usuarios:
            with st.expander(f"{u.get('nome', 'Sem Nome')} ({u.get('nivel', '-')})"):
                st.markdown(f"**Usuário:** {u.get('usuario', '')}")
                st.markdown(f"**Email:** {u.get('email', '')}")
                st.markdown(f"**Nível:** {u.get('nivel', '')}")
                st.markdown(f"**Páginas permitidas:** {', '.join(u.get('permissoes', []))}")
                st.markdown(f"_Criado em: {u.get('criado_em', '')}_")

                col1, col2 = st.columns(2)
                if col1.button("🗑️ Excluir", key=f"excluir_{u['id']}"):
                    usuarios = [usr for usr in usuarios if usr["id"] != u["id"]]
                    salvar_usuarios(usuarios)
                    st.success("Usuário excluído com sucesso!")
                    st.rerun()
