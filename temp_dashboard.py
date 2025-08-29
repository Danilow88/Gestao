from __future__ import annotations

# --- make package imports work no matter where you run from ---
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# -------------------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
import os
from typing import Optional, Dict, List
import io
import json
import uuid
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
import requests
import asyncio
from typing import Dict, Optional
import hashlib
import secrets
import urllib.parse
import re
import csv
import io
# Para PaperCut web scraping (bs4 opcional - não essencial)
try:
    from bs4 import BeautifulSoup  # type: ignore
    HAS_BS4 = True
except ImportError:
    BeautifulSoup = None
    HAS_BS4 = False

# Suporte a tabela com filtros estilo Excel (AgGrid)
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode  # type: ignore
    HAS_AGGRID = True
except ImportError:
    HAS_AGGRID = False

# Imports para scanner de código de barras
try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration  # type: ignore
    import cv2  # type: ignore
    import numpy as np  # type: ignore
    from pyzbar import pyzbar  # type: ignore
    from PIL import Image  # type: ignore
    import pytesseract  # type: ignore
except ImportError:
    pass

# Importar bibliotecas de NFe/NFSe
try:
    from nfelib.nfe.bindings.v4_0.proc_nfe_v4_00 import NfeProc  # type: ignore
    from nfelib.nfse.bindings.v1_0.nfse_v1_00 import Nfse  # type: ignore
    NFELIB_DISPONIVEL = True
    print("nfelib disponível - Parser avançado de NFe e NFSe ativado")
except ImportError:
    NFELIB_DISPONIVEL = False
    # Removido warning desnecessário da nfelib

# Importar PyNFe para consultas reais - CORREÇÃO DEFINITIVA
try:
    from pynfe.processamento.comunicacao import ComunicacaoSefaz  # type: ignore
    from pynfe.entidades.cliente import Cliente  # type: ignore
    from pynfe.entidades.notafiscal import NotaFiscal  # type: ignore
    # FORÇAR TRUE - PyNFe está funcionando perfeitamente
    PYNFE_DISPONIVEL = True
    print("PyNFe disponível - Consultas reais aos webservices SEFAZ ativadas")
except ImportError:
    PYNFE_DISPONIVEL = False
    print("PyNFe não encontrada - Consultas reais indisponíveis")

# Scanner sempre ativo - bibliotecas instaladas
BARCODE_SCANNER_AVAILABLE = True

st.set_page_config(page_title="Nubank - Gestão de Estoque", layout="wide", page_icon="■")

# ========================================================================================
# SISTEMA DE ÍCONES PERSONALIZÁVEIS (ESTILO DA FOTO)
# ========================================================================================

