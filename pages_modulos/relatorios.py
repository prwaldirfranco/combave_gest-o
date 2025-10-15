import streamlit as st
import os
import json
import pandas as pd
from io import BytesIO
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics

# Configuração da fonte para ReportLab (Suporte a caracteres especiais)
# Certifique-se de que a fonte 'HeiseiMin-W3' está disponível ou substitua por outra
# se você encontrar problemas de caracteres acentuados no PDF.
try:
    pdfmetrics.registerFont(UnicodeCIDFont('HeiseiMin-W3'))
except Exception:
    # Fallback simples se a fonte complexa não carregar (embora seja improvável em ambientes padrão)
    pass

# Constantes
CAMINHO_MEMBROS = "data/membros.json"
CAMINHO_FINANCEIRO = "data/financeiro.json"
CAMINHO_LOGO = "data/logo.png"
NOME_IGREJA = "Comunidade Batista Vida Efatá"

# --- Funções Auxiliares ---

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

# --- Módulo de Relatórios de Membros ---

def gerar_pdf_membros(membros, df_analise):
    """Gera o PDF com lista de membros e análise estatística."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Cabeçalho
    if os.path.exists(CAMINHO_LOGO):
        elements.append(RLImage(CAMINHO_LOGO, width=50, height=50))
    elements.append(Paragraph(f"<b>{NOME_IGREJA}</b>", styles['Heading1']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("📋 Relatório de Membros", styles['Heading2']))
    elements.append(Paragraph(f"Data de Geração: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Tabela de Análise
    elements.append(Paragraph("Estatísticas de Membros:", styles['Heading3']))
    dados_analise = [["Total", "Ativos", "Funções Únicas"]] + df_analise.values.tolist()
    
    tabela_analise = Table(dados_analise, repeatRows=1)
    tabela_analise.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.8, 0.9, 1)),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        # Usando fonte registrada para acentos
        ('FONTNAME', (0, 0), (-1, -1), 'HeiseiMin-W3'), 
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elements.append(tabela_analise)
    elements.append(Spacer(1, 18))


    # Tabela Principal
    elements.append(Paragraph("Lista Detalhada de Membros:", styles['Heading3']))
    
    membros_pdf = []
    for m in membros:
        membros_pdf.append([
            m["nome"], 
            m.get("funcao", "-"), 
            m.get("status", "-"), 
            m.get("telefone", "-")
        ])
    
    dados_lista = [["Nome", "Função", "Status", "Telefone"]] + membros_pdf
    
    col_widths = [150, 100, 70, 120]
    tabela = Table(dados_lista, colWidths=col_widths, repeatRows=1)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'HeiseiMin-W3'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
    ]))
    elements.append(tabela)
    doc.build(elements)
    buffer.seek(0)
    return buffer

def exibir_membros():
    membros = carregar_json(CAMINHO_MEMBROS)
    membros_validos = [m for m in membros if "nome" in m and "funcao" in m and "status" in m]

    st.header("👥 Relatório de Membros")
    
    if not membros_validos:
        st.info("Nenhum membro cadastrado.")
        return
        
    df_membros = pd.DataFrame(membros_validos)
    
    # 1. Filtros
    col_status, col_funcao = st.columns(2)
    status_options = ["Todos"] + df_membros["status"].unique().tolist()
    funcao_options = ["Todas"] + df_membros["funcao"].unique().tolist()
    
    status_filtro = col_status.selectbox("Filtrar por Status:", status_options)
    funcao_filtro = col_funcao.selectbox("Filtrar por Função:", funcao_options)
    
    df_filtrado = df_membros.copy()
    if status_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["status"] == status_filtro]
    if funcao_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado["funcao"] == funcao_filtro]

    membros_filtrados = df_filtrado.to_dict('records')

    # 2. Métricas
    total_membros = len(membros_validos)
    membros_ativos = len(df_membros[df_membros['status'] == 'Ativo'])
    funcoes_unicas = df_membros['funcao'].nunique()

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Membros Totais", total_membros)
    col_m2.metric("Membros Ativos", membros_ativos, delta=f"{membros_ativos/total_membros:.1%}" if total_membros else None)
    col_m3.metric("Funções na Igreja", funcoes_unicas)
    
    st.markdown("---")
    
    # DataFrame para análise no PDF
    df_analise_pdf = pd.DataFrame({
        'Total': [total_membros],
        'Ativos': [membros_ativos],
        'Funções Únicas': [funcoes_unicas]
    })
    
    # 3. Tabela de Visualização
    colunas_vis = ["nome", "funcao", "status", "telefone", "data_nascimento"]
    df_visual = df_filtrado[[c for c in colunas_vis if c in df_filtrado.columns]]
    df_visual.columns = [c.capitalize().replace("_", " ") for c in df_visual.columns]

    st.subheader(f"Lista Detalhada ({len(df_visual)} Registros)")
    st.dataframe(df_visual, use_container_width=True, hide_index=True)

    # 4. Exportações
    col_d1, col_d2, col_d3 = st.columns(3)
    
    # Excel
    buffer_excel = BytesIO()
    with pd.ExcelWriter(buffer_excel, engine="openpyxl") as writer:
        df_visual.to_excel(writer, sheet_name="Membros", index=False)
    buffer_excel.seek(0)
    col_d1.download_button("📥 Baixar Excel", data=buffer_excel, file_name="relatorio_membros_filtrado.xlsx", use_container_width=True)

    # PDF
    col_d2.download_button("📄 Baixar PDF", data=gerar_pdf_membros(membros_filtrados, df_analise_pdf), 
                           file_name="relatorio_membros_completo.pdf", mime="application/pdf", use_container_width=True)

# --- Módulo de Relatórios Financeiros ---

def gerar_pdf_financeiro(df_fin, totais):
    """Gera o PDF com o relatório financeiro, incluindo totais e saldo."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Cabeçalho
    if os.path.exists(CAMINHO_LOGO):
        elements.append(RLImage(CAMINHO_LOGO, width=50, height=50))
    elements.append(Paragraph(f"<b>{NOME_IGREJA}</b>", styles['Heading1']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("💰 Relatório Financeiro", styles['Heading2']))
    elements.append(Paragraph(f"Data de Geração: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Tabela de Totais (Resumo Principal)
    elements.append(Paragraph("Resumo Financeiro:", styles['Heading3']))
    
    dados_resumo = [
        ["Entradas", "Saídas", "Saldo Final"],
        [f"R$ {totais['Entradas']:,.2f}", f"R$ {totais['Saídas']:,.2f}", f"R$ {totais['Saldo']:,.2f}"]
    ]
    
    tabela_resumo = Table(dados_resumo, repeatRows=1)
    tabela_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.8, 1, 0.8)),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'HeiseiMin-W3'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, 1), 'RIGHT'),
    ]))
    elements.append(tabela_resumo)
    elements.append(Spacer(1, 6))
    
    # Tabela de Análise (Dizimistas e Projeção)
    dados_resumo_adicional = [
        ["Dizimistas Únicos (Filtro)", "Projeção Anual (Entradas)"],
        [f"{totais['Dizimistas']}", f"R$ {totais['Projecao']:,.2f}"]
    ]
    
    tabela_resumo_adicional = Table(dados_resumo_adicional, repeatRows=1)
    tabela_resumo_adicional.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(1, 0.95, 0.8)),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'HeiseiMin-W3'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, 1), 'RIGHT'),
    ]))
    elements.append(tabela_resumo_adicional)
    elements.append(Spacer(1, 18))

    # Tabela Detalhada (Com correção do erro 'Valor (R$) not in list')
    elements.append(Paragraph("Movimentações Detalhadas:", styles['Heading3']))
    
    colunas_tabela = df_fin.columns.tolist()
    dados = [colunas_tabela] + df_fin.values.tolist()
    
    valor_col_index = -1
    if 'Valor (R$)' in colunas_tabela:
        valor_col_index = colunas_tabela.index('Valor (R$)')
    
    if valor_col_index != -1:
        for i in range(1, len(dados)):
            valor = dados[i][valor_col_index]
            try:
                dados[i][valor_col_index] = f"R$ {float(valor):,.2f}"
            except (ValueError, TypeError):
                dados[i][valor_col_index] = str(valor)
    
    col_widths = [60, 40, 90, 60, 150, 70, 70]
    tabela = Table(dados, colWidths=col_widths[:len(colunas_tabela)], repeatRows=1)
    
    style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, -1), 'HeiseiMin-W3'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
    ]

    if valor_col_index != -1:
        style_commands.append(('ALIGN', (valor_col_index, 1), (valor_col_index, -1), 'RIGHT'))
        
    tabela.setStyle(TableStyle(style_commands))
    
    elements.append(tabela)
    doc.build(elements)
    buffer.seek(0)
    return buffer

