import streamlit as st
from menu import mostrar_menu

st.set_page_config(page_title="Sistema Igreja", layout="wide", initial_sidebar_state="expanded")

# Oculta o menu lateral padrão do Streamlit
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

if 'logado' not in st.session_state:
    st.session_state.logado = False

if st.session_state.logado:
    mostrar_menu()
else:
    from login import login
    login()