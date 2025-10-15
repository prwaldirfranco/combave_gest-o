import streamlit as st
import os
import json
import uuid
from datetime import datetime, date

CAMINHO_EVENTOS = "data/eventos.json"

def carregar_eventos():
    """Carrega a lista de eventos do arquivo JSON."""
    if os.path.exists(CAMINHO_EVENTOS):
        with open(CAMINHO_EVENTOS, "r", encoding="utf-8") as f:
            try:
                # Retorna a lista, ou uma lista vazia se o arquivo estiver vazio
                return json.load(f) or [] 
            except json.JSONDecodeError:
                return []
    return []

def salvar_eventos(eventos):
    """Salva a lista de eventos no arquivo JSON."""
    with open(CAMINHO_EVENTOS, "w", encoding="utf-8") as f:
        json.dump(eventos, f, indent=4, ensure_ascii=False)

# --- Funções Auxiliares de Exibição ---

def exibir_form_cadastro(eventos):
    """Exibe o formulário de cadastro de novo evento com layout em colunas."""
    st.subheader("➕ Novo Evento")
    
    with st.form("form_evento", clear_on_submit=True):
        
        # 1. Colunas para dados básicos
        col_titulo, col_responsavel = st.columns([2, 1])
        with col_titulo:
            titulo = st.text_input("Título do Evento *", help="Nome principal do evento")
        with col_responsavel:
            responsavel = st.text_input("Responsável / Líder *")
            
        # 2. Colunas para Data e Hora
        col_data, col_horario = st.columns(2)
        with col_data:
            # Garante que a data mínima seja a de hoje
            data = st.date_input("Data do Evento *", min_value=date.today())
        with col_horario:
            horario = st.time_input("Horário *")
        
        # 3. Local e Descrição
        local = st.text_input("Local (Ex: Templo Principal, Salão Social, Online)")
        descricao = st.text_area("Descrição do Evento (Detalhes, objetivo, etc.)")

        st.markdown("---")
        enviado = st.form_submit_button("💾 Salvar Evento", type="primary", use_container_width=True)

        if enviado:
            # Validação básica
            if not titulo or not responsavel:
                st.error("Por favor, preencha o Título e o Responsável.")
                return

            novo_evento = {
                "id": str(uuid.uuid4()),
                "titulo": titulo,
                "data": str(data),
                "horario": str(horario),
                "local": local,
                "responsavel": responsavel,
                "descricao": descricao,
                "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            eventos.append(novo_evento)
            salvar_eventos(eventos)
            st.session_state["evento_sucesso"] = True
            st.rerun()

    # Exibe a mensagem de sucesso após o rerun
    if st.session_state.get("evento_sucesso"):
        st.success("✅ Evento cadastrado com sucesso!")
        del st.session_state["evento_sucesso"]

def listar_eventos(eventos):
    """Exibe a lista de eventos com filtro e funcionalidade de edição/exclusão."""
    st.subheader("📋 Calendário de Eventos")

    if not eventos:
        st.info("Nenhum evento cadastrado ainda.")
        return

    # 1. Filtro e Ordenação
    col_filtro, col_ordem = st.columns(2)
    
    opcoes_filtro = ["Próximos Eventos", "Eventos Passados", "Todos"]
    filtro_data = col_filtro.selectbox("Filtrar por data:", opcoes_filtro)
    
    eventos_filtrados = []
    data_hoje = date.today()
    
    for e in eventos:
        data_evento = datetime.strptime(e["data"], "%Y-%m-%d").date()
        if filtro_data == "Próximos Eventos" and data_evento >= data_hoje:
            eventos_filtrados.append(e)
        elif filtro_data == "Eventos Passados" and data_evento < data_hoje:
            eventos_filtrados.append(e)
        elif filtro_data == "Todos":
            eventos_filtrados.append(e)

    # Ordena: Próximos (crescente), Passados (decrescente)
    if filtro_data == "Próximos Eventos":
        eventos_ordenados = sorted(eventos_filtrados, key=lambda e: e["data"], reverse=False)
    else:
        eventos_ordenados = sorted(eventos_filtrados, key=lambda e: e["data"], reverse=True)
        
    st.info(f"Mostrando **{len(eventos_ordenados)}** eventos.")

    # 2. Exibição Detalhada com Edição
    for evento in eventos_ordenados:
        
        # Inicializa estado de edição
        if f"editando_{evento['id']}" not in st.session_state:
            st.session_state[f"editando_{evento['id']}"] = False

        if st.session_state[f"editando_{evento['id']}"]:
            # --- Modo de Edição ---
            exibir_form_edicao(evento, eventos)
        else:
            # --- Modo de Visualização ---
            data_formatada = datetime.strptime(evento['data'], "%Y-%m-%d").strftime("%d/%m/%Y")
            
            # Título do expander com emoji de status
            status_emoji = "🟢" if datetime.strptime(evento['data'], "%Y-%m-%d").date() >= date.today() else "⚪"
            
            with st.expander(f"{status_emoji} **{evento['titulo']}** — {data_formatada} às {evento['horario']}", expanded=False):
                col_info, col_botoes = st.columns([3, 1])

                with col_info:
                    st.markdown(f"**Local:** {evento['local']}")
                    st.markdown(f"**Responsável:** {evento['responsavel']}")
                    st.markdown(f"**Descrição:** {evento['descricao']}")
                    st.caption(f"ID: {evento['id'][:8]} | Criado em: {evento.get('criado_em', 'N/A')}")
                
                with col_botoes:
                    if col_botoes.button("✏️ Editar", key=f"btn_editar_{evento['id']}", use_container_width=True):
                        st.session_state[f"editando_{evento['id']}"] = True
                        st.rerun()

                    if col_botoes.button("🗑️ Excluir", key=f"btn_excluir_{evento['id']}", use_container_width=True, type="secondary"):
                        eventos = [e for e in eventos if e["id"] != evento["id"]]
                        salvar_eventos(eventos)
                        st.success("Evento excluído com sucesso.")
                        st.rerun()

def exibir_form_edicao(evento, eventos):
    """Formulário para editar um evento."""
    st.subheader(f"✏️ Editando: {evento['titulo']}")

    with st.form(f"form_editar_{evento['id']}"):
        
        # Pré-populando os valores
        data_atual = datetime.strptime(evento["data"], "%Y-%m-%d").date()
        horario_atual = datetime.strptime(evento["horario"], "%H:%M:%S").time()

        col_titulo, col_responsavel = st.columns([2, 1])
        with col_titulo:
            titulo_edit = st.text_input("Título do Evento *", value=evento["titulo"])
        with col_responsavel:
            responsavel_edit = st.text_input("Responsável / Líder *", value=evento["responsavel"])
            
        col_data, col_horario = st.columns(2)
        with col_data:
            data_edit = st.date_input("Data do Evento *", value=data_atual, min_value=date.today())
        with col_horario:
            horario_edit = st.time_input("Horário *", value=horario_atual)
        
        local_edit = st.text_input("Local", value=evento["local"])
        descricao_edit = st.text_area("Descrição do Evento", value=evento["descricao"])

        st.markdown("---")
        col_salvar, col_cancelar = st.columns(2)
        salvar = col_salvar.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
        cancelar = col_cancelar.form_submit_button("❌ Cancelar Edição", use_container_width=True)

        if salvar:
            if not titulo_edit or not responsavel_edit:
                st.error("O Título e o Responsável são obrigatórios.")
                return

            # Encontra e atualiza o evento na lista
            for i, e in enumerate(eventos):
                if e["id"] == evento["id"]:
                    eventos[i].update({
                        "titulo": titulo_edit,
                        "data": str(data_edit),
                        "horario": str(horario_edit),
                        "local": local_edit,
                        "responsavel": responsavel_edit,
                        "descricao": descricao_edit,
                    })
                    break
            
            salvar_eventos(eventos)
            st.success("✅ Evento atualizado com sucesso!")
            st.session_state[f"editando_{evento['id']}"] = False
            st.rerun()
            
        if cancelar:
            st.session_state[f"editando_{evento['id']}"] = False
            st.rerun()
            
def exibir():
    st.title("📅 Gerenciamento de Eventos")
    os.makedirs(os.path.dirname(CAMINHO_EVENTOS) or '.', exist_ok=True)
    eventos = carregar_eventos()

    aba = st.radio("Escolha uma opção:", ["➕ Novo Evento", "📋 Lista de Eventos"], horizontal=True)

    st.markdown("---")

    if aba == "➕ Novo Evento":
        exibir_form_cadastro(eventos)

    elif aba == "📋 Lista de Eventos":
        listar_eventos(eventos)

if __name__ == '__main__':
    exibir()