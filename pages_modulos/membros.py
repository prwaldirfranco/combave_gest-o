import streamlit as st
import json
import os
from datetime import datetime, date
from PIL import Image
import uuid
# Para aprimorar a visualização dos dados na lista
import pandas as pd 

# --- Configurações de Caminho ---
CAMINHO_DADOS = "data/membros.json"
CAMINHO_FOTOS = "data/fotos_membros"
os.makedirs(CAMINHO_FOTOS, exist_ok=True)
# --------------------------------

def carregar_membros():
    """Carrega a lista de membros do arquivo JSON."""
    if os.path.exists(CAMINHO_DADOS):
        try:
            with open(CAMINHO_DADOS, "r", encoding="utf-8") as f:
                # Garante que, se o arquivo estiver vazio, retorna uma lista vazia
                return json.load(f) or []
        except json.JSONDecodeError:
            return []
    return []

def salvar_membros(membros):
    """Salva a lista de membros no arquivo JSON."""
    with open(CAMINHO_DADOS, "w", encoding="utf-8") as f:
        json.dump(membros, f, indent=4, ensure_ascii=False)

def exibir():
    st.title("👥 Gerenciamento de Membros")
    
    # Adicionando um container para o rádio, que fica mais limpo
    with st.container(border=True):
        aba = st.radio("Selecione a ação:", ["➕ Cadastrar Membro", "📋 Lista de Membros", "📈 Estatísticas Rápidas"], horizontal=True)

    st.markdown("---") # Linha de separação

    if aba == "➕ Cadastrar Membro":
        # Melhoria: Organiza o formulário em colunas para melhor usabilidade
        cadastrar_membro_form()

    elif aba == "📋 Lista de Membros":
        # Melhoria: Função dedicada para listagem e edição/exclusão
        listar_membros()
        
    elif aba == "📈 Estatísticas Rápidas":
        # Nova Aba: Visualização rápida de dados
        exibir_estatisticas()


# --- Funções para Melhoria de Organização e Reuso ---

