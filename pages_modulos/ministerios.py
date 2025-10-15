import streamlit as st
import os
import json
import uuid
from datetime import datetime
from PIL import Image
import pandas as pd # Importar Pandas para visualização tabular

CAMINHO_MINISTERIOS = "data/ministerios.json"
CAMINHO_LOGOS = "data/logos_ministerios"
CAMINHO_MEMBROS = "data/membros.json"

os.makedirs(os.path.dirname(CAMINHO_MINISTERIOS) or '.', exist_ok=True)
os.makedirs(CAMINHO_LOGOS, exist_ok=True)

def carregar_ministerios():
    """Carrega a lista de ministérios."""
    if os.path.exists(CAMINHO_MINISTERIOS):
        with open(CAMINHO_MINISTERIOS, "r", encoding="utf-8") as f:
            try:
                return json.load(f) or []
            except json.JSONDecodeError:
                return []
    return []

def salvar_ministerios(lista):
    """Salva a lista de ministérios."""
    with open(CAMINHO_MINISTERIOS, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)

def carregar_membros():
    """Carrega a lista de membros."""
    if os.path.exists(CAMINHO_MEMBROS):
        with open(CAMINHO_MEMBROS, "r", encoding="utf-8") as f:
            try:
                # Carrega os membros e cria um DataFrame para busca eficiente
                membros_data = json.load(f) or []
                return membros_data, pd.DataFrame(membros_data)
            except json.JSONDecodeError:
                return [], pd.DataFrame()
    return [], pd.DataFrame()

# --- Funções Auxiliares ---

def obter_contato_responsavel(nome_responsavel, df_membros):
    """Busca o telefone do responsável no DataFrame de membros."""
    if nome_responsavel and not df_membros.empty:
        # Usa loc para buscar o membro pelo nome e obter o telefone
        resp_info = df_membros.loc[df_membros['nome'] == nome_responsavel]
        if not resp_info.empty:
            return resp_info['telefone'].iloc[0]
    return ""

