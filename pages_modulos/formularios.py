import streamlit as st
import json
import uuid
import os
from datetime import datetime
import pandas as pd
from pathlib import Path
from io import BytesIO

# --- Configuração de Caminhos ---
CAMINHO_BASE = Path("data")
CAMINHO_FORMULARIOS = CAMINHO_BASE / "formularios.json"
CAMINHO_RESPOSTAS = CAMINHO_BASE / "respostas_formularios.json"

# Garante que o diretório 'data' exista
CAMINHO_BASE.mkdir(exist_ok=True)

# --- Funções de Leitura/Escrita ---

def carregar_json(caminho):
    """Carrega a lista de dados do arquivo JSON de forma segura."""
    if caminho.exists():
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = f.read()
                return json.loads(conteudo) if conteudo else []
        except json.JSONDecodeError:
            return []
    return []

def salvar_formularios(formularios):
    """Salva a lista de formulários."""
    with open(CAMINHO_FORMULARIOS, "w", encoding="utf-8") as f:
        json.dump(formularios, f, indent=4, ensure_ascii=False)

def carregar_respostas():
    """Carrega a lista de respostas de forma segura."""
    return carregar_json(CAMINHO_RESPOSTAS)

# --- Módulo de Criação de Formulário (Corrigido e Melhorado) ---

def criar_formulario():
    st.subheader("➕ Criar Novo Formulário Dinâmico")

    # Passo 1 - Título e Descrição
    with st.form("form_criar_formulario", clear_on_submit=True):
        st.info("Passo 1: Defina o Título e a Descrição")
        titulo = st.text_input("Título do Formulário *", key="titulo_novo")
        descricao = st.text_area("Descrição", key="descricao_nova")
        enviado = st.form_submit_button("💾 Salvar Formulário Final", type="primary")

    # Passo 2 - Adicionar Campos (fora do form)
    st.markdown("---")
    st.info("Passo 2: Adicione os Campos")

    if "campos_formulario" not in st.session_state:
        st.session_state["campos_formulario"] = []

    with st.container(border=True):
        col_add1, col_add2, col_add3, col_add4 = st.columns([3, 2, 2, 1])
        nova_pergunta = col_add1.text_input("Pergunta/Rótulo", key="nova_pergunta")
        novo_tipo = col_add2.selectbox(
            "Tipo de Campo",
            ["texto", "texto_longo", "numero", "opcoes", "data", "checkbox"],
            key="novo_tipo"
        )
        novo_obrigatorio = col_add3.checkbox("Obrigatório?", key="novo_obrigatorio")

        opcoes_str = ""
        if novo_tipo == "opcoes":
            opcoes_str = st.text_input("Opções (separadas por vírgula)", key="novas_opcoes")

        if col_add4.button("➕ Adicionar Campo", key="btn_add_campo"):
            if nova_pergunta:
                novo_campo = {
                    "id": str(uuid.uuid4()),
                    "tipo": novo_tipo,
                    "pergunta": nova_pergunta,
                    "obrigatorio": novo_obrigatorio,
                }
                if novo_tipo == "opcoes":
                    novo_campo["opcoes"] = [o.strip() for o in opcoes_str.split(",") if o.strip()]
                st.session_state["campos_formulario"].append(novo_campo)
                st.rerun()
            else:
                st.warning("O rótulo da pergunta não pode ser vazio.")

    st.markdown("#### Campos Atuais:")
    if not st.session_state.campos_formulario:
        st.info("Adicione campos acima para começar a construir seu formulário.")
        campos_para_salvar = []
    else:
        campos_para_salvar = []
        for i, campo in enumerate(st.session_state.campos_formulario):
            col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns([3, 1.5, 1, 1, 0.5])
            col_c1.markdown(f"**{campo['pergunta']}**")
            col_c2.markdown(f"`{campo['tipo'].title()}`")
            col_c3.markdown("✅ Obrigatório" if campo["obrigatorio"] else "❌ Opcional")
            if campo["tipo"] == "opcoes":
                col_c4.markdown(f"({len(campo['opcoes'])} opções)")
            if col_c5.button("🗑️", key=f"del_campo_{i}"):
                del st.session_state.campos_formulario[i]
                st.rerun()
            campos_para_salvar.append(campo)

    # Salvamento Final
    if enviado:
        if not titulo or not campos_para_salvar:
            st.warning("Preencha o título e adicione ao menos um campo.")
        else:
            formularios = carregar_json(CAMINHO_FORMULARIOS)
            novo_formulario = {
                "id": str(uuid.uuid4()),
                "titulo": titulo,
                "descricao": descricao,
                "campos": campos_para_salvar,
                "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "ativo": True,
            }
            formularios.append(novo_formulario)
            salvar_formularios(formularios)
            st.success(f"✅ Formulário '{titulo}' criado com sucesso! Use o ID: **{novo_formulario['id']}**")
            st.session_state["campos_formulario"] = []

# --- Módulo de Visualização de Formulários ---