def cadastrar_membro_form():
    """Função dedicada ao formulário de cadastro."""
    st.subheader("📝 Novo Cadastro")
    
    with st.form("form_membro", clear_on_submit=True):
        
        # 1. Dados Pessoais (Colunas)
        st.subheader("👤 Dados Pessoais")
        col_nome, col_cpf_rg = st.columns([2, 1])
        col_nasc, col_funcao, col_status = st.columns(3)
        
        with col_nome:
            nome = st.text_input("Nome Completo *", help="Campo obrigatório")
        
        with col_cpf_rg:
            cpf = st.text_input("CPF", placeholder="Ex: 000.000.000-00")
            rg = st.text_input("RG")
        
        with col_nasc:
            nascimento = st.date_input("Data de Nascimento", min_value=date(1900, 1, 1), value=date.today())
        
        with col_funcao:
            opcoes_funcao = ["Membro", "Pastor", "Diácono", "Evangelista", "Visitante", "Lider", "Outro"]
            funcao = st.selectbox("Função na Igreja *", opcoes_funcao, help="Campo obrigatório")
        
        with col_status:
            status = st.selectbox("Status", ["Ativo", "Inativo", "Afastado"])
        
        # 2. Contato
        st.markdown("---")
        st.subheader("📞 Contato")
        col_tel, col_email = st.columns(2)
        
        with col_tel:
            telefone = st.text_input("Telefone / WhatsApp", placeholder="Ex: (99) 99999-9999")
        
        with col_email:
            email = st.text_input("Email")
        
        # 3. Endereço
        st.markdown("---")
        st.subheader("🏠 Endereço")
        col_cep, col_rua = st.columns([1, 3])
        col_num, col_bairro = st.columns(2)
        col_cidade, col_estado = st.columns(2)
        
        with col_cep:
            cep = st.text_input("CEP", placeholder="Ex: 00000-000")
        with col_rua:
            rua = st.text_input("Rua")
        with col_num:
            numero = st.text_input("Número")
        with col_bairro:
            bairro = st.text_input("Bairro")
        with col_cidade:
            cidade = st.text_input("Cidade")
        with col_estado:
            estado = st.text_input("Estado")
            
        # 4. Foto e Observações
        st.markdown("---")
        col_obs, col_foto = st.columns([3, 1])
        
        with col_foto:
             foto = st.file_uploader("🖼️ Foto do Membro", type=["jpg", "jpeg", "png"])
        
        with col_obs:
            observacoes = st.text_area("📝 Observações (Anotações adicionais)")
        
        st.markdown("---")
        enviado = st.form_submit_button("💾 Salvar Novo Membro", type="primary", use_container_width=True)
        
        # Lógica de Salvamento e Validação
        if enviado:
            if not nome or not funcao:
                st.error("Campos marcados com * são obrigatórios (Nome Completo e Função na Igreja).")
                return

            membros = carregar_membros()
            id_membro = str(uuid.uuid4())

            # Lógica de salvar foto
            caminho_foto_salva = ""
            if foto:
                try:
                    extensao = foto.name.split('.')[-1]
                    nome_arquivo = f"{id_membro}.{extensao}"
                    caminho_foto_salva = os.path.join(CAMINHO_FOTOS, nome_arquivo)
                    
                    # Salva a imagem
                    with open(caminho_foto_salva, "wb") as f:
                        f.write(foto.read())
                    st.toast("Foto salva!", icon="📷")
                except Exception as e:
                     st.warning(f"Erro ao salvar a foto: {e}")
                     caminho_foto_salva = ""

            # Cria o objeto membro
            novo_membro = {
                "id": id_membro,
                "nome": nome,
                "cpf": cpf,
                "rg": rg,
                "nascimento": str(nascimento),
                "funcao": funcao,
                "status": status,
                "telefone": telefone,
                "email": email,
                "cep": cep,
                "rua": rua,
                "numero": numero,
                "bairro": bairro,
                "cidade": cidade,
                "estado": estado,
                "observacoes": observacoes,
                "foto": caminho_foto_salva,
                "cadastrado_em": str(datetime.now().strftime("%d/%m/%Y %H:%M"))
            }

            membros.append(novo_membro)
            salvar_membros(membros)
            st.success("✅ Membro cadastrado com sucesso! Recarregando...")
            # Não usamos st.rerun() dentro de um form, mas a mensagem é exibida.

def listar_membros():
    """Função dedicada à listagem, busca, edição e exclusão de membros."""
    membros = carregar_membros()
    st.subheader("📋 Membros Cadastrados")

    if not membros:
        st.info("Nenhum membro cadastrado ainda.")
        return

    # Melhoria: Filtragem mais robusta
    col_busca, col_status_filtro = st.columns([3, 1])
    
    with col_busca:
        busca = st.text_input("🔍 Pesquisar por Nome, CPF ou Telefone", key="busca_membro")
    
    with col_status_filtro:
        filtro_status = st.selectbox("Filtrar Status", ["Todos", "Ativo", "Inativo", "Afastado"], index=0)

    # Lógica de Filtragem
    membros_filtrados = membros
    if filtro_status != "Todos":
        membros_filtrados = [m for m in membros_filtrados if m.get("status") == filtro_status]

    if busca:
        busca_lower = busca.lower()
        membros_filtrados = [
            m for m in membros_filtrados 
            if busca_lower in m["nome"].lower() or 
               busca_lower in m.get("cpf", "").lower() or 
               busca_lower in m.get("telefone", "").lower()
        ]

    st.info(f"Mostrando **{len(membros_filtrados)}** de **{len(membros)}** membros.")
    
    if not membros_filtrados:
        st.warning("Nenhum membro encontrado com os filtros aplicados.")
        return

    # Melhoria: Tabela de resumo (para visibilidade rápida)
    df_membros = pd.DataFrame(membros_filtrados)
    df_exibicao = df_membros[['nome', 'funcao', 'status', 'telefone', 'cidade']]
    df_exibicao.columns = ['Nome', 'Função', 'Status', 'Telefone', 'Cidade']
    st.dataframe(df_exibicao, use_container_width=True, hide_index=True)
    
    st.markdown("---")

    # Exibição Detalhada e Edição/Exclusão
    for membro in membros_filtrados:
        # A chave de estado para controle de edição é crucial
        if f"editando_{membro['id']}" not in st.session_state:
            st.session_state[f"editando_{membro['id']}"] = False

        if st.session_state[f"editando_{membro['id']}"]:
            # --- Modo de Edição ---
            exibir_form_edicao(membro, membros)
            
        else:
            # --- Modo de Visualização ---
            with st.expander(f"**{membro['nome']}** ({membro.get('funcao', '')}) - Status: {membro.get('status', '')}", expanded=False):
                col_info, col_botoes = st.columns([3, 1])
                
                with col_botoes:
                    if st.button("✏️ Editar", key=f"btn_editar_{membro['id']}", use_container_width=True):
                        st.session_state[f"editando_{membro['id']}"] = True
                        st.rerun() # Recarrega para mostrar o formulário de edição

                    if st.button("🗑️ Excluir", key=f"btn_excluir_{membro['id']}", use_container_width=True):
                        excluir_membro(membro, membros)
                        
                with col_info:
                    exibir_detalhes_membro(membro)

