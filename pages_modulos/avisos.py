import streamlit as st
import os
import json
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

CAMINHO_AVISOS = "data/avisos.json"
CAMINHO_MINISTERIOS = "data/ministerios.json"
CAMINHO_MEMBROS = "data/membros.json"

EMAIL_REMETENTE = "combavecarapebus@gmail.com"
SENHA_APP = "pmlzkbcbexzdokjo"

def carregar_avisos():
    if os.path.exists(CAMINHO_AVISOS):
        with open(CAMINHO_AVISOS, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def salvar_avisos(lista):
    with open(CAMINHO_AVISOS, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)

def carregar_membros():
    if os.path.exists(CAMINHO_MEMBROS):
        with open(CAMINHO_MEMBROS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def carregar_ministerios():
    if os.path.exists(CAMINHO_MINISTERIOS):
        with open(CAMINHO_MINISTERIOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def enviar_emails(destinatarios_emails, titulo, mensagem, autor):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    for email in destinatarios_emails:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Aviso da Igreja: {titulo}"
            msg["From"] = EMAIL_REMETENTE
            msg["To"] = email

            text = f"{titulo}\n\n{mensagem}\n\nEnviado por {autor} em {datetime.now().strftime('%d/%m/%Y %H:%M')}"

            html = f"""<html>
<body>
<h2>{titulo}</h2>
<p>{mensagem}</p>
<hr>
<p style='font-size:12px;color:gray;'>Enviado por {autor} em {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
</body>
</html>"""

            msg.attach(MIMEText(text, "plain"))
            msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(EMAIL_REMETENTE, SENHA_APP)
                server.sendmail(EMAIL_REMETENTE, email, msg.as_string())

        except Exception as e:
            st.warning(f"❌ Erro ao enviar e-mail para {email}: {e}")

def exibir():
    st.title("📧 Comunicação / Avisos")

    aba = st.radio("Escolha uma opção:", ["➕ Novo Aviso", "📋 Avisos Enviados"])
    avisos = carregar_avisos()
    ministerios = carregar_ministerios()
    membros = carregar_membros()

    nomes_ministerios = [m["nome"] for m in ministerios]
    nomes_membros = [m["nome"] for m in membros]

    if aba == "➕ Novo Aviso":
        with st.form("form_aviso", clear_on_submit=True):
            titulo = st.text_input("Título do Aviso")
            mensagem = st.text_area("Mensagem")
            autor = st.text_input("Autor do Aviso")

            destinatario_tipo = st.radio("Destinatários", ["Todos os Membros", "Ministério Específico", "Selecionar Membros"])

            emails_destino = []
            destinatarios = []

            if destinatario_tipo == "Ministério Específico":
                ministerio = st.selectbox("Escolha o Ministério", nomes_ministerios)
                destinatarios = [ministerio]
                emails_destino = [m.get("email") for m in membros if m.get("funcao") == ministerio and m.get("email")]

            elif destinatario_tipo == "Selecionar Membros":
                membros_escolhidos = st.multiselect("Escolha os Membros", nomes_membros)
                destinatarios = membros_escolhidos
                emails_destino = [m.get("email") for m in membros if m["nome"] in membros_escolhidos and m.get("email")]

            else:
                destinatarios = ["Todos"]
                emails_destino = [m.get("email") for m in membros if m.get("email")]

            enviado = st.form_submit_button("📨 Enviar Aviso")

            if enviado:
                if not titulo.strip() or not mensagem.strip():
                    st.warning("⚠️ Preencha o título e a mensagem antes de enviar.")
                else:
                    aviso = {
                        "id": str(uuid.uuid4()),
                        "titulo": titulo,
                        "mensagem": mensagem,
                        "autor": autor,
                        "destinatarios": destinatarios,
                        "tipo_destinatario": destinatario_tipo,
                        "data_envio": str(datetime.now())
                    }
                    avisos.append(aviso)
                    salvar_avisos(avisos)

                    if emails_destino:
                        enviar_emails(emails_destino, titulo, mensagem, autor)
                        st.success(f"✅ Aviso enviado com sucesso para {len(emails_destino)} destinatários!")
                    else:
                        st.warning("⚠️ Nenhum destinatário com e-mail válido encontrado.")

                    st.rerun()

    elif aba == "📋 Avisos Enviados":
        if not avisos:
            st.info("Nenhum aviso enviado ainda.")
            return

        for aviso in reversed(avisos):
            with st.expander(f"{aviso['titulo']} — por {aviso['autor']}"):
                st.markdown(f"**🕒 Enviado em:** {aviso['data_envio']}")
                st.markdown(f"**📨 Destinatários ({aviso['tipo_destinatario']}):**")
                for d in aviso['destinatarios']:
                    st.markdown(f"- {d}")
                st.markdown("---")
                st.markdown("**📝 Mensagem:**")
                st.markdown(aviso["mensagem"])

                col1, col2 = st.columns([1, 1])
                if col1.button("🗑️ Excluir", key=f"del_{aviso['id']}"):
                    avisos = [a for a in avisos if a["id"] != aviso["id"]]
                    salvar_avisos(avisos)
                    st.success("Aviso excluído.")
                    st.rerun()