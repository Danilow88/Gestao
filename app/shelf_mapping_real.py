"""
Módulo de Mapeamento de Prateleiras com Dados Reais
Versão otimizada para mostrar dados do inventário unificado
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def load_unified_inventory():
    """Carrega dados do inventário unificado"""
    try:
        inventario_file = "inventario_unificado_20250827.csv"
        unified_data = pd.read_csv(inventario_file)
        
        # Converter valores numéricos
        unified_data['valor'] = pd.to_numeric(unified_data['valor'], errors='coerce').fillna(0)
        unified_data['qtd'] = pd.to_numeric(unified_data['qtd'], errors='coerce').fillna(0)
        
        # Calcular valor total
        unified_data['valor_total'] = unified_data['valor'] * unified_data['qtd']
        
        # Tratar valores nulos
        for col in unified_data.columns:
            if unified_data[col].dtype == 'object':
                unified_data[col] = unified_data[col].fillna('Não Informado')
        
        return unified_data
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar inventário: {str(e)}")
        return pd.DataFrame()

def create_advanced_filters(unified_data):
    """Cria filtros avançados para os dados"""
    
    st.markdown("### Filtros Avançados")
    
    # Filtros principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        locais = ['Todos'] + sorted(unified_data['local'].unique().tolist())
        local_filtro = st.selectbox("Local", locais, key="local_filter")
    
    with col2:
        prateleiras = ['Todas'] + sorted(unified_data['prateleira'].unique().tolist())
        prateleira_filtro = st.selectbox("Prateleira", prateleiras, key="shelf_filter")
    
    with col3:
        fornecedores = ['Todos'] + sorted(unified_data['fornecedor'].unique().tolist())
        fornecedor_filtro = st.selectbox("Fornecedor", fornecedores, key="supplier_filter")
    
    with col4:
        categorias = ['Todas'] + sorted(unified_data['categoria'].unique().tolist())
        categoria_filtro = st.selectbox("Categoria", categorias, key="category_filter")
    
    # Filtros secundários
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        ruas = ['Todas'] + sorted(unified_data['rua'].unique().tolist())
        rua_filtro = st.selectbox("Rua", ruas, key="street_filter")
    
    with col6:
        setores = ['Todos'] + sorted(unified_data['setor'].unique().tolist())
        setor_filtro = st.selectbox("Setor", setores, key="sector_filter")
    
    with col7:
        conferido_options = ['Todos', 'Conferido', 'Não Conferido']
        conferido_filtro = st.selectbox("Status", conferido_options, key="checked_filter")
    
    with col8:
        marcas = ['Todas'] + sorted(unified_data['marca'].unique().tolist())
        marca_filtro = st.selectbox("Marca", marcas, key="brand_filter")
    
    return {
        'local': local_filtro,
        'prateleira': prateleira_filtro, 
        'fornecedor': fornecedor_filtro,
        'categoria': categoria_filtro,
        'rua': rua_filtro,
        'setor': setor_filtro,
        'conferido': conferido_filtro,
        'marca': marca_filtro
    }

def apply_filters(unified_data, filters):
    """Aplica os filtros selecionados aos dados"""
    
    dados_filtrados = unified_data.copy()
    
    if filters['local'] != 'Todos':
        dados_filtrados = dados_filtrados[dados_filtrados['local'] == filters['local']]
    
    if filters['prateleira'] != 'Todas':
        dados_filtrados = dados_filtrados[dados_filtrados['prateleira'] == filters['prateleira']]
    
    if filters['fornecedor'] != 'Todos':
        dados_filtrados = dados_filtrados[dados_filtrados['fornecedor'] == filters['fornecedor']]
    
    if filters['categoria'] != 'Todas':
        dados_filtrados = dados_filtrados[dados_filtrados['categoria'] == filters['categoria']]
    
    if filters['rua'] != 'Todas':
        dados_filtrados = dados_filtrados[dados_filtrados['rua'] == filters['rua']]
    
    if filters['setor'] != 'Todos':
        dados_filtrados = dados_filtrados[dados_filtrados['setor'] == filters['setor']]
    
    if filters['conferido'] != 'Todos':
        if filters['conferido'] == 'Conferido':
            dados_filtrados = dados_filtrados[dados_filtrados['conferido'] == True]
        else:
            dados_filtrados = dados_filtrados[dados_filtrados['conferido'] == False]
    
    if filters['marca'] != 'Todas':
        dados_filtrados = dados_filtrados[dados_filtrados['marca'] == filters['marca']]
    
    return dados_filtrados

def show_summary_metrics(dados_filtrados):
    """Mostra métricas resumo dos dados filtrados"""
    
    st.markdown("### Resumo dos Dados")
    
    if not dados_filtrados.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_itens = int(dados_filtrados['qtd'].sum())
            st.metric("Total de Itens", f"{total_itens:,}")
        
        with col2:
            valor_total = dados_filtrados['valor_total'].sum()
            st.metric("Valor Total", f"R$ {valor_total:,.2f}")
        
        with col3:
            prateleiras_utilizadas = dados_filtrados['prateleira'].nunique()
            st.metric("Prateleiras", f"{prateleiras_utilizadas:,}")
        
        with col4:
            fornecedores_diferentes = dados_filtrados['fornecedor'].nunique()
            st.metric("Fornecedores", f"{fornecedores_diferentes:,}")
    else:
        st.warning("⚠️ Nenhum dado encontrado com os filtros aplicados")

def render_data_table(dados_filtrados):
    """Renderiza tabela de dados detalhados"""
    
    st.markdown("### Dados Detalhados")
    
    if not dados_filtrados.empty:
        # Selecionar colunas para exibição
        colunas_exibicao = ['tag', 'itens', 'categoria', 'marca', 'modelo', 'qtd', 'valor', 'valor_total', 
                           'prateleira', 'rua', 'setor', 'local', 'fornecedor', 'conferido', 'uso']
        
        # Filtrar apenas colunas existentes
        colunas_existentes = [col for col in colunas_exibicao if col in dados_filtrados.columns]
        dados_exibir = dados_filtrados[colunas_existentes].copy()
        
        # Formatação para exibição
        dados_exibir['valor'] = dados_exibir['valor'].apply(lambda x: f"R$ {x:,.2f}")
        dados_exibir['valor_total'] = dados_exibir['valor_total'].apply(lambda x: f"R$ {x:,.2f}")
        
        # Renomear colunas
        rename_cols = {
            'tag': 'TAG', 'itens': 'Item', 'categoria': 'Categoria', 'marca': 'Marca',
            'modelo': 'Modelo', 'qtd': 'Qtd', 'valor': 'Valor Unit.', 'valor_total': 'Valor Total',
            'prateleira': 'Prateleira', 'rua': 'Rua', 'setor': 'Setor', 'local': 'Local',
            'fornecedor': 'Fornecedor', 'conferido': 'Conferido', 'uso': 'Uso'
        }
        
        dados_exibir = dados_exibir.rename(columns=rename_cols)
        
        # Exibir dados editáveis
        st.data_editor(
            dados_exibir,
            use_container_width=True,
            height=400,
            column_config={
                'Conferido': st.column_config.CheckboxColumn('Conferido'),
                'Qtd': st.column_config.NumberColumn('Qtd', min_value=0)
            }
        )

def create_visualizations(dados_filtrados):
    """Cria visualizações dos dados"""
    
    st.markdown("### Análises Visuais")
    
    if dados_filtrados.empty:
        st.info("ℹ️ Nenhum dado para visualizar")
        return
    
    tab1, tab2, tab3, tab4 = st.tabs(["Por Prateleira", "Por Fornecedor", "Por Categoria", "Por Local"])
    
    with tab1:
        # Análise por prateleira
        dist_prateleira = dados_filtrados.groupby('prateleira').agg({
            'qtd': 'sum',
            'valor_total': 'sum'
        }).reset_index()
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig_qtd = px.bar(
                dist_prateleira,
                x='prateleira',
                y='qtd',
                title="Quantidade por Prateleira",
                labels={'prateleira': 'Prateleira', 'qtd': 'Quantidade'}
            )
            st.plotly_chart(fig_qtd, use_container_width=True)
        
        with col_chart2:
            fig_valor = px.bar(
                dist_prateleira,
                x='prateleira',
                y='valor_total',
                title="Valor Total por Prateleira (R$)",
                labels={'prateleira': 'Prateleira', 'valor_total': 'Valor (R$)'}
            )
            st.plotly_chart(fig_valor, use_container_width=True)
    
    with tab2:
        # Análise por fornecedor
        dist_fornecedor = dados_filtrados.groupby('fornecedor').agg({
            'qtd': 'sum',
            'valor_total': 'sum'
        }).reset_index()
        
        fig_fornecedor = px.pie(
            dist_fornecedor,
            values='valor_total',
            names='fornecedor',
            title="Distribuição de Valor por Fornecedor"
        )
        st.plotly_chart(fig_fornecedor, use_container_width=True)
    
    with tab3:
        # Análise por categoria
        dist_categoria = dados_filtrados.groupby('categoria').agg({
            'qtd': 'sum',
            'valor_total': 'sum'
        }).reset_index()
        
        fig_categoria = px.treemap(
            dist_categoria,
            path=['categoria'],
            values='valor_total',
            title="Mapa de Valor por Categoria"
        )
        st.plotly_chart(fig_categoria, use_container_width=True)
    
    with tab4:
        # Análise por local
        dist_local = dados_filtrados.groupby('local').agg({
            'qtd': 'sum',
            'valor_total': 'sum'
        }).reset_index()
        
        fig_local = px.bar(
            dist_local,
            x='local',
            y='valor_total',
            title="Valor Total por Local (R$)",
            labels={'local': 'Local', 'valor_total': 'Valor (R$)'}
        )
        fig_local.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig_local, use_container_width=True)

def create_export_options(dados_filtrados):
    """Cria opções de exportação"""
    
    st.markdown("### Exportar Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not dados_filtrados.empty:
            csv_data = dados_filtrados.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv_data,
                file_name=f"estoque_filtrado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Gerar Excel") and not dados_filtrados.empty:
            try:
                excel_filename = f"estoque_filtrado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                dados_filtrados.to_excel(excel_filename, index=False)
                st.success(f"✅ Arquivo Excel gerado: {excel_filename}")
            except Exception as e:
                st.error(f"❌ Erro ao gerar Excel: {str(e)}")

def render_shelf_mapping_page():
    """Função principal para renderizar a página de mapeamento de prateleiras"""
    
    # Aplicar estilos CSS para visibilidade dos filtros
    st.markdown("""
    <style>
    /* Estilos para labels dos filtros */
    .stSelectbox > label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Estilos para títulos das seções */
    .main h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Estilos para selectboxes */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 8px !important;
    }
    
    /* Estilos para dropdowns */
    .stSelectbox > div > div > div[role="listbox"] {
        background: white !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Estilos para opções do dropdown */
    .stSelectbox > div > div > div[role="option"] {
        color: #1f2937 !important;
        background: white !important;
    }
    
    .stSelectbox > div > div > div[role="option"]:hover {
        background: rgba(139, 92, 246, 0.1) !important;
        color: #1f2937 !important;
    }
    
    /* Estilos para métricas */
    [data-testid="metric-container"] {
        background: rgba(139, 92, 246, 0.1) !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    [data-testid="metric-container"] > div {
        color: #FFFFFF !important;
    }
    
    /* Estilos para data editor */
    .stDataEditor {
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    
    /* Estilos para botões de download */
    .stDownloadButton > button {
        background: rgba(139, 92, 246, 0.9) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    .stDownloadButton > button:hover {
        background: rgba(124, 58, 237, 1) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("## Estoque por Prateleira")
    
    # Carregar dados
    unified_data = load_unified_inventory()
    
    if unified_data.empty:
        st.error("❌ Não foi possível carregar os dados do inventário")
        return
    
    st.success("✅ Dados carregados com sucesso!")
    
    # Criar filtros
    filters = create_advanced_filters(unified_data)
    
    # Aplicar filtros
    dados_filtrados = apply_filters(unified_data, filters)
    
    # Mostrar métricas
    show_summary_metrics(dados_filtrados)
    
    # Renderizar tabela
    render_data_table(dados_filtrados)
    
    # Criar visualizações
    create_visualizations(dados_filtrados)
    
    # Opções de exportação
    create_export_options(dados_filtrados)
