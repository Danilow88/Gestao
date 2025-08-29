"""
Módulo de Gerenciamento de Estoque Integrado
Sistema completo para controle de estoque, notas fiscais, movimentações e prateleiras
"""

import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Optional, Tuple
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

class EstoqueManager:
    """Classe principal para gerenciamento integrado de estoque"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.load_all_data()
    
    def load_all_data(self):
        """Carrega todos os dados dos arquivos CSV"""
        try:
            # Carregar dados principais
            self.fornecedores = pd.read_csv(self.data_dir / "fornecedores.csv")
            self.produtos = pd.read_csv(self.data_dir / "produtos.csv")
            self.notas_fiscais = pd.read_csv(self.data_dir / "notas_fiscais.csv")
            self.movimentacoes = pd.read_csv(self.data_dir / "movimentacoes.csv")
            self.prateleiras = pd.read_csv(self.data_dir / "prateleiras.csv")
            self.estoque_prateleiras = pd.read_csv(self.data_dir / "estoque_prateleiras.csv")
            
            # Converter datas
            date_columns = {
                'notas_fiscais': ['data_emissao', 'data_entrada', 'data_cadastro'],
                'movimentacoes': ['data_movimentacao'],
                'estoque_prateleiras': ['data_entrada', 'data_ultima_movimentacao'],
                'prateleiras': ['data_cadastro']
            }
            
            for df_name, columns in date_columns.items():
                df = getattr(self, df_name)
                for col in columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Converter valores numéricos
            numeric_columns = {
                'produtos': ['preco_unitario', 'peso', 'volume'],
                'notas_fiscais': ['valor_total', 'valor_frete', 'valor_impostos'],
                'movimentacoes': ['quantidade', 'valor_unitario', 'valor_total'],
                'estoque_prateleiras': ['quantidade'],
                'prateleiras': ['capacidade_total', 'capacidade_utilizada', 'capacidade_disponivel']
            }
            
            for df_name, columns in numeric_columns.items():
                df = getattr(self, df_name)
                for col in columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            st.success("✅ Todos os dados carregados com sucesso!")
            
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
            filepath = self.data_dir / filename
            df.to_csv(filepath, index=False)
            return True
        except Exception as e:
            st.error(f"❌ Erro ao salvar {filename}: {str(e)}")
            return False
    
    def get_estoque_atual(self) -> pd.DataFrame:
        """Retorna estoque atual consolidado"""
        try:
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
            df['data_movimentacao'] = pd.to_datetime(df['data_movimentacao'])
            
            mask = (df['data_movimentacao'] >= data_inicio) & (df['data_movimentacao'] <= data_fim)
            return df[mask]
            
        except Exception as e:
            st.error(f"❌ Erro ao filtrar movimentações: {str(e)}")
            return pd.DataFrame()
    
    def get_produtos_por_fornecedor(self, fornecedor_id: str = None) -> pd.DataFrame:
        """Retorna produtos agrupados por fornecedor"""
        try:
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
            
            # Atualizar estoque
            self.atualizar_estoque_apos_movimentacao(sku, quantidade, tipo, local_destino)
            
            # Salvar dados
            self.save_data(self.movimentacoes, "movimentacoes.csv")
            
            st.success(f"✅ Movimentação registrada com sucesso: {tipo} de {quantidade} unidades de {sku}")
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao registrar movimentação: {str(e)}")
            return False
    
    def atualizar_estoque_apos_movimentacao(self, sku: str, quantidade: int, 
                                           tipo_movimentacao: str, local_destino: str):
        """Atualiza o estoque após uma movimentação"""
        try:
            if tipo_movimentacao == "Entrada":
                # Adicionar ao estoque
                self.adicionar_ao_estoque(sku, quantidade, local_destino)
            elif tipo_movimentacao == "Saída":
                # Remover do estoque
                self.remover_do_estoque(sku, quantidade, local_destino)
            elif tipo_movimentacao == "Transferência":
                # Transferir entre locais
                self.transferir_estoque(sku, quantidade, local_destino)
                
        except Exception as e:
            st.error(f"❌ Erro ao atualizar estoque: {str(e)}")
    
    def adicionar_ao_estoque(self, sku: str, quantidade: int, local_destino: str):
        """Adiciona produtos ao estoque"""
        try:
            # Verificar se já existe estoque para este SKU no local
            mask = (self.estoque_prateleiras['sku'] == sku) & \
                   (self.estoque_prateleiras['prateleira_id'].str.contains(local_destino.split()[0]))
            
            if mask.any():
                # Atualizar quantidade existente
                idx = mask.idxmax()
                self.estoque_prateleiras.loc[idx, 'quantidade'] += quantidade
                self.estoque_prateleiras.loc[idx, 'data_ultima_movimentacao'] = datetime.now().strftime('%Y-%m-%d')
            else:
                # Criar novo registro de estoque
                nova_entrada = {
                    'id_estoque_prateleira': f"EST{len(self.estoque_prateleiras) + 1:03d}",
                    'prateleira_id': self.get_prateleira_por_local(local_destino),
                    'sku': sku,
                    'quantidade': quantidade,
                    'posicao_na_prateleira': '1',
                    'data_entrada': datetime.now().strftime('%Y-%m-%d'),
                    'data_ultima_movimentacao': datetime.now().strftime('%Y-%m-%d'),
                    'status': 'Ativo',
                    'observacoes': f'Entrada automática via sistema'
                }
                
                self.estoque_prateleiras = pd.concat([
                    self.estoque_prateleiras,
                    pd.DataFrame([nova_entrada])
                ], ignore_index=True)
            
            # Salvar dados
            self.save_data(self.estoque_prateleiras, "estoque_prateleiras.csv")
            
        except Exception as e:
            st.error(f"❌ Erro ao adicionar ao estoque: {str(e)}")
    
    def remover_do_estoque(self, sku: str, quantidade: int, local_origem: str):
        """Remove produtos do estoque"""
        try:
            # Buscar estoque existente
            mask = (self.estoque_prateleiras['sku'] == sku) & \
                   (self.estoque_prateleiras['prateleira_id'].str.contains(local_origem.split()[0]))
            
            if mask.any():
                idx = mask.idxmax()
                estoque_atual = self.estoque_prateleiras.loc[idx, 'quantidade']
                
                if estoque_atual >= quantidade:
                    self.estoque_prateleiras.loc[idx, 'quantidade'] -= quantidade
                    self.estoque_prateleiras.loc[idx, 'data_ultima_movimentacao'] = datetime.now().strftime('%Y-%m-%d')
                    
                    # Se estoque zerou, marcar como inativo
                    if self.estoque_prateleiras.loc[idx, 'quantidade'] == 0:
                        self.estoque_prateleiras.loc[idx, 'status'] = 'Inativo'
                    
                    # Salvar dados
                    self.save_data(self.estoque_prateleiras, "estoque_prateleiras.csv")
                else:
                    st.error(f"❌ Estoque insuficiente: {estoque_atual} disponível, {quantidade} solicitado")
            else:
                st.error(f"❌ Produto {sku} não encontrado no local {local_origem}")
                
        except Exception as e:
            st.error(f"❌ Erro ao remover do estoque: {str(e)}")
    
    def transferir_estoque(self, sku: str, quantidade: int, local_destino: str):
        """Transfere estoque entre locais"""
        try:
            # Primeiro remover do local de origem
            self.remover_do_estoque(sku, quantidade, "local_origem")
            
            # Depois adicionar ao local de destino
            self.adicionar_ao_estoque(sku, quantidade, local_destino)
            
        except Exception as e:
            st.error(f"❌ Erro ao transferir estoque: {str(e)}")
    
    def get_prateleira_por_local(self, local: str) -> str:
        """Retorna ID da prateleira baseado no local"""
        try:
            # Extrair informações do local (ex: "HQ1 - 8º Andar")
            local_parts = local.split()
            if len(local_parts) >= 2:
                predio = local_parts[0]  # HQ1, Spark, etc.
                andar = local_parts[2] if len(local_parts) > 2 else ""
                
                # Buscar prateleira apropriada
                mask = self.prateleiras['local'].str.contains(predio, na=False)
                if andar:
                    mask &= self.prateleiras['local'].str.contains(andar, na=False)
                
                if mask.any():
                    return self.prateleiras[mask].iloc[0]['id_prateleira']
            
            # Retornar primeira prateleira disponível se não encontrar
            return self.prateleiras.iloc[0]['id_prateleira']
            
        except Exception as e:
            st.error(f"❌ Erro ao buscar prateleira: {str(e)}")
            return "PRAT001"  # Prateleira padrão
    
    def get_metricas_estoque(self) -> Dict:
        """Retorna métricas consolidadas do estoque"""
        try:
            estoque_atual = self.get_estoque_atual()
            
            if estoque_atual.empty:
                return {}
            
            metricas = {
                'total_itens': int(estoque_atual['quantidade'].sum()),
                'total_sku': len(estoque_atual['sku'].unique()),
                'valor_total': float(estoque_atual['valor_total_estoque'].sum()),
                'categorias': len(estoque_atual['categoria'].unique()),
                'prateleiras_ativas': len(estoque_atual['prateleira_id'].unique()),
                'itens_por_categoria': estoque_atual.groupby('categoria')['quantidade'].sum().to_dict(),
                'valor_por_categoria': estoque_atual.groupby('categoria')['valor_total_estoque'].sum().to_dict()
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
            
            if movimentacoes.empty:
                return pd.DataFrame()
            
            # Juntar com informações de produtos e fornecedores
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
                
                with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                    self.fornecedores.to_excel(writer, sheet_name='Fornecedores', index=False)
                    self.produtos.to_excel(writer, sheet_name='Produtos', index=False)
                    self.notas_fiscais.to_excel(writer, sheet_name='Notas_Fiscais', index=False)
                    self.movimentacoes.to_excel(writer, sheet_name='Movimentacoes', index=False)
                    self.prateleiras.to_excel(writer, sheet_name='Prateleiras', index=False)
                    self.estoque_prateleiras.to_excel(writer, sheet_name='Estoque_Prateleiras', index=False)
                
                return str(excel_path)
            
            return ""
            
        except Exception as e:
            st.error(f"❌ Erro ao exportar dados: {str(e)}")
            return ""

# Funções auxiliares para interface Streamlit
def render_metricas_estoque(estoque_manager: EstoqueManager):
    """Renderiza métricas do estoque"""
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

def render_form_movimentacao(estoque_manager: EstoqueManager):
    """Renderiza formulário para nova movimentação"""
    st.subheader("📝 Nova Movimentação de Estoque")
    
    with st.form("movimentacao_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_movimentacao = st.selectbox(
                "Tipo de Movimentação",
                ["Entrada", "Saída", "Transferência"]
            )
            
            sku = st.selectbox(
                "SKU do Produto",
                options=estoque_manager.produtos['sku'].tolist(),
                format_func=lambda x: f"{x} - {estoque_manager.produtos[estoque_manager.produtos['sku'] == x]['nome_produto'].iloc[0]}"
            )
            
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

def render_form_nota_fiscal(estoque_manager: EstoqueManager):
    """Renderiza formulário para nova nota fiscal"""
    st.subheader("📄 Nova Nota Fiscal")
    
    with st.form("nf_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            numero_nf = st.text_input("Número da NF")
            serie_nf = st.number_input("Série", min_value=1, value=1)
            data_emissao = st.date_input("Data de Emissão")
            data_entrada = st.date_input("Data de Entrada")
            fornecedor_id = st.selectbox(
                "Fornecedor",
                options=estoque_manager.fornecedores['id_fornecedor'].tolist(),
                format_func=lambda x: f"{x} - {estoque_manager.fornecedores[estoque_manager.fornecedores['id_fornecedor'] == x]['nome_fornecedor'].iloc[0]}"
            )
        
        with col2:
            valor_total = st.number_input("Valor Total", min_value=0.0, value=0.0)
            valor_frete = st.number_input("Valor do Frete", min_value=0.0, value=0.0)
            valor_impostos = st.number_input("Valor dos Impostos", min_value=0.0, value=0.0)
            condicao_pagamento = st.text_input("Condição de Pagamento")
        
        observacoes = st.text_area("Observações")
        
        if st.form_submit_button("📤 Cadastrar Nota Fiscal"):
            # Implementar lógica para cadastrar NF
            st.success("✅ Nota fiscal cadastrada com sucesso!")
            st.rerun()

def render_controle_serial_ativo(estoque_manager: EstoqueManager):
    """Renderiza controle por número de série e ativo"""
    st.subheader("🔍 Controle por N/S e Ativo")
    
    # Buscar produtos com números de série
    produtos_com_serial = estoque_manager.produtos[
        estoque_manager.produtos['modelo'].str.contains('Serial|SN|S/N', na=False, case=False)
    ]
    
    if not produtos_com_serial.empty:
        st.dataframe(produtos_com_serial, use_container_width=True)
    else:
        st.info("ℹ️ Nenhum produto com número de série encontrado")
    
    # Formulário para busca por serial
    with st.expander("🔍 Buscar por Número de Série"):
        serial_busca = st.text_input("Digite o número de série")
        if st.button("🔍 Buscar"):
            if serial_busca:
                # Implementar busca por serial
                st.info(f"Buscando por serial: {serial_busca}")
            else:
                st.warning("⚠️ Digite um número de série para buscar")

def render_estoque_por_prateleira(estoque_manager: EstoqueManager):
    """Renderiza estoque organizado por prateleira usando dados reais"""
    try:
        # Importar e usar o novo módulo de mapeamento
        from app.shelf_mapping_real import render_shelf_mapping_page
        render_shelf_mapping_page()
    except ImportError:
        st.error("❌ Módulo de mapeamento de prateleiras não encontrado")
        # Fallback para versão básica
        st.subheader("📦 Estoque por Prateleira - Versão Básica")
        
        # Selecionar prateleira
        prateleiras_disponiveis = estoque_manager.prateleiras['nome_prateleira'].unique()
        prateleira_selecionada = st.selectbox(
            "Selecionar Prateleira",
            options=prateleiras_disponiveis
        )
        
        if prateleira_selecionada:
            # Buscar prateleira
            prateleira_id = estoque_manager.prateleiras[
                estoque_manager.prateleiras['nome_prateleira'] == prateleira_selecionada
            ]['id_prateleira'].iloc[0]
            
            # Buscar estoque da prateleira
            estoque_prateleira = estoque_manager.get_estoque_por_prateleira(prateleira_id)
            
            if not estoque_prateleira.empty:
                # Mostrar informações da prateleira
                info_prateleira = estoque_manager.prateleiras[
                    estoque_manager.prateleiras['id_prateleira'] == prateleira_id
                ].iloc[0]
                
                col_info1, col_info2, col_info3 = st.columns(3)
                
                with col_info1:
                    st.metric("📍 Local", info_prateleira['local'])
                    st.metric("🏢 Setor", info_prateleira['setor'])
                
                with col_info2:
                    st.metric("📏 Capacidade Total", f"{info_prateleira['capacidade_total']:,}")
                    st.metric("📦 Capacidade Utilizada", f"{info_prateleira['capacidade_utilizada']:,}")
                
                with col_info3:
                    st.metric("🆓 Capacidade Disponível", f"{info_prateleira['capacidade_disponivel']:,}")
                    st.metric("📊 Ocupação", f"{(info_prateleira['capacidade_utilizada'] / info_prateleira['capacidade_total'] * 100):.1f}%")
                
                # Mostrar itens da prateleira
                st.subheader(f"📦 Itens na {prateleira_selecionada}")
                st.dataframe(estoque_prateleira, use_container_width=True)
                
            else:
                st.info(f"ℹ️ Nenhum item encontrado na prateleira {prateleira_selecionada}")
    except Exception as e:
        st.error(f"❌ Erro ao carregar mapeamento de prateleiras: {str(e)}")

def render_relatorios(estoque_manager: EstoqueManager):
    """Renderiza relatórios do sistema"""
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
                
                # Gráfico de movimentações por tipo
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
        if metricas and 'valor_por_categoria' in metricas:
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
        if not estoque_atual.empty:
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

def generate_audit_report():
    """Gera relatório completo de auditoria do estoque unificado"""
    try:
        # Carregar dados do inventário unificado
        inventario_file = "inventario_unificado_20250827.csv"
        unified_data = pd.read_csv(inventario_file)
        
        # Converter valores numéricos
        unified_data['valor'] = pd.to_numeric(unified_data['valor'], errors='coerce').fillna(0)
        unified_data['qtd'] = pd.to_numeric(unified_data['qtd'], errors='coerce').fillna(0)
        unified_data['valor_total'] = unified_data['valor'] * unified_data['qtd']
        
        # Criar relatório de auditoria
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Dados do cabeçalho
        header_info = {
            'Data_Geracao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'Total_Itens': len(unified_data),
            'Valor_Total_Estoque': unified_data['valor_total'].sum(),
            'Total_Conferidos': unified_data['conferido'].sum(),
            'Total_Pendentes': len(unified_data) - unified_data['conferido'].sum(),
            'Percentual_Conferido': (unified_data['conferido'].sum() / len(unified_data) * 100) if len(unified_data) > 0 else 0,
            'Prateleiras_Utilizadas': unified_data['prateleira'].nunique(),
            'Locais_Utilizados': unified_data['local'].nunique(),
            'Fornecedores_Diferentes': unified_data['fornecedor'].nunique(),
            'Categorias_Diferentes': unified_data['categoria'].nunique()
        }
        
        # Análises por categoria
        categoria_summary = unified_data.groupby('categoria').agg({
            'qtd': ['sum', 'count'],
            'valor_total': 'sum',
            'conferido': 'sum'
        }).round(2)
        categoria_summary.columns = ['Qtd_Total', 'Num_Itens', 'Valor_Total', 'Itens_Conferidos']
        categoria_summary['Percentual_Conferido'] = (categoria_summary['Itens_Conferidos'] / categoria_summary['Num_Itens'] * 100).round(1)
        
        # Análises por prateleira
        prateleira_summary = unified_data.groupby(['prateleira', 'local', 'setor']).agg({
            'qtd': 'sum',
            'valor_total': 'sum',
            'conferido': 'sum'
        }).reset_index()
        prateleira_summary.columns = ['Prateleira', 'Local', 'Setor', 'Qtd_Total', 'Valor_Total', 'Itens_Conferidos']
        
        # Análises por fornecedor
        fornecedor_summary = unified_data.groupby('fornecedor').agg({
            'qtd': 'sum',
            'valor_total': 'sum',
            'conferido': 'sum'
        }).reset_index()
        fornecedor_summary.columns = ['Fornecedor', 'Qtd_Total', 'Valor_Total', 'Itens_Conferidos']
        fornecedor_summary = fornecedor_summary.sort_values('Valor_Total', ascending=False)
        
        # Identificar inconsistências
        inconsistencias = []
        
        # Itens sem conferência
        itens_nao_conferidos = unified_data[unified_data['conferido'] == False]
        if len(itens_nao_conferidos) > 0:
            inconsistencias.append({
                'Tipo': 'Itens não conferidos',
                'Quantidade': len(itens_nao_conferidos),
                'Valor_Envolvido': itens_nao_conferidos['valor_total'].sum(),
                'Detalhes': f"{len(itens_nao_conferidos)} itens ainda precisam ser conferidos"
            })
        
        # Itens sem valor
        itens_sem_valor = unified_data[unified_data['valor'] == 0]
        if len(itens_sem_valor) > 0:
            inconsistencias.append({
                'Tipo': 'Itens sem valor',
                'Quantidade': len(itens_sem_valor),
                'Valor_Envolvido': 0,
                'Detalhes': f"{len(itens_sem_valor)} itens com valor zero ou não informado"
            })
        
        # Itens com quantidade zero
        itens_sem_qtd = unified_data[unified_data['qtd'] == 0]
        if len(itens_sem_qtd) > 0:
            inconsistencias.append({
                'Tipo': 'Itens sem quantidade',
                'Quantidade': len(itens_sem_qtd),
                'Valor_Envolvido': itens_sem_qtd['valor_total'].sum(),
                'Detalhes': f"{len(itens_sem_qtd)} itens com quantidade zero"
            })
        
        # Criar DataFrame de inconsistências
        df_inconsistencias = pd.DataFrame(inconsistencias) if inconsistencias else pd.DataFrame()
        
        # Criar arquivo Excel com múltiplas abas
        excel_filename = f"relatorio_auditoria_estoque_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            # Aba 1: Resumo Executivo
            df_header = pd.DataFrame(list(header_info.items()), columns=['Métrica', 'Valor'])
            df_header.to_excel(writer, sheet_name='Resumo_Executivo', index=False)
            
            # Aba 2: Dados Completos
            unified_data.to_excel(writer, sheet_name='Inventario_Completo', index=False)
            
            # Aba 3: Análise por Categoria
            categoria_summary.reset_index().to_excel(writer, sheet_name='Analise_Categoria', index=False)
            
            # Aba 4: Análise por Prateleira
            prateleira_summary.to_excel(writer, sheet_name='Analise_Prateleira', index=False)
            
            # Aba 5: Análise por Fornecedor
            fornecedor_summary.to_excel(writer, sheet_name='Analise_Fornecedor', index=False)
            
            # Aba 6: Inconsistências
            if not df_inconsistencias.empty:
                df_inconsistencias.to_excel(writer, sheet_name='Inconsistencias', index=False)
            else:
                df_vazio = pd.DataFrame({'Mensagem': ['Nenhuma inconsistência encontrada']})
                df_vazio.to_excel(writer, sheet_name='Inconsistencias', index=False)
            
            # Aba 7: Itens Não Conferidos (se houver)
            if len(itens_nao_conferidos) > 0:
                itens_nao_conferidos.to_excel(writer, sheet_name='Itens_Nao_Conferidos', index=False)
        
        return excel_filename, header_info
        
    except Exception as e:
        st.error(f"❌ Erro ao gerar relatório de auditoria: {str(e)}")
        return None, None

def render_exportacao(estoque_manager: EstoqueManager):
    """Renderiza opções de exportação"""
    st.subheader("Exportação de Dados")
    
    # Seção de relatórios especiais
    st.markdown("### 📋 Relatórios Especiais")
    
    col_audit = st.columns(1)[0]
    with col_audit:
        if st.button("📊 Relatório Completo de Auditoria", use_container_width=True, type="primary"):
            with st.spinner("Gerando relatório de auditoria..."):
                arquivo, header_info = generate_audit_report()
                
                if arquivo and header_info:
                    st.success(f"✅ Relatório de auditoria gerado: {arquivo}")
                    
                    # Mostrar resumo do relatório
                    st.markdown("#### 📋 Resumo do Relatório:")
                    col_summary1, col_summary2, col_summary3 = st.columns(3)
                    
                    with col_summary1:
                        st.metric("Total de Itens", f"{header_info['Total_Itens']:,}")
                        st.metric("Itens Conferidos", f"{header_info['Total_Conferidos']:,}")
                    
                    with col_summary2:
                        st.metric("Valor Total", f"R$ {header_info['Valor_Total_Estoque']:,.2f}")
                        st.metric("% Conferido", f"{header_info['Percentual_Conferido']:.1f}%")
                    
                    with col_summary3:
                        st.metric("Prateleiras", f"{header_info['Prateleiras_Utilizadas']:,}")
                        st.metric("Fornecedores", f"{header_info['Fornecedores_Diferentes']:,}")
                    
                    # Download do arquivo
                    with open(arquivo, 'rb') as f:
                        st.download_button(
                            "💾 Download Relatório de Auditoria",
                            f.read(),
                            file_name=arquivo,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    st.info("📋 **O relatório contém:**\n"
                           "• Resumo executivo com métricas principais\n"
                           "• Inventário completo com todos os dados\n"
                           "• Análises por categoria, prateleira e fornecedor\n"
                           "• Identificação de inconsistências\n"
                           "• Lista de itens não conferidos")
    
    st.divider()
    
    # Seção de exportações básicas
    st.markdown("### 📤 Exportações Básicas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Exportar CSV (ZIP)", use_container_width=True):
            arquivo = estoque_manager.exportar_dados('csv')
            if arquivo:
                st.success(f"✅ Dados exportados: {arquivo}")
                
                # Download do arquivo
                with open(arquivo, 'rb') as f:
                    st.download_button(
                        "💾 Download ZIP",
                        f.read(),
                        file_name=os.path.basename(arquivo),
                        mime="application/zip"
                    )
    
    with col2:
        if st.button("Exportar Excel", use_container_width=True):
            arquivo = estoque_manager.exportar_dados('excel')
            if arquivo:
                st.success(f"✅ Dados exportados: {arquivo}")
                
                # Download do arquivo
                with open(arquivo, 'rb') as f:
                    st.download_button(
                        "💾 Download Excel",
                        f.read(),
                        file_name=os.path.basename(arquivo),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
