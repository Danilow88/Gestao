import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple
import os
import json

class EstoqueController:
    def __init__(self):
        self.csv_files = {
            'produtos': 'estoque_produtos.csv',
            'fornecedores': 'estoque_fornecedores.csv',
            'usuarios': 'estoque_usuarios.csv',
            'prateleiras': 'estoque_prateleiras.csv',
            'movimentacoes': 'estoque_movimentacoes.csv',
            'ativos': 'estoque_ativos.csv'
        }
        self.load_data()
    
    def load_data(self):
        """Carrega todos os dados dos arquivos CSV"""
        self.data = {}
        for key, filename in self.csv_files.items():
            try:
                if os.path.exists(filename):
                    self.data[key] = pd.read_csv(filename)
                else:
                    st.warning(f"Arquivo {filename} não encontrado. Criando arquivo vazio.")
                    self.data[key] = pd.DataFrame()
            except Exception as e:
                st.error(f"Erro ao carregar {filename}: {e}")
                self.data[key] = pd.DataFrame()
    
    def save_data(self, key: str):
        """Salva dados em um arquivo CSV específico"""
        try:
            if key in self.data:
                self.data[key].to_csv(self.csv_files[key], index=False)
                return True
        except Exception as e:
            st.error(f"Erro ao salvar {key}: {e}")
            return False
        return False
    
    def add_produto(self, sku: str, nome: str, categoria: str, descricao: str, 
                    unidade_medida: str, preco_unitario: float, estoque_minimo: int,
                    fornecedor_id: str):
        """Adiciona novo produto ao estoque"""
        if sku in self.data['produtos']['sku'].values:
            return False, "SKU já existe"
        
        novo_produto = {
            'sku': sku,
            'nome': nome,
            'categoria': categoria,
            'descricao': descricao,
            'unidade_medida': unidade_medida,
            'preco_unitario': preco_unitario,
            'estoque_minimo': estoque_minimo,
            'estoque_atual': 0,
            'fornecedor_id': fornecedor_id,
            'ativo': True,
            'data_cadastro': datetime.now().strftime('%Y-%m-%d')
        }
        
        self.data['produtos'] = pd.concat([self.data['produtos'], 
                                         pd.DataFrame([novo_produto])], ignore_index=True)
        self.save_data('produtos')
        return True, "Produto adicionado com sucesso"
    
    def add_fornecedor(self, fornecedor_id: str, nome: str, cnpj: str, telefone: str,
                       email: str, endereco: str, cidade: str, estado: str, cep: str):
        """Adiciona novo fornecedor"""
        if fornecedor_id in self.data['fornecedores']['fornecedor_id'].values:
            return False, "ID do fornecedor já existe"
        
        novo_fornecedor = {
            'fornecedor_id': fornecedor_id,
            'nome': nome,
            'cnpj': cnpj,
            'telefone': telefone,
            'email': email,
            'endereco': endereco,
            'cidade': cidade,
            'estado': estado,
            'cep': cep,
            'ativo': True,
            'data_cadastro': datetime.now().strftime('%Y-%m-%d')
        }
        
        self.data['fornecedores'] = pd.concat([self.data['fornecedores'], 
                                             pd.DataFrame([novo_fornecedor])], ignore_index=True)
        self.save_data('fornecedores')
        return True, "Fornecedor adicionado com sucesso"
    
    def add_usuario(self, usuario_id: str, nome: str, email: str, telefone: str,
                    departamento: str, cargo: str, nivel_acesso: str):
        """Adiciona novo usuário"""
        if usuario_id in self.data['usuarios']['usuario_id'].values:
            return False, "ID do usuário já existe"
        
        novo_usuario = {
            'usuario_id': usuario_id,
            'nome': nome,
            'email': email,
            'telefone': telefone,
            'departamento': departamento,
            'cargo': cargo,
            'nivel_acesso': nivel_acesso,
            'ativo': True,
            'data_cadastro': datetime.now().strftime('%Y-%m-%d'),
            'ultimo_acesso': datetime.now().strftime('%Y-%m-%d')
        }
        
        self.data['usuarios'] = pd.concat([self.data['usuarios'], 
                                         pd.DataFrame([novo_usuario])], ignore_index=True)
        self.save_data('usuarios')
        return True, "Usuário adicionado com sucesso"
    
    def add_prateleira(self, prateleira_id: str, nome: str, corredor: str, setor: str,
                       capacidade_maxima: int, responsavel_id: str):
        """Adiciona nova prateleira"""
        if prateleira_id in self.data['prateleiras']['prateleira_id'].values:
            return False, "ID da prateleira já existe"
        
        nova_prateleira = {
            'prateleira_id': prateleira_id,
            'nome': nome,
            'corredor': corredor,
            'setor': setor,
            'capacidade_maxima': capacidade_maxima,
            'capacidade_atual': 0,
            'responsavel_id': responsavel_id,
            'ativo': True,
            'data_cadastro': datetime.now().strftime('%Y-%m-%d')
        }
        
        self.data['prateleiras'] = pd.concat([self.data['prateleiras'], 
                                            pd.DataFrame([nova_prateleira])], ignore_index=True)
        self.save_data('prateleiras')
        return True, "Prateleira adicionada com sucesso"
    
    def registrar_movimentacao(self, sku: str, numero_serie: str, tipo_movimentacao: str,
                             quantidade: int, motivo: str, usuario_id: str,
                             prateleira_origem: str, prateleira_destino: str, observacoes: str):
        """Registra movimentação no estoque"""
        movimentacao_id = f"MOV{len(self.data['movimentacoes']) + 1:03d}"
        
        nova_movimentacao = {
            'movimentacao_id': movimentacao_id,
            'sku': sku,
            'numero_serie': numero_serie,
            'tipo_movimentacao': tipo_movimentacao,
            'quantidade': quantidade,
            'motivo': motivo,
            'usuario_id': usuario_id,
            'data_movimentacao': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'prateleira_origem': prateleira_origem,
            'prateleira_destino': prateleira_destino,
            'observacoes': observacoes
        }
        
        # Atualiza estoque do produto
        if sku in self.data['produtos']['sku'].values:
            idx = self.data['produtos']['sku'] == sku
            if tipo_movimentacao == 'Entrada':
                self.data['produtos'].loc[idx, 'estoque_atual'] += quantidade
            elif tipo_movimentacao == 'Saída':
                self.data['produtos'].loc[idx, 'estoque_atual'] -= quantidade
                if self.data['produtos'].loc[idx, 'estoque_atual'].iloc[0] < 0:
                    self.data['produtos'].loc[idx, 'estoque_atual'] = 0
        
        # Atualiza capacidade das prateleiras
        if prateleira_origem and prateleira_origem in self.data['prateleiras']['prateleira_id'].values:
            idx = self.data['prateleiras']['prateleira_id'] == prateleira_origem
            self.data['prateleiras'].loc[idx, 'capacidade_atual'] -= quantidade
        
        if prateleira_destino and prateleira_destino in self.data['prateleiras']['prateleira_id'].values:
            idx = self.data['prateleiras']['prateleira_id'] == prateleira_destino
            self.data['prateleiras'].loc[idx, 'capacidade_atual'] += quantidade
        
        self.data['movimentacoes'] = pd.concat([self.data['movimentacoes'], 
                                              pd.DataFrame([nova_movimentacao])], ignore_index=True)
        
        self.save_data('movimentacoes')
        self.save_data('produtos')
        self.save_data('prateleiras')
        
        return True, "Movimentação registrada com sucesso"
    
    def add_ativo(self, numero_serie: str, sku: str, status: str, localizacao: str,
                  usuario_responsavel: str, valor_aquisicao: float, fornecedor_id: str,
                  garantia_ate: str, observacoes: str):
        """Adiciona novo ativo por número de série"""
        if numero_serie in self.data['ativos']['numero_serie'].values:
            return False, "Número de série já existe"
        
        novo_ativo = {
            'numero_serie': numero_serie,
            'sku': sku,
            'status': status,
            'localizacao': localizacao,
            'usuario_responsavel': usuario_responsavel,
            'data_aquisicao': datetime.now().strftime('%Y-%m-%d'),
            'valor_aquisicao': valor_aquisicao,
            'fornecedor_id': fornecedor_id,
            'garantia_ate': garantia_ate,
            'observacoes': observacoes,
            'ativo': True
        }
        
        self.data['ativos'] = pd.concat([self.data['ativos'], 
                                       pd.DataFrame([novo_ativo])], ignore_index=True)
        self.save_data('ativos')
        return True, "Ativo adicionado com sucesso"
    
    def get_estoque_baixo(self) -> pd.DataFrame:
        """Retorna produtos com estoque abaixo do mínimo"""
        if 'produtos' not in self.data or self.data['produtos'].empty:
            return pd.DataFrame()
        
        return self.data['produtos'][
            self.data['produtos']['estoque_atual'] <= self.data['produtos']['estoque_minimo']
        ]
    
    def get_movimentacoes_periodo(self, data_inicio: str, data_fim: str) -> pd.DataFrame:
        """Retorna movimentações em um período específico"""
        if 'movimentacoes' not in self.data or self.data['movimentacoes'].empty:
            return pd.DataFrame()
        
        movimentacoes = self.data['movimentacoes'].copy()
        movimentacoes['data_movimentacao'] = pd.to_datetime(movimentacoes['data_movimentacao'])
        
        return movimentacoes[
            (movimentacoes['data_movimentacao'] >= data_inicio) &
            (movimentacoes['data_movimentacao'] <= data_fim)
        ]
    
    def get_produtos_por_fornecedor(self) -> pd.DataFrame:
        """Retorna produtos agrupados por fornecedor"""
        if 'produtos' not in self.data or 'fornecedores' not in self.data:
            return pd.DataFrame()
        
        return pd.merge(self.data['produtos'], self.data['fornecedores'], 
                       on='fornecedor_id', how='left')
    
    def get_estoque_por_prateleira(self) -> pd.DataFrame:
        """Retorna estoque organizado por prateleira"""
        if 'prateleiras' not in self.data:
            return pd.DataFrame()
        
        return self.data['prateleiras'].copy()
    
    def get_valor_total_estoque(self) -> float:
        """Calcula o valor total do estoque"""
        if 'produtos' not in self.data or self.data['produtos'].empty:
            return 0.0
        
        return (self.data['produtos']['estoque_atual'] * 
                self.data['produtos']['preco_unitario']).sum()
    
    def get_estatisticas_gerais(self) -> Dict:
        """Retorna estatísticas gerais do estoque"""
        if 'produtos' not in self.data or self.data['produtos'].empty:
            return {}
        
        total_produtos = len(self.data['produtos'])
        total_ativos = len(self.data['ativos']) if 'ativos' in self.data else 0
        total_movimentacoes = len(self.data['movimentacoes']) if 'movimentacoes' in self.data else 0
        valor_total = self.get_valor_total_estoque()
        estoque_baixo = len(self.get_estoque_baixo())
        
        return {
            'total_produtos': total_produtos,
            'total_ativos': total_ativos,
            'total_movimentacoes': total_movimentacoes,
            'valor_total_estoque': valor_total,
            'produtos_estoque_baixo': estoque_baixo
        }
