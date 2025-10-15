import streamlit as st
import importlib
import json
from datetime import datetime

def carregar_config():
    try:
        with open("data/config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"nome_igreja": "Nome da Igreja", "logo": "data/logo_igreja.png"}

def carregar_membros():
    try:
        with open("data/membros.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def carregar_eventos():
    try:
        with open("data/eventos.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def carregar_ministerios():
    try:
        with open("data/ministerios.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def mostrar_menu():
    config = carregar_config()
    nome_igreja = config.get("nome_igreja", "Nome da Igreja")
    logo_path = config.get("logo", "data/logo_igreja.png")

    usuario = st.session_state.get("usuario", {})
    permissoes = usuario.get("permissoes", [])

    opcoes_disponiveis = {
        "🏠 Início": "inicio",
        "👥 Membros": "membros",
        "📅 Eventos": "eventos",
        "💒 Ministérios": "ministerios",
        "💰 Financeiro": "financeiro",
        "📈 Relatórios": "relatorios",
        "📚 Escola Bíblica": "escola_biblica",
        "📧 Avisos": "avisos",
        # "🧑‍🏫 Discipulado": "discipulado",
        "⚙️ Configurações": "configuracoes",
        "📝 Formulários": "formularios",
        "👤 Usuários": "usuarios"
    }

    menu = st.sidebar.radio("Menu", [p for p in opcoes_disponiveis if p in permissoes])

    if logo_path:
        st.sidebar.image(logo_path, use_container_width=True)
    st.sidebar.markdown(f"## {nome_igreja}")
    st.sidebar.markdown("---")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.session_state.usuario = None
        st.rerun()

    if menu == "🏠 Início":
        st.title("📊 Painel Inicial")
        membros = carregar_membros()
        eventos = carregar_eventos()
        eventos = sorted(eventos, key=lambda e: datetime.strptime(e["data"], "%Y-%m-%d"))
        ministerios = carregar_ministerios()
        mes_atual = datetime.now().strftime("%m")

        aniversariantes_mes = [
            m for m in membros if "nascimento" in m and m["nascimento"].split("-")[1] == mes_atual
        ]

        st.subheader("📅 Próximos Eventos")
        for ev in eventos[:5]:
            st.markdown(f"- **{ev['titulo']}** em {ev['data']} às {ev['horario']} - {ev['local']}")

        st.subheader("🎉 Aniversariantes do Mês")
        for m in aniversariantes_mes:
            data_nasc = datetime.strptime(m["nascimento"], "%Y-%m-%d").strftime("%d/%m")
            st.markdown(f"- {m['nome']} ({data_nasc})")

        st.subheader("💒 Ministérios")
        for minist in ministerios:
            st.markdown(f"- {minist['nome']} - Líder: {minist.get('responsavel', 'N/A')}")

    elif menu in opcoes_disponiveis:
        try:
            modulo = opcoes_disponiveis[menu]
            pagina = importlib.import_module(f"pages_modulos.{modulo}")
            pagina.exibir()
        except Exception as e:
            st.error(f"Erro ao carregar a página: {e}")
    else:
        st.warning("Você não tem permissão para acessar esse módulo.")