def listar_formularios():
    st.subheader("📋 Meus Formulários Ativos")
    formularios = carregar_json(CAMINHO_FORMULARIOS)

    if not formularios:
        st.info("Nenhum formulário criado ainda. Vá em '➕ Criar Formulário' para começar.")
        return

    respostas_map = {r["id_formulario"]: r for r in carregar_respostas()}

    for f in formularios:
        num_respostas = len([r for r in respostas_map if r == f["id"]])
        with st.expander(f"**{f['titulo']}** ({num_respostas} Resposta{'s' if num_respostas != 1 else ''})"):
            st.markdown(f"**Descrição:** {f.get('descricao', '-')}")
            st.markdown(f"**Criado em:** {f.get('criado_em', '-')}")
            st.markdown("**Link Público:**")
            link_publico = f"http://localhost:8501/?id={f['id']}"
            st.code(link_publico, language="text")

            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            with col1:
                if st.button("📨 Ver Respostas", key=f"respostas_{f['id']}", use_container_width=True):
                    st.session_state["aba_selecionada"] = "📬 Ver Respostas"
                    st.session_state["form_selecionado_id"] = f["id"]
                    st.rerun()
            with col2:
                st.button("📄 Duplicar", key=f"dup_{f['id']}", use_container_width=True, disabled=True)
            with col3:
                st.button("🚫 Desativar", key=f"desativar_{f['id']}", use_container_width=True, disabled=True)
            with col4:
                if st.button("🗑️ Excluir", key=f"del_{f['id']}", use_container_width=True):
                    formularios_restantes = [x for x in carregar_json(CAMINHO_FORMULARIOS) if x["id"] != f["id"]]
                    salvar_formularios(formularios_restantes)
                    st.success("Formulário excluído com sucesso.")
                    st.rerun()

# --- Módulo de Visualização de Respostas ---

def ver_respostas_formularios(form_id=None):
    st.subheader("📬 Análise de Respostas")

    formularios = carregar_json(CAMINHO_FORMULARIOS)
    respostas = carregar_respostas()

    if not formularios:
        st.warning("Nenhum formulário encontrado.")
        return

    opcoes_formularios = {f["titulo"]: f["id"] for f in formularios}
    default_form_title = ""
    if form_id:
        form_obj = next((f for f in formularios if f["id"] == form_id), None)
        if form_obj:
            default_form_title = form_obj["titulo"]

    titulo_escolhido = st.selectbox(
        "Escolha o formulário:",
        list(opcoes_formularios.keys()),
        index=list(opcoes_formularios.keys()).index(default_form_title) if default_form_title else 0,
    )

    id_escolhido = opcoes_formularios[titulo_escolhido]
    respostas_filtradas = [r for r in respostas if r["id_formulario"] == id_escolhido]

    if not respostas_filtradas:
        st.info("Nenhuma resposta registrada ainda para este formulário.")
        return

    dados_plana = []
    for r in respostas_filtradas:
        linha = r["respostas"]
        linha["ID Resposta"] = r["id_resposta"]
        linha["Enviado em"] = r["enviado_em"]
        dados_plana.append(linha)

    df_respostas = pd.DataFrame(dados_plana)
    cols = ["Enviado em", "ID Resposta"] + [c for c in df_respostas.columns if c not in ["Enviado em", "ID Resposta", "id_formulario"]]
    df_respostas = df_respostas[cols].sort_values(by="Enviado em", ascending=False)

    st.markdown(f"**Total de Respostas:** `{len(df_respostas)}`")
    st.dataframe(df_respostas, use_container_width=True, hide_index=True)

    buffer = BytesIO()
    df_respostas.to_csv(buffer, index=False, encoding="utf-8")
    buffer.seek(0)
    st.download_button(
        "📥 Baixar Respostas (CSV)",
        data=buffer,
        file_name=f"respostas_{id_escolhido}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

# --- Função Principal de Exibição ---

def exibir():
    st.set_page_config(layout="wide")
    st.title("📝 Gerenciamento de Formulários")

    if "aba_selecionada" not in st.session_state:
        st.session_state["aba_selecionada"] = "📋 Meus Formulários"

    aba_opcoes = ["➕ Criar Formulário", "📋 Meus Formulários", "📬 Ver Respostas"]
    aba_idx = aba_opcoes.index(st.session_state.get("aba_selecionada", "📋 Meus Formulários"))

    aba = st.radio("Escolha uma opção:", aba_opcoes, index=aba_idx)
    st.session_state["aba_selecionada"] = aba
    st.markdown("---")

    if aba == "➕ Criar Formulário":
        criar_formulario()
    elif aba == "📋 Meus Formulários":
        listar_formularios()
    elif aba == "📬 Ver Respostas":
        form_id = st.session_state.pop("form_selecionado_id", None)
        ver_respostas_formularios(form_id)

    # --- Rodapé Profissional ---
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align:center; color:gray; font-size:14px;'>
        © 2025 WB Informática — Todos os direitos reservados.<br>
        📞 Suporte técnico: <strong>(22) 99239-4905</strong> |
        💻 Desenvolvido por <strong>WB Informática</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    exibir()
