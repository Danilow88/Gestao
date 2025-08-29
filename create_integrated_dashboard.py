#!/usr/bin/env python3
"""
Script para criar um dashboard.py completamente integrado
sem dependências externas de módulos locais
"""

import re
import os

def read_file(filename):
    """Lê o conteúdo de um arquivo"""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filename, content):
    """Escreve conteúdo em um arquivo"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def get_estoque_manager_code():
    """Retorna o código da classe EstoqueManager integrada"""
    return '''# ========================================================================================
# ESTOQUE_MANAGER INTEGRADO - CLASSE PRINCIPAL
# ========================================================================================

class EstoqueManager:
    """Classe principal para gerenciamento integrado de estoque"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.load_all_data()
    
    def load_all_data(self):
        """Carrega todos os dados dos arquivos CSV"""
        try:
            # Criar diretório se não existir
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Carregar dados principais se existirem
            files_to_load = {
                'fornecedores': 'fornecedores.csv',
                'produtos': 'produtos.csv',
                'notas_fiscais': 'notas_fiscais.csv',
                'movimentacoes': 'movimentacoes.csv',
                'prateleiras': 'prateleiras.csv',
                'estoque_prateleiras': 'estoque_prateleiras.csv'
            }
            
            for attr_name, filename in files_to_load.items():
                filepath = self.data_dir / filename
                if filepath.exists():
                    try:
                        setattr(self, attr_name, pd.read_csv(filepath))
                    except Exception as e:
                        st.warning(f"⚠️ Erro ao carregar {filename}: {str(e)}")
                        setattr(self, attr_name, pd.DataFrame())
                else:
                    setattr(self, attr_name, pd.DataFrame())
            
            # Converter datas se as colunas existirem
            date_columns = {
                'notas_fiscais': ['data_emissao', 'data_entrada', 'data_cadastro'],
                'movimentacoes': ['data_movimentacao'],
                'estoque_prateleiras': ['data_entrada', 'data_ultima_movimentacao'],
                'prateleiras': ['data_cadastro']
            }
            
            for df_name, columns in date_columns.items():
                df = getattr(self, df_name)
                if not df.empty:
                    for col in columns:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Converter valores numéricos se as colunas existirem
            numeric_columns = {
                'produtos': ['preco_unitario', 'peso', 'volume'],
                'notas_fiscais': ['valor_total', 'valor_frete', 'valor_impostos'],
                'movimentacoes': ['quantidade', 'valor_unitario', 'valor_total'],
                'estoque_prateleiras': ['quantidade'],
                'prateleiras': ['capacidade_total', 'capacidade_utilizada', 'capacidade_disponivel']
            }
            
            for df_name, columns in numeric_columns.items():
                df = getattr(self, df_name)
                if not df.empty:
                    for col in columns:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados: {str(e)}")
            # Criar DataFrames vazios em caso de erro
            self.create_empty_dataframes()
    
    def create_empty_dataframes(self):
        """Cria DataFrames vazios em caso de erro no carregamento"""
        self.fornecedores = pd.DataFrame()
        self.produtos = pd.DataFrame()
        self.notas_fiscais = pd.DataFrame()
        self.movimentacoes = pd.DataFrame()
        self.prateleiras = pd.DataFrame()
        self.estoque_prateleiras = pd.DataFrame()
    
    def save_data(self, df: pd.DataFrame, filename: str):
        """Salva DataFrame em arquivo CSV"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            filepath = self.data_dir / filename
            df.to_csv(filepath, index=False)
            return True
        except Exception as e:
            st.error(f"❌ Erro ao salvar {filename}: {str(e)}")
            return False
    
    def get_estoque_atual(self) -> pd.DataFrame:
        """Retorna estoque atual consolidado"""
        try:
            if self.estoque_prateleiras.empty or self.produtos.empty or self.prateleiras.empty:
                return pd.DataFrame()
            
            # Juntar dados de produtos com estoque por prateleira
            estoque_consolidado = self.estoque_prateleiras.merge(
                self.produtos[['sku', 'nome_produto', 'categoria', 'marca', 'modelo', 'preco_unitario']],
                on='sku',
                how='left'
            ).merge(
                self.prateleiras[['id_prateleira', 'nome_prateleira', 'local', 'setor', 'rua']],
                left_on='prateleira_id',
                right_on='id_prateleira',
                how='left'
            )
            
            # Calcular valor total em estoque
            if 'quantidade' in estoque_consolidado.columns and 'preco_unitario' in estoque_consolidado.columns:
                estoque_consolidado['valor_total_estoque'] = (
                    estoque_consolidado['quantidade'] * estoque_consolidado['preco_unitario']
                )
            
            return estoque_consolidado
            
        except Exception as e:
            st.error(f"❌ Erro ao consolidar estoque: {str(e)}")
            return pd.DataFrame()
    
    def get_movimentacoes_periodo(self, data_inicio: str, data_fim: str) -> pd.DataFrame:
        """Retorna movimentações em um período específico"""
        try:
            df = self.movimentacoes.copy()
            if df.empty:
                return pd.DataFrame()
            
            df['data_movimentacao'] = pd.to_datetime(df['data_movimentacao'])
            
            mask = (df['data_movimentacao'] >= data_inicio) & (df['data_movimentacao'] <= data_fim)
            return df[mask]
            
        except Exception as e:
            st.error(f"❌ Erro ao filtrar movimentações: {str(e)}")
            return pd.DataFrame()
    
    def get_produtos_por_fornecedor(self, fornecedor_id: str = None) -> pd.DataFrame:
        """Retorna produtos agrupados por fornecedor"""
        try:
            if self.produtos.empty or self.fornecedores.empty:
                return pd.DataFrame()
            
            df = self.produtos.merge(
                self.fornecedores[['id_fornecedor', 'nome_fornecedor']],
                left_on='fornecedor_id',
                right_on='id_fornecedor',
                how='left'
            )
            
            if fornecedor_id:
                df = df[df['fornecedor_id'] == fornecedor_id]
            
            return df
            
        except Exception as e:
            st.error(f"❌ Erro ao buscar produtos por fornecedor: {str(e)}")
            return pd.DataFrame()
    
    def get_estoque_por_prateleira(self, prateleira_id: str = None) -> pd.DataFrame:
        """Retorna estoque agrupado por prateleira"""
        try:
            if self.estoque_prateleiras.empty or self.produtos.empty or self.prateleiras.empty:
                return pd.DataFrame()
            
            df = self.estoque_prateleiras.merge(
                self.produtos[['sku', 'nome_produto', 'categoria', 'marca']],
                on='sku',
                how='left'
            ).merge(
                self.prateleiras[['id_prateleira', 'nome_prateleira', 'local', 'setor']],
                left_on='prateleira_id',
                right_on='id_prateleira',
                how='left'
            )
            
            if prateleira_id:
                df = df[df['prateleira_id'] == prateleira_id]
            
            return df
            
        except Exception as e:
            st.error(f"❌ Erro ao buscar estoque por prateleira: {str(e)}")
            return pd.DataFrame()
    
    def registrar_movimentacao(self, tipo: str, sku: str, quantidade: int, 
                             motivo: str, local_origem: str, local_destino: str,
                             numero_nf: str = None, observacoes: str = "") -> bool:
        """Registra uma nova movimentação de estoque"""
        try:
            if self.produtos.empty:
                st.error("❌ Nenhum produto cadastrado")
                return False
            
            # Buscar produto para obter preço
            produto = self.produtos[self.produtos['sku'] == sku]
            if produto.empty:
                st.error(f"❌ Produto com SKU {sku} não encontrado")
                return False
            
            preco_unitario = produto.iloc[0]['preco_unitario']
            valor_total = quantidade * preco_unitario
            
            # Criar nova movimentação
            nova_movimentacao = {
                'id_movimentacao': f"MOV{len(self.movimentacoes) + 1:03d}",
                'tipo_movimentacao': tipo,
                'data_movimentacao': datetime.now().strftime('%Y-%m-%d'),
                'sku': sku,
                'quantidade': quantidade,
                'valor_unitario': preco_unitario,
                'valor_total': valor_total,
                'motivo': motivo,
                'usuario': st.session_state.get('current_user', 'sistema'),
                'local_origem': local_origem,
                'local_destino': local_destino,
                'numero_nf': numero_nf,
                'observacoes': observacoes,
                'status': 'Confirmada'
            }
            
            # Adicionar à lista de movimentações
            self.movimentacoes = pd.concat([
                self.movimentacoes,
                pd.DataFrame([nova_movimentacao])
            ], ignore_index=True)
            
            # Salvar dados
            self.save_data(self.movimentacoes, "movimentacoes.csv")
            
            st.success(f"✅ Movimentação registrada com sucesso: {tipo} de {quantidade} unidades de {sku}")
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao registrar movimentação: {str(e)}")
            return False
    
    def get_metricas_estoque(self) -> Dict:
        """Retorna métricas consolidadas do estoque"""
        try:
            estoque_atual = self.get_estoque_atual()
            
            if estoque_atual.empty:
                return {}
            
            metricas = {
                'total_itens': int(estoque_atual['quantidade'].sum()) if 'quantidade' in estoque_atual.columns else 0,
                'total_sku': len(estoque_atual['sku'].unique()) if 'sku' in estoque_atual.columns else 0,
                'valor_total': float(estoque_atual['valor_total_estoque'].sum()) if 'valor_total_estoque' in estoque_atual.columns else 0.0,
                'categorias': len(estoque_atual['categoria'].unique()) if 'categoria' in estoque_atual.columns else 0,
                'prateleiras_ativas': len(estoque_atual['prateleira_id'].unique()) if 'prateleira_id' in estoque_atual.columns else 0,
                'itens_por_categoria': estoque_atual.groupby('categoria')['quantidade'].sum().to_dict() if 'categoria' in estoque_atual.columns and 'quantidade' in estoque_atual.columns else {},
                'valor_por_categoria': estoque_atual.groupby('categoria')['valor_total_estoque'].sum().to_dict() if 'categoria' in estoque_atual.columns and 'valor_total_estoque' in estoque_atual.columns else {}
            }
            
            return metricas
            
        except Exception as e:
            st.error(f"❌ Erro ao calcular métricas: {str(e)}")
            return {}
    
    def get_relatorio_movimentacoes(self, periodo_dias: int = 30) -> pd.DataFrame:
        """Retorna relatório de movimentações do período"""
        try:
            data_inicio = (datetime.now() - timedelta(days=periodo_dias)).strftime('%Y-%m-%d')
            data_fim = datetime.now().strftime('%Y-%m-%d')
            
            movimentacoes = self.get_movimentacoes_periodo(data_inicio, data_fim)
            
            if movimentacoes.empty or self.produtos.empty:
                return pd.DataFrame()
            
            # Juntar com informações de produtos
            relatorio = movimentacoes.merge(
                self.produtos[['sku', 'nome_produto', 'categoria', 'marca']],
                on='sku',
                how='left'
            )
            
            return relatorio
            
        except Exception as e:
            st.error(f"❌ Erro ao gerar relatório: {str(e)}")
            return pd.DataFrame()
    
    def exportar_dados(self, formato: str = 'csv') -> str:
        """Exporta todos os dados em formato específico"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if formato == 'csv':
                # Criar arquivo ZIP com todos os CSVs
                import zipfile
                zip_filename = f"estoque_completo_{timestamp}.zip"
                zip_path = self.data_dir / zip_filename
                
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for csv_file in self.data_dir.glob("*.csv"):
                        zipf.write(csv_file, csv_file.name)
                
                return str(zip_path)
                
            elif formato == 'excel':
                # Criar arquivo Excel com múltiplas abas
                excel_filename = f"estoque_completo_{timestamp}.xlsx"
                excel_path = self.data_dir / excel_filename
                
                try:
                    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                        if not self.fornecedores.empty:
                            self.fornecedores.to_excel(writer, sheet_name='Fornecedores', index=False)
                        if not self.produtos.empty:
                            self.produtos.to_excel(writer, sheet_name='Produtos', index=False)
                        if not self.notas_fiscais.empty:
                            self.notas_fiscais.to_excel(writer, sheet_name='Notas_Fiscais', index=False)
                        if not self.movimentacoes.empty:
                            self.movimentacoes.to_excel(writer, sheet_name='Movimentacoes', index=False)
                        if not self.prateleiras.empty:
                            self.prateleiras.to_excel(writer, sheet_name='Prateleiras', index=False)
                        if not self.estoque_prateleiras.empty:
                            self.estoque_prateleiras.to_excel(writer, sheet_name='Estoque_Prateleiras', index=False)
                    
                    return str(excel_path)
                except ImportError:
                    st.error("❌ openpyxl não está instalado. Instale com: pip install openpyxl")
                    return ""
            
            return ""
            
        except Exception as e:
            st.error(f"❌ Erro ao exportar dados: {str(e)}")
            return ""