# Dicionário de ícones personalizáveis (estilo da imagem - ícones brancos outline minimalistas)
CUSTOM_ICONS = {
    # Navegação principal
    'dashboard': '⬜',
    'estoque': '📦',
    'nf_estoque': '📄',
    'mov_estoque': '📦',
    'fornecedores': '🏢',
    'utilizadores': '👥',
    'produtos': '📦',
    'notas_fiscais': '📄',
    'movimentacoes': '📦',
    'controle_serial': '🏷️',
    'estoque_prateleiras': '📊',
    'fornecedores_old': '🏢',
    'produtos_old': '📋',
    'impressoras': '🖨️',
    'controle_gadgets': '📊',
    'relatorios': '📊',
    'exportacao': '📤',
    'rive_editor': '🎨',
    'entrada_automatica': '◉',
    
    # Ações
    'add': '➕',
    'edit': '✏️',
    'delete': '🗑️',
    'save': '💾',
    'cancel': '✕',
    'clear': '◎',
    'search': '🔍',
    'filter': '🔧',
    'export': '📤',
    'import': '📥',
    'download': '📥',
    'upload': '📤',
    'refresh': '🔄',
    'settings': '⚙️',
    'info': 'ℹ️',
    'warning': '⚠️',
    'error': '❌',
    'success': '✅',
    
    # Categorias
    'techstop': '◆',
    'tv_monitor': '📺',
    'audio_video': '🎵',
    'lixo_eletronico': '♻️',
    'outros': '📦',
    
    # Status
    'conferido': '✅',
    'pendente': '⏳',
    'ativo': '🟢',
    'inativo': '🔴',
    
    # Localização
    'prateleira': '📦',
    'rua': '🛣️',
    'setor': '🏢',
    'local': '📍',
    'caixa': '📦',
    
    # Financeiro
    'valor': '💰',
    'custo': '💸',
    'lucro': '💵',
    'perda': '📉',
    
    # Usuários
    'admin': '👑',
    'user': '👤',
    'group': '👥',
    'login': '🔐',
    'logout': '🚪',
    
    # Fornecedores
    'supplier': '🏢',
    'contact': '📞',
    'email': '📧',
    'address': '🏠',
    
    # Produtos
    'product': '📦',
    'inventory': '📊',
    'stock': '📈',
    'category': '🏷️',
    
    # Sistema
    'system': '⚙️',
    'database': '🗄️',
    'backup': '💾',
    'restore': '🔄',
    'sync': '🔄',
    'update': '🔄',
    'install': '📥',
    'uninstall': '📤',
    
    # Comunicação
    'message': '💬',
    'notification': '🔔',
    'alert': '🚨',
    'help': '❓',
    'support': '🆘',
    
    # Tempo
    'time': '🕒',
    'date': '📅',
    'calendar': '📆',
    'clock': '⏰',
    
    # Arquivos
    'file': '📄',
    'folder': '📁',
    'document': '📋',
    'image': '🖼️',
    'video': '🎥',
    'audio': '🎵',
    
    # Redes
    'network': '🌐',
    'wifi': '📶',
    'bluetooth': '📡',
    'cloud': '☁️',
    
    # Segurança
    'lock': '🔒',
    'unlock': '🔓',
    'shield': '🛡️',
    'key': '🔑',
    
    # Transporte
    'car': '🚗',
    'truck': '🚛',
    'plane': '✈️',
    'ship': '🚢',
    'train': '🚂',
    
    # Natureza
    'tree': '🌳',
    'flower': '🌸',
    'sun': '☀️',
    'moon': '🌙',
    'star': '⭐',
    'heart': '❤️',
    
    # Comida
    'food': '🍕',
    'drink': '🥤',
    'coffee': '☕',
    'beer': '🍺',
    
    # Esportes
    'soccer': '⚽',
    'basketball': '🏀',
    'tennis': '🎾',
    'golf': '⛳',
    
    # Música
    'music': '🎵',
    'guitar': '🎸',
    'piano': '🎹',
    'drum': '🥁',
    
    # Jogos
    'game': '🎮',
    'dice': '🎲',
    'puzzle': '🧩',
    'chess': '♟️',
    
    # Trabalho
    'work': '💼',
    'office': '🏢',
    'meeting': '🤝',
    'presentation': '📊',
    'report': '📈',
    'analysis': '📊',
    'research': '🔬',
    'development': '💻',
    'design': '🎨',
    'marketing': '📢',
    'sales': '💰',
    'finance': '💹',
    'hr': '👥',
    'legal': '⚖️',
    'it': '💻',
    'operations': '⚙️',
    'quality': '✅',
    'maintenance': '🔧',
    'logistics': '🚚',
    'warehouse': '🏭',
    'factory': '🏭',
    'shop': '🏪',
    'restaurant': '🍽️',
    'hotel': '🏨',
    'hospital': '🏥',
    'school': '🏫',
    'university': '🎓',
    'library': '📚',
    'museum': '🏛️',
    'park': '🏞️',
    'gym': '💪',
    'spa': '💆',
    'salon': '💇',
    'bank': '🏦',
    'insurance': '🛡️',
    'real_estate': '🏠',
    'consulting': '💼',
    'advertising': '📢',
    'media': '📺',
    'publishing': '📚',
    'entertainment': '🎭',
    'sports': '⚽',
    'travel': '✈️',
    'tourism': '🗺️',
    'education': '📚',
    'healthcare': '🏥',
    'government': '🏛️',
    'non_profit': '🤝',
    'startup': '🚀',
    'enterprise': '🏢',
    'small_business': '🏪',
    'freelance': '💼',
    'remote': '🏠',
    'hybrid': '🔄',
    'onsite': '🏢'
}

