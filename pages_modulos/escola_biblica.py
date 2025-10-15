import streamlit as st
import os
import json
import uuid
from datetime import datetime

CAMINHO_TURMAS = "data/escola_biblica.json"
CAMINHO_MEMBROS = "data/membros.json"

def carregar_turmas():
    if os.path.exists(CAMINHO_TURMAS):
        with open(CAMINHO_TURMAS, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def salvar_turmas(lista):
    with open(CAMINHO_TURMAS, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)

def carregar_membros():
    if os.path.exists(CAMINHO_MEMBROS):
        with open(CAMINHO_MEMBROS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def exibir():
    st.title("📚 Escola Bíblica / Discipulado")

    aba = st.radio("Selecione:", ["➕ Nova Turma", "📋 Turmas Cadastradas"])
    turmas = carregar_turmas()
    membros = carregar_membros()
    nomes_membros = [m["nome"] for m in membros]

    if aba == "➕ Nova Turma":
        with st.form("form_turma", clear_on_submit=True):
            nome = st.text_input("Nome da Turma")
            professor_nome = st.selectbox("Professor Responsável", nomes_membros)
            dia_semana = st.selectbox("Dia da Semana", ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"])
            horario = st.time_input("Horário da Aula")
            alunos = st.multiselect("Alunos", nomes_membros)
            descricao = st.text_area("Descrição / Observações")

            enviado = st.form_submit_button("💾 Salvar Turma")

            if enviado:
                nova_turma = {
                    "id": str(uuid.uuid4()),
                    "nome": nome,
                    "professor": professor_nome,
                    "dia_semana": dia_semana,
                    "horario": str(horario),
                    "alunos": alunos,
                    "descricao": descricao,
                    "criado_em": str(datetime.now())
                }
                turmas.append(nova_turma)
                salvar_turmas(turmas)
                st.success("✅ Turma cadastrada com sucesso!")
                st.rerun()

    elif aba == "📋 Turmas Cadastradas":
        if not turmas:
            st.info("Nenhuma turma cadastrada.")
            return

        for turma in turmas:
            with st.expander(f"{turma['nome']} — Prof: {turma['professor']}"):
                st.markdown(f"📆 **Dia/Horário:** {turma['dia_semana']} às {turma['horario']}")
                st.markdown(f"📝 **Descrição:** {turma['descricao']}")
                st.markdown(f"👥 **Alunos ({len(turma['alunos'])}):**")
                for aluno in turma["alunos"]:
                    st.markdown(f"- {aluno}")
                st.markdown(f"_Criado em: {turma['criado_em']}_")

                col1, col2 = st.columns([1, 1])
                if col1.button("🗑️ Excluir", key=f"del_{turma['id']}"):
                    turmas = [t for t in turmas if t["id"] != turma["id"]]
                    salvar_turmas(turmas)
                    st.success("Turma excluída.")
                    st.rerun()

                if col2.button("✏️ Editar", key=f"edit_{turma['id']}"):
                    st.session_state["editando_turma"] = turma["id"]
                    st.rerun()

        # Formulário de edição
        if "editando_turma" in st.session_state:
            turma = next((t for t in turmas if t["id"] == st.session_state["editando_turma"]), None)
            if turma:
                st.subheader(f"✏️ Editar Turma: {turma['nome']}")
                with st.form("form_editar_turma"):
                    nome = st.text_input("Nome da Turma", value=turma["nome"])
                    professor_nome = st.selectbox("Professor Responsável", nomes_membros, index=nomes_membros.index(turma["professor"]))
                    dia_semana = st.selectbox("Dia da Semana", ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"], index=["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"].index(turma["dia_semana"]))
                    horario = st.time_input("Horário da Aula")
                    alunos = st.multiselect("Alunos", nomes_membros, default=turma["alunos"])
                    descricao = st.text_area("Descrição / Observações", value=turma["descricao"])
                    salvar = st.form_submit_button("💾 Salvar Alterações")

                    if salvar:
                        turma["nome"] = nome
                        turma["professor"] = professor_nome
                        turma["dia_semana"] = dia_semana
                        turma["horario"] = str(horario)
                        turma["alunos"] = alunos
                        turma["descricao"] = descricao
                        salvar_turmas(turmas)
                        st.success("Turma atualizada com sucesso!")
                        del st.session_state["editando_turma"]
                        st.rerun()