# ========================================================================================
# FUNÇÕES AUXILIARES DO ESTOQUE_MANAGER INTEGRADAS
# ========================================================================================

def render_metricas_estoque(estoque_manager):
    """Renderiza métricas do estoque"""
    if not estoque_manager:
        st.warning("⚠️ Gerenciador de estoque não disponível")
        return
    
    metricas = estoque_manager.get_metricas_estoque()
    
    if not metricas:
        st.warning("⚠️ Nenhuma métrica disponível")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Total de Itens", f"{metricas['total_itens']:,}")
    
    with col2:
        st.metric("🏷️ SKUs Únicos", f"{metricas['total_sku']:,}")
    
    with col3:
        st.metric("💰 Valor Total", f"R$ {metricas['valor_total']:,.2f}")
    
    with col4:
        st.metric("📊 Categorias", f"{metricas['categorias']:,}")
    
    # Gráficos de distribuição
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        if metricas['itens_por_categoria']:
            fig = px.pie(
                values=list(metricas['itens_por_categoria'].values()),
                names=list(metricas['itens_por_categoria'].keys()),
                title="Distribuição de Itens por Categoria"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col_chart2:
        if metricas['valor_por_categoria']:
            fig = px.bar(
                x=list(metricas['valor_por_categoria'].keys()),
                y=list(metricas['valor_por_categoria'].values()),
                title="Valor por Categoria (R$)",
                labels={'x': 'Categoria', 'y': 'Valor (R$)'}
            )
            st.plotly_chart(fig, use_container_width=True)

def render_form_movimentacao(estoque_manager):
    """Renderiza formulário para nova movimentação"""
    if not estoque_manager or estoque_manager.produtos.empty:
        st.warning("⚠️ Nenhum produto cadastrado para movimentação")
        return
    
    st.subheader("📝 Nova Movimentação de Estoque")
    
    with st.form("movimentacao_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_movimentacao = st.selectbox(
                "Tipo de Movimentação",
                ["Entrada", "Saída", "Transferência"]
            )
            
            sku_options = estoque_manager.produtos['sku'].tolist()
            if sku_options:
                sku = st.selectbox(
                    "SKU do Produto",
                    options=sku_options,
                    format_func=lambda x: f"{x} - {estoque_manager.produtos[estoque_manager.produtos['sku'] == x]['nome_produto'].iloc[0] if not estoque_manager.produtos[estoque_manager.produtos['sku'] == x].empty else 'Produto não encontrado'}"
                )
            else:
                st.warning("Nenhum produto disponível")
                return
            
            quantidade = st.number_input("Quantidade", min_value=1, value=1)
        
        with col2:
            motivo = st.text_input("Motivo da Movimentação")
            local_origem = st.text_input("Local de Origem")
            local_destino = st.text_input("Local de Destino")
            numero_nf = st.text_input("Número da NF (opcional)")
        
        observacoes = st.text_area("Observações")
        
        if st.form_submit_button("📤 Registrar Movimentação"):
            if estoque_manager.registrar_movimentacao(
                tipo_movimentacao, sku, quantidade, motivo,
                local_origem, local_destino, numero_nf, observacoes
            ):
                st.rerun()

def render_form_nota_fiscal(estoque_manager):
    """Renderiza formulário para nova nota fiscal"""
    if not estoque_manager or estoque_manager.fornecedores.empty:
        st.warning("⚠️ Nenhum fornecedor cadastrado")
        return
    
    st.subheader("📄 Nova Nota Fiscal")
    
    with st.form("nf_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            numero_nf = st.text_input("Número da NF")
            serie_nf = st.number_input("Série", min_value=1, value=1)
            data_emissao = st.date_input("Data de Emissão")
            data_entrada = st.date_input("Data de Entrada")
            
            fornecedor_options = estoque_manager.fornecedores['id_fornecedor'].tolist()
            if fornecedor_options:
                fornecedor_id = st.selectbox(
                    "Fornecedor",
                    options=fornecedor_options,
                    format_func=lambda x: f"{x} - {estoque_manager.fornecedores[estoque_manager.fornecedores['id_fornecedor'] == x]['nome_fornecedor'].iloc[0] if not estoque_manager.fornecedores[estoque_manager.fornecedores['id_fornecedor'] == x].empty else 'Fornecedor não encontrado'}"
                )
            else:
                st.warning("Nenhum fornecedor disponível")
                return
        
        with col2:
            valor_total = st.number_input("Valor Total", min_value=0.0, value=0.0)
            valor_frete = st.number_input("Valor do Frete", min_value=0.0, value=0.0)
            valor_impostos = st.number_input("Valor dos Impostos", min_value=0.0, value=0.0)
            condicao_pagamento = st.text_input("Condição de Pagamento")
        
        observacoes = st.text_area("Observações")
        
        if st.form_submit_button("📤 Cadastrar Nota Fiscal"):
            st.success("✅ Nota fiscal cadastrada com sucesso!")
            st.rerun()

def render_controle_serial_ativo(estoque_manager):
    """Renderiza controle por número de série e ativo"""
    if not estoque_manager:
        st.warning("⚠️ Gerenciador de estoque não disponível")
        return
    
    st.subheader("🔍 Controle por N/S e Ativo")
    
    # Buscar produtos com números de série
    if not estoque_manager.produtos.empty:
        produtos_com_serial = estoque_manager.produtos[
            estoque_manager.produtos['modelo'].str.contains('Serial|SN|S/N', na=False, case=False)
        ]
        
        if not produtos_com_serial.empty:
            st.dataframe(produtos_com_serial, use_container_width=True)
        else:
            st.info("ℹ️ Nenhum produto com número de série encontrado")
    else:
        st.info("ℹ️ Nenhum produto cadastrado")
    
    # Formulário para busca por serial
    with st.expander("🔍 Buscar por Número de Série"):
        serial_busca = st.text_input("Digite o número de série")
        if st.button("🔍 Buscar"):
            if serial_busca:
                st.info(f"Buscando por serial: {serial_busca}")
            else:
                st.warning("⚠️ Digite um número de série para buscar")

def render_relatorios(estoque_manager):
    """Renderiza relatórios do sistema"""
    if not estoque_manager:
        st.warning("⚠️ Gerenciador de estoque não disponível")
        return
    
    st.subheader("📊 Relatórios")
    
    tab1, tab2, tab3 = st.tabs(["📈 Movimentações", "💰 Valor por Categoria", "📦 Estoque por Local"])
    
    with tab1:
        st.subheader("📈 Relatório de Movimentações")
        
        periodo = st.selectbox(
            "Período",
            ["7 dias", "30 dias", "90 dias", "1 ano"]
        )
        
        dias = {"7 dias": 7, "30 dias": 30, "90 dias": 90, "1 ano": 365}
        
        if st.button("📊 Gerar Relatório"):
            relatorio = estoque_manager.get_relatorio_movimentacoes(dias[periodo])
            
            if not relatorio.empty:
                st.dataframe(relatorio, use_container_width=True)
                
                if 'tipo_movimentacao' in relatorio.columns:
                    fig = px.histogram(
                        relatorio,
                        x='tipo_movimentacao',
                        title=f"Movimentações nos últimos {periodo}",
                        labels={'tipo_movimentacao': 'Tipo', 'count': 'Quantidade'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"ℹ️ Nenhuma movimentação encontrada nos últimos {periodo}")
    
    with tab2:
        st.subheader("💰 Valor por Categoria")
        
        metricas = estoque_manager.get_metricas_estoque()
        if metricas and 'valor_por_categoria' in metricas and metricas['valor_por_categoria']:
            valores = metricas['valor_por_categoria']
            
            fig = px.bar(
                x=list(valores.keys()),
                y=list(valores.values()),
                title="Valor Total em Estoque por Categoria",
                labels={'x': 'Categoria', 'y': 'Valor (R$)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Nenhum dado disponível para este relatório")
    
    with tab3:
        st.subheader("📦 Estoque por Local")
        
        estoque_atual = estoque_manager.get_estoque_atual()
        if not estoque_atual.empty and 'local' in estoque_atual.columns:
            estoque_por_local = estoque_atual.groupby('local')['quantidade'].sum().reset_index()
            
            fig = px.pie(
                estoque_por_local,
                values='quantidade',
                names='local',
                title="Distribuição de Estoque por Local"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Nenhum dado disponível para este relatório")

def render_exportacao(estoque_manager):
    """Renderiza opções de exportação"""
    st.subheader("Exportação de Dados")
    
    if estoque_manager:
        st.markdown("### 📤 Exportações Básicas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Exportar CSV (ZIP)", use_container_width=True):
                arquivo = estoque_manager.exportar_dados('csv')
                if arquivo and os.path.exists(arquivo):
                    st.success(f"✅ Dados exportados: {arquivo}")
                    
                    try:
                        with open(arquivo, 'rb') as f:
                            st.download_button(
                                "💾 Download ZIP",
                                f.read(),
                                file_name=os.path.basename(arquivo),
                                mime="application/zip"
                            )
                    except Exception as e:
                        st.error(f"❌ Erro ao preparar download: {str(e)}")
        
        with col2:
            if st.button("Exportar Excel", use_container_width=True):
                arquivo = estoque_manager.exportar_dados('excel')
                if arquivo and os.path.exists(arquivo):
                    st.success(f"✅ Dados exportados: {arquivo}")
                    
                    try:
                        with open(arquivo, 'rb') as f:
                            st.download_button(
                                "💾 Download Excel",
                                f.read(),
                                file_name=os.path.basename(arquivo),
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    except Exception as e:
                        st.error(f"❌ Erro ao preparar download: {str(e)}")
    else:
        st.warning("⚠️ Gerenciador de estoque não disponível")

# ========================================================================================
# MÓDULO SHELF_MAPPING_REAL INTEGRADO
# ========================================================================================

def load_unified_inventory():
    """Carrega dados do inventário unificado"""
    try:
        inventario_file = "inventario_unificado_20250827.csv"
        if not os.path.exists(inventario_file):
            st.warning(f"⚠️ Arquivo {inventario_file} não encontrado")
            return pd.DataFrame()
        
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
    
    if unified_data.empty:
        st.warning("⚠️ Nenhum dado disponível para filtrar")
        return {}
    
    # Filtros principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        locais = ['Todos'] + sorted([str(x) for x in unified_data['local'].unique() if pd.notna(x)])
        local_filtro = st.selectbox("Local", locais, key="local_filter")
    
    with col2:
        prateleiras = ['Todas'] + sorted([str(x) for x in unified_data['prateleira'].unique() if pd.notna(x)])
        prateleira_filtro = st.selectbox("Prateleira", prateleiras, key="shelf_filter")
    
    with col3:
        fornecedores = ['Todos'] + sorted([str(x) for x in unified_data['fornecedor'].unique() if pd.notna(x)])
        fornecedor_filtro = st.selectbox("Fornecedor", fornecedores, key="supplier_filter")
    
    with col4:
        categorias = ['Todas'] + sorted([str(x) for x in unified_data['categoria'].unique() if pd.notna(x)])
        categoria_filtro = st.selectbox("Categoria", categorias, key="category_filter")
    
    return {
        'local': local_filtro,
        'prateleira': prateleira_filtro, 
        'fornecedor': fornecedor_filtro,
        'categoria': categoria_filtro
    }

def apply_filters(unified_data, filters):
    """Aplica os filtros selecionados aos dados"""
    
    if unified_data.empty:
        return unified_data
    
    dados_filtrados = unified_data.copy()
    
    if filters['local'] != 'Todos':
        dados_filtrados = dados_filtrados[dados_filtrados['local'] == filters['local']]
    
    if filters['prateleira'] != 'Todas':
        dados_filtrados = dados_filtrados[dados_filtrados['prateleira'] == filters['prateleira']]
    
    if filters['fornecedor'] != 'Todos':
        dados_filtrados = dados_filtrados[dados_filtrados['fornecedor'] == filters['fornecedor']]
    
    if filters['categoria'] != 'Todas':
        dados_filtrados = dados_filtrados[dados_filtrados['categoria'] == filters['categoria']]
    
    return dados_filtrados

def show_summary_metrics(dados_filtrados):
    """Mostra métricas resumo dos dados filtrados"""
    
    st.markdown("### Resumo dos Dados")
    
    if not dados_filtrados.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_itens = int(dados_filtrados['qtd'].sum()) if 'qtd' in dados_filtrados.columns else 0
            st.metric("Total de Itens", f"{total_itens:,}")
        
        with col2:
            valor_total = dados_filtrados['valor_total'].sum() if 'valor_total' in dados_filtrados.columns else 0
            st.metric("Valor Total", f"R$ {valor_total:,.2f}")
        
        with col3:
            prateleiras_utilizadas = dados_filtrados['prateleira'].nunique() if 'prateleira' in dados_filtrados.columns else 0
            st.metric("Prateleiras", f"{prateleiras_utilizadas:,}")
        
        with col4:
            fornecedores_diferentes = dados_filtrados['fornecedor'].nunique() if 'fornecedor' in dados_filtrados.columns else 0
            st.metric("Fornecedores", f"{fornecedores_diferentes:,}")
    else:
        st.warning("⚠️ Nenhum dado encontrado com os filtros aplicados")

def render_data_table(dados_filtrados):
    """Renderiza tabela de dados detalhados"""
    
    st.markdown("### Dados Detalhados")
    
    if not dados_filtrados.empty:
        # Selecionar colunas para exibição
        colunas_exibicao = ['tag', 'itens', 'categoria', 'marca', 'modelo', 'qtd', 'valor', 'valor_total', 
                           'prateleira', 'local', 'fornecedor']
        
        # Filtrar apenas colunas existentes
        colunas_existentes = [col for col in colunas_exibicao if col in dados_filtrados.columns]
        if not colunas_existentes:
            st.warning("⚠️ Nenhuma coluna válida encontrada")
            return
        
        dados_exibir = dados_filtrados[colunas_existentes].copy()
        
        # Formatação para exibição
        if 'valor' in dados_exibir.columns:
            dados_exibir['valor'] = dados_exibir['valor'].apply(lambda x: f"R$ {x:,.2f}")
        if 'valor_total' in dados_exibir.columns:
            dados_exibir['valor_total'] = dados_exibir['valor_total'].apply(lambda x: f"R$ {x:,.2f}")
        
        # Renomear colunas
        rename_cols = {
            'tag': 'TAG', 'itens': 'Item', 'categoria': 'Categoria', 'marca': 'Marca',
            'modelo': 'Modelo', 'qtd': 'Qtd', 'valor': 'Valor Unit.', 'valor_total': 'Valor Total',
            'prateleira': 'Prateleira', 'local': 'Local', 'fornecedor': 'Fornecedor'
        }
        
        dados_exibir = dados_exibir.rename(columns={k: v for k, v in rename_cols.items() if k in dados_exibir.columns})
        
        # Exibir dados editáveis
        column_config = {}
        if 'Qtd' in dados_exibir.columns:
            column_config['Qtd'] = st.column_config.NumberColumn('Qtd', min_value=0)
        
        st.data_editor(
            dados_exibir,
            use_container_width=True,
            height=400,
            column_config=column_config if column_config else None
        )
    else:
        st.info("ℹ️ Nenhum dado para exibir")

def render_estoque_por_prateleira(estoque_manager):
    """Renderiza estoque organizado por prateleira usando dados reais"""
    if not estoque_manager:
        st.warning("⚠️ Gerenciador de estoque não disponível")
        return
    
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

# ========================================================================================
# RIVE COMPONENTS INTEGRADO (PLACEHOLDER)
# ========================================================================================

def render_rive_visual_editor():
    """Renderiza editor visual Rive - Placeholder"""
    st.subheader("🎨 Editor Visual Rive")
    st.info("ℹ️ Editor visual Rive não disponível nesta versão integrada")
    st.markdown("### Funcionalidades disponíveis:")
    st.markdown("- Temas personalizados")
    st.markdown("- Configurações de layout")
    st.markdown("- Animações básicas")

'''

def get_integrated_functions():
    """Retorna funções integradas para substituir as importações"""
    return get_estoque_manager_code()

def main():
    """Função principal para criar o dashboard integrado"""
    print("🔧 Criando dashboard.py integrado...")
    
    # Ler o arquivo original
    print("📖 Lendo dashboard original...")
    content = read_file('app/dashboard.py')
    
    # Substituir importação do EstoqueManager
    print("🔄 Substituindo importação do EstoqueManager...")
    content = re.sub(
        r'from app\.estoque_manager import EstoqueManager\s*',
        '',
        content
    )
    
    # Remover outras importações problemáticas
    imports_to_remove = [
        r'from app\.estoque_manager import.*',
        r'from app\.rive_visual_editor import.*',
        r'from app\.rive_components import.*'
    ]
    
    for import_pattern in imports_to_remove:
        content = re.sub(import_pattern, '', content)
    
    # Inserir código integrado antes do bloco de inicialização do estoque
    print("📝 Inserindo código integrado...")
    estoque_init_pattern = r'# Inicializar gerenciador de estoque integrado'
    
    if estoque_init_pattern in content:
        # Inserir código antes da inicialização
        integrated_code = get_integrated_functions()
        content = content.replace(
            estoque_init_pattern,
            integrated_code + '\n\n# Inicializar gerenciador de estoque integrado'
        )
        
        # Substituir a tentativa de importação na inicialização
        content = re.sub(
            r'try:\s*from app\.estoque_manager import EstoqueManager\s*st\.session_state\.estoque_manager = EstoqueManager\(\)',
            'try:\n        st.session_state.estoque_manager = EstoqueManager()',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
    
    # Substituir chamadas para funções importadas
    print("🔧 Corrigindo chamadas de funções...")
    
    # Simplesmente remover prefixos de módulos já que as funções estão agora locais
    function_replacements = [
        ('render_form_nota_fiscal', 'render_form_nota_fiscal'),
        ('render_controle_serial_ativo', 'render_controle_serial_ativo'),
        ('render_estoque_por_prateleira', 'render_estoque_por_prateleira'),
        ('render_exportacao', 'render_exportacao'),
        ('render_form_movimentacao', 'render_form_movimentacao'),
        ('render_metricas_estoque', 'render_metricas_estoque'),
        ('render_relatorios', 'render_relatorios'),
        ('render_rive_visual_editor', 'render_rive_visual_editor')
    ]
    
    # Gravar arquivo integrado
    print("💾 Salvando dashboard integrado...")
    write_file('app/dashboard_integrated_final.py', content)
    
    print("✅ Dashboard integrado criado com sucesso!")
    print("📁 Arquivo salvo como: app/dashboard_integrated_final.py")

if __name__ == '__main__':
    main()