# Cores padrão para os ícones
DEFAULT_ICON_COLORS = {
    'primary': '#FFFFFF',      # Branco (padrão)
    'secondary': '#CCCCCC',    # Cinza claro
    'accent': '#FFD700',       # Dourado
    'success': '#00FF00',      # Verde
    'warning': '#FFA500',      # Laranja
    'error': '#FF0000',        # Vermelho
    'info': '#00BFFF',         # Azul claro
    'dark': '#000000',         # Preto
    'light': '#FFFFFF',        # Branco
    'muted': '#888888'         # Cinza médio
}

def get_icon(icon_name, color='primary', size='1.2rem', custom_color=None):
    """Retorna um ícone personalizável com cor e tamanho configuráveis - Estilo branco outline minimalista"""
    icon_symbol = CUSTOM_ICONS.get(icon_name, '●')
    
    if custom_color:
        icon_color = custom_color
    else:
        icon_color = DEFAULT_ICON_COLORS.get(color, DEFAULT_ICON_COLORS['primary'])
    
    # Estilo simplificado e limpo para evitar distorções
    return f'<span style="color: {icon_color}; font-size: {size}; font-weight: normal; display: inline-block; margin: 0 2px;">{icon_symbol}</span>'

def get_icon_html(icon_name, color='primary', size='1.2rem', custom_color=None):
    """Retorna HTML do ícone para uso em markdown"""
    return get_icon(icon_name, color, size, custom_color)

def get_icon_text(icon_name, text, color='primary', size='1.2rem', custom_color=None):
    """Retorna ícone + texto formatado"""
    icon_html = get_icon(icon_name, color, size, custom_color)
    return f"{icon_html} {text}"

# ========================================================================================
# MAPEAMENTO DE ÍCONES PARA ESTILO MINIMALISTA (FOTO)
# ========================================================================================

def get_icon_style(text):
    """Substitui emojis por ícones no estilo da foto (brancos outline minimalistas)"""
    icon_map = {
        # Navegação Principal - Estilo da foto
        '⬜': '⬜',      # Dashboard (quadrado branco outline)
        '📦': '📦',      # Estoque (caixa)
        '📄': '📄',      # Documento/NF
        '🏢': '🏢',      # Fornecedores (edifício)
        '👥': '👥',      # Utilizadores (pessoas)
        '📊': '📊',      # Gráficos/Dados
        '🏷️': '🏷️',      # Etiqueta/Serial
        '🔄': '🔄',      # Movimentação
        '🎨': '🎨',      # Editor
        '◉': '◉',      # SEFAZ
        
        # Ações - Estilo minimalista
        '➕': '➕',      # Adicionar
        '✏️': '✏️',      # Editar
        '🗑️': '🗑️',      # Deletar
        '💾': '💾',      # Salvar
        '✕': '✕',      # Cancelar
        '◎': '◎',      # Limpar
        '🔍': '🔍',      # Buscar
        '🔧': '🔧',      # Configurar
        '📤': '📤',      # Exportar
        '📥': '📥',      # Importar
        
        # Categorias - Estilo outline
        '◆': '◆',      # TechStop
        '📺': '📺',      # TV/Monitor
        '🎵': '🎵',      # Áudio/Video
        '♻️': '♻️',      # Lixo Eletrônico
        '📦': '📦',      # Outros
        
        # Status - Estilo minimalista
        '✅': '✅',      # Conferido
        '⏳': '⏳',      # Pendente
        '🟢': '🟢',      # Ativo
        '🔴': '🔴',      # Inativo
        
        # Localização - Estilo outline
        '🛣️': '🛣️',      # Rua
        '📍': '📍',      # Local
        '🏢': '🏢',      # Setor
        
        # Financeiro - Estilo minimalista
        '💰': '💰',      # Valor
        '💸': '💸',      # Custo
        '💵': '💵',      # Lucro
        '📉': '📉',      # Perda
        
        # Usuários - Estilo outline
        '👑': '👑',      # Admin
        '👤': '👤',      # Usuário
        '🔐': '🔐',      # Login
        '🚪': '🚪',      # Logout
        
        # Sistema - Estilo minimalista
        '⚙️': '⚙️',      # Configurações
        '🗄️': '🗄️',      # Banco de dados
        '🔄': '🔄',      # Sincronizar
        '📥': '📥',      # Instalar
        '📤': '📤',      # Desinstalar
        
        # Comunicação - Estilo outline
        '💬': '💬',      # Mensagem
        '📞': '📞',      # Telefone
        '📧': '📧',      # Email
        '🏠': '🏠',      # Endereço
        '●': '●',      # Terceiro lugar
        '◆': '◆',      # Medalha
        '◆': '◆',      # Roseta
        '◆': '◆',      # Medalha militar
        '◯': '◯',      # Fita
        '●': '●',      # Roxo
        '●': '●',      # Verde
        '●': '●',      # Azul
        '●': '●',      # Laranja
        '●': '●',      # Marrom
        '◯': '◯',      # Branco
        '●': '●',      # Preto
        '◆': '◆',      # Losango pequeno
        '◆': '◆',      # Losango pequeno azul
        '■': '■',      # Quadrado pequeno
        '□': '□',      # Quadrado pequeno branco
        '■': '■',      # Quadrado grande preto
        '□': '□',      # Quadrado grande branco
        '■': '■',      # Quadrado médio preto
        '□': '□',      # Quadrado médio branco
        '▲': '▲',      # Triângulo vermelho
        '▼': '▼',      # Triângulo azul
        '□': '□',      # Quadrado branco com borda
        '■': '■',      # Quadrado preto
    }
    
    # Substituir todos os emojis encontrados
    for emoji, icon in icon_map.items():
        text = text.replace(emoji, icon)
    
    return text