def exibir_detalhes_membro(membro):
    """Exibe os detalhes de um membro dentro do expander."""
    cols_detalhe = st.columns([1, 2])
    
    # Coluna 1: Foto
    if membro.get("foto") and os.path.exists(membro["foto"]):
        cols_detalhe[0].image(membro["foto"], width=150)
    else:
        cols_detalhe[0].markdown("🖼️ **Sem Foto**")

    # Coluna 2: Dados
    with cols_detalhe[1]:
        # Formatação de data
        try:
            nascimento_formatada = datetime.strptime(membro["nascimento"], "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
             nascimento_formatada = membro["nascimento"]
             
        # Tabela simples para organização
        dados_detalhes = {
            "ID": membro.get('id'),
            "Nascimento": nascimento_formatada,
            "CPF/RG": f"{membro.get('cpf', '')} / {membro.get('rg', '')}",
            "Telefone": membro.get('telefone', ''),
            "Email": membro.get('email', '')
        }
        st.json(dados_detalhes)
        
        st.markdown(f"**Endereço:** {membro.get('rua', '')}, {membro.get('numero', '')} - {membro.get('bairro', '')}, {membro.get('cidade', '')} - {membro.get('estado', '')} | CEP: {membro.get('cep', '')}")
        st.markdown(f"**Observações:** *{membro.get('observacoes', 'Nenhuma.')}*")
        st.caption(f"Cadastrado em: {membro.get('cadastrado_em', 'N/A')}")

def exibir_form_edicao(membro, membros):
    """Formulário de edição para um membro específico."""
    st.subheader(f"✏️ Editando: {membro['nome']}")
    with st.form(f"form_editar_{membro['id']}"):
        # Pega a data de nascimento atual para pré-preencher o date_input
        try:
            data_nasc_atual = datetime.strptime(membro["nascimento"], "%Y-%m-%d").date()
        except ValueError:
            data_nasc_atual = date.today()
            
        # Campos de edição com colunas
        col_nome, col_cpf_rg = st.columns([2, 1])
        with col_nome:
            nome_edit = st.text_input("Nome Completo", value=membro["nome"])
        with col_cpf_rg:
            cpf_edit = st.text_input("CPF", value=membro["cpf"])
            rg_edit = st.text_input("RG", value=membro["rg"])

        col_nasc, col_funcao, col_status = st.columns(3)
        with col_nasc:
            nascimento_edit = st.date_input("Data de Nascimento", value=data_nasc_atual, min_value=date(1900, 1, 1))
        with col_funcao:
            opcoes_funcao = ["Membro", "Pastor", "Diácono", "Evangelista", "Visitante", "Lider", "Outro"]
            funcao_edit = st.selectbox("Função", opcoes_funcao, index=opcoes_funcao.index(membro["funcao"]))
        with col_status:
            opcoes_status = ["Ativo", "Inativo", "Afastado"]
            status_edit = st.selectbox("Status", opcoes_status, index=opcoes_status.index(membro["status"]))
        
        # Contato e Endereço
        col_tel, col_email = st.columns(2)
        with col_tel:
            telefone_edit = st.text_input("Telefone", value=membro["telefone"])
        with col_email:
            email_edit = st.text_input("Email", value=membro["email"])
        
        col_cep, col_rua = st.columns([1, 3])
        with col_cep:
            cep_edit = st.text_input("CEP", value=membro["cep"])
        with col_rua:
            rua_edit = st.text_input("Rua", value=membro["rua"])
            
        col_num, col_bairro = st.columns(2)
        with col_num:
            numero_edit = st.text_input("Número", value=membro["numero"])
        with col_bairro:
            bairro_edit = st.text_input("Bairro", value=membro["bairro"])
            
        col_cidade, col_estado = st.columns(2)
        with col_cidade:
            cidade_edit = st.text_input("Cidade", value=membro["cidade"])
        with col_estado:
            estado_edit = st.text_input("Estado", value=membro["estado"])
            
        observacoes_edit = st.text_area("Observações", value=membro["observacoes"])
        
        st.markdown("---")
        col_salvar, col_cancelar = st.columns(2)

        salvar = col_salvar.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
        cancelar = col_cancelar.form_submit_button("❌ Cancelar Edição", use_container_width=True)

        if salvar:
            membro.update({
                "nome": nome_edit, "cpf": cpf_edit, "rg": rg_edit,
                "nascimento": str(nascimento_edit), "funcao": funcao_edit,
                "status": status_edit, "telefone": telefone_edit, 
                "email": email_edit, "cep": cep_edit, "rua": rua_edit,
                "numero": numero_edit, "bairro": bairro_edit,
                "cidade": cidade_edit, "estado": estado_edit,
                "observacoes": observacoes_edit,
            })
            salvar_membros(membros)
            st.success("✅ Membro atualizado com sucesso!")
            st.session_state[f"editando_{membro['id']}"] = False
            st.rerun()
            
        if cancelar:
            st.session_state[f"editando_{membro['id']}"] = False
            st.rerun()

def excluir_membro(membro, membros):
    """Remove um membro e sua foto (se existir)."""
    membros[:] = [m for m in membros if m["id"] != membro["id"]]
    salvar_membros(membros)
    if membro.get("foto") and os.path.exists(membro["foto"]):
        os.remove(membro["foto"])
    st.success(f"Membro **{membro['nome']}** excluído com sucesso.")
    st.rerun()

def exibir_estatisticas():
    """Exibe estatísticas rápidas sobre os membros."""
    membros = carregar_membros()
    st.subheader("📊 Resumo dos Membros")
    
    total_membros = len(membros)
    if total_membros == 0:
        st.info("Cadastre o primeiro membro para ver as estatísticas!")
        return
        
    membros_ativos = len([m for m in membros if m.get("status") == "Ativo"])
    membros_inativos = len([m for m in membros if m.get("status") == "Inativo"])
    membros_afastados = len([m for m in membros if m.get("status") == "Afastado"])

    col_total, col_ativos, col_inativos = st.columns(3)
    
    col_total.metric("Total de Membros", total_membros)
    col_ativos.metric("Membros Ativos", membros_ativos, f"{membros_ativos - membros_inativos}") # Um delta simples
    col_inativos.metric("Membros Inativos/Afastados", membros_inativos + membros_afastados)

    st.markdown("---")
    st.subheader("Distribuição por Função")
    funcoes = [m.get("funcao", "Não Especificado") for m in membros]
    funcoes_counts = pd.Series(funcoes).value_counts().to_dict()
    
    df_funcoes = pd.DataFrame(list(funcoes_counts.items()), columns=['Função', 'Contagem'])
    
    st.bar_chart(df_funcoes, x='Função', y='Contagem')


if __name__ == '__main__':
    exibir()