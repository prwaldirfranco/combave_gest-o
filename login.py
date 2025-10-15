import streamlit as st
import json
import random  # Importa a biblioteca para funcionalidades aleatórias
from utils.auth import verificar_credenciais

# --- Início da Seção de Versículos ---
# Você pode adicionar, remover ou editar versículos nesta lista facilmente
versiculos = [
    {
        "texto": "Porque Deus amou o mundo de tal maneira que deu o seu Filho unigênito, para que todo aquele que nele crê não pereça, mas tenha a vida eterna.",
        "referencia": "João 3:16"
    },
    {
        "texto": "O Senhor é o meu pastor; nada me faltará.",
        "referencia": "Salmos 23:1"
    },
    {
        "texto": "Posso todas as coisas em Cristo que me fortalece.",
        "referencia": "Filipenses 4:13"
    },
    {
        "texto": "O choro pode durar uma noite, mas a alegria vem pela manhã.",
        "referencia": "Salmos 30:5"
    },
    {
        "texto": "Confie no Senhor de todo o seu coração e não se apoie em seu próprio entendimento.",
        "referencia": "Provérbios 3:5"
    },
    {
        "texto": "Porque sou eu que conheço os planos que tenho para vocês', diz o Senhor, 'planos de fazê-los prosperar e não de lhes causar dano, planos de dar-lhes esperança e um futuro.",
        "referencia": "Jeremias 29:11"
    }
]
# --- Fim da Seção de Versículos ---


def carregar_config():
    try:
        with open("data/config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"nome_igreja": "Sistema Igreja", "logo": None}

def login():
    config = carregar_config()
    nome_igreja = config.get("nome_igreja", "Sistema Igreja")
    logo_path = config.get("logo")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Exibe o logo se ele existir, com largura definida
        if logo_path:
            # AQUI: Ajustamos a largura do logo para 150 pixels
            st.image(logo_path, width=150)

        st.header(f"Login - {nome_igreja}")

        with st.container(border=True):
            usuario = st.text_input(
                "👤 Usuário",
                placeholder="Digite seu nome de usuário",
                key="login_usuario"
            )
            senha = st.text_input(
                "🔑 Senha",
                type="password",
                placeholder="Digite sua senha",
                key="login_senha"
            )

            if st.button("Entrar", use_container_width=True, type="primary"):
                usuario_autenticado = verificar_credenciais(usuario, senha)
                if usuario_autenticado:
                    st.session_state.logado = True
                    st.session_state.usuario = usuario_autenticado
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

        st.divider() # Adiciona uma linha divisória para separar visualmente

        # --- Início da Exibição do Versículo Aleatório ---
        versiculo_escolhido = random.choice(versiculos)
        st.markdown(f"*{versiculo_escolhido['texto']}*")
        st.caption(versiculo_escolhido['referencia'])
        # --- Fim da Exibição do Versículo Aleatório ---