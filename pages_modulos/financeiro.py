import streamlit as st
import os
import json
import uuid
from datetime import datetime, date
from io import BytesIO
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

CAMINHO_FINANCEIRO = "data/financeiro.json"
CAMINHO_MEMBROS = "data/membros.json"

# Categorias aprimoradas
CATEGORIAS_ENTRADA = ["Dízimo", "Oferta", "Doação Específica", "Renda de Eventos", "Outra Receita"]
CATEGORIAS_SAIDA = ["Aluguel/IPTU", "Luz/Água/Telefone", "Salários/Pró-Labore", "Manutenção/Reformas", "Missões", "Ação Social", "Outra Despesa"]
MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

# --- Funções de Leitura/Escrita ---

def carregar_json(caminho):
    """Carrega a lista de dados do arquivo JSON."""
    os.makedirs(os.path.dirname(caminho) or '.', exist_ok=True)
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f) or []
        except json.JSONDecodeError:
            return []
    return []

def salvar_json(dados, caminho):
    """Salva a lista de dados no arquivo JSON."""
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# --- Funções de Relatório PDF ---

def gerar_pdf_analise(dados):
    """Gera um PDF detalhado da análise financeira."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("💰 Relatório Financeiro Detalhado da Igreja", styles["Heading1"]))
    elements.append(Spacer(1, 12))

    total_entradas = sum(d["valor"] for d in dados if d["tipo"] == "Entrada")
    total_saidas = sum(d["valor"] for d in dados if d["tipo"] == "Saída")
    saldo = total_entradas - total_saidas

    elements.append(Paragraph(f"**Total de Entradas:** R$ {total_entradas:,.2f}", styles["Normal"]))
    elements.append(Paragraph(f"**Total de Saídas:** R$ {total_saidas:,.2f}", styles["Normal"]))
    elements.append(Paragraph(f"**Saldo Total:** R$ {saldo:,.2f}", styles["Heading3"]))
    elements.append(Spacer(1, 18))

    # Tabela de dados
    dados_tabela = [["Data", "Tipo", "Categoria", "Valor", "Descrição"]]
    for d in sorted(dados, key=lambda x: x["data"], reverse=True):
        dados_tabela.append([
            d.get("data", "-"),
            d.get("tipo", "-"),
            d.get("categoria", "-"),
            f"R$ {d.get('valor', 0):,.2f}",
            d.get("descricao", "-")
        ])

    tabela = Table(dados_tabela, colWidths=[60, 40, 90, 60, 150], repeatRows=1)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (3,1), (3,-1), 'RIGHT'),
    ]))
    elements.append(Paragraph("Histórico de Movimentações:", styles["Heading3"]))
    elements.append(Spacer(1, 6))
    elements.append(tabela)
    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- Funções de Exibição de Telas ---

def exibir_registro_movimento(dados, nomes_membros):
    """Exibe o formulário de registro de entrada/saída."""
    st.subheader("➕ Registrar Nova Movimentação")
    
    with st.form("form_financeiro", clear_on_submit=True):
        
        # Colunas 1: Tipo e Categoria
        col_tipo, col_categoria = st.columns(2)
        with col_tipo:
            tipo = st.selectbox("Tipo de Movimento *", ["Entrada", "Saída"])
        with col_categoria:
            categorias_disponiveis = CATEGORIAS_ENTRADA if tipo == "Entrada" else CATEGORIAS_SAIDA
            categoria = st.selectbox("Categoria *", categorias_disponiveis)

        # Colunas 2: Valor e Data
        col_valor, col_data = st.columns(2)
        with col_valor:
            valor = st.number_input("Valor (R$)*", min_value=0.01, format="%.2f", step=0.01)
        with col_data:
            data = st.date_input("Data do Movimento *", value=date.today())

        # Mês de Referência
        mes_referencia = st.selectbox("📅 Mês de Referência", MESES, index=datetime.now().month - 1)
        
        # Dizimista (aparece apenas para Dízimo)
        dizimista = ""
        if categoria == "Dízimo" and tipo == "Entrada" and nomes_membros:
            st.markdown("---")
            dizimista = st.selectbox("Selecione o membro dizimista (Opcional)", ["Não Identificado"] + nomes_membros)

        descricao = st.text_input("Descrição (Obrigatório)*", placeholder="Ex: Pagamento da conta de luz de Outubro")
        observacoes = st.text_area("Observações (Opcional)")

        st.markdown("---")
        enviado = st.form_submit_button("💾 Salvar Registro", type="primary", use_container_width=True)

        if enviado:
            if valor <= 0 or not descricao:
                st.error("Por favor, preencha o **Valor** e a **Descrição**.")
                return

            novo = {
                "id": str(uuid.uuid4()),
                "tipo": tipo,
                "categoria": categoria,
                "valor": valor,
                "data": str(data),
                "mes_referencia": mes_referencia,
                "descricao": descricao,
                "observacoes": observacoes,
                "dizimista": dizimista if dizimista != "Não Identificado" else "",
                "registrado_em": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            dados.append(novo)
            salvar_json(dados, CAMINHO_FINANCEIRO)
            st.session_state["financeiro_sucesso"] = True
            st.rerun()

    if st.session_state.get("financeiro_sucesso"):
        st.success("✅ Registro salvo com sucesso!")
        del st.session_state["financeiro_sucesso"]

def exibir_historico_e_balanco(dados, nomes_membros):
    """Exibe o Balanço, Métricas, Gráficos e a Tabela de Ação."""
    if not dados:
        st.info("Nenhuma movimentação registrada ainda. Registre a primeira na aba '➕ Registrar Movimento'.")
        return

    df = pd.DataFrame(dados)
    df['data'] = pd.to_datetime(df['data'])
    
    # Filtros de Período
    st.markdown("### 🔎 Filtro de Período")
    col_inicio, col_fim = st.columns(2)
    data_min = df['data'].min().date()
    data_max = df['data'].max().date()
    
    filtro_inicio = col_inicio.date_input("Data Inicial", value=data_min, min_value=data_min, max_value=data_max)
    filtro_fim = col_fim.date_input("Data Final", value=data_max, min_value=data_min, max_value=data_max)
    
    dados_filtrados = df[(df['data'].dt.date >= filtro_inicio) & (df['data'].dt.date <= filtro_fim)]
    
    # 1. Visão Geral (Métricas)
    st.markdown("---")
    st.markdown("## 📊 Visão Geral do Caixa")

    total_entradas = dados_filtrados[dados_filtrados['tipo'] == 'Entrada']['valor'].sum()
    total_saidas = dados_filtrados[dados_filtrados['tipo'] == 'Saída']['valor'].sum()
    saldo = total_entradas - total_saidas
    
    col1, col2, col3 = st.columns(3)
    col1.metric("💸 Total Entradas", f"R$ {total_entradas:,.2f}")
    col2.metric("💵 Total Saídas", f"R$ {total_saidas:,.2f}")
    col3.metric("📈 Saldo no Período", f"R$ {saldo:,.2f}", delta_color=("normal" if saldo >= 0 else "inverse"))
    
    # 2. Balanço por Categoria (Gráficos)
    st.markdown("---")
    st.markdown("## 🧾 Balanço por Categoria")
    
    col_grafico1, col_grafico2 = st.columns(2)
    
    # Distribuição de Entradas
    entradas_cat = dados_filtrados[dados_filtrados['tipo'] == 'Entrada'].groupby('categoria')['valor'].sum().sort_values(ascending=False)
    if not entradas_cat.empty:
        col_grafico1.markdown("#### Distribuição de Receitas")
        col_grafico1.dataframe(entradas_cat.apply(lambda x: f"R$ {x:,.2f}"), use_container_width=True)
        col_grafico1.bar_chart(entradas_cat)
    else:
        col_grafico1.info("Sem Entradas no período.")
    
    # Distribuição de Saídas
    saidas_cat = dados_filtrados[dados_filtrados['tipo'] == 'Saída'].groupby('categoria')['valor'].sum().sort_values(ascending=False)
    if not saidas_cat.empty:
        col_grafico2.markdown("#### Distribuição de Despesas")
        col_grafico2.dataframe(saidas_cat.apply(lambda x: f"R$ {x:,.2f}"), use_container_width=True)
        col_grafico2.bar_chart(saidas_cat)
    else:
        col_grafico2.info("Sem Saídas no período.")

    # 3. Histórico de Movimentações (Tabela de Ação)
    st.markdown("---")
    st.markdown("## 📋 Histórico Detalhado (Selecionar Linha para Ação)")
    
    # Botão de Exportar PDF
    col_pdf, col_spacer = st.columns([1, 3])
    with col_pdf:
         st.download_button(
            "📥 Baixar PDF do Balanço",
            data=gerar_pdf_analise(dados_filtrados.to_dict('records')),
            file_name=f"balanco_financeiro_{filtro_inicio.strftime('%Y%m%d')}_a_{filtro_fim.strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    # Tabela para seleção
    dados_tabela = dados_filtrados[['data', 'tipo', 'categoria', 'valor', 'descricao', 'dizimista', 'id']].rename(columns={
        'data': 'Data', 'tipo': 'Tipo', 'categoria': 'Categoria', 'valor': 'Valor (R$)', 'descricao': 'Descrição', 'dizimista': 'Dizimista'
    })
    
    dados_tabela['Valor (R$)'] = dados_tabela['Valor (R$)'].apply(lambda x: f"R$ {x:,.2f}")
    
    if "edicao_financeira_id" not in st.session_state:
        st.session_state["edicao_financeira_id"] = None

    # Exibe a tabela para seleção
    st.dataframe(
        dados_tabela.drop(columns=['id']),
        hide_index=True,
        use_container_width=True,
        on_select="rerun",
        selection_mode="single-row" 
    )
    
    # Lógica de Edição/Exclusão via seleção da linha
    selecao = st.session_state.get('dataframe_select_rows')
    if selecao and selecao.get('selection') and len(selecao['selection']['rows']) > 0:
        index_selecionado = selecao['selection']['rows'][0]
        id_selecionado = dados_filtrados.iloc[index_selecionado]['id']
        movimento_selecionado = df[df['id'] == id_selecionado].iloc[0].to_dict()
        
        st.markdown("---")
        st.markdown(f"### ⚙️ Ação: {movimento_selecionado['descricao'][:50]}...")
        
        col_edita, col_exclui = st.columns(2)
        
        if col_edita.button("✏️ Editar Movimento", key="btn_edita_mov", use_container_width=True, type="primary"):
            st.session_state["edicao_financeira_id"] = id_selecionado
            st.rerun()

        if col_exclui.button("🗑️ Excluir Movimento", key="btn_exclui_mov", use_container_width=True, type="secondary"):
            dados_atualizados = [d for d in dados if d["id"] != id_selecionado]
            salvar_json(dados_atualizados, CAMINHO_FINANCEIRO)
            st.success("Movimentação excluída com sucesso.")
            st.rerun()

def exibir_form_edicao_historico(dados):
    """Exibe o formulário de edição para um item selecionado."""
    mov_id = st.session_state["edicao_financeira_id"]
    mov_original = next((d for d in dados if d["id"] == mov_id), None)

    if not mov_original:
        st.error("Erro: Movimentação não encontrada para edição.")
        st.session_state["edicao_financeira_id"] = None
        return

    st.header(f"✏️ Editando: {mov_original['descricao'][:50]}...")
    
    with st.form("form_edicao_movimento"):
        st.info(f"Tipo: **{mov_original['tipo']}** | Categoria: **{mov_original['categoria']}**")

        col_valor_edit, col_data_edit = st.columns(2)
        with col_valor_edit:
             novo_valor = st.number_input("Valor (R$)*", value=mov_original["valor"], min_value=0.01, format="%.2f", step=0.01)
        with col_data_edit:
             novo_data = st.date_input("Data do Movimento *", value=datetime.strptime(mov_original["data"], '%Y-%m-%d').date())

        novo_mes = st.selectbox("📅 Mês de Referência", MESES, index=MESES.index(mov_original["mes_referencia"]))
        
        # Lógica de dizimista para edição
        novo_dizimista = mov_original.get("dizimista", "")
        if mov_original["categoria"] == "Dízimo":
            membros = carregar_json(CAMINHO_MEMBROS)
            nomes_membros = [m["nome"] for m in membros]
            # Encontra o índice para pré-seleção
            default_options = ["Não Identificado"] + nomes_membros
            try:
                default_index = default_options.index(novo_dizimista) if novo_dizimista else 0
            except ValueError:
                default_index = 0
            
            novo_dizimista = st.selectbox("Membro Dizimista", default_options, index=default_index)

        nova_desc = st.text_input("Descrição*", value=mov_original["descricao"])
        nova_obs = st.text_area("Observações", value=mov_original["observacoes"])

        st.markdown("---")
        col_salva, col_cancela = st.columns(2)
        confirmado = col_salva.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True)
        cancelado = col_cancela.form_submit_button("❌ Cancelar Edição", use_container_width=True)

        if confirmado:
            if novo_valor <= 0 or not nova_desc:
                st.error("Por favor, preencha o **Valor** e a **Descrição**.")
                return

            mov_original["valor"] = novo_valor
            mov_original["data"] = str(novo_data)
            mov_original["mes_referencia"] = novo_mes
            mov_original["descricao"] = nova_desc
            mov_original["observacoes"] = nova_obs
            mov_original["dizimista"] = novo_dizimista if novo_dizimista != "Não Identificado" else ""
            
            salvar_json(dados, CAMINHO_FINANCEIRO)
            st.success("Movimentação atualizada com sucesso!")
            st.session_state["edicao_financeira_id"] = None
            st.rerun()

        if cancelado:
             st.session_state["edicao_financeira_id"] = None
             st.rerun()

# --- Função Principal ---

def exibir():
    st.title("💰 Gestão Financeira da Igreja")
    
    # Carrega dados
    dados = carregar_json(CAMINHO_FINANCEIRO)
    membros = carregar_json(CAMINHO_MEMBROS)
    nomes_membros = [m["nome"] for m in membros]

    # Abas
    aba = st.radio("Selecione:", ["➕ Registrar Movimento", "📊 Balanço e Análise"], horizontal=True)

    st.markdown("---")

    # Controla a exibição do formulário de edição
    if st.session_state.get("edicao_financeira_id"):
        exibir_form_edicao_historico(dados)
    elif aba == "➕ Registrar Movimento":
        exibir_registro_movimento(dados, nomes_membros)
    elif aba == "📊 Balanço e Análise":
        exibir_historico_e_balanco(dados, nomes_membros)

if __name__ == '__main__':
    exibir()