def exibir_form_cadastro_ministerio(ministerios, nomes_membros, df_membros):
    """Formulário de cadastro com layout em colunas e validação."""
    st.subheader("➕ Novo Ministério")

    with st.form("form_ministerio", clear_on_submit=True):
        col_nome, col_logo = st.columns([2, 1])
        with col_nome:
            nome = st.text_input("Nome do Ministério *")
        with col_logo:
            logo = st.file_uploader("Logo do Ministério", type=["jpg", "jpeg", "png"])
            
        descricao = st.text_area("Descrição do Ministério")

        # Responsável e Contato
        st.markdown("---")
        responsavel_nome = st.selectbox("Responsável pelo Ministério *", nomes_membros)
        
        # O contato deve ser recalculado toda vez que o selectbox muda
        contato_responsavel = obter_contato_responsavel(responsavel_nome, df_membros)
        st.info(f"📞 **Contato do Líder Selecionado:** `{contato_responsavel}`")

        st.markdown("---")
        membros_participantes = st.multiselect("Membros Participantes", nomes_membros)
        enviado = st.form_submit_button("💾 Salvar Ministério", type="primary", use_container_width=True)

        if enviado:
            if not nome or not responsavel_nome:
                st.error("Por favor, preencha o Nome do Ministério e o Responsável.")
                return

            id_min = str(uuid.uuid4())
            caminho_logo = ""

            # Lógica de upload de logo
            if logo:
                try:
                    ext = logo.name.split(".")[-1]
                    nome_arquivo = f"{id_min}.{ext}"
                    caminho_logo = os.path.join(CAMINHO_LOGOS, nome_arquivo)
                    with open(caminho_logo, "wb") as f:
                        f.write(logo.read())
                except Exception as e:
                    st.warning(f"Erro ao salvar logo: {e}")
                    caminho_logo = ""

            novo = {
                "id": id_min,
                "nome": nome,
                "descricao": descricao,
                "responsavel": responsavel_nome,
                "contato_responsavel": contato_responsavel,
                "membros": membros_participantes,
                "logo": caminho_logo,
                "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            ministerios.append(novo)
            salvar_ministerios(ministerios)
            st.session_state["ministerio_sucesso"] = True
            st.rerun()

    if st.session_state.get("ministerio_sucesso"):
        st.success("✅ Ministério cadastrado com sucesso!")
        del st.session_state["ministerio_sucesso"]

# --- Listagem e Edição ---

def exibir_listagem_ministerios(ministerios, nomes_membros, df_membros):
    """Exibe a lista de ministérios com expanders, exclusão e edição integrada."""
    st.subheader("📋 Ministérios Ativos")

    # Inicia ou limpa o estado de edição para evitar bugs
    if "editando_id" not in st.session_state:
        st.session_state["editando_id"] = None

    # Verifica se há algum ministério em edição
    ministerio_em_edicao = next((m for m in ministerios if m["id"] == st.session_state["editando_id"]), None)
    
    # Se houver um item em edição, o formulário é exibido no topo da lista
    if ministerio_em_edicao:
        exibir_form_edicao(ministerio_em_edicao, ministerios, nomes_membros, df_membros)
        st.markdown("---") # Separa o formulário de edição da lista

    for m in ministerios:
        # Se um ministério está sendo editado, pulamos o expander dele para não duplicar
        if m["id"] == st.session_state["editando_id"]:
            continue
            
        # O expander só aparece para os que não estão em edição
        with st.expander(f"**{m['nome']}** — Líder: {m['responsavel']} ({len(m.get('membros', []))} Membros)", expanded=False):
            
            # Layout das informações
            col_logo, col_info, col_botoes = st.columns([1, 2, 1])
            
            # Coluna 1: Logo
            if m.get("logo") and os.path.exists(m["logo"]):
                col_logo.image(m["logo"], width=100)
            else:
                col_logo.markdown("🖼️ **Sem logo**")

            # Coluna 2: Informações
            with col_info:
                st.markdown(f"📄 **Descrição:** {m['descricao']}")
                st.markdown(f"📞 **Contato do Líder:** {m['contato_responsavel']}")
                st.caption(f"Criado em: {m.get('criado_em', 'N/D')}")
                
            # Coluna 3: Botões
            with col_botoes:
                 if col_botoes.button("📝 Editar", key=f"edit_{m['id']}", use_container_width=True):
                    st.session_state["editando_id"] = m["id"]
                    st.rerun()
                
                 if col_botoes.button("🗑️ Excluir", key=f"del_{m['id']}", use_container_width=True, type="secondary"):
                    excluir_ministerio(m, ministerios)
                    
            st.markdown("---")
            
            # Membros do Ministério (abaixo das informações)
            membros_df = pd.DataFrame({"Membro": m.get("membros", [])})
            if not membros_df.empty:
                 st.markdown("👥 **Membros Participantes:**")
                 st.dataframe(membros_df, hide_index=True, use_container_width=True)


def exibir_form_edicao(ministerio, ministerios, nomes_membros, df_membros):
    """Formulário de edição que substitui o expander."""
    st.header(f"✏️ Editando: {ministerio['nome']}")
    
    with st.form(f"form_editar_{ministerio['id']}"):
        
        col_nome, col_logo = st.columns([2, 1])
        with col_nome:
            nome_edit = st.text_input("Nome do Ministério *", value=ministerio["nome"])
        with col_logo:
            logo_upload = st.file_uploader("Atualizar Logo", type=["jpg", "jpeg", "png"])
            st.caption(f"Logo atual: {'Sim' if ministerio.get('logo') else 'Não'}")
            
        descricao_edit = st.text_area("Descrição", value=ministerio["descricao"])

        # Responsável e Contato
        try:
             indice_responsavel = nomes_membros.index(ministerio["responsavel"])
        except ValueError:
             indice_responsavel = 0 # Define o primeiro se o líder anterior não for encontrado
             
        responsavel_nome_edit = st.selectbox("Responsável *", nomes_membros, index=indice_responsavel)
        contato_responsavel_edit = obter_contato_responsavel(responsavel_nome_edit, df_membros)
        st.info(f"📞 **Contato do Líder:** `{contato_responsavel_edit}`")

        membros_participantes_edit = st.multiselect("Membros Participantes", nomes_membros, default=ministerio.get("membros", []))
        
        st.markdown("---")
        col_salvar, col_cancelar = st.columns(2)
        salvar = col_salvar.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
        cancelar = col_cancelar.form_submit_button("❌ Cancelar Edição", use_container_width=True)

        if salvar:
             if not nome_edit or not responsavel_nome_edit:
                st.error("Por favor, preencha o Nome do Ministério e o Responsável.")
                return
                
             # Lógica de atualização de logo
             caminho_logo_edit = ministerio.get("logo", "")
             if logo_upload:
                 # Remove a logo antiga, se existir
                 if caminho_logo_edit and os.path.exists(caminho_logo_edit):
                     os.remove(caminho_logo_edit)
                 # Salva a nova logo
                 ext = logo_upload.name.split(".")[-1]
                 nome_arquivo = f"{ministerio['id']}.{ext}"
                 caminho_logo_edit = os.path.join(CAMINHO_LOGOS, nome_arquivo)
                 with open(caminho_logo_edit, "wb") as f:
                     f.write(logo_upload.read())
            
             # Atualiza os dados
             ministerio["nome"] = nome_edit
             ministerio["descricao"] = descricao_edit
             ministerio["responsavel"] = responsavel_nome_edit
             ministerio["contato_responsavel"] = contato_responsavel_edit
             ministerio["membros"] = membros_participantes_edit
             ministerio["logo"] = caminho_logo_edit

             salvar_ministerios(ministerios)
             st.success("✅ Ministério atualizado com sucesso!")
             st.session_state["editando_id"] = None
             st.rerun()

        if cancelar:
            st.session_state["editando_id"] = None
            st.rerun()

def excluir_ministerio(ministerio, ministerios):
    """Função para excluir ministério e sua logo."""
    if ministerio.get("logo") and os.path.exists(ministerio["logo"]):
        os.remove(ministerio["logo"])
    ministerios[:] = [x for x in ministerios if x["id"] != ministerio["id"]]
    salvar_ministerios(ministerios)
    st.success(f"Ministério '{ministerio['nome']}' excluído.")
    st.rerun()


# --- Função Principal ---

def exibir():
    st.title("💒 Gerenciamento de Ministérios")

    # Carrega dados e prepara a lista de nomes e DataFrame de membros
    membros_list, df_membros = carregar_membros()
    nomes_membros = [m["nome"] for m in membros_list]
    if not nomes_membros:
        st.warning("⚠️ **Alerta:** Nenhum membro encontrado. Cadastre membros primeiro para atribuir responsáveis.")
        nomes_membros = ["Nenhum Membro Cadastrado"]
        
    ministerios = carregar_ministerios()

    aba = st.radio("Selecione:", ["➕ Novo Ministério", "📋 Lista de Ministérios"], horizontal=True)
    
    st.markdown("---")

    if aba == "➕ Novo Ministério":
        exibir_form_cadastro_ministerio(ministerios, nomes_membros, df_membros)

    elif aba == "📋 Lista de Ministérios":
        if not ministerios:
            st.info("Nenhum ministério cadastrado. Use a aba '➕ Novo Ministério' para começar.")
            return
        exibir_listagem_ministerios(ministerios, nomes_membros, df_membros)

if __name__ == '__main__':
    exibir()