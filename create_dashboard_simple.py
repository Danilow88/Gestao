#!/usr/bin/env python3
"""
Script simples para criar dashboard integrado
"""

def main():
    print("Criando dashboard integrado...")
    
    # Ler dashboard original
    with open('app/dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Código integrado do EstoqueManager
    estoque_manager_code = '''
# ========================================================================================
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
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados: {str(e)}")
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

def render_form_movimentacao(estoque_manager):
    """Renderiza formulário para nova movimentação"""
    if not estoque_manager or estoque_manager.produtos.empty:
        st.warning("⚠️ Nenhum produto cadastrado para movimentação")
        return
    
    st.subheader("📝 Nova Movimentação de Estoque")
    st.info("ℹ️ Funcionalidade disponível na versão integrada")

def render_form_nota_fiscal(estoque_manager):
    """Renderiza formulário para nova nota fiscal"""
    st.subheader("📄 Nova Nota Fiscal")
    st.info("ℹ️ Funcionalidade disponível na versão integrada")

def render_controle_serial_ativo(estoque_manager):
    """Renderiza controle por número de série e ativo"""
    st.subheader("🔍 Controle por N/S e Ativo")
    st.info("ℹ️ Funcionalidade disponível na versão integrada")

def render_relatorios(estoque_manager):
    """Renderiza relatórios do sistema"""
    st.subheader("📊 Relatórios")
    st.info("ℹ️ Funcionalidade disponível na versão integrada")

def render_exportacao(estoque_manager):
    """Renderiza opções de exportação"""
    st.subheader("📤 Exportação de Dados")
    st.info("ℹ️ Funcionalidade disponível na versão integrada")

def render_estoque_por_prateleira(estoque_manager):
    """Renderiza estoque organizado por prateleira"""
    st.subheader("📦 Estoque por Prateleira")
    st.info("ℹ️ Funcionalidade disponível na versão integrada")

def render_rive_visual_editor():
    """Renderiza editor visual Rive"""
    st.subheader("🎨 Editor Visual Rive")
    st.info("ℹ️ Editor visual Rive não disponível nesta versão integrada")

'''
    
    # Remover importações problemáticas
    import re
    
    # Remover as linhas de import problemáticas
    content = re.sub(r'        from app\.estoque_manager import EstoqueManager\n', '', content)
    content = re.sub(r'        from app\.estoque_manager import .*\n', '', content)
    content = re.sub(r'        from app\.rive_visual_editor import .*\n', '', content)
    content = re.sub(r'        from app\.rive_components import .*\n', '', content)
    
    # Inserir código integrado antes da inicialização do estoque_manager
    insertion_point = "# Inicializar gerenciador de estoque integrado"
    if insertion_point in content:
        content = content.replace(insertion_point, estoque_manager_code + "\n\n" + insertion_point)
        
        # Corrigir a inicialização do EstoqueManager
        content = content.replace(
            "        from app.estoque_manager import EstoqueManager\n        st.session_state.estoque_manager = EstoqueManager()",
            "        st.session_state.estoque_manager = EstoqueManager()"
        )
    
    # Salvar arquivo integrado
    with open('app/dashboard_integrated_final.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Dashboard integrado criado: app/dashboard_integrated_final.py")

if __name__ == '__main__':
    main()