def exibir_financeiro():
    financeiro = carregar_json(CAMINHO_FINANCEIRO)
    if not financeiro:
        st.info("Nenhum lançamento encontrado.")
        return

    st.header("💰 Relatório Financeiro")
    
    # Conversão e limpeza inicial
    df_fin_full = pd.DataFrame(financeiro)
    df_fin_full['valor'] = pd.to_numeric(df_fin_full['valor'], errors='coerce').fillna(0)
    
    # 1. Filtros (AJUSTADO AQUI)
    
    # Lista de todas as categorias únicas presentes no JSON
    # Garante que mesmo categorias novas/não padrão sejam incluídas
    tipos_disponiveis = sorted(df_fin_full['categoria'].unique().tolist())
    
    meses_disponiveis = sorted(set(f.get("mes_referencia", "") for f in financeiro if f.get("mes_referencia")))

    col1, col2, col3 = st.columns(3)
    # Agora usa a lista completa de categorias do DataFrame
    tipo_filtro = col1.selectbox("Filtrar por categoria:", ["Todos"] + tipos_disponiveis) 
    mes_filtro = col2.selectbox("Filtrar por mês de referência:", ["Todos"] + meses_disponiveis)
    mov_filtro = col3.selectbox("Filtrar por Tipo:", ["Ambos", "Entrada", "Saída"])

    # Aplicar filtros
    df_fin = df_fin_full.copy()
    if tipo_filtro != "Todos":
        df_fin = df_fin[df_fin["categoria"] == tipo_filtro]
    if mes_filtro != "Todos":
        df_fin = df_fin[df_fin["mes_referencia"] == mes_filtro]
    if mov_filtro != "Ambos":
        df_fin = df_fin[df_fin["tipo"] == mov_filtro]
    
    # 2. Cálculos e Métricas
    total_entradas = df_fin[df_fin['tipo'] == 'Entrada']['valor'].sum()
    total_saidas = df_fin[df_fin['tipo'] == 'Saída']['valor'].sum()
    saldo = total_entradas - total_saidas
    
    # Cálculo de Dizimistas do Mês (do filtro atual)
    numero_dizimistas = 0
    if mes_filtro != "Todos":
        df_dizimo_mes = df_fin[(df_fin['categoria'] == 'Dízimo') & (df_fin['dizimista'] != '')]
        numero_dizimistas = df_dizimo_mes['dizimista'].nunique()

    # Cálculo da Projeção Anual
    total_entradas_ano = df_fin_full[df_fin_full['tipo'] == 'Entrada']['valor'].sum()
    
    df_entradas_ano = df_fin_full[df_fin_full['tipo'] == 'Entrada'].copy()
    df_entradas_ano['data'] = pd.to_datetime(df_entradas_ano['data'], errors='coerce')
    df_entradas_ano['AnoMes'] = df_entradas_ano['data'].dt.to_period('M')
    
    meses_registrados_count = df_entradas_ano['AnoMes'].nunique()
    
    media_mensal = total_entradas_ano / meses_registrados_count if meses_registrados_count else 0
    projecao_anual = media_mensal * 12

    # 3. Exibição das Métricas
    st.markdown("### 📊 Resumo do Período Filtrado")
    
    # Linha 1: Entradas, Saídas, Saldo
    col_f1, col_f2, col_f3 = st.columns(3)
    col_f1.metric("Entradas Filtradas", f"R$ {total_entradas:,.2f}")
    col_f2.metric("Saídas Filtradas", f"R$ {total_saidas:,.2f}")
    col_f3.metric("Saldo do Período", f"R$ {saldo:,.2f}", delta_color=("normal" if saldo >= 0 else "inverse"))
    
    # Linha 2: Dizimistas e Projeção
    st.markdown("---")
    st.markdown("### 🎯 Análise e Projeção")
    
    col_a1, col_a2 = st.columns(2)
    if mes_filtro != "Todos":
        col_a1.metric(f"🙏 Dizimistas Únicos ({mes_filtro})", numero_dizimistas)
    else:
        col_a1.metric("🙏 Dizimistas Únicos", "Filtre o mês")
    
    col_a2.metric("🔮 Projeção Anual (Entradas)", f"R$ {projecao_anual:,.2f}")
    
    st.markdown("---")
    
    # 4. Tabela de Visualização (Com formatação)
    colunas = ["data", "tipo", "categoria", "valor", "descricao", "mes_referencia"]
    if "dizimista" in df_fin.columns:
        colunas.append("dizimista")
        
    df_visual = df_fin[colunas].copy()
    df_visual.columns = [c.capitalize().replace("_", " ") for c in df_visual.columns]
    
    # Renomeia a coluna de valor para a formatação do Streamlit/PDF
    df_visual.rename(columns={'Valor': 'Valor (R$)'}, inplace=True)
    
    def color_movimento(val):
        color = 'green' if 'Entrada' in val else 'red'
        return f'color: {color}'

    df_visual_formatado = df_visual.style.applymap(color_movimento, subset=pd.IndexSlice[:, ['Tipo']])
    df_visual_formatado = df_visual_formatado.format({'Valor (R$)': 'R$ {:,.2f}'})

    st.subheader(f"Movimentações Filtradas ({len(df_visual)} Registros)")
    st.dataframe(df_visual_formatado, use_container_width=True, hide_index=True)

    # Dicionário de totais para o PDF
    totais_pdf = {
        'Entradas': total_entradas,
        'Saídas': total_saidas,
        'Saldo': saldo,
        'Dizimistas': numero_dizimistas,
        'Projecao': projecao_anual
    }

    # 5. Exportações
    col_d1, col_d2, col_d3 = st.columns(3)

    # Excel (Exporta o DataFrame não formatado para dados brutos)
    buffer_excel_fin = BytesIO()
    with pd.ExcelWriter(buffer_excel_fin, engine="openpyxl") as writer:
        df_export = df_fin[colunas].copy()
        df_export.columns = [c.capitalize().replace("_", " ") for c in df_export.columns]
        df_export.rename(columns={'Valor': 'Valor (R$)'}, inplace=True)
        
        df_export.to_excel(writer, sheet_name="Financeiro", index=False)
    buffer_excel_fin.seek(0)
    col_d1.download_button("📥 Baixar Excel", data=buffer_excel_fin, file_name="relatorio_financeiro_filtrado.xlsx", use_container_width=True)

    # PDF
    col_d2.download_button("📄 Baixar PDF", data=gerar_pdf_financeiro(df_visual, totais_pdf), 
                           file_name="relatorio_financeiro_completo.pdf", mime="application/pdf", use_container_width=True)


# --- Função Principal ---

def exibir():
    st.set_page_config(page_title="Relatórios da Igreja", layout="wide")
    st.title("📈 Relatórios Gerenciais da Igreja")
    st.markdown("---")
    
    # Estado de sessão para evitar erros de inicialização
    if "edicao_financeira_id" not in st.session_state:
        st.session_state["edicao_financeira_id"] = None
        
    opcao = st.selectbox("Escolha o módulo do relatório:", ["👥 Membros", "💰 Financeiro"])

    st.markdown("---")

    if opcao == "👥 Membros":
        exibir_membros()
    elif opcao == "💰 Financeiro":
        exibir_financeiro()

if __name__ == '__main__':
    exibir()