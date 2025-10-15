import streamlit as st
import json
import os
import pandas as pd
from pathlib import Path
from io import BytesIO
from datetime import datetime

# --- Configuração de Caminhos ---
CAMINHO_BASE = Path("data")
CAMINHO_FORMULARIOS = CAMINHO_BASE / "formularios.json"
CAMINHO_RESPOSTAS = CAMINHO_BASE / "respostas_formularios.json"

# Garante que o diretório 'data' exista
CAMINHO_BASE.mkdir(exist_ok=True)

# --- Funções de Leitura Segura ---

def carregar_json_seguro(caminho):
    """Carrega a lista de dados do arquivo JSON de forma segura."""
    if caminho.exists():
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = f.read()
                # Retorna a lista se o arquivo não estiver vazio
                return json.loads(conteudo) if conteudo else []
        except json.JSONDecodeError:
            return []
    return []

def carregar_formularios():
    return carregar_json_seguro(CAMINHO_FORMULARIOS)

def carregar_respostas():
    return carregar_json_seguro(CAMINHO_RESPOSTAS)

# --- Módulo Principal de Visualização ---

def exibir_respostas_formularios():
    st.title("📬 Análise de Respostas dos Formulários")
    
    formularios = carregar_formularios()
    respostas = carregar_respostas()

    if not formularios:
        st.warning("⚠️ Nenhum formulário criado ainda. Crie um no módulo de Gerenciamento de Formulários.")
        return

    if not respostas:
        st.info("ℹ️ Nenhuma resposta registrada ainda.")
        return

    # 1. Seleção do Formulário
    opcoes_formularios = {f["titulo"]: f["id"] for f in formularios}
    titulo_escolhido = st.selectbox("Escolha o formulário para análise:", list(opcoes_formularios.keys()))

    id_escolhido = opcoes_formularios[titulo_escolhido]
    respostas_filtradas = [r for r in respostas if r["id_formulario"] == id_escolhido]

    if not respostas_filtradas:
        st.info(f"ℹ️ Nenhuma resposta para o formulário **{titulo_escolhido}** ainda.")
        return

    st.markdown("---")
    
    # 2. Transformar as respostas em um DataFrame
    dados_plana = []
    for r in respostas_filtradas:
        linha = r.get("respostas", {}) # Pega o dicionário de respostas
        linha["ID Resposta"] = r["id_resposta"]
        linha["Enviado em"] = r["enviado_em"]
        dados_plana.append(linha)
    
    df_respostas = pd.DataFrame(dados_plana)
    
    # Reordenar colunas (colunas de metadados primeiro)
    cols = ["Enviado em", "ID Resposta"] + [col for col in df_respostas.columns if col not in ["Enviado em", "ID Resposta", "id_formulario"]]
    df_respostas = df_respostas[cols]
    
    # 3. Exibição da Tabela e Métricas
    st.subheader(f"Respostas para '{titulo_escolhido}'")
    st.markdown(f"**Total de Respostas:** `{len(df_respostas)}`")
    
    # O Streamlit renderiza os booleanos e datas de forma amigável
    st.dataframe(df_respostas, use_container_width=True, hide_index=True)

    # 4. Exportação
    st.markdown("---")
    st.subheader("Opções de Exportação")
    
    col_csv, col_excel = st.columns(2)

    # CSV
    buffer_csv = BytesIO()
    df_respostas.to_csv(buffer_csv, index=False, encoding='utf-8')
    buffer_csv.seek(0)
    col_csv.download_button(
        "📥 Baixar CSV",
        data=buffer_csv,
        file_name=f"respostas_{id_escolhido}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    # Excel
    buffer_excel = BytesIO()
    with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
        df_respostas.to_excel(writer, index=False, sheet_name='Respostas')
    buffer_excel.seek(0)
    col_excel.download_button(
        "📥 Baixar Excel",
        data=buffer_excel,
        file_name=f"respostas_{id_escolhido}_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )


if __name__ == "__main__":
    exibir_respostas_formularios()