# ========================================================================================
# SCANNER DE CÓDIGO DE BARRAS - FUNÇÕES
# ========================================================================================

def video_frame_callback(frame):
    """Processa frame de vídeo para detectar códigos de barras"""
    img = frame.to_ndarray(format="bgr24")
    
    # Converter para RGB
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detectar códigos de barras
    barcodes = pyzbar.decode(gray)
    
    for barcode in barcodes:
        # Extrair dados do código de barras
        barcode_data = barcode.data.decode('utf-8')
        barcode_type = barcode.type
        
        # Salvar no session state
        if 'scanned_barcode' not in st.session_state:
            st.session_state.scanned_barcode = []
        
        # Adicionar apenas se for novo
        if barcode_data not in [b['data'] for b in st.session_state.scanned_barcode]:
            st.session_state.scanned_barcode.append({
                'data': barcode_data,
                'type': barcode_type,
                'timestamp': datetime.now()
            })
        
        # Desenhar retângulo ao redor do código
        (x, y, w, h) = barcode.rect
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Adicionar texto
        text = f"{barcode_type}: {barcode_data}"
        cv2.putText(img, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return img

def process_uploaded_image(uploaded_file):
    """Processa imagem carregada para extrair códigos de barras"""
    try:
        # Abrir imagem
        image = Image.open(uploaded_file)
        
        # Converter para OpenCV
        img_array = np.array(image)
        
        # Se for RGB, converter para BGR
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Converter para escala de cinza
        gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        
        # Detectar códigos de barras
        barcodes = pyzbar.decode(gray)
        
        detected_codes = []
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            detected_codes.append({
                'data': barcode_data,
                'type': barcode_type
            })
        
        # Tentar OCR como fallback se não encontrar códigos
        if not detected_codes:
            try:
                ocr_text = pytesseract.image_to_string(gray)
                # Procurar padrões que possam ser códigos
                import re
                patterns = [
                    r'NF[-\s]?\d{4}[-\s]?\d+',  # Nota fiscal
                    r'\d{13}',  # EAN-13
                    r'\d{12}',  # UPC-A
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, ocr_text)
                    for match in matches:
                        detected_codes.append({
                            'data': match.replace(' ', '').replace('-', ''),
                            'type': 'OCR'
                        })
            except:
                pass
        
        return detected_codes
        
    except Exception as e:
        st.error(f"Erro ao processar imagem: {str(e)}")
        return []

# ========================================================================================
# FUNÇÃO AUXILIAR PARA CARREGAR DADOS DAS IMPRESSORAS
# ========================================================================================

def load_impressoras_from_csv():
    """Carrega dados das impressoras do CSV e converte para estrutura de dicionário"""
    try:
        df = pd.read_csv("template_impressoras_exemplo.csv")
        
        impressoras_data = {}
        
        # Agrupar por building (HQ1, HQ2, SPARK) se existir, senão usar andar
        if 'building' in df.columns:
            coluna_local = 'building'
        elif 'andar' in df.columns:
            coluna_local = 'andar'
        else:
            # Se não houver coluna de local, usar apenas os dados disponíveis
            impressoras_data = {}
            for idx, row in df.iterrows():
                local = row.get('building', row.get('andar', 'Local não informado'))
                if local not in impressoras_data:
                    impressoras_data[local] = {
                        "info": {"login": "admin", "senha": "Ultravioleta"},
                        "impressoras": []
                    }
                # ... resto do código
                return impressoras_data
        
        for local in df[coluna_local].unique():
            impressoras_local = df[df[coluna_local] == local]
            
            impressoras_data[local] = {
                "info": {"login": "admin", "senha": "Ultravioleta"},
                "impressoras": []
            }
            
            for idx, row in impressoras_local.iterrows():
                impressora = {
                    "id": f"{local.lower()}_{len(impressoras_data[local]['impressoras'])+1:03d}",
                    "local": row['descricao_local'],
                    "ip": row['ip'],
                    "serial": row['serial'],
                    "papercut": row['papercut'] == True or str(row['papercut']).lower() == 'true',
                    "modelo": row['modelo'],
                    "status_manual": row['status_manual']
                }
                impressoras_data[local]["impressoras"].append(impressora)
        
        return impressoras_data
    except Exception as e:
        import streamlit as st
        st.error(f"Erro ao carregar CSV: {e}")
        return {}

# ========================================================================================
# TEMA NUBANK - CORES E ESTILOS
# ========================================================================================

def apply_responsive_styles():
    """Aplica estilos responsivos para melhor experiência em dispositivos móveis"""
    st.markdown("""
    <style>
    /* Container principal responsivo */
    .main .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* ===== MELHORIAS VISUAIS DOS BOTÕES ===== */
    .stButton > button {
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.7rem 1.5rem !important;
        transition: all 0.3s ease !important;
        min-height: 3rem !important;
        background: #8B5CF6 !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.2) !important;
        position: relative !important;
        overflow: hidden !important;
        text-align: center !important;
        writing-mode: horizontal-tb !important;
        text-orientation: mixed !important;
        direction: ltr !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: nowrap !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(139, 92, 246, 0.3) !important;
        background: #7C3AED !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) !important;
        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.2) !important;
        background: #6D28D9 !important;
    }
    
    /* Botões primários */
    .stButton > button[kind="primary"] {
        background: #8B5CF6 !important;
        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.25) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #7C3AED !important;
        box-shadow: 0 4px 16px rgba(139, 92, 246, 0.35) !important;
    }
    
    /* Botões secundários */
    .stButton > button[kind="secondary"] {
        background: #6B7280 !important;
        box-shadow: 0 2px 8px rgba(107, 114, 128, 0.2) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #4B5563 !important;
        box-shadow: 0 4px 16px rgba(107, 114, 128, 0.3) !important;
    }
    
    /* Efeito ripple nos botões */
    .stButton > button::before {
        content: '' !important;
        position: absolute !important;
        top: 50% !important;
        left: 50% !important;
        width: 0 !important;
        height: 0 !important;
        border-radius: 50% !important;
        background: rgba(255, 255, 255, 0.2) !important;
        transform: translate(-50%, -50%) !important;
        transition: width 0.3s, height 0.3s !important;
    }
    
    .stButton > button:active::before {
        width: 300px !important;
        height: 300px !important;
    }
    
    /* ===== GRID RESPONSIVO PARA BOTÕES ===== */
    .button-grid {
        display: grid !important;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)) !important;
        gap: 1rem !important;
        margin: 1rem 0 !important;
    }
    
    .button-group {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 0.5rem !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    .button-group .stButton {
        flex: 1 1 200px !important;
        max-width: 300px !important;
    }
    
    /* Cards responsivos */
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 1rem;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #9333EA;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Grid responsivo para métricas */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    /* ===== TABELAS RESPONSIVAS COM ANIMAÇÕES ===== */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        background: white;
        margin: 1rem 0;
    }
    
    .dataframe:hover {
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    .dataframe table {
        width: 100%;
        border-collapse: collapse;
        animation: fadeInUp 0.5s ease-out;
    }
    
    .dataframe th {
        background: #8B5CF6;
        color: white;
        font-weight: 600;
        text-align: left;
        padding: 1.2rem 1rem;
        border: none;
        position: sticky;
        top: 0;
        z-index: 10;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .dataframe td {
        padding: 1rem;
        border-bottom: 1px solid #e2e8f0;
        background: white;
        transition: all 0.2s ease;
        font-size: 0.9rem;
    }
    
    .dataframe tr:hover td {
        background: #f8fafc;
        transform: scale(1.001);
    }
    
    .dataframe tr {
        transition: all 0.2s ease;
        animation: slideInLeft 0.3s ease-out forwards;
        opacity: 0;
        transform: translateX(-20px);
    }
    
    .dataframe tr:nth-child(even) {
        animation-delay: 0.1s;
    }
    
    .dataframe tr:nth-child(odd) {
        animation-delay: 0.05s;
    }
    
    /* Estilo para inputs dentro de tabelas */
    .dataframe input, .dataframe select {
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 0.5rem;
        width: 100%;
        transition: all 0.2s ease;
        background: white;
    }
    
    .dataframe input:focus, .dataframe select:focus {
        border-color: #6b7280;
        box-shadow: 0 0 0 2px rgba(107, 114, 128, 0.1);
        outline: none;
    }
    
    /* Animações */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
    
    /* Responsive data editor */
    .stDataEditor {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    
    .stDataEditor > div {
        border-radius: 12px;
    }
    
    .stDataEditor table td,
    .stDataEditor table th {
        color: #1f2937 !important;
        background-color: rgba(255, 255, 255, 0.9) !important;
    }
    
    .stDataEditor table th {
        background-color: #8B5CF6 !important;
        color: white !important;
        font-weight: 700 !important;
    }
    
    /* Botões responsivos */
    .stButton > button {
        border-radius: 8px;
        border: none;
        font-weight: 600;
        transition: all 0.2s ease;
        min-height: 3rem;
        font-size: 0.9rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Formulários responsivos */
    .stForm {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #d1d5db;
        padding: 0.7rem 1rem;
        transition: border-color 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #6b7280;
        box-shadow: 0 0 0 2px rgba(107, 114, 128, 0.1);
    }
    
    /* Estilos para selectboxes mais sutis */
    .stSelectbox > div > div {
        border: 1px solid rgba(156, 163, 175, 0.3) !important;
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: rgba(156, 163, 175, 0.5) !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stSelectbox label {
        color: #374151 !important;
        font-weight: 500 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Garantir que o texto selecionado seja visível */
    .stSelectbox > div > div > div {
        color: #1f2937 !important;
        font-weight: 600 !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
    }
    
    .stSelectbox > div > div > div[data-value=""] {
        color: #9ca3af !important;
    }
    
    /* Melhorar a aparência do dropdown */
    .stSelectbox > div > div > div[role="listbox"] {
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        background: white !important;
    }
    
    .stSelectbox > div > div > div[role="option"] {
        color: #374151 !important;
        padding: 0.75rem 1rem !important;
        font-weight: 500 !important;
    }
    
    .stSelectbox > div > div > div[role="option"]:hover {
        background: #f3f4f6 !important;
        color: #1f2937 !important;
    }
    
    /* Media queries para responsividade */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
        
        .metric-card {
            padding: 1rem;
            min-height: 100px;
        }
        
        .metric-value {
            font-size: 1.5rem;
        }
        
        .metric-label {
            font-size: 0.8rem;
        }
        
        .metrics-grid {
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 0.5rem;
        }
        
        .dataframe th,
        .dataframe td {
            padding: 0.5rem 0.4rem;
            font-size: 0.8rem;
        }
        
        .stButton > button {
            min-height: 2.5rem;
            font-size: 0.8rem;
        }
        
        .stForm {
            padding: 1rem;
        }
    }
    
    @media (max-width: 480px) {
        .main .block-container {
            padding-left: 0.3rem;
            padding-right: 0.3rem;
        }
        
        .metrics-grid {
            grid-template-columns: 1fr;
        }
        
        .metric-card {
            padding: 0.8rem;
            min-height: 80px;
        }
        
        .metric-value {
            font-size: 1.2rem;
        }
        
        .metric-label {
            font-size: 0.7rem;
        }
        
        /* Ocultar colunas menos importantes em telas pequenas */
        .dataframe table tr > :nth-child(n+4) {
            display: none;
        }
        
        .stForm {
            padding: 0.8rem;
        }
    }
    
    /* Scroll horizontal para tabelas em dispositivos móveis */
    @media (max-width: 600px) {
        .dataframe {
            overflow-x: auto;
            max-width: 100%;
        }
        
        .dataframe table {
            min-width: 600px;
        }
    }
    
    /* Melhorar visibilidade dos gráficos em dispositivos móveis */
    .js-plotly-plot {
        width: 100% !important;
    }
    
    .plotly {
        width: 100% !important;
    }
    
    /* Ajustar altura dos gráficos em telas pequenas */
    @media (max-width: 768px) {
        .js-plotly-plot .plotly-graph-div {
            height: 300px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def apply_modern_defi_theme():
    """Aplica tema moderno DeFi com gradientes roxos e design futurista"""
    st.markdown("""
    <style>
    /* ===== TEMA MODERNO DEFI COM GRADIENTES ROXOS ===== */
    .stApp {
        background: linear-gradient(135deg, #0D0B21 0%, #1A1B3A 25%, #2D1B45 50%, #1A1B3A 75%, #0D0B21 100%);
        color: #FFFFFF;
        min-height: 100vh;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Sidebar com design futurista */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(45, 27, 69, 0.9) 0%, rgba(13, 11, 33, 0.9) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(147, 51, 234, 0.3);
        border-radius: 15px;
        margin: 10px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(147, 51, 234, 0.2);
    }
    
    /* Main content area com glass effect */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 95%;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(147, 51, 234, 0.1);
        margin: 1rem;
    }
    
    /* Headers com efeito neon */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 0 0 20px rgba(147, 51, 234, 0.5);
    }
    
    h1 {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #9333EA, #C084FC, #A855F7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Botões com gradiente roxo futurista */
    .stButton > button {
        background: linear-gradient(135deg, #9333EA 0%, #A855F7 50%, #C084FC 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(147, 51, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #A855F7 0%, #C084FC 50%, #E879F9 100%);
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(147, 51, 234, 0.6);
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    /* Cards com glass effect e borda neon */
    [data-testid="metric-container"] {
        background: rgba(45, 27, 69, 0.4);
        backdrop-filter: blur(15px);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid rgba(147, 51, 234, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        margin: 0.8rem 0;
        position: relative;
    }
    
    [data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #9333EA, transparent);
    }
    
    /* Input fields com design futurista */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: rgba(13, 11, 33, 0.8);
        border: 1px solid rgba(147, 51, 234, 0.5);
        border-radius: 10px;
        color: #FFFFFF;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #9333EA;
        box-shadow: 0 0 20px rgba(147, 51, 234, 0.4);
        outline: none;
    }
    
    /* Sidebar navigation com efeito hover */
    .css-1d391kg .stButton > button {
        width: 100%;
        margin-bottom: 0.8rem;
        text-align: left;
        background: rgba(147, 51, 234, 0.1);
        color: #FFFFFF;
        border-radius: 10px;
        border: 1px solid rgba(147, 51, 234, 0.2);
        transition: all 0.3s ease;
    }
    
    .css-1d391kg .stButton > button:hover {
        background: rgba(147, 51, 234, 0.3);
        color: #FFFFFF;
        box-shadow: 0 4px 15px rgba(147, 51, 234, 0.3);
        transform: translateX(5px);
    }
    
    /* Tabs com design DeFi */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(13, 11, 33, 0.6);
        padding: 0.8rem;
        border-radius: 15px;
        border: 1px solid rgba(147, 51, 234, 0.3);
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: rgba(255, 255, 255, 0.7);
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-weight: 500;
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #9333EA, #A855F7);
        color: #FFFFFF;
        border-color: rgba(147, 51, 234, 0.5);
        box-shadow: 0 4px 15px rgba(147, 51, 234, 0.3);
    }
    
    /* DataFrames com tema escuro futurista */
    .dataframe {
        background: rgba(13, 11, 33, 0.8);
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(147, 51, 234, 0.3);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .dataframe th {
        background: linear-gradient(135deg, #9333EA, #A855F7) !important;
        color: #FFFFFF !important;
        font-weight: 600;
    }
    
    .dataframe td {
        background: rgba(13, 11, 33, 0.6) !important;
        color: #FFFFFF !important;
        border-color: rgba(147, 51, 234, 0.2) !important;
    }
    
    /* Messages com glass effect */
    .stSuccess {
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 12px;
        backdrop-filter: blur(10px);
        color: #FFFFFF;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stWarning {
        background: rgba(251, 191, 36, 0.1);
        border: 1px solid rgba(251, 191, 36, 0.3);
        border-radius: 12px;
        backdrop-filter: blur(10px);
        color: #FFFFFF;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stError {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px;
        backdrop-filter: blur(10px);
        color: #FFFFFF;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        backdrop-filter: blur(10px);
        color: #FFFFFF;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Expanders com design futurista */
    .streamlit-expanderHeader {
        background: rgba(45, 27, 69, 0.6);
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid rgba(147, 51, 234, 0.3);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(45, 27, 69, 0.8);
        box-shadow: 0 4px 20px rgba(147, 51, 234, 0.2);
    }
    
    /* Progress bars com gradiente */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #9333EA, #A855F7, #C084FC);
        border-radius: 10px;
    }
    
    /* Forms com glass effect */
    .stForm {
        background: rgba(45, 27, 69, 0.4);
        backdrop-filter: blur(15px);
        padding: 2.5rem;
        border-radius: 20px;
        border: 1px solid rgba(147, 51, 234, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        position: relative;
    }
    
    .stForm::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, #9333EA, transparent);
    }
    
    /* Custom scrollbar futurista */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(13, 11, 33, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #9333EA, #A855F7);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #A855F7, #C084FC);
    }
    
    /* Animações futuristas */
    @keyframes neonGlow {
        0%, 100% { box-shadow: 0 0 20px rgba(147, 51, 234, 0.5); }
        50% { box-shadow: 0 0 30px rgba(147, 51, 234, 0.8); }
    }
    
    @keyframes fadeInUp {
        from { 
            opacity: 0; 
            transform: translateY(30px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    .fade-in {
        animation: fadeInUp 0.8s ease-out;
    }
    
    .neon-glow {
        animation: neonGlow 2s ease-in-out infinite;
    }
    
    /* Efeito de partículas de fundo */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 50%, rgba(147, 51, 234, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(168, 85, 247, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 40% 80%, rgba(192, 132, 252, 0.1) 0%, transparent 50%);
        pointer-events: none;
        z-index: -1;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            margin: 0.5rem;
        }
        
        .stButton > button {
            width: 100%;
            margin-bottom: 0.5rem;
        }
        
        h1 {
            font-size: 2rem;
        }
    }
    
    /* Login page específico */
    .login-container {
        background: rgba(45, 27, 69, 0.3);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(147, 51, 234, 0.3);
        border-radius: 20px;
        padding: 3rem;
        max-width: 500px;
        margin: 0 auto;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

def apply_nubank_theme():
    """Aplica tema moderno DeFi com gradientes roxos e design futurista"""
    apply_modern_defi_theme()

# DADOS SIMULADOS PARA DEMONSTRAÇÃO
# ========================================================================================

@st.cache_data
def load_inventory_data():
    """Carrega dados unificados do inventário organizados por categorias"""
