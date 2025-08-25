import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from estoque_controller import EstoqueController
import os

# Configuração da página
st.set_page_config(
    page_title="Sistema de Controle de Estoque - Finance Vibes",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização do controlador
@st.cache_resource
def get_estoque_controller():
    return EstoqueController()

estoque = get_estoque_controller()

# Título principal
st.title("📦 Sistema de Controle de Estoque Unificado")
st.markdown("---")

# Sidebar para navegação
st.sidebar.title("🎯 Navegação")
pagina = st.sidebar.selectbox(
    "Selecione a funcionalidade:",
    [
        "🏠 Dashboard Principal",
        "📊 Estatísticas Gerais",
        "📦 Cadastro de Produtos",
        "🏢 Cadastro de Fornecedores",
        "👥 Cadastro de Usuários",
        "🗂️ Cadastro de Prateleiras",
        "🔄 Movimentações",
        "🔢 Controle por N/S e Ativo",
        "📋 Controle por SKU e Quantidade",
        "🗺️ Mapeamento de Prateleiras",
        "📈 Relatórios e Análises"
    ]
)

# Dashboard Principal
if pagina == "🏠 Dashboard Principal":
    st.header("🏠 Dashboard Principal do Estoque")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    stats = estoque.get_estatisticas_gerais()
    
    with col1:
        st.metric("Total de Produtos", stats.get('total_produtos', 0))
    
    with col2:
        st.metric("Total de Ativos", stats.get('total_ativos', 0))
    
    with col3:
        st.metric("Movimentações", stats.get('total_movimentacoes', 0))
    
    with col4:
        st.metric("Valor Total", f"R$ {stats.get('valor_total_estoque', 0):,.2f}")
    
    # Alertas de estoque baixo
    st.subheader("⚠️ Alertas de Estoque Baixo")
    estoque_baixo = estoque.get_estoque_baixo()
    
    if not estoque_baixo.empty:
        st.dataframe(estoque_baixo[['sku', 'nome', 'estoque_atual', 'estoque_minimo']], 
                    use_container_width=True)
    else:
        st.success("✅ Nenhum produto com estoque baixo!")
    
    # Gráfico de produtos por categoria
    st.subheader("📊 Produtos por Categoria")
    if 'produtos' in estoque.data and not estoque.data['produtos'].empty:
        produtos_categoria = estoque.data['produtos'].groupby('categoria').size().reset_index(name='quantidade')
        fig = px.pie(produtos_categoria, values='quantidade', names='categoria', 
                    title="Distribuição de Produtos por Categoria")
        st.plotly_chart(fig, use_container_width=True)

# Estatísticas Gerais
elif pagina == "📊 Estatísticas Gerais":
    st.header("📊 Estatísticas Gerais do Estoque")
    
    # Métricas detalhadas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Valor por Categoria")
        if 'produtos' in estoque.data and not estoque.data['produtos'].empty:
            valor_categoria = estoque.data['produtos'].groupby('categoria').agg({
                'estoque_atual': 'sum',
                'preco_unitario': lambda x: (x * estoque.data['produtos'].loc[x.index, 'estoque_atual']).sum()
            }).reset_index()
            valor_categoria.columns = ['Categoria', 'Quantidade', 'Valor Total']
            st.dataframe(valor_categoria, use_container_width=True)
    
    with col2:
        st.subheader("📦 Capacidade das Prateleiras")
        if 'prateleiras' in estoque.data and not estoque.data['prateleiras'].empty:
            prateleiras_ocupacao = estoque.data['prateleiras'].copy()
            prateleiras_ocupacao['Ocupação (%)'] = (prateleiras_ocupacao['capacidade_atual'] / 
                                                   prateleiras_ocupacao['capacidade_maxima'] * 100).round(2)
            st.dataframe(prateleiras_ocupacao[['nome', 'capacidade_atual', 'capacidade_maxima', 'Ocupação (%)']], 
                        use_container_width=True)

# Cadastro de Produtos
elif pagina == "📦 Cadastro de Produtos":
    st.header("📦 Cadastro de Produtos")
    
    with st.expander("➕ Adicionar Novo Produto", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            sku = st.text_input("SKU*", placeholder="Ex: SKU001")
            nome = st.text_input("Nome do Produto*", placeholder="Ex: Notebook Dell")
            categoria = st.selectbox("Categoria*", ["Informática", "Periféricos", "Monitores", "Audio e Video", "Outros"])
            descricao = st.text_area("Descrição", placeholder="Descrição detalhada do produto")
        
        with col2:
            unidade_medida = st.selectbox("Unidade de Medida*", ["unidade", "kg", "m", "l", "par"])
            preco_unitario = st.number_input("Preço Unitário (R$)*", min_value=0.0, value=0.0, step=0.01)
            estoque_minimo = st.number_input("Estoque Mínimo*", min_value=0, value=0, step=1)
            fornecedor_id = st.selectbox("Fornecedor*", 
                                       estoque.data.get('fornecedores', pd.DataFrame())['fornecedor_id'].tolist() 
                                       if 'fornecedores' in estoque.data else [])
        
        if st.button("✅ Adicionar Produto"):
            if sku and nome and categoria and unidade_medida and preco_unitario >= 0 and estoque_minimo >= 0 and fornecedor_id:
                success, message = estoque.add_produto(sku, nome, categoria, descricao, unidade_medida, 
                                                     preco_unitario, estoque_minimo, fornecedor_id)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Por favor, preencha todos os campos obrigatórios!")
    
    # Lista de produtos
    st.subheader("📋 Lista de Produtos")
    if 'produtos' in estoque.data and not estoque.data['produtos'].empty:
        st.dataframe(estoque.data['produtos'], use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado ainda.")

# Cadastro de Fornecedores
elif pagina == "🏢 Cadastro de Fornecedores":
    st.header("🏢 Cadastro de Fornecedores")
    
    with st.expander("➕ Adicionar Novo Fornecedor", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            fornecedor_id = st.text_input("ID do Fornecedor*", placeholder="Ex: FORN001")
            nome = st.text_input("Nome da Empresa*", placeholder="Ex: Tech Solutions Ltda")
            cnpj = st.text_input("CNPJ*", placeholder="Ex: 12.345.678/0001-90")
            telefone = st.text_input("Telefone*", placeholder="Ex: (11) 9999-8888")
            email = st.text_input("Email*", placeholder="Ex: contato@empresa.com")
        
        with col2:
            endereco = st.text_input("Endereço*", placeholder="Ex: Rua das Tecnologias 123")
            cidade = st.text_input("Cidade*", placeholder="Ex: São Paulo")
            estado = st.selectbox("Estado*", ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
            cep = st.text_input("CEP*", placeholder="Ex: 01234-567")
        
        if st.button("✅ Adicionar Fornecedor"):
            if fornecedor_id and nome and cnpj and telefone and email and endereco and cidade and estado and cep:
                success, message = estoque.add_fornecedor(fornecedor_id, nome, cnpj, telefone, email, 
                                                        endereco, cidade, estado, cep)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Por favor, preencha todos os campos obrigatórios!")
    
    # Lista de fornecedores
    st.subheader("📋 Lista de Fornecedores")
    if 'fornecedores' in estoque.data and not estoque.data['fornecedores'].empty:
        st.dataframe(estoque.data['fornecedores'], use_container_width=True)
    else:
        st.info("Nenhum fornecedor cadastrado ainda.")

# Cadastro de Usuários
elif pagina == "👥 Cadastro de Usuários":
    st.header("👥 Cadastro de Usuários")
    
    with st.expander("➕ Adicionar Novo Usuário", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            usuario_id = st.text_input("ID do Usuário*", placeholder="Ex: USR001")
            nome = st.text_input("Nome Completo*", placeholder="Ex: João Silva")
            email = st.text_input("Email*", placeholder="Ex: joao.silva@empresa.com")
            telefone = st.text_input("Telefone*", placeholder="Ex: (11) 9999-1111")
        
        with col2:
            departamento = st.selectbox("Departamento*", ["TI", "Compras", "Almoxarifado", "Financeiro", "Marketing", "RH", "Outros"])
            cargo = st.text_input("Cargo*", placeholder="Ex: Analista de Sistemas")
            nivel_acesso = st.selectbox("Nível de Acesso*", ["Administrador", "Operador", "Visualizador"])
        
        if st.button("✅ Adicionar Usuário"):
            if usuario_id and nome and email and telefone and departamento and cargo and nivel_acesso:
                success, message = estoque.add_usuario(usuario_id, nome, email, telefone, 
                                                     departamento, cargo, nivel_acesso)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Por favor, preencha todos os campos obrigatórios!")
    
    # Lista de usuários
    st.subheader("📋 Lista de Usuários")
    if 'usuarios' in estoque.data and not estoque.data['usuarios'].empty:
        st.dataframe(estoque.data['usuarios'], use_container_width=True)
    else:
        st.info("Nenhum usuário cadastrado ainda.")

# Cadastro de Prateleiras
elif pagina == "🗂️ Cadastro de Prateleiras":
    st.header("🗂️ Cadastro de Prateleiras")
    
    with st.expander("➕ Adicionar Nova Prateleira", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            prateleira_id = st.text_input("ID da Prateleira*", placeholder="Ex: PRAT001")
            nome = st.text_input("Nome da Prateleira*", placeholder="Ex: Corredor A - Prateleira 1")
            corredor = st.selectbox("Corredor*", ["A", "B", "C", "D", "E", "F"])
            setor = st.selectbox("Setor*", ["Informática", "Periféricos", "Monitores", "Audio e Video", "Outros"])
        
        with col2:
            capacidade_maxima = st.number_input("Capacidade Máxima*", min_value=1, value=100, step=1)
            responsavel_id = st.selectbox("Responsável*", 
                                        estoque.data.get('usuarios', pd.DataFrame())['usuario_id'].tolist() 
                                        if 'usuarios' in estoque.data else [])
        
        if st.button("✅ Adicionar Prateleira"):
            if prateleira_id and nome and corredor and setor and capacidade_maxima > 0 and responsavel_id:
                success, message = estoque.add_prateleira(prateleira_id, nome, corredor, setor, 
                                                        capacidade_maxima, responsavel_id)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Por favor, preencha todos os campos obrigatórios!")
    
    # Lista de prateleiras
    st.subheader("📋 Lista de Prateleiras")
    if 'prateleiras' in estoque.data and not estoque.data['prateleiras'].empty:
        st.dataframe(estoque.data['prateleiras'], use_container_width=True)
    else:
        st.info("Nenhuma prateleira cadastrada ainda.")

# Movimentações
elif pagina == "🔄 Movimentações":
    st.header("🔄 Controle de Movimentações")
    
    with st.expander("➕ Registrar Nova Movimentação", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            sku = st.selectbox("SKU do Produto*", 
                              estoque.data.get('produtos', pd.DataFrame())['sku'].tolist() 
                              if 'produtos' in estoque.data else [])
            numero_serie = st.text_input("Número de Série", placeholder="Ex: NS001 (opcional)")
            tipo_movimentacao = st.selectbox("Tipo de Movimentação*", ["Entrada", "Saída", "Transferência", "Inventário"])
            quantidade = st.number_input("Quantidade*", min_value=1, value=1, step=1)
            motivo = st.selectbox("Motivo*", ["Compra de fornecedor", "Requisição", "Devolução", "Transferência", "Ajuste inventário", "Outros"])
        
        with col2:
            usuario_id = st.selectbox("Usuário Responsável*", 
                                    estoque.data.get('usuarios', pd.DataFrame())['usuario_id'].tolist() 
                                    if 'usuarios' in estoque.data else [])
            prateleira_origem = st.selectbox("Prateleira Origem", 
                                           [""] + estoque.data.get('prateleiras', pd.DataFrame())['prateleira_id'].tolist() 
                                           if 'prateleiras' in estoque.data else [])
            prateleira_destino = st.selectbox("Prateleira Destino", 
                                            [""] + estoque.data.get('prateleiras', pd.DataFrame())['prateleira_id'].tolist() 
                                            if 'prateleiras' in estoque.data else [])
            observacoes = st.text_area("Observações", placeholder="Observações adicionais")
        
        if st.button("✅ Registrar Movimentação"):
            if sku and tipo_movimentacao and quantidade > 0 and motivo and usuario_id:
                success, message = estoque.registrar_movimentacao(sku, numero_serie, tipo_movimentacao, 
                                                               quantidade, motivo, usuario_id, 
                                                               prateleira_origem, prateleira_destino, observacoes)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Por favor, preencha todos os campos obrigatórios!")
    
    # Histórico de movimentações
    st.subheader("📋 Histórico de Movimentações")
    if 'movimentacoes' in estoque.data and not estoque.data['movimentacoes'].empty:
        st.dataframe(estoque.data['movimentacoes'], use_container_width=True)
    else:
        st.info("Nenhuma movimentação registrada ainda.")

# Controle por N/S e Ativo
elif pagina == "🔢 Controle por N/S e Ativo":
    st.header("🔢 Controle por Número de Série e Ativo")
    
    with st.expander("➕ Adicionar Novo Ativo", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            numero_serie = st.text_input("Número de Série*", placeholder="Ex: NS001")
            sku = st.selectbox("SKU do Produto*", 
                              estoque.data.get('produtos', pd.DataFrame())['sku'].tolist() 
                              if 'produtos' in estoque.data else [])
            status = st.selectbox("Status*", ["Em uso", "Em estoque", "Em manutenção", "Descartado", "Emprestado"])
            localizacao = st.text_input("Localização*", placeholder="Ex: Setor TI - Mesa 5")
        
        with col2:
            usuario_responsavel = st.selectbox("Usuário Responsável*", 
                                             estoque.data.get('usuarios', pd.DataFrame())['usuario_id'].tolist() 
                                             if 'usuarios' in estoque.data else [])
            valor_aquisicao = st.number_input("Valor de Aquisição (R$)*", min_value=0.0, value=0.0, step=0.01)
            fornecedor_id = st.selectbox("Fornecedor*", 
                                       estoque.data.get('fornecedores', pd.DataFrame())['fornecedor_id'].tolist() 
                                       if 'fornecedores' in estoque.data else [])
            garantia_ate = st.date_input("Garantia Até*", value=datetime.now().date() + timedelta(days=365))
            observacoes = st.text_area("Observações", placeholder="Observações sobre o ativo")
        
        if st.button("✅ Adicionar Ativo"):
            if numero_serie and sku and status and localizacao and usuario_responsavel and valor_aquisicao >= 0 and fornecedor_id:
                success, message = estoque.add_ativo(numero_serie, sku, status, localizacao, 
                                                   usuario_responsavel, valor_aquisicao, fornecedor_id, 
                                                   garantia_ate.strftime('%Y-%m-%d'), observacoes)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Por favor, preencha todos os campos obrigatórios!")
    
    # Lista de ativos
    st.subheader("📋 Lista de Ativos")
    if 'ativos' in estoque.data and not estoque.data['ativos'].empty:
        st.dataframe(estoque.data['ativos'], use_container_width=True)
    else:
        st.info("Nenhum ativo cadastrado ainda.")

# Controle por SKU e Quantidade
elif pagina == "📋 Controle por SKU e Quantidade":
    st.header("📋 Controle por SKU e Quantidade")
    
    if 'produtos' in estoque.data and not estoque.data['produtos'].empty:
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            categoria_filtro = st.selectbox("Filtrar por Categoria", 
                                          ["Todas"] + estoque.data['produtos']['categoria'].unique().tolist())
        
        with col2:
            fornecedor_filtro = st.selectbox("Filtrar por Fornecedor", 
                                           ["Todos"] + estoque.data['produtos']['fornecedor_id'].unique().tolist())
        
        with col3:
            estoque_status = st.selectbox("Status do Estoque", 
                                        ["Todos", "Em estoque", "Estoque baixo", "Sem estoque"])
        
        # Aplicar filtros
        produtos_filtrados = estoque.data['produtos'].copy()
        
        if categoria_filtro != "Todas":
            produtos_filtrados = produtos_filtrados[produtos_filtrados['categoria'] == categoria_filtro]
        
        if fornecedor_filtro != "Todos":
            produtos_filtrados = produtos_filtrados[produtos_filtrados['fornecedor_id'] == fornecedor_filtro]
        
        if estoque_status == "Em estoque":
            produtos_filtrados = produtos_filtrados[produtos_filtrados['estoque_atual'] > produtos_filtrados['estoque_minimo']]
        elif estoque_status == "Estoque baixo":
            produtos_filtrados = produtos_filtrados[produtos_filtrados['estoque_atual'] <= produtos_filtrados['estoque_minimo']]
        elif estoque_status == "Sem estoque":
            produtos_filtrados = produtos_filtrados[produtos_filtrados['estoque_atual'] == 0]
        
        # Exibir produtos filtrados
        st.subheader(f"📊 Produtos Encontrados: {len(produtos_filtrados)}")
        st.dataframe(produtos_filtrados, use_container_width=True)
        
        # Gráfico de estoque por categoria
        if not produtos_filtrados.empty:
            fig = px.bar(produtos_filtrados, x='categoria', y='estoque_atual', 
                        title="Estoque Atual por Categoria", 
                        color='estoque_atual', 
                        color_continuous_scale='RdYlGn')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum produto cadastrado ainda.")

# Mapeamento de Prateleiras
elif pagina == "🗺️ Mapeamento de Prateleiras":
    st.header("🗺️ Mapeamento de Prateleiras no Estoque")
    
    if 'prateleiras' in estoque.data and not estoque.data['prateleiras'].empty:
        # Visualização por corredor
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Ocupação por Corredor")
            ocupacao_corredor = estoque.data['prateleiras'].groupby('corredor').agg({
                'capacidade_atual': 'sum',
                'capacidade_maxima': 'sum'
            }).reset_index()
            ocupacao_corredor['Ocupação (%)'] = (ocupacao_corredor['capacidade_atual'] / 
                                               ocupacao_corredor['capacidade_maxima'] * 100).round(2)
            st.dataframe(ocupacao_corredor, use_container_width=True)
        
        with col2:
            st.subheader("📊 Ocupação por Setor")
            ocupacao_setor = estoque.data['prateleiras'].groupby('setor').agg({
                'capacidade_atual': 'sum',
                'capacidade_maxima': 'sum'
            }).reset_index()
            ocupacao_setor['Ocupação (%)'] = (ocupacao_setor['capacidade_atual'] / 
                                            ocupacao_setor['capacidade_maxima'] * 100).round(2)
            st.dataframe(ocupacao_setor, use_container_width=True)
        
        # Gráfico de ocupação
        fig = px.bar(estoque.data['prateleiras'], x='nome', y=['capacidade_atual', 'capacidade_maxima'],
                    title="Capacidade das Prateleiras", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        
        # Mapa visual das prateleiras
        st.subheader("🗺️ Mapa Visual das Prateleiras")
        for corredor in sorted(estoque.data['prateleiras']['corredor'].unique()):
            st.write(f"**Corredor {corredor}:**")
            prateleiras_corredor = estoque.data['prateleiras'][estoque.data['prateleiras']['corredor'] == corredor]
            
            cols = st.columns(len(prateleiras_corredor))
            for i, (_, prateleira) in enumerate(prateleiras_corredor.iterrows()):
                with cols[i]:
                    ocupacao_pct = (prateleira['capacidade_atual'] / prateleira['capacidade_maxima'] * 100)
                    if ocupacao_pct > 80:
                        color = "🔴"
                    elif ocupacao_pct > 50:
                        color = "🟡"
                    else:
                        color = "🟢"
                    
                    st.metric(
                        prateleira['nome'],
                        f"{prateleira['capacidade_atual']}/{prateleira['capacidade_maxima']}",
                        f"{ocupacao_pct:.1f}%"
                    )
                    st.write(f"{color} {prateleira['setor']}")
    else:
        st.info("Nenhuma prateleira cadastrada ainda.")

# Relatórios e Análises
elif pagina == "📈 Relatórios e Análises":
    st.header("📈 Relatórios e Análises")
    
    # Filtros de período
    col1, col2 = st.columns(2)
    
    with col1:
        data_inicio = st.date_input("Data Início", value=datetime.now().date() - timedelta(days=30))
    
    with col2:
        data_fim = st.date_input("Data Fim", value=datetime.now().date())
    
    # Relatório de movimentações
    st.subheader("📊 Relatório de Movimentações")
    movimentacoes_periodo = estoque.get_movimentacoes_periodo(
        data_inicio.strftime('%Y-%m-%d'), 
        data_fim.strftime('%Y-%m-%d')
    )
    
    if not movimentacoes_periodo.empty:
        # Estatísticas do período
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de Movimentações", len(movimentacoes_periodo))
        
        with col2:
            entradas = len(movimentacoes_periodo[movimentacoes_periodo['tipo_movimentacao'] == 'Entrada'])
            st.metric("Entradas", entradas)
        
        with col3:
            saidas = len(movimentacoes_periodo[movimentacoes_periodo['tipo_movimentacao'] == 'Saída'])
            st.metric("Saídas", saidas)
        
        with col4:
            transferencias = len(movimentacoes_periodo[movimentacoes_periodo['tipo_movimentacao'] == 'Transferência'])
            st.metric("Transferências", transferencias)
        
        # Gráfico de movimentações por tipo
        movimentacoes_tipo = movimentacoes_periodo['tipo_movimentacao'].value_counts()
        fig = px.pie(values=movimentacoes_tipo.values, names=movimentacoes_tipo.index, 
                    title="Movimentações por Tipo")
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela detalhada
        st.dataframe(movimentacoes_periodo, use_container_width=True)
    else:
        st.info("Nenhuma movimentação encontrada no período selecionado.")
    
    # Relatório de produtos por fornecedor
    st.subheader("🏢 Produtos por Fornecedor")
    produtos_fornecedor = estoque.get_produtos_por_fornecedor()
    
    if not produtos_fornecedor.empty:
        fig = px.bar(produtos_fornecedor.groupby('nome_y').size().reset_index(name='quantidade'),
                    x='nome_y', y='quantidade', title="Quantidade de Produtos por Fornecedor")
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(produtos_fornecedor[['sku', 'nome_x', 'categoria', 'estoque_atual', 'nome_y']], 
                    use_container_width=True)
    else:
        st.info("Nenhum produto ou fornecedor cadastrado ainda.")

# Footer
st.markdown("---")
st.markdown("📦 **Sistema de Controle de Estoque Unificado** - Finance Vibes")
st.markdown("Desenvolvido com ❤️ para gestão eficiente de estoque")

# Atualizar dados automaticamente
if st.button("🔄 Atualizar Dados"):
    estoque.load_data()
    st.success("Dados atualizados com sucesso!")
    st.rerun()
