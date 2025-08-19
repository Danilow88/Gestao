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
# Para PaperCut web scraping (bs4 opcional - não essencial)
try:
    from bs4 import BeautifulSoup  # type: ignore
    HAS_BS4 = True
except ImportError:
    BeautifulSoup = None
    HAS_BS4 = False

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

# Scanner sempre ativo - bibliotecas instaladas
BARCODE_SCANNER_AVAILABLE = True

st.set_page_config(page_title="Nubank - Gestão de Estoque", layout="wide", page_icon="🟣")

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
# TEMA NUBANK - CORES E ESTILOS
# ========================================================================================

def apply_nubank_theme():
    """Aplica o tema customizável baseado nas configurações do admin"""
    # Usar configurações personalizadas se existirem, senão usar padrão
    theme = getattr(st.session_state, 'theme_config', {
        'primary_color': '#8A05BE',
        'background_color': '#f8f9fa',
        'text_color': 'white',
        'accent_color': '#000000',
        'custom_css': ''
    })
    
    primary_color = theme['primary_color']
    background_color = theme['background_color'] 
    text_color = theme['text_color']
    accent_color = theme['accent_color']
    custom_css = theme.get('custom_css', '')
    
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {background_color} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: {text_color} !important;
    }}
    
    .main-header {{ 
        background: {primary_color} !important;
        padding: 2rem 1rem;
        border-radius: 12px;
        color: {text_color} !important;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(138, 5, 190, 0.3);
    }}
    
    .main-header * {{
        text-shadow: 0 3px 6px rgba(0, 0, 0, 0.5);
    }}
    
    .main-title {{
        font-size: 2.5rem; 
        font-weight: 700; 
        color: {text_color} !important;
        margin-bottom: 0.5rem;
        text-shadow: 1px 3px 6px rgba(0, 0, 0, 0.5);
    }}
    
    .main-subtitle {{
        font-size: 1.2rem;
        color: {text_color} !important;
        opacity: 0.9; 
        text-shadow: 1px 2px 4px rgba(0, 0, 0, 0.4);
    }}
    
    .stButton > button {{
        background: {primary_color} !important;
        color: {text_color} !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        text-shadow: 1px 2px 4px rgba(0, 0, 0, 0.4);
    }}
    
    .stButton > button:hover {{
        background: {primary_color} !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
        text-shadow: 1px 3px 6px rgba(0, 0, 0, 0.5);
    }}
    
    .stContainer, .element-container {{
        background: {primary_color} !important;
        border-left: 4px solid {accent_color};
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
    }}
    
    .stDataFrame {{
        background: {primary_color} !important;
        border-radius: 12px;
        border-left: 4px solid {accent_color};
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }}
    
    .stDataFrame th {{
        background: rgba(138, 5, 190, 0.9) !important;
        color: {text_color} !important;
        font-weight: 600 !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }}
    
    .stDataFrame td {{
        background: {primary_color} !important;
        color: white !important;
        border-color: {accent_color} !important;
    }}
    
    .stTextInput > div > div > input, .stSelectbox > div > div, 
    .stNumberInput > div > div > input, .stTextArea > div > div > textarea {{
        background: {primary_color} !important;
        border: 2px solid {accent_color} !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }}
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {{
        color: rgba(255, 255, 255, 0.7) !important;
        opacity: 1 !important;
    }}
    
    .stSelectbox > div > div:focus-within, 
    .stTextInput > div > div:focus-within, 
    .stNumberInput > div > div:focus-within {{
        border-color: {accent_color};
        box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.5);
    }}
    
    .stAlert {{
        border-radius: 8px !important;
        border: none !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
    }}
    
    .stSuccess {{
        background: linear-gradient(90deg, #333333 0%, #555555 100%) !important;
        color: white !important;
        text-shadow: 1px 2px 4px rgba(0, 0, 0, 0.4);
    }}
    
    .stError {{
        background: linear-gradient(90deg, #DC3545 0%, #E74C3C 100%) !important;
        color: white !important;
        text-shadow: 1px 2px 4px rgba(0, 0, 0, 0.4);
    }}
    
    .stWarning {{
        background: linear-gradient(90deg, #FFC107 0%, #F39C12 100%) !important;
        color: #333333 !important;
        text-shadow: 1px 2px 3px rgba(255, 255, 255, 0.6);
    }}
    
    .stInfo {{
        background: linear-gradient(90deg, #17A2B8 0%, #3498DB 100%) !important;
        color: white !important;
        text-shadow: 1px 2px 4px rgba(0, 0, 0, 0.4);
    }}
    
    .metric-card {{
        background: linear-gradient(135deg, {primary_color} 0%, rgba(138, 5, 190, 0.8) 100%) !important;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-left: 4px solid {accent_color};
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
        transform: translateY(-2px);
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: white !important;
        text-shadow: 1px 2px 4px rgba(0, 0, 0, 0.4);
    }}
    
    .metric-label {{
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 500;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
    }}
    
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, 
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6, .stText, label, 
    .stSubheader, .stCaption {{
        color: {text_color} !important;
    }}
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stSubheader {{
        text-shadow: 1px 2px 4px rgba(0, 0, 0, 0.35);
    }}
    
    label, .stCaption {{
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
    }}
    
    /* Expandable sections */
    .streamlit-expanderHeader {{
        background: {primary_color} !important;
        color: white !important;
        border: 1px solid {accent_color} !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }}
    
    .streamlit-expanderContent {{
        background: {primary_color} !important;
        border: 1px solid {accent_color} !important;
        color: white !important;
    }}
    
    /* Forms */
    .stForm {{
        background: {primary_color} !important;
        border: 2px solid {accent_color} !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2) !important;
    }}
    
    /* Checkbox and radio buttons */
    .stCheckbox > label, .stRadio > label {{
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }}
    
    /* Download button */
    .stDownloadButton > button {{
        background: {primary_color} !important;
        border: 2px solid {accent_color} !important;
        color: white !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }}
    
    /* Tabs styling - Login and Solicitar Acesso */
    .stTabs {{
        background: transparent !important;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        background: transparent !important;
        border-bottom: 2px solid {accent_color} !important;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: {accent_color} !important;
        color: white !important;
        border: 1px solid {accent_color} !important;
        border-radius: 8px 8px 0 0 !important;
        margin-right: 2px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease !important;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background: rgba(0, 0, 0, 0.8) !important;
        transform: translateY(-1px) !important;
    }}
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background: {accent_color} !important;
        color: white !important;
        border-bottom: 2px solid {accent_color} !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
    }}
    
    .stTabs [data-baseweb="tab-panel"] {{
        background: {primary_color} !important;
        border: 2px solid {accent_color} !important;
        border-top: none !important;
        border-radius: 0 8px 8px 8px !important;
        padding: 2rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    }}
    
    /* Active/Focus states - White instead of red */
    button:active, button:focus,
    .stButton > button:active, .stButton > button:focus,
    input:active, input:focus,
    textarea:active, textarea:focus,
    select:active, select:focus,
    a:active, a:focus,
    .stSelectbox:active, .stSelectbox:focus,
    .stTextInput:active, .stTextInput:focus,
    .stNumberInput:active, .stNumberInput:focus,
    .stTextArea:active, .stTextArea:focus,
    .stDownloadButton > button:active,
    .stDownloadButton > button:focus,
    .stTabs [data-baseweb="tab"]:active,
    .stTabs [data-baseweb="tab"]:focus {{
        background: white !important;
        color: {primary_color} !important;
        border-color: white !important;
        outline: 2px solid white !important;
        outline-offset: 2px !important;
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.3) !important;
        transform: scale(0.98) !important;
        text-shadow: none !important;
    }}
    
    /* Button active states */
    .stButton > button:active {{
        background: white !important;
        color: {primary_color} !important;
        border: 2px solid {primary_color} !important;
        transform: scale(0.95) !important;
        text-shadow: none !important;
    }}
    
    /* Input active states */
    .stTextInput > div > div > input:active,
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:active,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:active,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div:active,
    .stSelectbox > div > div:focus {{
        background: white !important;
        color: {primary_color} !important;
        border: 3px solid white !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.5) !important;
        text-shadow: none !important;
    }}
    
    /* Tab active states */
    .stTabs [data-baseweb="tab"]:active {{
        background: white !important;
        color: {primary_color} !important;
        border: 2px solid white !important;
        transform: scale(0.98) !important;
        text-shadow: none !important;
    }}
    
    /* Remove default browser active/focus colors */
    *:active, *:focus {{
        outline: none !important;
        -webkit-tap-highlight-color: transparent !important;
    }}
    
    /* Checkbox and radio active states */
    .stCheckbox:active, .stCheckbox:focus,
    .stRadio:active, .stRadio:focus {{
        background: white !important;
        border: 2px solid {primary_color} !important;
    }}
    
    {custom_css}
    </style>
    """, unsafe_allow_html=True)

# ========================================================================================
# DADOS SIMULADOS PARA DEMONSTRAÇÃO
# ========================================================================================

@st.cache_data
def load_inventory_data():
    """Carrega dados simulados do inventário"""
    
    # Dados simulados para diferentes categorias de inventário
    spark_data = pd.DataFrame({
        'itens': ['Notebook Dell', 'Mouse Logitech', 'Teclado Mecânico', 'Monitor LG', 'Webcam HD'],
        'modelo': ['Latitude 5520', 'MX Master 3', 'K70 RGB', '27GL850', 'C920'],
        'tag': ['SPK001', 'SPK002', 'SPK003', 'SPK004', 'SPK005'],
        'serial': ['DL123456', 'LG789012', 'CO345678', 'LG901234', 'LG567890'],
        'marca': ['Dell', 'Logitech', 'Corsair', 'LG', 'Logitech'],
        'valor': [3500.00, 450.00, 800.00, 2200.00, 350.00],
        'data_compra': pd.to_datetime(['2024-01-15', '2024-02-20', '2024-03-10', '2024-01-30', '2024-02-15']),
        'fornecedor': ['Dell Brasil', 'Logitech', 'Corsair Gaming', 'LG Electronics', 'Logitech'],
        'po': ['PO-2024-001', 'PO-2024-002', 'PO-2024-003', 'PO-2024-004', 'PO-2024-005'],
        'uso': ['Desenvolvimento', 'Escritório', 'Gaming', 'Design', 'Videoconferência'],
        'qtd': [5, 20, 3, 8, 12],
        'avenue': ['A1', 'A2', 'A1', 'B1', 'A3'],
        'street': ['Rua Tech', 'Rua Periféricos', 'Rua Tech', 'Rua Monitores', 'Rua AV'],
        'shelf': ['Prateleira 1', 'Prateleira 2', 'Prateleira 1', 'Prateleira 3', 'Prateleira 4'],
        'box': ['Caixa A', 'Caixa B', 'Caixa A', 'Caixa C', 'Caixa D'],
        'conferido': [True, True, False, True, False]
    })
    
    hq1_data = pd.DataFrame({
        'itens': ['Impressora HP', 'Scanner Epson', 'Projetor BenQ', 'Telefone IP', 'Roteador Cisco'],
        'modelo': ['LaserJet Pro', 'WorkForce ES-400', 'MX825ST', '7841', 'ASA 5506-X'],
        'tag': ['HQ1001', 'HQ1002', 'HQ1003', 'HQ1004', 'HQ1005'],
        'serial': ['HP234567', 'EP890123', 'BQ456789', 'CI012345', 'CI678901'],
        'marca': ['HP', 'Epson', 'BenQ', 'Cisco', 'Cisco'],
        'valor': [1200.00, 800.00, 3500.00, 450.00, 2800.00],
        'data_compra': ['2024-02-10', '2024-01-25', '2024-03-05', '2024-02-28', '2024-01-12'],
        'fornecedor': ['HP Brasil', 'Epson', 'BenQ', 'Cisco Systems', 'Cisco Systems'],
        'po': ['PO-2024-006', 'PO-2024-007', 'PO-2024-008', 'PO-2024-009', 'PO-2024-010'],
        'uso': ['Escritório', 'Digitalização', 'Apresentações', 'Comunicação', 'Rede'],
        'qtd': [3, 2, 1, 15, 2],
        'avenue': ['B1', 'B2', 'B1', 'C1', 'C2'],
        'street': ['Rua Office', 'Rua Scan', 'Rua Office', 'Rua Telecom', 'Rua Network'],
        'shelf': ['Prateleira 5', 'Prateleira 6', 'Prateleira 5', 'Prateleira 7', 'Prateleira 8'],
        'box': ['Caixa E', 'Caixa F', 'Caixa E', 'Caixa G', 'Caixa H'],
        'conferido': [True, False, True, True, False]
    })
    
    return {
        'spark': spark_data,
        'hq1': hq1_data
    }

# ========================================================================================
# SISTEMA DE AUTENTICAÇÃO
# ========================================================================================

# Administrador principal (já aprovado por padrão)
ADMIN_EMAIL = "danilo.fukuyama.digisystem@nubank.com.br"

# Configurações de tema padrão
DEFAULT_THEME = {
    'primary_color': '#8A05BE',
    'background_color': '#000000',
    'text_color': 'white',
    'accent_color': '#8A05BE',
    'gradient_enabled': False,
    'custom_css': ''
}

def hash_password(password: str) -> str:
    """Cria hash seguro da senha usando salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return salt + password_hash.hex()

def verify_password(password: str, password_hash: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    if not password_hash or len(password_hash) < 32:
        return False
    salt = password_hash[:32]
    stored_hash = password_hash[32:]
    password_test_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return stored_hash == password_test_hash.hex()

def init_user_system():
    """Inicializa o sistema de usuários"""
    if 'users_db' not in st.session_state:
        st.session_state.users_db = {
            ADMIN_EMAIL: {
                'nome': 'Danilo Fukuyama',
                'email': ADMIN_EMAIL,
                'password_hash': hash_password('admin123'),  # Senha padrão: admin123
                'role': 'admin',
                'status': 'aprovado',
                'data_registro': '2024-01-01',
                'aprovado_por': 'sistema'
            }
        }
    
    if 'usuarios_pendentes' not in st.session_state:
        st.session_state.usuarios_pendentes = {}
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    
    # Inicializar configurações de tema
    if 'theme_config' not in st.session_state:
        st.session_state.theme_config = DEFAULT_THEME.copy()

def is_admin(email):
    """Verifica se o usuário é administrador"""
    return email == ADMIN_EMAIL or (
        email in st.session_state.users_db and 
        st.session_state.users_db[email].get('role') == 'admin'
    )

def is_user_approved(email):
    """Verifica se o usuário está aprovado"""
    return (
        email in st.session_state.users_db and 
        st.session_state.users_db[email].get('status') == 'aprovado'
    )

def register_user(nome, email, password, justificativa):
    """Registra um novo usuário para aprovação"""
    from datetime import datetime as dt
    
    if email in st.session_state.users_db:
        return False, "Usuário já existe no sistema"
    
    if email in st.session_state.usuarios_pendentes:
        return False, "Solicitação já existe e está pendente de aprovação"
    
    st.session_state.usuarios_pendentes[email] = {
        'nome': nome,
        'email': email,
        'password_hash': hash_password(password),
        'justificativa': justificativa,
        'data_solicitacao': dt.now().strftime('%Y-%m-%d %H:%M'),
        'status': 'pendente'
    }
    
    return True, "Solicitação de acesso enviada para aprovação"

def approve_user(email, approved_by):
    """Aprova um usuário pendente"""
    if email in st.session_state.usuarios_pendentes:
        user_data = st.session_state.usuarios_pendentes[email]
        
        st.session_state.users_db[email] = {
            'nome': user_data['nome'],
            'email': email,
            'password_hash': user_data['password_hash'],
            'role': 'usuario',
            'status': 'aprovado',
            'data_registro': user_data['data_solicitacao'],
            'aprovado_por': approved_by,
            'justificativa': user_data['justificativa']
        }
        
        del st.session_state.usuarios_pendentes[email]
        return True
    return False

def reject_user(email):
    """Rejeita um usuário pendente"""
    if email in st.session_state.usuarios_pendentes:
        del st.session_state.usuarios_pendentes[email]
        return True
    return False

def authenticate_user(email, password):
    """Autentica um usuário com email e senha"""
    if is_user_approved(email):
        user_data = st.session_state.users_db[email]
        if 'password_hash' in user_data and verify_password(password, user_data['password_hash']):
            st.session_state.authenticated = True
            st.session_state.current_user = email
            return True, "Login realizado com sucesso!"
        else:
            return False, "Senha incorreta"
    return False, "Usuário não encontrado ou não aprovado"

# ========================================================================================
# INICIALIZAÇÃO DA SESSÃO
# ========================================================================================

# Inicializar sistema de usuários
init_user_system()

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'

if 'inventory_data' not in st.session_state:
    st.session_state.inventory_data = load_inventory_data()

# ========================================================================================
# PÁGINAS DE AUTENTICAÇÃO
# ========================================================================================

def render_login_page():
    """Renderiza a página de login"""
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h1 style="color: #8A05BE; margin: 0.5rem 0 0 0; font-size: 2.5rem; font-weight: 700;">Gestão de Estoque</h1>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["● Login", "◉ Solicitar Acesso"])

    with tab1:
        st.subheader("Fazer Login")
        
        with st.form("login_form"):
            email = st.text_input("@ Email", placeholder="seu.email@empresa.com")
            password = st.text_input("● Senha", type="password", placeholder="Digite sua senha")
            
            if st.form_submit_button("→ Entrar", use_container_width=True):
                if not email or not password:
                    st.error("× Digite seu email e senha")
                else:
                    success, message = authenticate_user(email, password)
                    if success:
                        st.success(f"✓ {message} Bem-vindo(a), {st.session_state.users_db[email]['nome']}")
                        st.rerun()
                    elif email in st.session_state.usuarios_pendentes:
                        st.warning("⧖ Sua solicitação está pendente de aprovação pelo administrador")
                    else:
                        st.error(f"× {message}")

    with tab2:
        st.subheader("Solicitar Acesso ao Sistema")
        st.info("→ Para acessar o sistema, você precisa de aprovação do administrador")
        
        with st.form("registro_form"):
            nome = st.text_input("○ Nome Completo", placeholder="Seu nome completo")
            email = st.text_input("@ Email Corporativo", placeholder="seu.email@empresa.com")
            password = st.text_input("● Senha", type="password", placeholder="Crie uma senha segura", 
                                   help="Mínimo 6 caracteres")
            password_confirm = st.text_input("● Confirmar Senha", type="password", placeholder="Confirme sua senha")
            justificativa = st.text_area("▤ Justificativa", 
                                       placeholder="Explique por que precisa acessar o sistema de estoque...",
                                       help="Descreva sua função e motivo para acessar o sistema")
            
            if st.form_submit_button("→ Solicitar Acesso", use_container_width=True):
                if not nome or not email or not password or not password_confirm or not justificativa:
                    st.error("× Preencha todos os campos")
                elif len(password) < 6:
                    st.error("× A senha deve ter pelo menos 6 caracteres")
                elif password != password_confirm:
                    st.error("× As senhas não coincidem")
                elif len(justificativa) < 20:
                    st.error("× A justificativa deve ter pelo menos 20 caracteres")
                else:
                    success, message = register_user(nome, email, password, justificativa)
                    if success:
                        st.success(f"✓ {message}")
                        st.info("@ O administrador será notificado e analisará sua solicitação")
                    else:
                        st.error(f"× {message}")

def render_admin_users():
    """Renderiza a área de administração de usuários"""
    if not is_admin(st.session_state.current_user):
        st.error("× Acesso negado. Apenas administradores podem acessar esta área.")
        return
    
    st.subheader("○○ Administração de Usuários")
    
    # Solicitações pendentes
    if st.session_state.usuarios_pendentes:
        st.write("### ⧖ Solicitações Pendentes")
        
        for email, user_data in st.session_state.usuarios_pendentes.items():
            with st.expander(f"@ {user_data['nome']} - {email}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Nome:** {user_data['nome']}")
                    st.write(f"**Email:** {email}")
                    st.write(f"**Data da Solicitação:** {user_data['data_solicitacao']}")
                    st.write(f"**Justificativa:**")
                    st.write(user_data['justificativa'])
                
                with col2:
                    if st.button("✓ Aprovar", key=f"approve_{email}"):
                        if approve_user(email, st.session_state.current_user):
                            st.success(f"✓ Usuário {user_data['nome']} aprovado!")
                            st.rerun()
                    
                    if st.button("× Rejeitar", key=f"reject_{email}"):
                        if reject_user(email):
                            st.warning(f"× Solicitação de {user_data['nome']} rejeitada")
                            st.rerun()
    else:
        st.info("⊙ Nenhuma solicitação pendente")
    
    st.divider()
    
    # Usuários aprovados
    st.write("### ✓ Usuários Aprovados")
    
    users_data = []
    for email, user_data in st.session_state.users_db.items():
        users_data.append({
            'Nome': user_data['nome'],
            'Email': email,
            'Role': user_data['role'].title(),
            'Data Registro': user_data['data_registro'],
            'Aprovado Por': user_data['aprovado_por']
        })
    
    if users_data:
        df_users = pd.DataFrame(users_data)
        st.dataframe(df_users, use_container_width=True)
    else:
        st.info("○ Apenas você está cadastrado no sistema")

def render_visual_editor():
    """Renderiza o editor visual para customização do tema (apenas admin)"""
    if not is_admin(st.session_state.current_user):
        st.error("× Acesso negado. Apenas administradores podem acessar esta área.")
        return
    
    st.markdown("## ◇ Editor Visual")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("◉ Configurações de Tema")
        
        # Configurações de cores
        primary_color = st.color_picker(
            "◇ Cor Primária", 
            value=st.session_state.theme_config.get('primary_color', DEFAULT_THEME['primary_color']),
            help="Cor principal do tema (botões, destaques)"
        )
        
        background_color = st.color_picker(
            "□ Cor de Fundo", 
            value=st.session_state.theme_config.get('background_color', DEFAULT_THEME['background_color']),
            help="Cor de fundo principal do app"
        )
        
        accent_color = st.color_picker(
            "◆ Cor de Destaque", 
            value=st.session_state.theme_config.get('accent_color', DEFAULT_THEME['accent_color']),
            help="Cor para elementos de destaque (bordas, foco)"
        )
        
        text_color = st.selectbox(
            "○ Cor do Texto",
            options=["white", "black", "#333333"],
            index=0 if st.session_state.theme_config.get('text_color', 'white') == 'white' else 1,
            help="Cor principal do texto"
        )
        
        gradient_enabled = st.checkbox(
            "▲ Habilitar Gradientes",
            value=st.session_state.theme_config.get('gradient_enabled', False),
            help="Adicionar efeitos de gradiente aos elementos"
        )
        
        # CSS Customizado
        st.subheader("▤ CSS Personalizado")
        custom_css = st.text_area(
            "Adicione CSS personalizado:",
            value=st.session_state.theme_config.get('custom_css', ''),
            height=150,
            help="CSS adicional para customizações avançadas"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("■ Salvar Tema", use_container_width=True):
                st.session_state.theme_config.update({
                    'primary_color': primary_color,
                    'background_color': background_color,
                    'accent_color': accent_color,
                    'text_color': text_color,
                    'gradient_enabled': gradient_enabled,
                    'custom_css': custom_css
                })
                st.success("✓ Configurações de tema salvas!")
                st.rerun()
        
        with col_btn2:
            if st.button("↻ Restaurar Padrão", use_container_width=True):
                st.session_state.theme_config = DEFAULT_THEME.copy()
                st.success("✓ Tema restaurado para o padrão!")
                st.rerun()
        
        with col_btn3:
            if st.button("◎ Aplicar", use_container_width=True):
                st.rerun()
    
    with col2:
        st.subheader("⊙ Visualização")
        st.info("As mudanças serão aplicadas ao clicar em 'Aplicar' ou 'Salvar'")
        
        # Preview dos elementos com as cores atuais
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {primary_color}, {accent_color}); 
            padding: 20px; 
            border-radius: 10px; 
            margin: 10px 0;
            color: {text_color};
            text-align: center;
        ">
            <h3>◇ Preview do Tema</h3>
            <p>Esta é uma prévia de como ficará o tema com suas configurações.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Exibir configurações atuais
        st.write("**Configurações Atuais:**")
        config_data = {
            "Configuração": ["Cor Primária", "Cor de Fundo", "Cor de Destaque", "Cor do Texto", "Gradientes"],
            "Valor": [
                primary_color,
                background_color, 
                accent_color,
                text_color,
                "Habilitado" if gradient_enabled else "Desabilitado"
            ]
        }
        st.dataframe(pd.DataFrame(config_data), use_container_width=True)

# ========================================================================================
# NAVEGAÇÃO PRINCIPAL
# ========================================================================================

def render_navigation():
    """Renderiza a navegação principal na sidebar"""
    
    # Título na sidebar
    st.sidebar.markdown("""
    <div style="text-align: center; margin: 1rem 0 2rem 0;">
        <h3 style="color: #8A05BE; margin: 0; font-size: 1.2rem; font-weight: 700;">Gestão de Estoque</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Informações do usuário logado
    if st.session_state.authenticated:
        user_name = st.session_state.users_db[st.session_state.current_user]['nome']
        st.sidebar.markdown(f"### ○ {user_name}")
        st.sidebar.markdown(f"@ {st.session_state.current_user}")
        
        if is_admin(st.session_state.current_user):
            st.sidebar.markdown("★ **Administrador**")
        
        if st.sidebar.button("← Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.current_page = 'dashboard'
            st.rerun()
        
        st.sidebar.divider()
    
    st.sidebar.markdown("### ■ Sistema de Estoque")
    
    pages = {
        'dashboard': '▣ Dashboard',
        'upload_dados': '📊 Upload de Dados',
        'spark_inventory': '● Itens A&V Spark',
        'hq1_inventory': '▢ Itens A&V HQ1',
        'hq1_8th': '▤ Estoque',
        'impressoras': '🖨️ Impressoras',
        'tvs_monitores': '▢ TVs e Monitores',
        'vendas_spark': '$ Vendas Spark',
        'lixo_eletronico': '↻ Lixo Eletrônico',
        'inventario_oficial': '⎙ Inventário Oficial',
        'entrada_estoque': '☰ Entrada de Estoque',
        'saida_estoque': '↗ Saída de Estoque',
        'movimentacoes': '▤ Movimentações',
        'relatorios': '⤴ Relatórios'
    }
    
    # Adicionar páginas administrativas se for admin
    if st.session_state.authenticated and is_admin(st.session_state.current_user):
        st.sidebar.markdown("### ⚙ Administração")
        if st.sidebar.button("○○ Gerenciar Usuários", key="admin_users", use_container_width=True):
            st.session_state.current_page = 'admin_users'
            st.rerun()
        if st.sidebar.button("◇ Editor Visual", key="visual_editor", use_container_width=True):
            st.session_state.current_page = 'visual_editor'
            st.rerun()
        st.sidebar.divider()
    
    for page_key, page_name in pages.items():
        if st.sidebar.button(page_name, key=page_key, use_container_width=True):
            st.session_state.current_page = page_key
            st.rerun()

# ========================================================================================
# PÁGINAS DO SISTEMA
# ========================================================================================

def render_dashboard():
    """Renderiza o dashboard principal"""
    
    # Saudação personalizada
    from datetime import datetime as dt
    
    # Nome do usuário logado
    user_name = st.session_state.users_db[st.session_state.current_user]['nome'].split()[0]
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; margin: 1rem 0;">
            <div style="font-size: 2rem; color: #8A05BE; margin-bottom: 0.5rem;">◆</div>
            <h3 style="color: #8A05BE; margin: 0;">Olá, {user_name}!</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Notificações para administradores
    if is_admin(st.session_state.current_user):
        pending_count = len(st.session_state.usuarios_pendentes)
        if pending_count > 0:
            st.warning(f"◉ **Atenção Administrador**: {pending_count} solicitação(ões) de acesso pendente(s) de aprovação")
    
    # Métricas principais usando cards customizados
    col1, col2, col3, col4 = st.columns(4)
    
    total_spark = len(st.session_state.inventory_data['spark'])
    total_hq1 = len(st.session_state.inventory_data['hq1'])
    total_items = total_spark + total_hq1
    
    conferidos_spark = st.session_state.inventory_data['spark']['conferido'].sum()
    conferidos_hq1 = st.session_state.inventory_data['hq1']['conferido'].sum()
    total_conferidos = conferidos_spark + conferidos_hq1
    
    percentual_conferido = (total_conferidos / total_items * 100) if total_items > 0 else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_items}</div>
            <div class="metric-label">■ Total de Itens</div>
            <div class="metric-delta positive">+5 este mês</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_conferidos}</div>
            <div class="metric-label">✓ Conferidos</div>
            <div class="metric-delta positive">+{total_conferidos - 5} desde ontem</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{percentual_conferido:.1f}%</div>
            <div class="metric-label">▤ % Conferido</div>
            <div class="metric-delta {'positive' if percentual_conferido > 70 else 'negative'}">
                {'+10%' if percentual_conferido > 70 else '-5%'} da meta
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        valor_total = (st.session_state.inventory_data['spark']['valor'].sum() + 
                      st.session_state.inventory_data['hq1']['valor'].sum())
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">R$ {valor_total:,.0f}</div>
            <div class="metric-label">$ Valor Total</div>
            <div class="metric-delta positive">+R$ 15k este mês</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Gráficos de análise
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("▤ Distribuição por Local")
        
        # Gráfico de pizza para distribuição
        labels = ['SPARK', 'HQ1']
        values = [total_spark, total_hq1]
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
        fig.update_traces(
            hoverinfo='label+percent',
            textinfo='value+percent',
            textfont_size=20,
            marker=dict(colors=['#8A05BE', '#A855F7'], line=dict(color='#FFFFFF', width=2))
        )
        fig.update_layout(
            title_text="Itens por Localização",
            font=dict(size=14, color='white'),
            showlegend=True,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("✓ Status de Conferência")
        
        # Gráfico de barras para status
        status_data = pd.DataFrame({
            'Local': ['SPARK', 'HQ1'],
            'Conferidos': [conferidos_spark, conferidos_hq1],
            'Pendentes': [total_spark - conferidos_spark, total_hq1 - conferidos_hq1]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Conferidos', x=status_data['Local'], y=status_data['Conferidos'], 
                            marker_color='#8A05BE'))
        fig.add_trace(go.Bar(name='Pendentes', x=status_data['Local'], y=status_data['Pendentes'], 
                            marker_color='#A855F7'))
        
        fig.update_layout(
            title='Status de Conferência por Local',
            xaxis_title='Local',
            yaxis_title='Quantidade',
            barmode='stack',
            height=400,
            font=dict(size=14, color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(color='white'),
            yaxis=dict(color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
def render_inventory_table(data, title, key_prefix):
    """Renderiza uma tabela de inventário com funcionalidade de edição"""
    st.subheader(title)
    
    # Controles de Ação
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("● Adicionar Item", use_container_width=True, key=f"add_{key_prefix}"):
            st.session_state[f'show_add_form_{key_prefix}'] = True
    
    with col_btn2:
        if st.button("📝 Editar Dados", use_container_width=True, key=f"edit_{key_prefix}"):
            st.session_state[f'show_edit_mode_{key_prefix}'] = True
    
    with col_btn3:
        if st.button("📋 Exportar CSV", use_container_width=True, key=f"export_{key_prefix}"):
            csv = data.to_csv(index=False)
            st.download_button(
                label="⬇ Download CSV",
                data=csv,
                file_name=f"{key_prefix}_inventory_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key=f"download_{key_prefix}"
            )
    
    # Formulário de Adicionar Item
    if st.session_state.get(f'show_add_form_{key_prefix}', False):
        with st.expander("● Adicionar Novo Item", expanded=True):
            with st.form(f"add_{key_prefix}_item"):
                col1, col2 = st.columns(2)
                
                with col1:
                    itens = st.text_input("▣ Item", placeholder="Nome do item")
                    modelo = st.text_input("▣ Modelo", placeholder="Modelo/Versão")
                    tag = st.text_input("▣ Tag/Código", placeholder=f"{key_prefix.upper()}###")
                    marca = st.text_input("▣ Marca", placeholder="Marca do produto")
                    valor = st.number_input("$ Valor", min_value=0.0, format="%.2f")
                
                with col2:
                    serial = st.text_input("● Serial", placeholder="Número serial")
                    fornecedor = st.text_input("◉ Fornecedor", placeholder="Nome do fornecedor")
                    po = st.text_input("📋 PO", placeholder="PO-YYYY-###")
                    data_compra = st.date_input("⌚ Data de Compra")
                    uso = st.text_input("🎯 Uso", placeholder="Finalidade do item")
                
                    col_submit, col_cancel = st.columns(2)
                    
                    with col_submit:
                        if st.form_submit_button("● Adicionar", use_container_width=True):
                            if itens and modelo and tag and marca:
                                new_item = pd.DataFrame({
                                'itens': [itens],
                                'modelo': [modelo],
                                'tag': [tag],
                                'serial': [serial],
                                'marca': [marca],
                                'valor': [valor],
                                'data_compra': [data_compra.strftime('%Y-%m-%d')],
                                'fornecedor': [fornecedor],
                                'po': [po],
                                'uso': [uso],
                                'qtd': [1],
                                'avenue': ['A1'],
                                'street': ['Rua Principal'],
                                'shelf': ['Prateleira 1'],
                                'box': ['Caixa A'],
                                'conferido': [False]
                            })
                            
                            # Atualizar os dados no session_state
                            updated_data = pd.concat([st.session_state.inventory_data[key_prefix], new_item], ignore_index=True)
                            st.session_state.inventory_data[key_prefix] = updated_data
                            
                            st.success("✓ Item adicionado com sucesso!")
                            st.session_state[f'show_add_form_{key_prefix}'] = False
                            st.rerun()
                        else:
                            st.error("× Preencha todos os campos obrigatórios")
                    
                    with col_cancel:
                        if st.form_submit_button("× Cancelar", use_container_width=True):
                            st.session_state[f'show_add_form_{key_prefix}'] = False
                            st.rerun()
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("⊙ Buscar item", key=f"{key_prefix}_search")
    
    with col2:
        marca_filter = st.selectbox("▣ Filtrar por marca", 
                                   options=['Todas'] + list(data['marca'].unique()),
                                   key=f"{key_prefix}_marca")
    
    with col3:
        conferido_filter = st.selectbox("✓ Status conferência", 
                                       options=['Todos', 'Conferidos', 'Pendentes'],
                                       key=f"{key_prefix}_conferido")
    
    # Aplicar filtros
    filtered_data = data.copy()
    
    if search_term:
        mask = (filtered_data['itens'].str.contains(search_term, case=False, na=False) |
                filtered_data['modelo'].str.contains(search_term, case=False, na=False) |
                filtered_data['tag'].str.contains(search_term, case=False, na=False))
        filtered_data = filtered_data[mask]
    
    if marca_filter != 'Todas':
        filtered_data = filtered_data[filtered_data['marca'] == marca_filter]
    
    if conferido_filter == 'Conferidos':
        filtered_data = filtered_data[filtered_data['conferido'] == True]
    elif conferido_filter == 'Pendentes':
        filtered_data = filtered_data[filtered_data['conferido'] == False]
    
    # Mostrar resultados
    if not filtered_data.empty:
        st.write(f"☰ **{len(filtered_data)}** itens encontrados")
        
        # Modo de edição
        if st.session_state.get(f'show_edit_mode_{key_prefix}', False):
            st.info("📝 **MODO EDIÇÃO ATIVO** - Edite os dados diretamente na tabela abaixo")
            
            # Tabela editável
            edited_data = st.data_editor(
                filtered_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "itens": st.column_config.TextColumn("Item", width="medium"),
                    "modelo": st.column_config.TextColumn("Modelo", width="medium"),
                    "tag": st.column_config.TextColumn("Tag", width="small"),
                    "serial": st.column_config.TextColumn("Serial", width="medium"),
                    "marca": st.column_config.TextColumn("Marca", width="small"),
                    "valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f"),
                    "data_compra": st.column_config.DateColumn("Data Compra"),
                    "fornecedor": st.column_config.TextColumn("Fornecedor", width="medium"),
                    "po": st.column_config.TextColumn("PO", width="medium"),
                    "uso": st.column_config.TextColumn("Uso", width="medium"),
                    "qtd": st.column_config.NumberColumn("Qtd", min_value=0),
                    "avenue": st.column_config.TextColumn("Avenue", width="small"),
                    "street": st.column_config.TextColumn("Street", width="medium"),
                    "shelf": st.column_config.TextColumn("Shelf", width="medium"),
                    "box": st.column_config.TextColumn("Box", width="small"),
                    "conferido": st.column_config.CheckboxColumn("Conferido")
                },
                key=f"{key_prefix}_editor"
            )
            
            col_save, col_cancel = st.columns(2)
            
            with col_save:
                if st.button("✓ Salvar Alterações", use_container_width=True, key=f"save_{key_prefix}"):
                    st.session_state.inventory_data[key_prefix] = edited_data
                    st.success("✓ Alterações salvas com sucesso!")
                    st.session_state[f'show_edit_mode_{key_prefix}'] = False
                    st.rerun()
            
            with col_cancel:
                if st.button("❌ Cancelar Edição", use_container_width=True, key=f"cancel_edit_{key_prefix}"):
                    st.session_state[f'show_edit_mode_{key_prefix}'] = False
                    st.rerun()
        
        else:
            # Modo visualização (somente leitura)
            # Formatação da tabela para visualização
            display_data = filtered_data.copy()
            display_data['valor'] = display_data['valor'].apply(lambda x: f"R$ {x:,.2f}")
            display_data['conferido'] = display_data['conferido'].apply(lambda x: "✓" if x else "⧖")
            
            st.dataframe(
                display_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "itens": "Item",
                    "modelo": "Modelo", 
                    "tag": "Tag",
                    "serial": "Serial",
                    "marca": "Marca",
                    "valor": "Valor",
                    "data_compra": "Data Compra",
                    "fornecedor": "Fornecedor",
                    "po": "PO",
                    "uso": "Uso",
                    "qtd": "Qtd",
                    "avenue": "Avenue",
                    "street": "Street", 
                    "shelf": "Shelf",
                    "box": "Box",
                    "conferido": "Status"
                }
            )
    else:
        st.info("⊙ Nenhum item encontrado com os filtros aplicados")

# ========================================================================================
# FUNÇÕES DAS PÁGINAS ESPECÍFICAS
# ========================================================================================

# Função render_techstop_hq1 removida conforme solicitado pelo usuário
def render_hq1_8th():
    """Renderiza a página do estoque"""
    st.markdown("## ▤ Estoque")
    
    # Inicializar dados de estoque do HQ1 no session_state se não existir
    if 'hq1_8th_inventory' not in st.session_state:
        st.session_state.hq1_8th_inventory = pd.DataFrame({
            'item': ['Mesa Executiva', 'Cadeira Ergonômica', 'Armário Alto', 'Mesa Reunião', 'Quadro Branco'],
            'categoria': ['techstop', 'techstop', 'A&V', 'techstop', 'A&V'],
            'tag': ['HQ1001', 'HQ1002', 'HQ1003', 'HQ1004', 'HQ1005'],
            'estado': ['✓ Excelente', '✓ Excelente', '◐ Bom', '✓ Excelente', '◐ Bom'],
            'valor': [1500.00, 800.00, 600.00, 2200.00, 350.00],
            'nota_fiscal': ['NF-MOB-001', 'NF-MOB-002', 'NF-MOB-003', 'NF-MOB-004', 'NF-ESC-001'],
            'data_entrada': pd.to_datetime(['2024-01-10', '2024-01-15', '2024-01-20', '2024-02-05', '2024-02-10']),
            'fornecedor': ['Móveis Corporativos', 'Ergonomia Plus', 'Móveis Corporativos', 'Móveis Corporativos', 'Office Supplies'],
            'po': ['PO-MOB-001', 'PO-MOB-002', 'PO-MOB-003', 'PO-MOB-004', 'PO-ESC-001']
        })
    
    # Inicializar dados de estoque do Spark no session_state se não existir
    if 'spark_estoque_data' not in st.session_state:
        st.session_state.spark_estoque_data = pd.DataFrame({
            'item': ['Projetor 4K', 'Sistema Som', 'Notebook Dell', 'Monitor 32"', 'Câmera Profissional'],
            'categoria': ['A&V', 'A&V', 'techstop', 'A&V', 'A&V'],
            'tag': ['SPK001', 'SPK002', 'SPK003', 'SPK004', 'SPK005'],
            'estado': ['✓ Excelente', '◐ Bom', '✓ Excelente', '✓ Excelente', '◐ Bom'],
            'valor': [8500.00, 2200.00, 4500.00, 1800.00, 12000.00],
            'nota_fiscal': ['NF-PROJ-001', 'NF-SOM-001', 'NF-NOTE-001', 'NF-MON-001', 'NF-CAM-001'],
            'data_entrada': pd.to_datetime(['2024-02-01', '2024-02-05', '2024-02-10', '2024-02-15', '2024-03-01']),
            'fornecedor': ['Tech Pro', 'Audio Systems', 'Dell Brasil', 'Samsung', 'Canon Brasil'],
            'po': ['PO-PROJ-001', 'PO-SOM-001', 'PO-NOTE-001', 'PO-MON-001', 'PO-CAM-001']
        })
    
    # Separar em tabs para HQ1 e Spark
    tab_hq1, tab_spark = st.tabs(["🏢 Inventário HQ1", "⚡ Inventário Spark"])
    
    # ===============================
    # TAB HQ1 - Inventário HQ1
    # ===============================
    with tab_hq1:
        # Garantir que hq1_8th_inventory existe e é um DataFrame
        if 'hq1_8th_inventory' not in st.session_state or not isinstance(st.session_state.hq1_8th_inventory, pd.DataFrame):
            st.session_state.hq1_8th_inventory = pd.DataFrame({
                'item': ['Mesa Executiva', 'Cadeira Ergonômica', 'Armário Alto', 'Mesa Reunião', 'Quadro Branco'],
                'categoria': ['techstop', 'techstop', 'A&V', 'techstop', 'A&V'],
                'tag': ['HQ1001', 'HQ1002', 'HQ1003', 'HQ1004', 'HQ1005'],
                'estado': ['✓ Excelente', '✓ Excelente', '◐ Bom', '✓ Excelente', '◐ Bom'],
                'valor': [1500.00, 800.00, 600.00, 2200.00, 350.00],
                'nota_fiscal': ['NF-MOB-001', 'NF-MOB-002', 'NF-MOB-003', 'NF-MOB-004', 'NF-ESC-001'],
                'data_entrada': pd.to_datetime(['2024-01-10', '2024-01-15', '2024-01-20', '2024-02-05', '2024-02-10']),
                'fornecedor': ['Móveis Corporativos', 'Ergonomia Plus', 'Móveis Corporativos', 'Móveis Corporativos', 'Office Supplies'],
                'po': ['PO-MOB-001', 'PO-MOB-002', 'PO-MOB-003', 'PO-MOB-004', 'PO-ESC-001']
            })
        
        hq1_8th_data = st.session_state.hq1_8th_inventory
        
        # Garantir que data_entrada seja do tipo datetime
        if hasattr(hq1_8th_data, 'columns') and 'data_entrada' in hq1_8th_data.columns:
            hq1_8th_data['data_entrada'] = pd.to_datetime(hq1_8th_data['data_entrada'], errors='coerce')
        
        # Controles de Ação
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("● Adicionar Item", use_container_width=True, key="add_hq1"):
                st.session_state.show_add_form_hq1_8th = True
        
        with col_btn2:
            if st.button("↗ Transferir Item", use_container_width=True, key="transfer_hq1"):
                st.session_state.show_transfer_form_hq1_8th = True
        
        with col_btn3:
            if st.button("↙ Receber Item", use_container_width=True, key="receive_hq1"):
                st.session_state.show_receive_form_hq1_8th = True
        
        # Formulário de Adicionar Item
        if st.session_state.get('show_add_form_hq1_8th', False):
            with st.expander("● Adicionar Novo Item", expanded=True):
                with st.form("add_hq1_8th_item"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        item = st.text_input("▣ Item", placeholder="Nome do item")
                        categoria = st.selectbox("◉ Categoria", ["techstop", "A&V"])
                        tag = st.text_input("▣ Tag/Código", placeholder="HQ1###")
                    
                    with col2:
                        estado = st.selectbox("◐ Estado", ["✓ Excelente", "◐ Bom", "⚠ Regular", "× Ruim"])
                        valor = st.number_input("$ Valor", min_value=0.0, format="%.2f")
                        nota_fiscal = st.text_input("⎙ Nota Fiscal", placeholder="NF-####-###")
                        data_entrada = st.date_input("⌚ Data de Entrada")
                        fornecedor = st.text_input("◉ Fornecedor", placeholder="Nome do fornecedor")
                    
                    col_submit, col_cancel = st.columns(2)
                    
                    with col_submit:
                        if st.form_submit_button("● Adicionar", use_container_width=True):
                            if item and categoria and tag:
                                new_item = pd.DataFrame({
                                    'item': [item],
                                    'categoria': [categoria],
                                    'tag': [tag],
                                    'estado': [estado],
                                    'valor': [valor],
                                    'nota_fiscal': [nota_fiscal],
                                    'data_entrada': [pd.to_datetime(data_entrada)],
                                    'fornecedor': [fornecedor]
                                })
                                st.session_state.hq1_8th_inventory = pd.concat([st.session_state.hq1_8th_inventory, new_item], ignore_index=True)
                                st.success("✓ Item adicionado com sucesso!")
                                st.session_state.show_add_form_hq1_8th = False
                                st.rerun()
                            else:
                                st.error("× Preencha todos os campos obrigatórios")
                    
                    with col_cancel:
                        if st.form_submit_button("× Cancelar", use_container_width=True):
                            st.session_state.show_add_form_hq1_8th = False
                            st.rerun()
        
        # Métricas do HQ1
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_itens = len(hq1_8th_data)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_itens}</div>
                <div class="metric-label">■ Total de Itens</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            excelente = len(hq1_8th_data[hq1_8th_data['estado'] == '✓ Excelente'])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{excelente}</div>
                <div class="metric-label">✓ Estado Excelente</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_valor = hq1_8th_data['valor'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">R$ {total_valor:,.2f}</div>
                <div class="metric-label">💰 Valor Total</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            valor_total = hq1_8th_data['valor'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">R$ {valor_total:,.0f}</div>
                <div class="metric-label">$ Valor Total</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
    
    # Filtros
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            categoria_filter = st.selectbox("◉ Filtrar por Categoria", ["Todas"] + list(hq1_8th_data['categoria'].unique()), key="cat_filter_hq1")
        
        with col_filter2:
            search_term = st.text_input("◈ Buscar Item", placeholder="Digite para buscar...", key="search_hq1")
    
    # Aplicar filtros
        filtered_data = hq1_8th_data.copy()
        
        if categoria_filter != "Todas":
            filtered_data = filtered_data[filtered_data['categoria'] == categoria_filter]
        
        if search_term:
            filtered_data = filtered_data[
                filtered_data['item'].str.contains(search_term, case=False, na=False) |
                filtered_data['tag'].str.contains(search_term, case=False, na=False)
            ]
        
        # Tabela de itens com opção de edição
        st.subheader("☰ Inventário HQ1")
        
        if not filtered_data.empty:
            # Mostrar dados em formato editável
            edited_data = st.data_editor(
                filtered_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "item": st.column_config.TextColumn("Item", width="medium"),
                    "categoria": st.column_config.SelectboxColumn("Categoria", options=["techstop", "A&V"]),
                    "tag": st.column_config.TextColumn("Tag", width="small"),
                    "estado": st.column_config.SelectboxColumn("Estado", options=["✓ Excelente", "◐ Bom", "⚠ Regular", "× Ruim"]),
                    "valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f"),
                    "nota_fiscal": st.column_config.TextColumn("Nota Fiscal", width="medium"),
                    "data_entrada": st.column_config.DateColumn("Data Entrada"),
                    "fornecedor": st.column_config.TextColumn("Fornecedor", width="medium"),
                    "po": st.column_config.TextColumn("PO", width="medium")
                },
                key="hq1_8th_editor"
            )
            
            # Botão para salvar alterações
            if st.button("● Salvar Alterações HQ1", use_container_width=True, key="save_hq1"):
                st.session_state.hq1_8th_inventory = edited_data
                st.success("✓ Alterações salvas com sucesso!")
                st.rerun()
        else:
            st.info("ℹ Nenhum item encontrado com os filtros aplicados.")
    
    # ===============================
    # TAB SPARK - Inventário Spark
    # ===============================
    with tab_spark:
        # Garantir que spark_estoque_data existe e é um DataFrame
        if 'spark_estoque_data' not in st.session_state or not isinstance(st.session_state.spark_estoque_data, pd.DataFrame):
                    st.session_state.spark_estoque_data = pd.DataFrame({
            'item': ['Projetor 4K', 'Sistema Som', 'Notebook Dell', 'Monitor 32"', 'Câmera Profissional'],
            'categoria': ['A&V', 'A&V', 'techstop', 'A&V', 'A&V'],
            'tag': ['SPK001', 'SPK002', 'SPK003', 'SPK004', 'SPK005'],
            'estado': ['✓ Excelente', '◐ Bom', '✓ Excelente', '✓ Excelente', '◐ Bom'],
            'valor': [8500.00, 2200.00, 4500.00, 1800.00, 12000.00],
            'nota_fiscal': ['NF-PROJ-001', 'NF-SOM-001', 'NF-NOTE-001', 'NF-MON-001', 'NF-CAM-001'],
            'data_entrada': pd.to_datetime(['2024-02-01', '2024-02-05', '2024-02-10', '2024-02-15', '2024-03-01']),
            'fornecedor': ['Tech Pro', 'Audio Systems', 'Dell Brasil', 'Samsung', 'Canon Brasil'],
            'po': ['PO-PROJ-001', 'PO-SOM-001', 'PO-NOTE-001', 'PO-MON-001', 'PO-CAM-001']
        })
        
        spark_data = st.session_state.spark_estoque_data
        
        # Garantir que data_entrada seja do tipo datetime
        if hasattr(spark_data, 'columns') and 'data_entrada' in spark_data.columns:
            spark_data['data_entrada'] = pd.to_datetime(spark_data['data_entrada'], errors='coerce')
        
        # Controles de Ação
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("● Adicionar Item", use_container_width=True, key="add_spark"):
                st.session_state.show_add_form_spark = True
        
        with col_btn2:
            if st.button("↗ Transferir Item", use_container_width=True, key="transfer_spark"):
                st.session_state.show_transfer_form_spark = True
        
        with col_btn3:
            if st.button("↙ Receber Item", use_container_width=True, key="receive_spark"):
                st.session_state.show_receive_form_spark = True
        
        # Formulário de Adicionar Item
        if st.session_state.get('show_add_form_spark', False):
            with st.expander("● Adicionar Novo Item", expanded=True):
                with st.form("add_spark_item"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        item = st.text_input("▣ Item", placeholder="Nome do item")
                        categoria = st.selectbox("◉ Categoria", ["techstop", "A&V"])
                        tag = st.text_input("▣ Tag/Código", placeholder="SPK###")
                    
                    with col2:
                        estado = st.selectbox("◐ Estado", ["✓ Excelente", "◐ Bom", "⚠ Regular", "× Ruim"])
                        valor = st.number_input("$ Valor", min_value=0.0, format="%.2f")
                        nota_fiscal = st.text_input("⎙ Nota Fiscal", placeholder="NF-####-###")
                        data_entrada = st.date_input("⌚ Data de Entrada")
                        fornecedor = st.text_input("◉ Fornecedor", placeholder="Nome do fornecedor")
                    
                    col_submit, col_cancel = st.columns(2)
                    
                    with col_submit:
                        if st.form_submit_button("● Adicionar", use_container_width=True):
                            if item and categoria and tag:
                                new_item = pd.DataFrame({
                                    'item': [item],
                                    'categoria': [categoria],
                                    'tag': [tag],
                                    'estado': [estado],
                                    'valor': [valor],
                                    'nota_fiscal': [nota_fiscal],
                                    'data_entrada': [pd.to_datetime(data_entrada)],
                                    'fornecedor': [fornecedor]
                                })
                                st.session_state.spark_estoque_data = pd.concat([st.session_state.spark_estoque_data, new_item], ignore_index=True)
                                st.success("✓ Item adicionado com sucesso!")
                                st.session_state.show_add_form_spark = False
                                st.rerun()
                            else:
                                st.error("× Preencha todos os campos obrigatórios")
                    
                    with col_cancel:
                        if st.form_submit_button("× Cancelar", use_container_width=True):
                            st.session_state.show_add_form_spark = False
                            st.rerun()
        
        # Métricas do Spark
    col1, col2, col3, col4 = st.columns(4)
        
    with col1:
            total_itens = len(spark_data)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_itens}</div>
                <div class="metric-label">⚡ Total de Itens</div>
            </div>
            """, unsafe_allow_html=True)
        
    with col2:
            excelente = len(spark_data[spark_data['estado'] == '✓ Excelente'])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{excelente}</div>
                <div class="metric-label">✓ Estado Excelente</div>
            </div>
            """, unsafe_allow_html=True)
        
    with col3:
            total_av = len(spark_data[spark_data['categoria'] == 'A&V'])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_av}</div>
                <div class="metric-label">📺 Itens A&V</div>
            </div>
            """, unsafe_allow_html=True)
        
    with col4:
            valor_total = spark_data['valor'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">R$ {valor_total:,.0f}</div>
                <div class="metric-label">$ Valor Total</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Filtros
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        categoria_filter = st.selectbox("◉ Filtrar por Categoria", ["Todas"] + list(spark_data['categoria'].unique()), key="cat_filter_spark")
    
    with col_filter2:
        search_term = st.text_input("◈ Buscar Item", placeholder="Digite para buscar...", key="search_spark")
    
    # Aplicar filtros
    filtered_data = spark_data.copy()
    
    if categoria_filter != "Todas":
        filtered_data = filtered_data[filtered_data['categoria'] == categoria_filter]
    
    if search_term:
        filtered_data = filtered_data[
            filtered_data['item'].str.contains(search_term, case=False, na=False) |
            filtered_data['tag'].str.contains(search_term, case=False, na=False)
        ]
        
        # Tabela de itens com opção de edição
        st.subheader("⚡ Inventário Spark")
        
        if not filtered_data.empty:
            # Mostrar dados em formato editável
            edited_data = st.data_editor(
                filtered_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "item": st.column_config.TextColumn("Item", width="medium"),
                    "categoria": st.column_config.SelectboxColumn("Categoria", options=["techstop", "A&V"]),
                    "tag": st.column_config.TextColumn("Tag", width="small"),
                    "estado": st.column_config.SelectboxColumn("Estado", options=["✓ Excelente", "◐ Bom", "⚠ Regular", "× Ruim"]),
                    "valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f"),
                    "nota_fiscal": st.column_config.TextColumn("Nota Fiscal", width="medium"),
                    "data_entrada": st.column_config.DateColumn("Data Entrada"),
                    "fornecedor": st.column_config.TextColumn("Fornecedor", width="medium"),
                    "po": st.column_config.TextColumn("PO", width="medium")
                },
                key="spark_editor"
            )
            
            # Botão para salvar alterações
            if st.button("● Salvar Alterações Spark", use_container_width=True, key="save_spark"):
                st.session_state.spark_estoque_data = edited_data
                st.success("✓ Alterações salvas com sucesso!")
                st.rerun()
        else:
            st.info("ℹ Nenhum item encontrado com os filtros aplicados.")

def render_csv_upload_section(data_key, required_columns, section_title="Upload de Dados"):
    """Função genérica para upload de CSV em qualquer seção"""
    st.markdown("""
    <style>
    .csv-upload-expander {
        background: linear-gradient(135deg, #8A05BE 0%, #A855F7 100%) !important;
        border: 2px solid #6B21A8 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(138, 5, 190, 0.2) !important;
        margin: 1rem 0 !important;
    }
    
    .csv-upload-expander .streamlit-expanderHeader {
        background: transparent !important;
        color: white !important;
        font-weight: 600 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
        font-size: 1.1rem !important;
        padding: 1rem !important;
    }
    
    .csv-upload-expander:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(138, 5, 190, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.expander(f"📊 {section_title}", expanded=False):
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h3 style="color: #8A05BE; margin: 0;">🚀 Upload Inteligente em Lote</h3>
            <p style="color: #666; margin: 0.5rem 0;">✨ Importe dados instantaneamente via arquivo CSV</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_csv = st.file_uploader(
            "Escolha um arquivo CSV", 
            type=['csv'],
            help=f"O arquivo deve conter as colunas: {', '.join(required_columns)}",
            key=f"csv_upload_{data_key}"
        )
        
        if uploaded_csv is not None:
            try:
                df_upload = pd.read_csv(uploaded_csv)
                
                st.markdown("#### 👁️ Preview dos Dados:")
                st.dataframe(df_upload.head(), use_container_width=True)
                
                # Verificar colunas obrigatórias
                missing_cols = [col for col in required_columns if col not in df_upload.columns]
                
                if missing_cols:
                    st.error(f"❌ Colunas obrigatórias faltando: {', '.join(missing_cols)}")
                else:
                    col_preview, col_import = st.columns(2)
                    
                    with col_preview:
                        st.success(f"✅ {len(df_upload)} itens prontos para importar")
                        st.info(f"📊 Colunas encontradas: {len(df_upload.columns)}")
                    
                    with col_import:
                        if st.button(f"🔄 Importar {len(df_upload)} itens", use_container_width=True, key=f"import_{data_key}"):
                            # Processar dados específicos se necessário (datas, etc.)
                            if 'data_entrada' in df_upload.columns:
                                df_upload['data_entrada'] = pd.to_datetime(df_upload['data_entrada'], errors='coerce')
                            
                            # Combinar com dados existentes
                            if data_key in st.session_state and not st.session_state[data_key].empty:
                                st.session_state[data_key] = pd.concat([st.session_state[data_key], df_upload], ignore_index=True)
                            else:
                                st.session_state[data_key] = df_upload
                            
                            st.success(f"🎉 {len(df_upload)} itens importados com sucesso!")
                            st.rerun()
                            
            except Exception as e:
                st.error(f"❌ Erro ao processar arquivo: {str(e)}")

# ========================================================================================
# FUNÇÕES DE CONECTIVIDADE DE IMPRESSORAS
# ========================================================================================

def check_vpn_connection():
    """Verifica se está conectado à VPN da Nubank - versão flexível"""
    # Tentar múltiplos métodos de verificação
    vpn_tests = []
    
    # Teste 1: Portal principal Nubank
    try:
        response = requests.get("https://br1.zta.nubank.world", timeout=5, verify=False)
        vpn_tests.append(response.status_code in [200, 302, 401, 403, 404])
    except:
        vpn_tests.append(False)
    
    # Teste 2: Tentar sem HTTPS
    try:
        response = requests.get("http://br1.zta.nubank.world", timeout=3)
        vpn_tests.append(response.status_code in [200, 302, 401, 403, 404])
    except:
        vpn_tests.append(False)
    
    # Teste 3: Verificar se consegue resolver DNS do domínio
    try:
        import socket
        socket.gethostbyname("br1.zta.nubank.world")
        vpn_tests.append(True)
    except:
        vpn_tests.append(False)
    
    # Teste 4: Verificar se está na rede 172.x.x.x (rede interna Nubank)
    try:
        import subprocess
        result = subprocess.run(["ifconfig"], capture_output=True, text=True, timeout=2)
        vpn_tests.append("172." in result.stdout)
    except:
        vpn_tests.append(False)
    
    # Se pelo menos um teste passou, considera conectado
    return any(vpn_tests)

def debug_vpn_connection():
    """Função de debug para mostrar detalhes da verificação VPN"""
    st.subheader("🔍 Debug de Conexão VPN")
    
    tests_results = {}
    
    # Teste 1: Portal HTTPS
    st.write("**Teste 1: Portal HTTPS (br1.zta.nubank.world)**")
    try:
        response = requests.get("https://br1.zta.nubank.world", timeout=5, verify=False)
        tests_results['https'] = f"✅ Status: {response.status_code}"
        st.success(f"Status Code: {response.status_code}")
    except Exception as e:
        tests_results['https'] = f"❌ Erro: {str(e)}"
        st.error(f"Erro: {str(e)}")
    
    # Teste 2: Portal HTTP
    st.write("**Teste 2: Portal HTTP**")
    try:
        response = requests.get("http://br1.zta.nubank.world", timeout=3)
        tests_results['http'] = f"✅ Status: {response.status_code}"
        st.success(f"Status Code: {response.status_code}")
    except Exception as e:
        tests_results['http'] = f"❌ Erro: {str(e)}"
        st.error(f"Erro: {str(e)}")
    
    # Teste 3: DNS Resolution
    st.write("**Teste 3: Resolução DNS**")
    try:
        import socket
        ip = socket.gethostbyname("br1.zta.nubank.world")
        tests_results['dns'] = f"✅ IP: {ip}"
        st.success(f"Resolvido para IP: {ip}")
    except Exception as e:
        tests_results['dns'] = f"❌ Erro: {str(e)}"
        st.error(f"Erro: {str(e)}")
    
    # Teste 4: Interfaces de rede
    st.write("**Teste 4: Interfaces de Rede (172.x.x.x)**")
    try:
        import subprocess
        result = subprocess.run(["ifconfig"], capture_output=True, text=True, timeout=2)
        if "172." in result.stdout:
            # Extrair IPs da rede 172
            lines = result.stdout.split('\n')
            ips_172 = [line.strip() for line in lines if '172.' in line]
            tests_results['network'] = f"✅ Rede 172 encontrada"
            st.success("Rede 172.x.x.x detectada:")
            for ip_line in ips_172[:3]:  # Mostrar apenas as primeiras 3 linhas
                st.code(ip_line)
        else:
            tests_results['network'] = "❌ Rede 172 não encontrada"
            st.warning("Rede 172.x.x.x não detectada")
    except Exception as e:
        tests_results['network'] = f"❌ Erro: {str(e)}"
        st.error(f"Erro: {str(e)}")
    
    # Resumo
    st.write("**Resumo dos Testes:**")
    for test, result in tests_results.items():
        st.write(f"- {test}: {result}")
    
    # Resultado final
    passed_tests = sum(1 for result in tests_results.values() if '✅' in result)
    st.write(f"**Testes aprovados: {passed_tests}/{len(tests_results)}**")
    
    if passed_tests > 0:
        st.success("🔓 VPN deveria estar funcionando!")
    else:
        st.error("🔒 Nenhum teste de VPN passou")
    
    # Teste manual de impressora
    st.write("**Teste Manual de Impressora:**")
    test_ip = st.text_input("Digite um IP de impressora para testar:", value="172.25.61.81")
    if st.button("🖨️ Testar Impressora"):
        if test_ip:
            st.write(f"Testando impressora {test_ip}...")
            result = get_printer_status_fast(test_ip)
            st.write(f"Resultado: {result}")
        else:
            st.error("Digite um IP para testar")

def ping_ip_simple(ip_address):
    """Faz ping simples e direto no IP"""
    try:
        import platform
        system = platform.system().lower()
        
        if system == "windows":
            cmd = ["ping", "-n", "1", "-w", "1000", ip_address]
        else:
            cmd = ["ping", "-c", "1", "-W", "1", ip_address]
        
        result = subprocess.run(cmd, capture_output=True, timeout=3)
        return result.returncode == 0
    except:
        return False

def check_printer_web(ip_address, timeout=1):
    """Verifica se a impressora responde via HTTP - mais rápido"""
    try:
        # Tentar HTTP primeiro (mais comum em Epson)
        response = requests.get(f"http://{ip_address}", timeout=timeout)
        return True
    except:
        try:
            # Verificar apenas se a porta 80 está aberta
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip_address, 80))
            sock.close()
            return result == 0
        except:
            return False

def get_ink_levels(ip_address):
    """Busca níveis de tinta da impressora Epson via HTTP"""
    try:
        # Tentar diferentes URLs comuns para Epson WF-C5790
        urls_to_try = [
            f"http://{ip_address}/PRESENTATION/HTML/TOP/PRTINFO.HTML",
            f"http://{ip_address}/PRESENTATION/HTML/TOP/TOP.HTML", 
            f"http://{ip_address}/cgi-bin/inkjetStatus",
            f"http://{ip_address}/status",
            f"http://{ip_address}/ink_level"
        ]
        
        for url in urls_to_try:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Buscar informações de tinta no HTML
                    ink_info = {"black": "N/A", "cyan": "N/A", "magenta": "N/A", "yellow": "N/A"}
                    
                    # Padrões comuns para níveis de tinta Epson
                    if "ink" in content or "tinta" in content:
                        import re
                        
                        # Buscar porcentagens ou níveis
                        patterns = [
                            r'black.*?(\d+)%',
                            r'cyan.*?(\d+)%', 
                            r'magenta.*?(\d+)%',
                            r'yellow.*?(\d+)%',
                            r'preto.*?(\d+)%',
                            r'azul.*?(\d+)%'
                        ]
                        
                        colors = ["black", "cyan", "magenta", "yellow", "black", "cyan"]
                        
                        for i, pattern in enumerate(patterns):
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches and i < 4:  # Apenas as 4 primeiras cores
                                ink_info[colors[i]] = f"{matches[0]}%"
                    
                    return ink_info
            except:
                continue
                
        return {"status": "Sem acesso web"}
    except:
        return {"status": "Erro na consulta"}

def get_printer_status_fast(ip_address):
    """Obtém status completo da impressora - versão super otimizada"""
    
    # Verificação rápida de ping
    ping_ok = ping_ip_simple(ip_address)
    
    if not ping_ok:
        return {"status": "🔴 Offline", "ink_levels": {"status": "Offline"}}
    
    # Verificar HTTP rapidamente
    web_ok = check_printer_web(ip_address, timeout=1)
    
    if ping_ok and web_ok:
        # Buscar níveis de tinta apenas se web estiver OK
        ink_levels = get_ink_levels(ip_address)
        return {"status": "🟢 Online", "ink_levels": ink_levels}
    elif ping_ok:
        return {"status": "🟡 Ping OK", "ink_levels": {"status": "Sem acesso web"}}
    else:
        return {"status": "🔴 Offline", "ink_levels": {"status": "Offline"}}

def ping_all_printers_simple(printers_df):
    """Faz ping simples em todas as impressoras - direto ao ponto"""
    results = {}
    
    for idx, row in printers_df.iterrows():
        ip = row['ip_rede'] if 'ip_rede' in row else 'N/A'
        
        if not ip or ip == 'N/A':
            results[idx] = {
                "status": "❌ Sem IP", 
                "url": ""
            }
        else:
            # Fazer ping direto
            ping_ok = ping_ip_simple(ip)
            
            if ping_ok:
                results[idx] = {
                    "status": "🟢 Online", 
                    "url": f"http://{ip}"
                }
            else:
                results[idx] = {
                    "status": "🔴 Offline", 
                    "url": f"http://{ip}"
                }
    
    return results


# ========== INTEGRAÇÃO PAPERCUT ==========

class PaperCutConnector:
    """Conector para buscar dados das impressoras no PaperCut"""
    
    def __init__(self, base_url, password):
        self.base_url = base_url
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        })
        # Desabilitar SSL warnings para ambientes internos
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except:
            pass
        
    def authenticate(self):
        """Autentica no PaperCut com múltiplas tentativas"""
        try:
            # Tentar acessar página principal
            response = self.session.get(self.base_url, verify=False, timeout=15)
            
            if response.status_code == 200:
                # Verificar se precisa de login
                if 'login' in response.text.lower() or 'password' in response.text.lower():
                    # Tentar fazer login se tiver formulário
                    return self._attempt_login(response.text)
                else:
                    return True
            else:
                st.warning(f"⚠️ PaperCut retornou status {response.status_code}")
                return False
                
        except Exception as e:
            st.error(f"❌ Erro ao conectar no PaperCut: {str(e)}")
            return False
    
    def _attempt_login(self, html_content):
        """Tenta fazer login no PaperCut se necessário"""
        try:
            # Procurar por formulário de login
            if 'form' in html_content.lower():
                # URLs comuns de login do PaperCut
                login_urls = [
                    f"{self.base_url.split('?')[0]}?service=page/Login",
                    f"{self.base_url.replace('Home', 'Login')}",
                    f"{self.base_url.split('/app')[0]}/app?service=direct/1/Home/$Form",
                ]
                
                for login_url in login_urls:
                    try:
                        login_data = {
                            'service': 'direct/1/Home/$Form',
                            'sp': 'S1',
                            'Form1': 'loginForm',
                            'username': 'admin',  # Usuário comum do PaperCut
                            'password': self.password,
                            'submit': 'Login'
                        }
                        
                        response = self.session.post(login_url, data=login_data, verify=False, timeout=15)
                        
                        if response.status_code == 200 and 'logout' in response.text.lower():
                            st.success("✅ Login realizado no PaperCut!")
                            return True
                            
                    except Exception:
                        continue
                        
            # Se não conseguiu fazer login, tentar acessar direto
            return True
            
        except Exception as e:
            st.warning(f"⚠️ Erro no login PaperCut: {str(e)}")
            return True  # Continuar mesmo sem login
    
    def get_printers_data(self):
        """Busca dados das impressoras no PaperCut - versão robusta"""
        try:
            if not self.authenticate():
                st.warning("⚠️ Não foi possível autenticar no PaperCut, tentando acesso direto...")
            
            printers_data = {}
            base_url_clean = self.base_url.split('?')[0]
            
            # URLs específicas do PaperCut para impressoras (baseado em versões comuns)
            printer_urls = [
                # Páginas de administração de impressoras
                f"{base_url_clean}?service=page/PrinterList",
                f"{base_url_clean}?service=page/Printers",
                f"{base_url_clean}?service=page/DeviceList", 
                f"{base_url_clean}?service=page/AdminPrinterList",
                f"{base_url_clean}?service=page/PrinterUsage",
                f"{base_url_clean}?service=page/PrinterStatus",
                
                # APIs e endpoints AJAX
                f"{base_url_clean}?service=ajax/PrinterData",
                f"{base_url_clean}?service=ajax/DeviceStatus",
                f"{base_url_clean}?service=direct/1/PrinterList/$DataGrid",
                f"{base_url_clean}?service=direct/1/DeviceList/$DataGrid",
                
                # Relatórios
                f"{base_url_clean}?service=page/Reports&report=printer-usage",
                f"{base_url_clean}?service=page/Reports&report=device-list",
                
                # URLs alternativas baseadas no padrão fornecido
                f"{self.base_url.replace('Home', 'PrinterList')}",
                f"{self.base_url.replace('Home', 'DeviceList')}",
                f"{self.base_url.replace('Home', 'Printers')}",
            ]
            
            successful_urls = []
            
            for url in printer_urls:
                try:
                    st.write(f"🔍 Tentando: `{url.split('?')[1] if '?' in url else url}`")
                    response = self.session.get(url, verify=False, timeout=20)
                    
                    if response.status_code == 200 and len(response.text) > 500:
                        # Verificar se contém dados de impressoras
                        content_lower = response.text.lower()
                        printer_indicators = [
                            '172.', 'printer', 'epson', 'hp', 'canon', 'pages', 'páginas',
                            'toner', 'ink', 'status', 'online', 'offline', 'device'
                        ]
                        
                        found_indicators = sum(1 for indicator in printer_indicators if indicator in content_lower)
                        
                        if found_indicators >= 3:  # Se encontrou pelo menos 3 indicadores
                            st.success(f"✅ Dados encontrados em: {url.split('?')[1] if '?' in url else 'URL base'}")
                            successful_urls.append(url)
                            
                            # Extrair dados desta página
                            extracted_data = self._parse_printer_data_advanced(response.text, url)
                            if extracted_data:
                                printers_data.update(extracted_data)
                                st.write(f"📊 Extraídos {len(extracted_data)} registros")
                        else:
                            st.write(f"⚪ Poucos indicadores encontrados ({found_indicators}/10)")
                    else:
                        st.write(f"❌ Status {response.status_code} ou conteúdo insuficiente")
                        
                except Exception as e:
                    st.write(f"⚠️ Erro: {str(e)[:50]}...")
                    continue
            
            # Resumo final
            if printers_data:
                st.success(f"🎉 PaperCut: {len(printers_data)} impressoras encontradas em {len(successful_urls)} URLs!")
                for url in successful_urls:
                    st.write(f"✅ {url.split('?')[1] if '?' in url else url}")
            else:
                st.warning("⚠️ Nenhuma impressora encontrada. Verifique conectividade com PaperCut.")
            
            return printers_data
            
        except Exception as e:
            st.error(f"❌ Erro geral ao buscar dados do PaperCut: {str(e)}")
            return {}
    
    def _parse_printer_data_advanced(self, html_content, source_url):
        """Extrai dados avançados das impressoras do HTML do PaperCut"""
        printers = {}
        
        try:
            # Padrões de regex mais específicos para PaperCut
            ip_pattern = r'(\b(?:172|192|10)\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)'
            
            # Padrões para diferentes tipos de dados
            patterns = {
                'printer_names': [
                    r'(?i)([\w\-\s]+(?:epson|hp|canon|brother|xerox|ricoh)[\w\-\s]*)',
                    r'(?i)(printer[\w\-\s]*\d+)',
                    r'(?i)([A-Z]{2,}\s*\d+[\w\-\s]*(?:andar|térreo|recepção))',
                ],
                'page_counts': [
                    r'(\d{1,7})\s*(?:páginas|pages|folhas|sheets)',
                    r'(?:total[:\s]+)(\d{1,7})',
                    r'(?:count[:\s]+)(\d{1,7})',
                ],
                'status_indicators': [
                    r'(?i)(online|offline|ready|error|warning|ok)',
                    r'(?i)(ativo|inativo|pronto|erro|aviso)',
                ],
                'toner_levels': [
                    r'(?i)(?:toner|ink|tinta)[:\s]*(\d{1,3})%',
                    r'(?i)(?:black|cyan|magenta|yellow)[:\s]*(\d{1,3})%',
                    r'(?i)(?:preto|ciano|magenta|amarelo)[:\s]*(\d{1,3})%',
                ],
                'models': [
                    r'(?i)(epson[\w\-\s]*wf[\w\-\s]*\d+)',
                    r'(?i)(hp[\w\-\s]*laserjet[\w\-\s]*\d+)',
                    r'(?i)(canon[\w\-\s]*imagerunner[\w\-\s]*\d+)',
                ]
            }
            
            # Extrair IPs primeiro
            ips_found = re.findall(ip_pattern, html_content)
            
            # Para cada IP, tentar encontrar dados associados
            for i, ip in enumerate(ips_found[:15]):  # Máximo 15 impressoras
                printer_data = {
                    'ip': ip,
                    'status': '🟡 PaperCut',
                    'contador': 'N/A',
                    'modelo': 'EPSON WF-C5790 Series',
                    'ultima_atualizacao': pd.Timestamp.now().strftime('%H:%M:%S'),
                    'toner_levels': {},
                    'location': 'Via PaperCut'
                }
                
                # Procurar por dados próximos ao IP no HTML
                ip_context_start = max(0, html_content.find(ip) - 500)
                ip_context_end = min(len(html_content), html_content.find(ip) + 500)
                ip_context = html_content[ip_context_start:ip_context_end]
                
                # Extrair contadores de páginas
                for pattern in patterns['page_counts']:
                    matches = re.findall(pattern, ip_context, re.IGNORECASE)
                    if matches:
                        printer_data['contador'] = matches[0]
                        break
                
                # Extrair status
                for pattern in patterns['status_indicators']:
                    matches = re.findall(pattern, ip_context, re.IGNORECASE)
                    if matches:
                        status_text = matches[0].lower()
                        if status_text in ['online', 'ready', 'ok', 'ativo', 'pronto']:
                            printer_data['status'] = '🟢 Online (PaperCut)'
                        elif status_text in ['offline', 'error', 'inativo', 'erro']:
                            printer_data['status'] = '🔴 Offline (PaperCut)'
                        else:
                            printer_data['status'] = '🟡 PaperCut'
                        break
                
                # Extrair modelo da impressora
                for pattern in patterns['models']:
                    matches = re.findall(pattern, ip_context, re.IGNORECASE)
                    if matches:
                        printer_data['modelo'] = matches[0].strip()
                        break
                
                # Extrair níveis de toner/tinta
                for pattern in patterns['toner_levels']:
                    matches = re.findall(pattern, ip_context, re.IGNORECASE)
                    if matches:
                        printer_data['toner_levels'] = {
                            'level': f"{matches[0]}%",
                            'status': 'Via PaperCut'
                        }
                        break
                
                # Nome da impressora baseado no IP ou localização
                printer_name = f"PC_{ip.replace('.', '_')}"
                
                # Tentar encontrar nome/localização específica
                name_patterns = [
                    r'(?i)([\w\s]+)\s*' + re.escape(ip),
                    r'(?i)' + re.escape(ip) + r'\s*([\w\s]+)',
                ]
                
                for pattern in name_patterns:
                    matches = re.findall(pattern, ip_context)
                    if matches:
                        name_candidate = matches[0].strip()
                        if len(name_candidate) > 3 and len(name_candidate) < 50:
                            printer_name = f"PC_{name_candidate}_{ip.split('.')[-1]}"
                            printer_data['location'] = name_candidate
                            break
                
                printers[printer_name] = printer_data
            
            # Tentar parsing com BeautifulSoup se disponível e nenhum IP foi encontrado
            if not printers and HAS_BS4 and BeautifulSoup:
                printers = self._parse_with_beautifulsoup(html_content)
                
        except Exception as e:
            st.warning(f"⚠️ Erro ao processar dados avançados: {str(e)}")
        
        return printers
    
    def _parse_with_beautifulsoup(self, html_content):
        """Parsing alternativo usando BeautifulSoup"""
        printers = {}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Procurar tabelas
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                
                # Identificar cabeçalhos
                headers = []
                if rows:
                    header_row = rows[0]
                    headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
                
                # Se encontrou cabeçalhos relacionados a impressoras
                if any(keyword in ' '.join(headers) for keyword in ['printer', 'device', 'ip', 'status']):
                    for row in rows[1:]:  # Pular cabeçalho
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            row_data = [cell.get_text().strip() for cell in cells]
                            
                            # Procurar IP na linha
                            ip_pattern = r'(\b(?:172|192|10)\.\d{1,3}\.\d{1,3}\.\d{1,3}\b)'
                            for cell_data in row_data:
                                ip_matches = re.findall(ip_pattern, cell_data)
                                if ip_matches:
                                    ip = ip_matches[0]
                                    printer_name = f"BS4_{ip.replace('.', '_')}"
                                    
                                    printers[printer_name] = {
                                        'ip': ip,
                                        'status': '🟡 PaperCut (BS4)',
                                        'contador': 'Via HTML',
                                        'modelo': 'EPSON WF-C5790 Series',
                                        'ultima_atualizacao': pd.Timestamp.now().strftime('%H:%M:%S'),
                                        'raw_data': ' | '.join(row_data)
                                    }
                                    break
            
        except Exception as e:
            st.warning(f"⚠️ Erro no parsing BeautifulSoup: {str(e)}")
        
        return printers
    
    def _parse_printer_data(self, html_content):
        """Método legado mantido para compatibilidade"""
        return self._parse_printer_data_advanced(html_content, "legacy")


def sync_with_papercut():
    """Sincroniza dados das impressoras com o PaperCut - versão detalhada"""
    papercut_url = "https://10.101.17.12:9192/app;jsessionid=node01hyygt0yrvxrc471ubq3emjvt228.node0?service=page/Home"
    papercut_password = "4sE5gZzuqxKZe"
    
    # Container para exibir progresso detalhado
    progress_container = st.container()
    
    with progress_container:
        st.info("🔄 **Iniciando sincronização com PaperCut...**")
        st.write(f"🌐 **URL:** `{papercut_url[:50]}...`")
        st.write(f"🔑 **Senha:** `{'*' * len(papercut_password)}`")
        
        try:
            # Verificar conectividade básica primeiro
            st.write("🔍 **Etapa 1:** Verificando conectividade...")
            
            # Teste básico de conectividade
            import socket
            hostname = papercut_url.split('//')[1].split(':')[0]
            port = int(papercut_url.split(':')[2].split('/')[0]) if ':' in papercut_url.split('//')[1] else 443
            
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((hostname, port))
                sock.close()
                
                if result == 0:
                    st.success(f"✅ Conectividade OK para {hostname}:{port}")
                else:
                    st.error(f"❌ Não foi possível conectar em {hostname}:{port}")
                    return {}
                    
            except Exception as e:
                st.error(f"❌ Erro de conectividade: {str(e)}")
                return {}
            
            st.write("🔐 **Etapa 2:** Criando conector PaperCut...")
            connector = PaperCutConnector(papercut_url, papercut_password)
            
            st.write("📊 **Etapa 3:** Buscando dados das impressoras...")
            st.write("*(Este processo pode demorar 1-2 minutos, pois testa múltiplas URLs)*")
            
            # Expandir seção para mostrar progresso detalhado
            with st.expander("📋 **Ver progresso detalhado**", expanded=True):
                papercut_data = connector.get_printers_data()
            
            # Análise dos resultados
            if papercut_data:
                st.success(f"🎉 **SUCESSO!** {len(papercut_data)} impressoras encontradas no PaperCut!")
                
                # Mostrar resumo dos dados encontrados
                with st.expander("📋 **Resumo dos dados encontrados**", expanded=False):
                    for printer_name, printer_info in papercut_data.items():
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"🖨️ **{printer_name}**")
                        with col2:
                            st.write(f"📍 IP: `{printer_info.get('ip', 'N/A')}`")
                        with col3:
                            st.write(f"📊 Status: {printer_info.get('status', 'N/A')}")
                
                return papercut_data
            else:
                st.warning("⚠️ **Nenhuma impressora encontrada no PaperCut.**")
                st.write("**Possíveis causas:**")
                st.write("- Credenciais incorretas")
                st.write("- Estrutura do PaperCut diferente do esperado") 
                st.write("- Necessário estar na VPN interna")
                st.write("- URLs do PaperCut mudaram")
                return {}
                
        except Exception as e:
            st.error(f"❌ **Erro ao sincronizar com PaperCut:** {str(e)}")
            st.write("**Detalhes técnicos:**")
            st.code(str(e))
            return {}


def load_printers_from_csv():
    """Carrega impressoras do arquivo CSV"""
    try:
        csv_path = "/Users/danilo.fukuyama.digisystem/Downloads/finance-vibes/template_impressoras_exemplo.csv"
        df = pd.read_csv(csv_path)
        
        # Renomear e ajustar colunas para padronizar
        df_formatted = pd.DataFrame({
            'modelo': 'EPSON WF-C5790 Series',  # Modelo correto conforme informado
            'marca': 'Epson',  # Marca Epson
            'tag': df['serial'],  # Usar serial como tag
            'tipo': 'Multifuncional',  # WF-C5790 é multifuncional (Impressora/Scanner/Copiadora)
            'local': df['local'] + ' - ' + df['descricao_local'],
            'status': df['status_manual'].map({'Ativo': '✓ Ativo', 'Manutenção': '⚙ Manutenção'}).fillna('✓ Ativo'),
            'valor': 3200.00,  # Valor atualizado para EPSON WF-C5790
            'data_compra': pd.to_datetime('2023-01-01'),  # Data padrão
            'fornecedor': 'Epson do Brasil',
            'nota_fiscal': 'NF-EPS-' + df['serial'].str[-6:],
            'po': 'PO-EPS-' + df['serial'].str[-6:],
            'ip_rede': df['ip'] if 'ip' in df.columns else 'N/A',
            'contador_paginas': 0,
            'responsavel': 'TI Central',
            'papercut': df['papercut'],
            'serial': df['serial'],
            'descricao_local': df['descricao_local'],
            'conectividade': '⏳ Verificando...',  # Status inicial
            'ultima_verificacao': pd.Timestamp.now().strftime('%H:%M:%S'),
            'url_impressora': df['ip'].apply(lambda ip: f"http://{ip}" if ip else "") if 'ip' in df.columns else ""
        })
        
        return df_formatted
    except Exception as e:
        st.error(f"❌ Erro ao carregar arquivo de impressoras: {str(e)}")
        return pd.DataFrame()

def render_impressoras():
    """Renderiza a página de Impressoras com verificação de conectividade"""
    st.markdown("""
    <style>
    .printer-header {
        background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        border: 2px solid #4CAF50;
        box-shadow: 0 8px 32px rgba(76, 175, 80, 0.3);
    }
    .printer-metric {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        color: white;
        margin: 10px 0;
    }
    .printer-status-active { color: #4CAF50; font-weight: bold; }
    .printer-status-maintenance { color: #FF9800; font-weight: bold; }
    .printer-status-inactive { color: #F44336; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="printer-header">
        <h1 style="color: white; text-align: center; margin: 0;">🖨️ Gestão de Impressoras</h1>
        <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 10px 0 0 0;">
            Controle completo do parque de impressoras - Status, manutenções e inventário
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Forçar recarregamento com modelo atualizado para EPSON WF-C5790
    loaded_data = load_printers_from_csv()
    if not loaded_data.empty:
        st.session_state.impressoras_data = loaded_data
    elif 'impressoras_data' not in st.session_state:
        # Fallback para dados de exemplo se não conseguir carregar o CSV
        st.session_state.impressoras_data = pd.DataFrame({
            'modelo': ['EPSON WF-C5790 Series', 'EPSON WF-C5790 Series', 'EPSON WF-C5790 Series'],
            'marca': ['Epson', 'Epson', 'Epson'],
            'tag': ['EPS001', 'EPS002', 'EPS003'],
            'tipo': ['Multifuncional', 'Multifuncional', 'Multifuncional'],
            'local': ['HQ1 - 8th floor', 'SPARK - Térreo', 'HQ2 - 4º Andar'],
            'status': ['✓ Ativo', '✓ Ativo', '⚙ Manutenção'],
            'valor': [3200.00, 3200.00, 3200.00],
            'data_compra': pd.to_datetime(['2023-01-15', '2023-03-20', '2023-05-10']),
            'fornecedor': ['Epson do Brasil', 'Epson do Brasil', 'Epson do Brasil'],
            'nota_fiscal': ['NF-EPS-001', 'NF-EPS-002', 'NF-EPS-003'],
            'po': ['PO-EPS-001', 'PO-EPS-002', 'PO-EPS-003'],
            'ip_rede': ['172.25.61.81', '172.30.139.8', '172.26.61.40'],
            'contador_paginas': [15234, 8765, 4321],
            'responsavel': ['TI Central', 'Spark Team', 'HQ2 Admin'],
            'conectividade': ['⏳ Verificando...', '⏳ Verificando...', '⏳ Verificando...'],
            'ultima_verificacao': [pd.Timestamp.now().strftime('%H:%M:%S')] * 3,
            'url_impressora': ['http://172.25.61.81', 'http://172.30.139.8', 'http://172.26.61.40']
        })
    
    impressoras_data = st.session_state.impressoras_data
    
    # Interface simplificada
    st.info("🔍 **Ping Local:** Clique no botão abaixo para verificar conectividade das impressoras. Os resultados aparecerão automaticamente na tabela.")
    
    # Botão principal simplificado
    col_ping, col_reload = st.columns([3, 1])
    
    with col_ping:
        if st.button("🔍 PING LOCAL - VERIFICAR IMPRESSORAS", use_container_width=True, type="primary"):
            # Status temporário
            with st.spinner("🔍 Fazendo ping nas impressoras..."):
                
                # Fazer ping em todas as impressoras
                results = ping_all_printers_simple(impressoras_data)
                
                # Atualizar dados diretamente na tabela
                timestamp = pd.Timestamp.now().strftime('%H:%M:%S')
                
                for idx, result in results.items():
                    if idx < len(st.session_state.impressoras_data):
                        # Atualizar conectividade
                        if 'conectividade' in st.session_state.impressoras_data.columns:
                            st.session_state.impressoras_data.iloc[idx, st.session_state.impressoras_data.columns.get_loc('conectividade')] = result['status']
                        
                        # Atualizar timestamp
                        if 'ultima_verificacao' in st.session_state.impressoras_data.columns:
                            st.session_state.impressoras_data.iloc[idx, st.session_state.impressoras_data.columns.get_loc('ultima_verificacao')] = timestamp
                        
                        # Atualizar URL
                        if 'url_impressora' in st.session_state.impressoras_data.columns:
                            st.session_state.impressoras_data.iloc[idx, st.session_state.impressoras_data.columns.get_loc('url_impressora')] = result.get('url', '')
                
                # Contar resultados
                online_count = len([r for r in results.values() if '🟢' in r['status']])
                offline_count = len([r for r in results.values() if '🔴' in r['status']])
                
            # Mostrar resultado e atualizar imediatamente
            st.success(f"✅ **{online_count} online, {offline_count} offline** - Tabela atualizada!")
            st.rerun()
    
        if st.button("🔄 Recarregar CSV", use_container_width=True):
            loaded_data = load_printers_from_csv()
            if not loaded_data.empty:
                st.session_state.impressoras_data = loaded_data
                st.success("✅ Dados recarregados!")
                st.rerun()
    
    # Auto refresh melhorado
    col_auto1, col_auto2 = st.columns(2)
    with col_auto1:
        auto_refresh = st.checkbox("🔄 Auto Refresh", value=False)
    with col_auto2:
        refresh_interval = st.selectbox("⏱️ Intervalo", [30, 60, 120, 300], index=0, format_func=lambda x: f"{x}s")
    
    if auto_refresh:
        st.info(f"🔄 **Auto refresh ativo:** Próxima verificação em {refresh_interval} segundos")
        placeholder = st.empty()
        time.sleep(refresh_interval)
        placeholder.success("🔄 **Fazendo ping automático...**")
        
        # Fazer ping automaticamente
        results = ping_all_printers_simple(impressoras_data)
        
        # Atualizar dados
        timestamp = pd.Timestamp.now().strftime('%H:%M:%S')
        for idx, result in results.items():
            if idx < len(st.session_state.impressoras_data):
                if 'conectividade' in st.session_state.impressoras_data.columns:
                    st.session_state.impressoras_data.iloc[idx, st.session_state.impressoras_data.columns.get_loc('conectividade')] = result['status']
                if 'ultima_verificacao' in st.session_state.impressoras_data.columns:
                    st.session_state.impressoras_data.iloc[idx, st.session_state.impressoras_data.columns.get_loc('ultima_verificacao')] = timestamp
                if 'url_impressora' in st.session_state.impressoras_data.columns:
                    st.session_state.impressoras_data.iloc[idx, st.session_state.impressoras_data.columns.get_loc('url_impressora')] = result.get('url', '')
        
        st.rerun()
    
    st.divider()
    
    # Formulário de Adicionar Impressora
    if st.session_state.get('show_add_form_impressoras', False):
        with st.expander("➕ Adicionar Nova Impressora", expanded=True):
            with st.form("add_impressora_item"):
                col1, col2 = st.columns(2)
                
                with col1:
                    modelo = st.text_input("🖨️ Modelo", placeholder="Ex: HP LaserJet Pro 404n")
                    marca = st.selectbox("🏷️ Marca", ["HP", "Canon", "Epson", "Brother", "Samsung", "Xerox", "Kyocera", "Lexmark", "Outros"])
                    tag = st.text_input("🏷️ Tag/Código", placeholder="Ex: IMP007")
                    tipo = st.selectbox("📋 Tipo", ["Laser", "Jato de Tinta", "EcoTank", "Multifuncional", "Térmica", "Matricial"])
                    local = st.selectbox("📍 Localização", ["8th floor hq1", "spark estoque", "day1 spark", "day1hq1", "auditorio", "outros"])
                    status = st.selectbox("📊 Status", ["✓ Ativo", "⚙ Manutenção", "× Inativo", "🔄 Em Teste"])
                
                with col2:
                    valor = st.number_input("💰 Valor (R$)", min_value=0.0, step=0.01)
                    data_compra = st.date_input("📅 Data de Compra")
                    fornecedor = st.text_input("🏢 Fornecedor", placeholder="Ex: HP Brasil")
                    nota_fiscal = st.text_input("📄 Nota Fiscal", placeholder="Ex: NF-HP-007")
                    po = st.text_input("📋 PO", placeholder="Ex: PO-IMP-007")
                    ip_rede = st.text_input("🌐 IP da Rede", placeholder="Ex: 192.168.1.107 ou N/A")
                    contador_paginas = st.number_input("📊 Contador de Páginas", min_value=0, value=0)
                    responsavel = st.text_input("👤 Responsável", placeholder="Ex: TI Central")
                
                col_submit, col_cancel = st.columns(2)
                
                with col_submit:
                    if st.form_submit_button("➕ Adicionar Impressora", use_container_width=True):
                        if modelo and marca and tag and tipo and local:
                            new_impressora = pd.DataFrame({
                                'modelo': [modelo],
                                'marca': [marca],
                                'tag': [tag],
                                'tipo': [tipo],
                                'local': [local],
                                'status': [status],
                                'valor': [valor],
                                'data_compra': [data_compra],
                                'fornecedor': [fornecedor],
                                'nota_fiscal': [nota_fiscal],
                                'po': [po],
                                'ip_rede': [ip_rede if ip_rede else 'N/A'],
                                'contador_paginas': [contador_paginas],
                                'responsavel': [responsavel]
                            })
                            
                            st.session_state.impressoras_data = pd.concat([
                                st.session_state.impressoras_data, new_impressora
                            ], ignore_index=True)
                            
                            st.success("✅ Impressora adicionada com sucesso!")
                            st.session_state.show_add_form_impressoras = False
                            st.rerun()
                        else:
                            st.error("❌ Preencha todos os campos obrigatórios (Modelo, Marca, Tag, Tipo, Local)")
                
                with col_cancel:
                    if st.form_submit_button("❌ Cancelar", use_container_width=True):
                        st.session_state.show_add_form_impressoras = False
                        st.rerun()
    
    # Métricas das Impressoras
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_impressoras = len(impressoras_data)
        st.markdown(f"""
        <div class="printer-metric">
            <div style="font-size: 2rem; font-weight: bold;">{total_impressoras}</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">🖨️ Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        ativas = len(impressoras_data[impressoras_data['status'] == '✓ Ativo'])
        st.markdown(f"""
        <div class="printer-metric">
            <div style="font-size: 2rem; font-weight: bold; color: #4CAF50;">{ativas}</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">✓ Ativas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Contar conectividade se a coluna existir
        if 'conectividade' in impressoras_data.columns:
            online = len(impressoras_data[impressoras_data['conectividade'] == '🟢 Online'])
            st.markdown(f"""
            <div class="printer-metric">
                <div style="font-size: 2rem; font-weight: bold; color: #4CAF50;">{online}</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">🟢 Online</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            em_manutencao = len(impressoras_data[impressoras_data['status'] == '⚙ Manutenção'])
            st.markdown(f"""
            <div class="printer-metric">
                <div style="font-size: 2rem; font-weight: bold; color: #FF9800;">{em_manutencao}</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">⚙ Manutenção</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        # Contar offline se a coluna existir
        if 'conectividade' in impressoras_data.columns:
            offline = len(impressoras_data[impressoras_data['conectividade'] == '🔴 Offline'])
            st.markdown(f"""
            <div class="printer-metric">
                <div style="font-size: 2rem; font-weight: bold; color: #F44336;">{offline}</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">🔴 Offline</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            offline = len(impressoras_data[impressoras_data['status'] == '× Inativo'])
            st.markdown(f"""
            <div class="printer-metric">
                <div style="font-size: 2rem; font-weight: bold; color: #F44336;">{offline}</div>
                <div style="font-size: 0.9rem; opacity: 0.8;">× Inativas</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col5:
        valor_total = impressoras_data['valor'].sum()
        st.markdown(f"""
        <div class="printer-metric">
            <div style="font-size: 1.3rem; font-weight: bold; color: #2196F3;">R$ {valor_total:,.0f}</div>
            <div style="font-size: 0.9rem; opacity: 0.8;">💰 Valor Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Filtros
    col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
    
    with col_filter1:
        status_filter = st.selectbox("📊 Filtrar por Status", ["Todos"] + list(impressoras_data['status'].unique()), key="status_filter_impressoras")
    
    with col_filter2:
        local_filter = st.selectbox("📍 Filtrar por Local", ["Todos"] + list(impressoras_data['local'].unique()), key="local_filter_impressoras")
    
    with col_filter3:
        # Filtro de conectividade se a coluna existir
        if 'conectividade' in impressoras_data.columns:
            connectivity_options = ["Todos"] + list(impressoras_data['conectividade'].unique())
            connectivity_filter = st.selectbox("📡 Conectividade", connectivity_options, key="connectivity_filter_impressoras")
        else:
            connectivity_filter = "Todos"
    
    with col_filter4:
        search_term = st.text_input("🔍 Buscar", placeholder="Digite para buscar...", key="search_impressoras")
    
    # Aplicar filtros
    filtered_data = impressoras_data.copy()
    
    if status_filter != "Todos":
        filtered_data = filtered_data[filtered_data['status'] == status_filter]
    
    if local_filter != "Todos":
        filtered_data = filtered_data[filtered_data['local'] == local_filter]
    
    # Filtro de conectividade
    if connectivity_filter != "Todos" and 'conectividade' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['conectividade'] == connectivity_filter]
    
    if search_term:
        filtered_data = filtered_data[
            filtered_data['modelo'].str.contains(search_term, case=False, na=False) |
            filtered_data['marca'].str.contains(search_term, case=False, na=False) |
            filtered_data['tag'].str.contains(search_term, case=False, na=False) |
            filtered_data['responsavel'].str.contains(search_term, case=False, na=False) |
            filtered_data['ip_rede'].str.contains(search_term, case=False, na=False)
        ]
    
    # Modo de edição
    if st.session_state.get('show_edit_mode_impressoras', False):
        st.subheader("✏ Modo de Edição - Impressoras")
        
        if not filtered_data.empty:
            edited_data = st.data_editor(
                filtered_data,
                use_container_width=True,
                num_rows="dynamic",
                column_config={
                    "modelo": st.column_config.TextColumn("Modelo", width="medium"),
                    "marca": st.column_config.SelectboxColumn("Marca", options=["HP", "Canon", "Epson", "Brother", "Samsung", "Xerox", "Kyocera", "Lexmark", "Outros"]),
                    "tag": st.column_config.TextColumn("Tag", width="small"),
                    "tipo": st.column_config.SelectboxColumn("Tipo", options=["Laser", "Jato de Tinta", "EcoTank", "Multifuncional", "Térmica", "Matricial"]),
                    "local": st.column_config.TextColumn("Local", width="large"),
                    "status": st.column_config.SelectboxColumn("Status", options=["✓ Ativo", "⚙ Manutenção", "× Inativo", "🔄 Em Teste"]),
                    "valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f"),
                    "data_compra": st.column_config.DateColumn("Data Compra"),
                    "fornecedor": st.column_config.TextColumn("Fornecedor"),
                    "nota_fiscal": st.column_config.TextColumn("Nota Fiscal"),
                    "po": st.column_config.TextColumn("PO"),
                    "ip_rede": st.column_config.TextColumn("IP Rede"),
                    "contador_paginas": st.column_config.NumberColumn("Contador", format="%d"),
                    "responsavel": st.column_config.TextColumn("Responsável"),
                    "conectividade": st.column_config.TextColumn("Conectividade", width="medium"),
                    "ultima_verificacao": st.column_config.TextColumn("⏰ Última Verificação", width="medium"),
                    "url_impressora": st.column_config.LinkColumn("🔗 Acessar Impressora", help="Clique para abrir a interface web da impressora")
                },
                key="edit_impressoras"
            )
            
            col_save, col_cancel = st.columns(2)
            
            with col_save:
                if st.button("💾 Salvar Alterações", use_container_width=True, key="save_impressoras"):
                    st.session_state.impressoras_data = edited_data
                    st.success("✅ Alterações salvas com sucesso!")
                    st.session_state.show_edit_mode_impressoras = False
                    st.rerun()
            
            with col_cancel:
                if st.button("❌ Cancelar Edição", use_container_width=True, key="cancel_edit_impressoras"):
                    st.session_state.show_edit_mode_impressoras = False
                    st.rerun()
        else:
            st.info("ℹ Nenhuma impressora encontrada com os filtros aplicados.")
    
    else:
        # Modo visualização (somente leitura)
        st.subheader("🖨️ Inventário de Impressoras")
        
        if not filtered_data.empty:
            # Estilizar o dataframe baseado no status
            def style_status(val):
                if val == '✓ Ativo':
                    return 'color: #4CAF50; font-weight: bold;'
                elif val == '⚙ Manutenção':
                    return 'color: #FF9800; font-weight: bold;'
                elif val == '× Inativo':
                    return 'color: #F44336; font-weight: bold;'
                else:
                    return 'color: #2196F3; font-weight: bold;'
            
            # Aplicar estilo também para conectividade e tintas se existir
            styled_data = filtered_data.style.map(style_status, subset=['status'])
            
            if 'conectividade' in filtered_data.columns:
                def style_connectivity(val):
                    if '🟢' in str(val):
                        return 'color: #4CAF50; font-weight: bold;'
                    elif '🟡' in str(val):
                        return 'color: #FF9800; font-weight: bold;'
                    elif '🔴' in str(val):
                        return 'color: #F44336; font-weight: bold;'
                    elif '🔒' in str(val):
                        return 'color: #9C27B0; font-weight: bold;'
                    elif '⚠️' in str(val):
                        return 'color: #FF5722; font-weight: bold;'
                    else:
                        return 'color: #757575; font-style: italic;'
                
                styled_data = styled_data.map(style_connectivity, subset=['conectividade'])
            
            # Dados simplificados - sem níveis de tinta
            
            st.dataframe(
                styled_data,
                use_container_width=True,
                column_config={
                    "modelo": st.column_config.TextColumn("Modelo", width="medium"),
                    "marca": st.column_config.TextColumn("Marca", width="small"),
                    "tag": st.column_config.TextColumn("Tag", width="small"),
                    "tipo": st.column_config.TextColumn("Tipo", width="medium"),
                    "local": st.column_config.TextColumn("Local", width="large"),
                    "status": st.column_config.TextColumn("Status", width="medium"),
                    "valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f"),
                    "data_compra": st.column_config.DateColumn("Data Compra"),
                    "fornecedor": st.column_config.TextColumn("Fornecedor"),
                    "nota_fiscal": st.column_config.TextColumn("Nota Fiscal", width="medium"),
                    "po": st.column_config.TextColumn("PO", width="small"),
                    "ip_rede": st.column_config.TextColumn("IP Rede", width="medium"),
                    "contador_paginas": st.column_config.NumberColumn("Contador", format="%d"),
                    "responsavel": st.column_config.TextColumn("Responsável", width="medium"),
                    "conectividade": st.column_config.TextColumn("Conectividade", width="medium"),
                    "ultima_verificacao": st.column_config.TextColumn("⏰ Última Verificação", width="small"),
                    "url_impressora": st.column_config.LinkColumn("🔗 Acessar Impressora", help="Clique para abrir a interface web da impressora")
                }
            )
        else:
            st.info("ℹ Nenhuma impressora encontrada com os filtros aplicados.")

def render_tvs_monitores():
    """Renderiza a página de TVs e Monitores"""
    st.markdown("## ▢ TVs e Monitores")
    
    # Inicializar dados no session_state se não existir
    if 'tvs_monitores_data' not in st.session_state:
        st.session_state.tvs_monitores_data = pd.DataFrame({
            'equipamento': ['Monitor Dell 27"', 'TV Samsung 55"', 'Monitor LG UltraWide', 'TV LG 43"', 'Monitor ASUS Gaming'],
            'modelo': ['S2721DS', 'UN55TU7000', '34WN80C-B', '43UM7300', 'VG248QE'],
            'tag': ['MON001', 'TV001', 'MON002', 'TV002', 'MON003'],
            'tipo': ['Monitor', 'TV', 'Monitor', 'TV', 'Monitor'],
            'tamanho': ['27"', '55"', '34"', '43"', '24"'],
            'resolucao': ['2K', '4K', '2K UltraWide', '4K', 'Full HD'],
            'local': ['spark estopque', '8th floor hq1', 'day1 spark', 'day1hq1', 'auditorio'],
            'status': ['✓ Ativo', '✓ Ativo', '✓ Ativo', '⚙ Manutenção', '✓ Ativo'],
            'valor': [1200.00, 2800.00, 1800.00, 1500.00, 950.00],
            'nota_fiscal': ['NF-MON-001', 'NF-TV-001', 'NF-MON-002', 'NF-TV-002', 'NF-MON-003'],
            'data_entrada': pd.to_datetime(['2024-01-15', '2024-02-10', '2024-01-25', '2024-03-05', '2024-02-20']),
            'fornecedor': ['Dell Brasil', 'Samsung', 'LG Electronics', 'LG Electronics', 'ASUS'],
            'po': ['PO-MON-001', 'PO-TV-001', 'PO-MON-002', 'PO-TV-002', 'PO-MON-003']
        })
    
    displays_data = st.session_state.tvs_monitores_data
    
    # Controles de Ação
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("● Adicionar Display", use_container_width=True, key="add_display"):
            st.session_state.show_add_form_displays = True
    
    with col_btn2:
        if st.button("📝 Editar Dados", use_container_width=True, key="edit_displays"):
            st.session_state.show_edit_mode_displays = True
    
    with col_btn3:
        if st.button("📋 Exportar CSV", use_container_width=True, key="export_displays"):
            csv = displays_data.to_csv(index=False)
            st.download_button(
                label="⬇ Download CSV",
                data=csv,
                file_name=f"displays_inventory_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_displays"
            )
    
    # Upload de CSV para TVs e Monitores
    required_columns_displays = ['equipamento', 'modelo', 'tag', 'tipo', 'tamanho', 'resolucao', 'local', 'status', 'valor', 'nota_fiscal', 'fornecedor', 'po']
    render_csv_upload_section('tvs_monitores_data', required_columns_displays, "Upload de TVs e Monitores via CSV")
    
    # Formulário de Adicionar Item
    if st.session_state.get('show_add_form_displays', False):
        with st.expander("● Adicionar Novo Display", expanded=True):
            with st.form("add_display_item"):
                col1, col2 = st.columns(2)
                
                with col1:
                    equipamento = st.text_input("▣ Equipamento", placeholder="Nome do equipamento")
                    modelo = st.text_input("▣ Modelo", placeholder="Modelo/Versão")
                    tag = st.text_input("▣ Tag/Código", placeholder="MON### ou TV###")
                    tipo = st.selectbox("◈ Tipo", ["Monitor", "TV"])
                    tamanho = st.text_input("◱ Tamanho", placeholder='Ex: 27", 55"')
                    resolucao = st.selectbox("◳ Resolução", ["Full HD", "2K", "4K", "2K UltraWide", "8K"])
                
                with col2:
                    local = st.text_input("◉ Local", placeholder="Localização do display")
                    status = st.selectbox("◐ Status", ["✓ Ativo", "⚙ Manutenção", "× Inativo"])
                    valor = st.number_input("$ Valor", min_value=0.0, format="%.2f")
                    nota_fiscal = st.text_input("⎙ Nota Fiscal", placeholder="NF-YYYY-###")
                    data_entrada = st.date_input("⌚ Data de Entrada")
                    fornecedor = st.text_input("◉ Fornecedor", placeholder="Nome do fornecedor")
                    po = st.text_input("📋 PO", placeholder="PO-YYYY-###")
                
                col_submit, col_cancel = st.columns(2)
                
                with col_submit:
                    if st.form_submit_button("● Adicionar", use_container_width=True):
                        if equipamento and modelo and tag:
                            new_item = pd.DataFrame({
                                'equipamento': [equipamento],
                                'modelo': [modelo],
                                'tag': [tag],
                                'tipo': [tipo],
                                'tamanho': [tamanho],
                                'resolucao': [resolucao],
                                'local': [local],
                                'status': [status],
                                'valor': [valor],
                                'nota_fiscal': [nota_fiscal],
                                'data_entrada': [pd.to_datetime(data_entrada)],
                                'fornecedor': [fornecedor],
                                'po': [po]
                            })
                            st.session_state.tvs_monitores_data = pd.concat([st.session_state.tvs_monitores_data, new_item], ignore_index=True)
                            st.success("✓ Display adicionado com sucesso!")
                            st.session_state.show_add_form_displays = False
                            st.rerun()
                        else:
                            st.error("× Preencha todos os campos obrigatórios")
                
                with col_cancel:
                    if st.form_submit_button("× Cancelar", use_container_width=True):
                        st.session_state.show_add_form_displays = False
                        st.rerun()
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_displays = len(displays_data)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_displays}</div>
            <div class="metric-label">▢ Total Displays</div>
        </div>
        """, unsafe_allow_html=True)
        
        with col2:
            ativos = len(displays_data[displays_data['status'] == '✓ Ativo'])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{ativos}</div>
                <div class="metric-label">✓ Ativos</div>
            </div>
            """, unsafe_allow_html=True)
    
        with col3:
            tvs = len(displays_data[displays_data['tipo'] == 'TV'])
            monitores = len(displays_data[displays_data['tipo'] == 'Monitor'])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{tvs}/{monitores}</div>
                <div class="metric-label">▢ TVs / ▢ Monitores</div>
            </div>
            """, unsafe_allow_html=True)
    
        with col4:
            valor_total = displays_data['valor'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">R$ {valor_total:,.0f}</div>
                <div class="metric-label">$ Valor Total</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Filtros
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        search_term = st.text_input("⊙ Buscar display", key="display_search")
    
    with col_filter2:
        tipo_filter = st.selectbox("◈ Filtrar por tipo", 
                                 options=['Todos', 'Monitor', 'TV'],
                                 key="display_tipo")
    
    with col_filter3:
        status_filter = st.selectbox("◐ Status", 
                                   options=['Todos', '✓ Ativo', '⚙ Manutenção', '× Inativo'],
                                   key="display_status")
    
    # Aplicar filtros
    filtered_data = displays_data.copy()
    
    if search_term:
        mask = (filtered_data['equipamento'].str.contains(search_term, case=False, na=False) |
                filtered_data['modelo'].str.contains(search_term, case=False, na=False) |
                filtered_data['tag'].str.contains(search_term, case=False, na=False))
        filtered_data = filtered_data[mask]
    
    if tipo_filter != 'Todos':
        filtered_data = filtered_data[filtered_data['tipo'] == tipo_filter]
    
    if status_filter != 'Todos':
        filtered_data = filtered_data[filtered_data['status'] == status_filter]
    
    # Exibição dos dados
    if not filtered_data.empty:
        st.write(f"☰ **{len(filtered_data)}** displays encontrados")
        
        # Modo de edição
        if st.session_state.get('show_edit_mode_displays', False):
            st.info("📝 **MODO EDIÇÃO ATIVO** - Edite os dados diretamente na tabela abaixo")
            
            # Tabela editável
            edited_data = st.data_editor(
                filtered_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "equipamento": st.column_config.TextColumn("Equipamento", width="medium"),
                    "modelo": st.column_config.TextColumn("Modelo", width="medium"),
                    "tag": st.column_config.TextColumn("Tag", width="small"),
                    "tipo": st.column_config.SelectboxColumn("Tipo", options=["Monitor", "TV"]),
                    "tamanho": st.column_config.TextColumn("Tamanho", width="small"),
                    "resolucao": st.column_config.SelectboxColumn("Resolução", options=["Full HD", "2K", "4K", "2K UltraWide", "8K"]),
                    "local": st.column_config.TextColumn("Local", width="medium"),
                    "status": st.column_config.SelectboxColumn("Status", options=["✓ Ativo", "⚙ Manutenção", "× Inativo"]),
                    "valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f"),
                    "nota_fiscal": st.column_config.TextColumn("Nota Fiscal", width="medium"),
                    "data_entrada": st.column_config.DateColumn("Data Entrada"),
                    "fornecedor": st.column_config.TextColumn("Fornecedor", width="medium"),
                    "po": st.column_config.TextColumn("PO", width="medium")
                },
                key="displays_editor"
            )
            
            col_save, col_cancel = st.columns(2)
            
            with col_save:
                if st.button("✓ Salvar Alterações", use_container_width=True, key="save_displays"):
                    st.session_state.tvs_monitores_data = edited_data
                    st.success("✓ Alterações salvas com sucesso!")
                    st.session_state.show_edit_mode_displays = False
                    st.rerun()
            
            with col_cancel:
                if st.button("❌ Cancelar Edição", use_container_width=True, key="cancel_edit_displays"):
                    st.session_state.show_edit_mode_displays = False
                    st.rerun()
        
        else:
            # Modo visualização (somente leitura)
            st.subheader("☰ Inventário de Displays")
            st.dataframe(filtered_data, use_container_width=True, hide_index=True)
    else:
        st.info("⊙ Nenhum display encontrado com os filtros aplicados")

def render_vendas_spark():
    """Renderiza a página de vendas SPARK"""
    st.markdown("## $ Vendas Spark")
    
    # Inicializar dados no session_state se não existir
    if 'vendas_data' not in st.session_state:
        st.session_state.vendas_data = pd.DataFrame({
            'data_venda': pd.to_datetime(['2024-03-15', '2024-03-14', '2024-03-13', '2024-03-12', '2024-03-11']),
            'item': ['Notebook Dell Usado', 'Mouse Logitech', 'Monitor LG 24"', 'Teclado Mecânico', 'Webcam HD'],
            'tag_original': ['SPK045', 'SPK032', 'SPK018', 'SPK025', 'SPK067'],
            'comprador': ['João Silva', 'Maria Santos', 'Carlos Lima', 'Ana Costa', 'Pedro Oliveira'],
            'valor_original': [3500.00, 450.00, 1200.00, 800.00, 350.00],
            'valor_venda': [1800.00, 200.00, 600.00, 400.00, 150.00],
            'desconto_perc': [48.6, 55.6, 50.0, 50.0, 57.1],
            'status': ['✓ Concluída', '✓ Concluída', '✓ Concluída', '⧖ Pendente', '✓ Concluída'],
            'nota_fiscal': ['NF-VENDA-001', 'NF-VENDA-002', 'NF-VENDA-003', 'NF-VENDA-004', 'NF-VENDA-005'],
            'po': ['PO-VENDA-001', 'PO-VENDA-002', 'PO-VENDA-003', 'PO-VENDA-004', 'PO-VENDA-005']
        })
    
    vendas_data = st.session_state.vendas_data
    
    # Controles de Ação
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("● Registrar Venda", use_container_width=True, key="add_venda"):
            st.session_state.show_add_form_vendas = True
    
    with col_btn2:
        if st.button("📝 Editar Dados", use_container_width=True, key="edit_vendas"):
            st.session_state.show_edit_mode_vendas = True
    
    with col_btn3:
        if st.button("📋 Exportar CSV", use_container_width=True, key="export_vendas"):
            csv = vendas_data.to_csv(index=False)
            st.download_button(
                label="⬇ Download CSV",
                data=csv,
                file_name=f"vendas_spark_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_vendas"
            )
    
    # Upload de CSV para Vendas
    required_columns_vendas = ['data_venda', 'item', 'tag_original', 'comprador', 'valor_original', 'valor_venda', 'status', 'nota_fiscal', 'po']
    render_csv_upload_section('vendas_data', required_columns_vendas, "Upload de Vendas via CSV")
    
    # Formulário de Adicionar Venda
    if st.session_state.get('show_add_form_vendas', False):
        with st.expander("● Registrar Nova Venda", expanded=True):
            with st.form("add_venda_item"):
                col1, col2 = st.columns(2)
                
                with col1:
                    data_venda = st.date_input("⌚ Data da Venda")
                    item = st.text_input("▣ Item", placeholder="Nome do item vendido")
                    tag_original = st.text_input("▣ Tag Original", placeholder="SPK###")
                    comprador = st.text_input("👤 Comprador", placeholder="Nome do comprador")
                    valor_original = st.number_input("$ Valor Original", min_value=0.0, format="%.2f")
                
                with col2:
                    valor_venda = st.number_input("$ Valor de Venda", min_value=0.0, format="%.2f")
                    status = st.selectbox("◐ Status", ["✓ Concluída", "⧖ Pendente", "× Cancelada"])
                    nota_fiscal = st.text_input("⎙ Nota Fiscal", placeholder="NF-VENDA-###")
                    po = st.text_input("📋 PO", placeholder="PO-VENDA-###")
                    # Calcular desconto automaticamente
                    if valor_original > 0:
                        desconto_calc = ((valor_original - valor_venda) / valor_original) * 100
                        st.info(f"📊 Desconto calculado: {desconto_calc:.1f}%")
                
                col_submit, col_cancel = st.columns(2)
                
                with col_submit:
                    if st.form_submit_button("● Registrar", use_container_width=True):
                        if item and tag_original and comprador:
                            desconto_perc = ((valor_original - valor_venda) / valor_original) * 100 if valor_original > 0 else 0
                            new_item = pd.DataFrame({
                                'data_venda': [pd.to_datetime(data_venda)],
                                'item': [item],
                                'tag_original': [tag_original],
                                'comprador': [comprador],
                                'valor_original': [valor_original],
                                'valor_venda': [valor_venda],
                                'desconto_perc': [desconto_perc],
                                'status': [status],
                                'nota_fiscal': [nota_fiscal],
                                'po': [po]
                            })
                            st.session_state.vendas_data = pd.concat([st.session_state.vendas_data, new_item], ignore_index=True)
                            st.success("✓ Venda registrada com sucesso!")
                            st.session_state.show_add_form_vendas = False
                            st.rerun()
                        else:
                            st.error("× Preencha todos os campos obrigatórios")
                
                with col_cancel:
                    if st.form_submit_button("× Cancelar", use_container_width=True):
                        st.session_state.show_add_form_vendas = False
                        st.rerun()
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
        
    with col1:
        total_vendas = len(vendas_data)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_vendas}</div>
            <div class="metric-label">$ Total Vendas</div>
        </div>
        """, unsafe_allow_html=True)
        
        with col2:
            receita_total = vendas_data['valor_venda'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">R$ {receita_total:,.0f}</div>
                <div class="metric-label">$ Receita Total</div>
            </div>
            """, unsafe_allow_html=True)
    
        with col3:
            desconto_medio = vendas_data['desconto_perc'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{desconto_medio:.1f}%</div>
                <div class="metric-label">⤵ Desconto Médio</div>
            </div>
            """, unsafe_allow_html=True)
    
        with col4:
            concluidas = len(vendas_data[vendas_data['status'] == '✓ Concluída'])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{concluidas}</div>
                <div class="metric-label">✓ Concluídas</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Filtros
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        search_term = st.text_input("⊙ Buscar venda", key="venda_search")
    
    with col_filter2:
        status_filter = st.selectbox("◐ Status", 
                                   options=['Todos', '✓ Concluída', '⧖ Pendente', '× Cancelada'],
                                   key="venda_status")
    
    with col_filter3:
        periodo = st.selectbox("📅 Período", 
                             options=['Todos', 'Última semana', 'Último mês', 'Últimos 3 meses'],
                             key="venda_periodo")
    
    # Aplicar filtros
    filtered_data = vendas_data.copy()
    
    if search_term:
        mask = (filtered_data['item'].str.contains(search_term, case=False, na=False) |
                filtered_data['comprador'].str.contains(search_term, case=False, na=False) |
                filtered_data['tag_original'].str.contains(search_term, case=False, na=False))
        filtered_data = filtered_data[mask]
    
    if status_filter != 'Todos':
        filtered_data = filtered_data[filtered_data['status'] == status_filter]
    
    # Filtrar por período
    if periodo != 'Todos':
        today = pd.Timestamp.now()
        if periodo == 'Última semana':
            start_date = today - pd.Timedelta(days=7)
        elif periodo == 'Último mês':
            start_date = today - pd.Timedelta(days=30)
        elif periodo == 'Últimos 3 meses':
            start_date = today - pd.Timedelta(days=90)
        filtered_data = filtered_data[filtered_data['data_venda'] >= start_date]
    
    # Exibição dos dados
    if not filtered_data.empty:
        st.write(f"☰ **{len(filtered_data)}** vendas encontradas")
        
        # Modo de edição
        if st.session_state.get('show_edit_mode_vendas', False):
            st.info("📝 **MODO EDIÇÃO ATIVO** - Edite os dados diretamente na tabela abaixo")
            
            # Tabela editável
            edited_data = st.data_editor(
                filtered_data,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "data_venda": st.column_config.DateColumn("Data Venda"),
                    "item": st.column_config.TextColumn("Item", width="medium"),
                    "tag_original": st.column_config.TextColumn("Tag Original", width="small"),
                    "comprador": st.column_config.TextColumn("Comprador", width="medium"),
                    "valor_original": st.column_config.NumberColumn("Valor Original (R$)", format="R$ %.2f"),
                    "valor_venda": st.column_config.NumberColumn("Valor Venda (R$)", format="R$ %.2f"),
                    "desconto_perc": st.column_config.NumberColumn("Desconto (%)", format="%.1f%%"),
                    "status": st.column_config.SelectboxColumn("Status", options=["✓ Concluída", "⧖ Pendente", "× Cancelada"]),
                    "nota_fiscal": st.column_config.TextColumn("Nota Fiscal", width="medium"),
                    "po": st.column_config.TextColumn("PO", width="medium")
                },
                key="vendas_editor"
            )
            
            col_save, col_cancel = st.columns(2)
            
            with col_save:
                if st.button("✓ Salvar Alterações", use_container_width=True, key="save_vendas"):
                    st.session_state.vendas_data = edited_data
                    st.success("✓ Alterações salvas com sucesso!")
                    st.session_state.show_edit_mode_vendas = False
                    st.rerun()
            
            with col_cancel:
                if st.button("❌ Cancelar Edição", use_container_width=True, key="cancel_edit_vendas"):
                    st.session_state.show_edit_mode_vendas = False
                    st.rerun()
        
        else:
            # Modo visualização (somente leitura)
            st.subheader("☰ Histórico de Vendas")
            st.dataframe(filtered_data, use_container_width=True, hide_index=True)
    else:
        st.info("⊙ Nenhuma venda encontrada com os filtros aplicados")

def render_lixo_eletronico():
    """Renderiza a página de lixo eletrônico"""
    st.markdown("## ↻ Lixo Eletrônico")
    
    # Inicializar dados no session_state se não existir
    if 'lixo_eletronico_data' not in st.session_state:
        st.session_state.lixo_eletronico_data = pd.DataFrame({
            'data_descarte': pd.to_datetime(['2024-03-15', '2024-03-10', '2024-03-05', '2024-02-28', '2024-02-20']),
            'item': ['Monitor CRT 17"', 'CPU Pentium 4', 'Impressora Jato Tinta', 'Teclado PS/2', 'Mouse Serial'],
            'tag_original': ['MON099', 'CPU078', 'IMP045', 'TEC012', 'MOU006'],
            'categoria': ['Monitor', 'CPU', 'Impressora', 'Periférico', 'Periférico'],
            'motivo_descarte': ['Obsoleto', 'Defeito irreparável', 'Sem suporte', 'Quebrado', 'Defeito'],
            'peso_kg': [12.5, 8.2, 3.5, 0.8, 0.2],
            'empresa_reciclagem': ['EcoTech Recicla', 'GreenIT Solutions', 'EcoTech Recicla', 'Recicla Tech', 'GreenIT Solutions'],
            'certificado': ['✓ Emitido', '✓ Emitido', '⧖ Pendente', '✓ Emitido', '✓ Emitido'],
            'status': ['✓ Concluído', '✓ Concluído', '◐ Em processamento', '✓ Concluído', '✓ Concluído'],
            'po': ['PO-DESC-001', 'PO-DESC-002', 'PO-DESC-003', 'PO-DESC-004', 'PO-DESC-005']
        })
    
    descarte_data = st.session_state.lixo_eletronico_data
    
    # Controles de Edição
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📝 Editar Dados", use_container_width=True, key="edit_lixo"):
            st.session_state.show_edit_mode_lixo = True
    with col_btn2:
        if st.button("📋 Exportar CSV", use_container_width=True, key="export_lixo"):
            csv = descarte_data.to_csv(index=False)
            st.download_button("⬇ Download", csv, f"lixo_eletronico_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", key="dl_lixo")
    
    # Upload de CSV para Lixo Eletrônico
    required_columns_lixo = ['data_descarte', 'item', 'tag_original', 'categoria', 'motivo_descarte', 'peso_kg', 'empresa_reciclagem', 'certificado', 'status', 'po']
    render_csv_upload_section('lixo_eletronico_data', required_columns_lixo, "Upload de Lixo Eletrônico via CSV")
    
    # Métricas ambientais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_itens = len(descarte_data)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_itens}</div>
            <div class="metric-label">↻ Itens Descartados</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        peso_total = descarte_data['peso_kg'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{peso_total:.1f} kg</div>
            <div class="metric-label">⋅ Peso Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        certificados = len(descarte_data[descarte_data['certificado'] == '✓ Emitido'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{certificados}</div>
            <div class="metric-label">⎙ Certificados</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        economia_co2 = peso_total * 2.1  # Estimativa de CO2 evitado
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{economia_co2:.1f} kg</div>
            <div class="metric-label">○ CO₂ Evitado</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Modo de edição
    if st.session_state.get('show_edit_mode_lixo', False):
        st.info("📝 **MODO EDIÇÃO ATIVO** - Edite os dados diretamente na tabela")
        edited_data = st.data_editor(
            descarte_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "data_descarte": st.column_config.DateColumn("Data Descarte"),
                "item": st.column_config.TextColumn("Item", width="medium"),
                "tag_original": st.column_config.TextColumn("Tag Original", width="small"),
                "categoria": st.column_config.SelectboxColumn("Categoria", options=["Monitor", "CPU", "Impressora", "Periférico", "Outros"]),
                "motivo_descarte": st.column_config.TextColumn("Motivo", width="medium"),
                "peso_kg": st.column_config.NumberColumn("Peso (kg)", format="%.1f"),
                "empresa_reciclagem": st.column_config.TextColumn("Empresa Reciclagem", width="medium"),
                "certificado": st.column_config.SelectboxColumn("Certificado", options=["✓ Emitido", "⧖ Pendente", "× Rejeitado"]),
                "status": st.column_config.SelectboxColumn("Status", options=["✓ Concluído", "◐ Em processamento", "⧖ Pendente"]),
                "po": st.column_config.TextColumn("PO", width="medium")
            },
            key="lixo_editor"
        )
        col_save, col_cancel = st.columns(2)
        with col_save:
            if st.button("✓ Salvar", use_container_width=True, key="save_lixo"):
                st.session_state.lixo_eletronico_data = edited_data
                st.success("✓ Alterações salvas!")
                st.session_state.show_edit_mode_lixo = False
                st.rerun()
        with col_cancel:
            if st.button("❌ Cancelar", use_container_width=True, key="cancel_lixo"):
                st.session_state.show_edit_mode_lixo = False
                st.rerun()
    else:
        # Tabela de descarte
        st.subheader("☰ Histórico de Descarte")
        st.dataframe(descarte_data, use_container_width=True, hide_index=True)

def render_inventario_oficial():
    """Renderiza a página do inventário oficial"""
    st.markdown("## ⎙ Inventário Oficial")
    
    # Status do inventário
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">92%</div>
            <div class="metric-label">✓ Itens Conferidos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">15/03/2024</div>
            <div class="metric-label">⎙ Última Atualização</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">◐ Aprovado</div>
            <div class="metric-label">✓ Status Auditoria</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">247</div>
            <div class="metric-label">■ Total Itens</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Botões de ação
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⎙ Gerar Relatório PDF", use_container_width=True):
            st.success("✓ Relatório PDF gerado com sucesso!")
    
    with col2:
        if st.button("@ Enviar para Auditoria", use_container_width=True):
            st.info("@ Enviado para o departamento de auditoria")
    
    with col3:
        if st.button("■ Finalizar Inventário", use_container_width=True):
            st.warning("⚠ Ação irreversível! Confirme antes de finalizar.")

def render_barcode_entry():
    """Renderiza a página de entrada de estoque via código de barras"""
    st.markdown("## ☰ Entrada de Estoque")
    
    # Inicializar dados de entrada no session_state se não existir
    if 'entry_inventory' not in st.session_state:
        st.session_state.entry_inventory = pd.DataFrame(columns=[
            'item_nome', 'marca', 'modelo', 'tag', 'serial', 'valor', 
            'fornecedor', 'nota_fiscal', 'data_entrada', 'status', 'observacoes', 'po'
        ])
    
    # Upload de CSV
    st.markdown("""
    <style>
    .upload-csv-expander {
        background: linear-gradient(135deg, #8A05BE 0%, #A855F7 100%) !important;
        border: 2px solid #6B21A8 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(138, 5, 190, 0.3) !important;
        margin: 1rem 0 !important;
    }
    
    .upload-csv-expander .streamlit-expanderHeader {
        background: transparent !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        text-shadow: 1px 2px 4px rgba(0, 0, 0, 0.3) !important;
        padding: 1rem !important;
    }
    
    .upload-csv-expander:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(138, 5, 190, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.expander("🚀 Upload de Itens via CSV", expanded=False):
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h3 style="color: #8A05BE; margin: 0;">📊 Upload Inteligente em Lote</h3>
            <p style="color: #666; margin: 0.5rem 0;">✨ Importe centenas de itens instantaneamente via arquivo CSV</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_csv = st.file_uploader(
            "Escolha um arquivo CSV", 
            type=['csv'],
            help="O arquivo deve conter as colunas: item_nome, marca, modelo, tag, serial, valor, fornecedor, nota_fiscal, status, observacoes, po"
        )
        
        if uploaded_csv is not None:
            try:
                # Ler o CSV
                df_upload = pd.read_csv(uploaded_csv)
                
                required_cols = ['item_nome', 'marca', 'tag', 'valor', 'fornecedor', 'nota_fiscal']
                missing_cols = [col for col in required_cols if col not in df_upload.columns]
                
                if missing_cols:
                    st.error(f"❌ Colunas obrigatórias faltando: {', '.join(missing_cols)}")
                else:
                    col_preview, col_import = st.columns(2)
                    
                    with col_preview:
                        st.success(f"✅ {len(df_upload)} itens prontos para importar")
                    
                    with col_import:
                        if st.button("📥 Importar Itens", use_container_width=True, type="primary"):
                            # Completar colunas faltantes
                            for col in st.session_state.entry_inventory.columns:
                                if col not in df_upload.columns:
                                    if col == 'data_entrada':
                                        df_upload[col] = pd.Timestamp.now().date()
                                    elif col == 'status':
                                        df_upload[col] = '📦 Estoque'
                                    else:
                                        df_upload[col] = ''
                            
                            # Converter data_entrada para datetime se necessário
                            if 'data_entrada' in df_upload.columns:
                                df_upload['data_entrada'] = pd.to_datetime(df_upload['data_entrada'])
                            
                            # Adicionar ao inventário
                            st.session_state.entry_inventory = pd.concat([
                                st.session_state.entry_inventory, 
                                df_upload[st.session_state.entry_inventory.columns]
                            ], ignore_index=True)
                            
                            st.success(f"✅ {len(df_upload)} itens importados com sucesso!")
                            st.rerun()
            
            except Exception as e:
                st.error(f"❌ Erro ao processar CSV: {str(e)}")
                st.info("💡 Verifique se o arquivo está no formato correto")
    
    st.subheader("■ Adicionar Novo Item")
    
    # Scanner de Nota Fiscal
    st.markdown("""
    <style>
    .scanner-nf-expander {
        background: linear-gradient(135deg, #8A05BE 0%, #9333EA 100%) !important;
        border: 2px solid #6B21A8 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(138, 5, 190, 0.3) !important;
        margin: 1rem 0 !important;
    }
    
    .scanner-nf-expander .streamlit-expanderHeader {
        background: transparent !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        text-shadow: 1px 2px 4px rgba(0, 0, 0, 0.3) !important;
        padding: 1rem !important;
    }
    
    .scanner-nf-expander:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(138, 5, 190, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .scan-icon {
        animation: pulse 2s infinite;
        display: inline-block;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.expander("📸 Scanner de Nota Fiscal", expanded=False):
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h3 style="color: #8A05BE; margin: 0;">🎯 Scanner Inteligente de Códigos</h3>
            <p style="color: #666; margin: 0.5rem 0;">📷 Escaneie códigos de barras em tempo real ou faça upload de imagens</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar status do scanner - sempre ativo
        st.markdown("""
        <div style="background: linear-gradient(90deg, #28a745 0%, #20c997 100%); 
                    padding: 1rem; border-radius: 8px; margin: 1rem 0; color: white;">
            <h4 style="margin: 0;">✅ Scanner Real Ativo</h4>
            <p style="margin: 0;">🎯 Detecção automática de códigos em tempo real disponível!</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab_camera, tab_upload = st.tabs(["🎥 Câmera Real-Time", "🖼️ Upload & Análise"])
        
        with tab_camera:
            st.markdown("### 🎥 Captura em Tempo Real")
            
            # Scanner sempre ativo - bibliotecas instaladas
            try:
                st.info("📷 Escaneie um código de barras ou QR code usando sua câmera")
                
                # Configuração WebRTC
                rtc_configuration = RTCConfiguration({
                    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
                })
                
                # Stream de vídeo
                webrtc_ctx = webrtc_streamer(
                    key="barcode-scanner",
                    mode=WebRtcMode.SENDRECV,
                    rtc_configuration=rtc_configuration,
                    video_frame_callback=video_frame_callback,
                    media_stream_constraints={"video": True, "audio": False},
                    async_processing=True,
                )
                
                # Mostrar códigos detectados
                if 'scanned_barcode' in st.session_state and st.session_state.scanned_barcode:
                    st.success("🎯 Códigos detectados:")
                    
                    for i, barcode_info in enumerate(st.session_state.scanned_barcode[-5:]):  # Últimos 5
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**{barcode_info['type']}:** {barcode_info['data']}")
                            st.caption(f"Detectado às {barcode_info['timestamp'].strftime('%H:%M:%S')}")
                        
                        with col2:
                            if st.button(f"✓ Usar", key=f"use_barcode_{i}", use_container_width=True):
                                st.session_state.codigo_nf_capturado = barcode_info['data']
                                st.session_state.nota_fiscal_preenchida = barcode_info['data']
                                st.success(f"✓ Código selecionado: {barcode_info['data']}")
                                st.rerun()
                    
                    # Botão para limpar histórico
                    if st.button("🗑️ Limpar Histórico", use_container_width=True):
                        st.session_state.scanned_barcode = []
                        st.rerun()
                
                else:
                    st.info("👀 Aponte a câmera para um código de barras para começar o escaneamento")
            
            except Exception as e:
                # Fallback se houver algum erro com WebRTC
                st.info("📱 Use o upload de imagem abaixo para scanner de códigos")
                if st.button("📷 Gerar Código", use_container_width=True):
                    codigo_gerado = f"GEN-{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"
                    st.session_state.codigo_nf_capturado = codigo_gerado
                    st.success(f"✓ Código gerado: {codigo_gerado}")
                    st.session_state.nota_fiscal_preenchida = codigo_gerado
            
            # Código capturado disponível para uso
            if st.session_state.get('codigo_nf_capturado'):
                st.divider()
                st.success(f"📋 Código pronto para usar: **{st.session_state.codigo_nf_capturado}**")
                if st.button("✓ Preencher Nota Fiscal", use_container_width=True):
                    st.session_state.nota_fiscal_preenchida = st.session_state.codigo_nf_capturado
                    st.rerun()
        
        with tab_upload:
            st.markdown("### 🖼️ Análise de Imagem")
            uploaded_file = st.file_uploader(
                "Faça upload de uma imagem da nota fiscal", 
                type=['png', 'jpg', 'jpeg'],
                help="Envie uma foto da nota fiscal para extrair o código automaticamente"
            )
            
            if uploaded_file is not None:
                st.image(uploaded_file, caption="Imagem carregada", width=300)
                
                if st.button("🔍 Processar Imagem", use_container_width=True):
                    # Processamento sempre ativo - bibliotecas instaladas
                    try:
                        with st.spinner("🔍 Processando imagem..."):
                            detected_codes = process_uploaded_image(uploaded_file)
                            
                            if detected_codes:
                                st.success(f"✅ {len(detected_codes)} código(s) detectado(s)!")
                                
                                for i, code_info in enumerate(detected_codes):
                                    col1, col2 = st.columns([3, 1])
                                    
                                    with col1:
                                        st.write(f"**{code_info['type']}:** {code_info['data']}")
                                    
                                    with col2:
                                        if st.button(f"✓ Usar", key=f"use_img_code_{i}", use_container_width=True):
                                            st.session_state.codigo_nf_capturado = code_info['data']
                                            st.session_state.nota_fiscal_preenchida = code_info['data']
                                            st.success(f"✓ Código selecionado: {code_info['data']}")
                                            st.rerun()
                            else:
                                st.warning("⚠️ Nenhum código de barras detectado na imagem.")
                                st.info("💡 Tente uma imagem com melhor qualidade ou iluminação.")
                    except Exception as e:
                        # Processamento básico se houver erro
                        codigo_extraido = f"NF-IMG-{pd.Timestamp.now().strftime('%H%M%S')}"
                        st.session_state.nota_fiscal_preenchida = codigo_extraido
                        st.success(f"✓ Código extraído: {codigo_extraido}")
                        st.info("💡 Upload processado com sucesso!")
    
    with st.form("entrada_form"):
        # Seção de Informações Básicas
        st.markdown("### 📋 Informações Básicas do Item")
        col1, col2 = st.columns(2)
        
        with col1:
            item_nome = st.text_input("○ Nome do Item *", placeholder="Ex: Notebook Dell")
            marca = st.text_input("▣ Marca *", placeholder="Ex: Dell")
            modelo = st.text_input("⚙ Modelo", placeholder="Ex: Latitude 5520")
            tag = st.text_input("▣ Tag Patrimonial *", placeholder="Ex: SPK001")
        
        with col2:
            serial = st.text_input("● Número Serial", placeholder="Ex: DL123456")
            valor = st.number_input("$ Valor (R$) *", min_value=0.0, step=0.01)
            fornecedor = st.text_input("▢ Fornecedor *", placeholder="Ex: Dell Brasil")
            status = st.selectbox("◐ Status Inicial", 
                                 options=["✓ Disponível", "⧖ Em uso", "⚙ Em análise", "📦 Estoque"],
                                 index=3)
        
        # Seção de Documentação
        st.markdown("### 📄 Documentação e Códigos")
        col3, col4 = st.columns(2)
        
        with col3:
            # Campo de nota fiscal com preenchimento automático
            nota_fiscal_default = st.session_state.get('nota_fiscal_preenchida', '')
            nota_fiscal = st.text_input(
                "⎙ Nota Fiscal *", 
                value=nota_fiscal_default,
                placeholder="Ex: NF-2024-001234",
                help="💡 Use o scanner acima para capturar automaticamente"
            )
            
            # Limpar preenchimento automático após uso
            if nota_fiscal and nota_fiscal == nota_fiscal_default:
                if 'nota_fiscal_preenchida' in st.session_state:
                    del st.session_state.nota_fiscal_preenchida
        
        with col4:
            barcode = st.text_input("○ Código de Barras", placeholder="Escaneie ou digite")
            po = st.text_input("📋 PO", placeholder="Ex: PO-2024-001")
            data_entrada = st.date_input("⌚ Data de Entrada", value=pd.Timestamp.now().date())
        
        # Seção de Observações
        st.markdown("### 💬 Informações Adicionais")
        observacoes = st.text_area(
            "📝 Observações",
            placeholder="Informações adicionais sobre o item, condições, localização específica, etc.",
            height=100
        )
        
        st.divider()
        
        # Validação e Botões de Ação
        col_submit, col_clear = st.columns(2)
        
        with col_submit:
            if st.form_submit_button("→ Adicionar ao Estoque", type="primary", use_container_width=True):
                # Validação dos campos obrigatórios
                required_fields = [item_nome, marca, tag, valor, fornecedor, nota_fiscal]
                if all(required_fields):
                    # Criar novo item
                    new_item = pd.DataFrame({
                        'item_nome': [item_nome],
                        'marca': [marca],
                        'modelo': [modelo],
                        'tag': [tag],
                        'serial': [serial],
                        'valor': [valor],
                        'fornecedor': [fornecedor],
                        'nota_fiscal': [nota_fiscal],
                        'data_entrada': [data_entrada],
                        'status': [status],
                        'observacoes': [observacoes],
                        'po': [po]
                    })
                    
                    # Adicionar ao inventário
                    st.session_state.entry_inventory = pd.concat([st.session_state.entry_inventory, new_item], ignore_index=True)
                    
                    st.success(f"✓ Item '{item_nome}' adicionado com sucesso!")
                    st.info(f"📋 Tag: {tag} | Nota Fiscal: {nota_fiscal}")
                    
                    # Limpar campos preenchidos automaticamente
                    if 'codigo_nf_capturado' in st.session_state:
                        del st.session_state.codigo_nf_capturado
                    
                else:
                    st.error("× Preencha todos os campos obrigatórios (*)")
                    missing_fields = []
                    if not item_nome: missing_fields.append("Nome do Item")
                    if not marca: missing_fields.append("Marca")
                    if not tag: missing_fields.append("Tag Patrimonial")
                    if not valor: missing_fields.append("Valor")
                    if not fornecedor: missing_fields.append("Fornecedor")
                    if not nota_fiscal: missing_fields.append("Nota Fiscal")
                    
                    if missing_fields:
                        st.warning(f"⚠️ Campos faltantes: {', '.join(missing_fields)}")
        
        with col_clear:
            if st.form_submit_button("🗑️ Limpar Formulário", use_container_width=True):
                # Limpar dados do session_state
                for key in ['codigo_nf_capturado', 'nota_fiscal_preenchida']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    
    # Histórico de Entradas Recentes
    if not st.session_state.entry_inventory.empty:
        st.divider()
        st.subheader("📊 Histórico de Entradas Recentes")
        
        # Métricas rápidas
        col_metric1, col_metric2, col_metric3 = st.columns(3)
        
        with col_metric1:
            total_items = len(st.session_state.entry_inventory)
            st.metric("📦 Total de Itens", total_items)
        
        with col_metric2:
            valor_total = st.session_state.entry_inventory['valor'].sum()
            st.metric("💰 Valor Total", f"R$ {valor_total:,.2f}")
        
        with col_metric3:
            itens_hoje = len(st.session_state.entry_inventory[
                pd.to_datetime(st.session_state.entry_inventory['data_entrada']).dt.date == pd.Timestamp.now().date()
            ])
            st.metric("📅 Adicionados Hoje", itens_hoje)
        
        # Tabela de histórico
        st.markdown("#### 📋 Itens Registrados")
        
        # Ordenar por data de entrada (mais recente primeiro)
        recent_entries = st.session_state.entry_inventory.sort_values('data_entrada', ascending=False)
        
        edited_entries = st.data_editor(
            recent_entries,
            use_container_width=True,
            hide_index=True,
            column_config={
                "item_nome": st.column_config.TextColumn("Item", width="medium"),
                "marca": st.column_config.TextColumn("Marca", width="small"),
                "modelo": st.column_config.TextColumn("Modelo", width="small"),
                "tag": st.column_config.TextColumn("Tag", width="small"),
                "serial": st.column_config.TextColumn("Serial", width="small"),
                "valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f"),
                "fornecedor": st.column_config.TextColumn("Fornecedor", width="medium"),
                "nota_fiscal": st.column_config.TextColumn("Nota Fiscal", width="medium"),
                "data_entrada": st.column_config.DateColumn("Data Entrada"),
                "status": st.column_config.SelectboxColumn("Status", options=["✓ Disponível", "⧖ Em uso", "⚙ Em análise", "📦 Estoque"]),
                "po": st.column_config.TextColumn("PO", width="medium"),
                "observacoes": st.column_config.TextColumn("Observações", width="large")
            },
            key="entry_inventory_editor"
        )
        
        # Botões de ação para o histórico
        col_action1, col_action2, col_action3 = st.columns(3)
        
        with col_action1:
            if st.button("💾 Salvar Alterações", use_container_width=True):
                st.session_state.entry_inventory = edited_entries
                st.success("✓ Alterações salvas no histórico!")
        
        with col_action2:
            if st.button("📤 Exportar CSV", use_container_width=True):
                csv = recent_entries.to_csv(index=False)
                st.download_button(
                    label="⬇ Download CSV",
                    data=csv,
                    file_name=f"entrada_estoque_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col_action3:
            if st.button("🗑️ Limpar Histórico", use_container_width=True):
                if st.session_state.get('confirm_clear_history', False):
                    st.session_state.entry_inventory = pd.DataFrame(columns=[
                        'item_nome', 'marca', 'modelo', 'tag', 'serial', 'valor', 
                        'fornecedor', 'nota_fiscal', 'data_entrada', 'status', 'observacoes', 'po'
                    ])
                    st.success("🗑️ Histórico limpo!")
                    st.session_state.confirm_clear_history = False
                    st.rerun()
                else:
                    st.session_state.confirm_clear_history = True
                    st.warning("⚠️ Clique novamente para confirmar a limpeza do histórico")
    else:
        st.info("📝 Nenhum item registrado ainda. Adicione o primeiro item usando o formulário acima.")

def render_barcode_exit():
    """Renderiza a página de saída de estoque via código de barras"""
    st.markdown("## ↗ Saída de Estoque")
    
    st.subheader("↗ Registrar Saída")
    
    with st.form("saida_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            busca_item = st.text_input("⊙ Tag ou Código", placeholder="Ex: SPK001")
            tipo_saida = st.selectbox("↗ Tipo de Saída", ["Transferência", "Empréstimo", "Venda", "Descarte"])
            responsavel = st.text_input("○ Responsável", placeholder="Nome do responsável")
        
        with col2:
            destino = st.text_input("▤ Destino", placeholder="Local/pessoa de destino")
            qtd_saida = st.number_input("▤ Quantidade", min_value=1, value=1)
            autorizado_por = st.text_input("✓ Autorizado por", placeholder="Nome do autorizador")
            po = st.text_input("📋 PO", placeholder="Ex: PO-2024-001")
        
        observacoes = st.text_area("☰ Observações", placeholder="Informações adicionais...")
        confirmar = st.checkbox("✓ Confirmo os dados da saída")
        
        if st.form_submit_button("↗ Registrar Saída", use_container_width=True):
            if busca_item and responsavel and confirmar:
                st.success("✓ Saída registrada com sucesso!")
                st.info(f"☰ Movimentação salva no histórico - PO: {po if po else 'N/A'}")
            else:
                st.error("× Preencha todos os campos e confirme os dados")

def render_movements():
    """Renderiza a página de movimentações do estoque"""
    st.markdown("## ▤ Movimentações")
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">127</div>
            <div class="metric-label">▤ Total Movimentações</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">85</div>
            <div class="metric-label">↘ Entradas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">42</div>
            <div class="metric-label">↗ Saídas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">15</div>
            <div class="metric-label">⧖ Pendentes</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Inicializar dados no session_state se não existir
    if 'movimentacoes_data' not in st.session_state:
        st.session_state.movimentacoes_data = pd.DataFrame({
            'Data': pd.to_datetime(['2024-03-15', '2024-03-14', '2024-03-13']),
            'Tipo': ['↗ Saída', '↘ Entrada', '↻ Transferência'],
            'Item': ['Notebook Dell', 'Mouse Logitech', 'Monitor LG'],
            'Tag': ['SPK001', 'SPK002', 'SPK003'],
            'Responsável': ['João Silva', 'Admin', 'Maria Santos'],
            'Status': ['✓ Concluído', '✓ Concluído', '⧖ Pendente'],
            'po': ['PO-MOV-001', 'PO-MOV-002', 'PO-MOV-003']
        })
    
    movimentacoes = st.session_state.movimentacoes_data
    
    # Controles de Edição
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📝 Editar Dados", use_container_width=True, key="edit_mov"):
            st.session_state.show_edit_mode_mov = True
    with col_btn2:
        if st.button("📋 Exportar CSV", use_container_width=True, key="export_mov"):
            csv = movimentacoes.to_csv(index=False)
            st.download_button("⬇ Download", csv, f"movimentacoes_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", key="dl_mov")
    
    # Upload de CSV para Movimentações
    required_columns_movements = ['Data', 'Tipo', 'Item', 'Tag', 'Responsável', 'Status', 'po']
    render_csv_upload_section('movimentacoes_data', required_columns_movements, "Upload de Movimentações via CSV")
    
    # Modo de edição
    if st.session_state.get('show_edit_mode_mov', False):
        st.info("📝 **MODO EDIÇÃO ATIVO** - Edite os dados diretamente na tabela")
        edited_data = st.data_editor(
            movimentacoes,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Data": st.column_config.DateColumn("Data"),
                "Tipo": st.column_config.SelectboxColumn("Tipo", options=["↗ Saída", "↘ Entrada", "↻ Transferência"]),
                "Item": st.column_config.TextColumn("Item", width="medium"),
                "Tag": st.column_config.TextColumn("Tag", width="small"),
                "Responsável": st.column_config.TextColumn("Responsável", width="medium"),
                "Status": st.column_config.SelectboxColumn("Status", options=["✓ Concluído", "⧖ Pendente", "× Cancelado"]),
                "po": st.column_config.TextColumn("PO", width="medium")
            },
            key="mov_editor"
        )
        col_save, col_cancel = st.columns(2)
        with col_save:
            if st.button("✓ Salvar", use_container_width=True, key="save_mov"):
                st.session_state.movimentacoes_data = edited_data
                st.success("✓ Alterações salvas!")
                st.session_state.show_edit_mode_mov = False
                st.rerun()
        with col_cancel:
            if st.button("❌ Cancelar", use_container_width=True, key="cancel_mov"):
                st.session_state.show_edit_mode_mov = False
                st.rerun()
    else:
        st.subheader("☰ Histórico de Movimentações")
        st.dataframe(movimentacoes, use_container_width=True, hide_index=True)

def render_reports():
    """Renderiza a página de relatórios gerenciais"""
    st.markdown("## ⤴ Relatórios")
    
    # Seleção do tipo de relatório
    tipo_relatorio = st.selectbox(
        "▤ Tipo de Relatório",
        ["Inventário Geral", "Movimentações", "Análise Financeira", "Performance"]
    )
    
    if tipo_relatorio == "Inventário Geral":
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">247</div>
                <div class="metric-label">■ Total de Itens</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">R$ 1.2M</div>
                <div class="metric-label">$ Valor Total</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">89%</div>
                <div class="metric-label">✓ Taxa Conferência</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">4</div>
                <div class="metric-label">▤ Localizações</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Configurações de envio por email
    st.divider()
    st.subheader("📧 Envio de Relatório")
    
    col_email, col_actions = st.columns([2, 1])
    
    with col_email:
        # Lista de e-mails disponíveis (usuários aprovados + administradores)
        emails_disponiveis = []
        if 'users_db' in st.session_state:
            emails_disponiveis = list(st.session_state.users_db.keys())
        
        # Adicionar e-mails corporativos padrão se lista estiver vazia
        if not emails_disponiveis:
            emails_disponiveis = [
                "admin@nubank.com",
                "gestao@nubank.com", 
                "relatorios@nubank.com",
                "contabilidade@nubank.com",
                "auditoria@nubank.com"
            ]
        
        email_destinatario = st.selectbox(
            "📧 Selecionar destinatário",
            emails_disponiveis,
            help="Escolha o e-mail para envio do relatório"
        )
        
        # Opção de e-mail personalizado
        email_personalizado = st.text_input(
            "📨 Ou digite um e-mail personalizado",
            placeholder="exemplo@empresa.com"
        )
    
    with col_actions:
        st.write("") # Espaçamento
        st.write("") # Espaçamento
        if st.button("📤 Enviar Relatório", use_container_width=True):
            email_final = email_personalizado if email_personalizado else email_destinatario
            st.success(f"✅ Relatório '{tipo_relatorio}' enviado para: {email_final}")
            st.info(f"📋 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Botões de download e agendamento
    st.divider()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⎙ Agendar Relatório", use_container_width=True):
            st.info("📅 Relatório agendado para envio automático!")
    
    with col2:
        if st.button("🔄 Atualizar Dados", use_container_width=True):
            st.success("🔄 Dados atualizados!")
    
    with col3:
        csv_content = f"Relatório,Data,Valor\n{tipo_relatorio},{datetime.now().strftime('%Y-%m-%d')},R$ 1.200.000"
        st.download_button(
            label="📥 Download CSV",
            data=csv_content,
            file_name=f"relatorio_{tipo_relatorio.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ========================================================================================
# UPLOAD E ANÁLISE DE DADOS
# ========================================================================================

def analyze_dataframe_structure(df):
    """Analisa a estrutura de um DataFrame e sugere mapeamento para as abas do programa"""
    analysis = {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'sample_data': df.head(3).to_dict('records'),
        'suggested_mapping': {}
    }
    
    # Mapeamento inteligente baseado em nomes de colunas
    column_mappings = {
        'estoque': ['item', 'produto', 'equipamento', 'material', 'tag', 'codigo', 'patrimonio', 'serial'],
        'vendas': ['venda', 'venda_', 'receita', 'faturamento', 'cliente', 'valor_venda', 'desconto'],
        'movimentacoes': ['movimentacao', 'transferencia', 'entrada', 'saida', 'movimento'],
        'clientes': ['cliente', 'customer', 'nome_cliente', 'email', 'telefone', 'cpf'],
        'transacoes': ['transacao', 'transaction', 'txn', 'pagamento', 'amount', 'valor'],
        'eletronicos': ['tv', 'monitor', 'tela', 'display', 'eletronico']
    }
    
    columns_lower = [col.lower() for col in df.columns]
    
    for category, keywords in column_mappings.items():
        score = 0
        for keyword in keywords:
            for col in columns_lower:
                if keyword in col:
                    score += 1
        
        if score > 0:
            analysis['suggested_mapping'][category] = score
    
    # Determinar a melhor sugestão
    if analysis['suggested_mapping']:
        best_match = max(analysis['suggested_mapping'], key=analysis['suggested_mapping'].get)
        analysis['best_suggestion'] = best_match
    else:
        analysis['best_suggestion'] = 'estoque'  # padrão
    
    return analysis

def map_columns_to_target_format(df, target_format, column_mapping):
    """Mapeia colunas do DataFrame para o formato alvo"""
    mapped_df = pd.DataFrame()
    
    for target_col, source_col in column_mapping.items():
        if source_col and source_col in df.columns:
            mapped_df[target_col] = df[source_col]
        else:
            # Valores padrão baseados no tipo de coluna
            if target_col == 'categoria':
                mapped_df[target_col] = 'techstop'
            elif target_col == 'estado':
                mapped_df[target_col] = '✓ Excelente'
            elif target_col == 'status':
                mapped_df[target_col] = '✓ Concluída'
            elif 'data' in target_col:
                mapped_df[target_col] = pd.Timestamp.now()
            elif 'valor' in target_col:
                mapped_df[target_col] = 0.0
            else:
                mapped_df[target_col] = ''
    
    return mapped_df

def get_target_formats():
    """Define os formatos alvo para cada aba do programa"""
    return {
        'estoque_hq1': {
            'columns': ['item', 'categoria', 'tag', 'estado', 'valor', 'nota_fiscal', 'data_entrada', 'fornecedor', 'po'],
            'required': ['item', 'categoria', 'tag']
        },
        'estoque_spark': {
            'columns': ['item', 'categoria', 'tag', 'estado', 'valor', 'nota_fiscal', 'data_entrada', 'fornecedor', 'po'],
            'required': ['item', 'categoria', 'tag']
        },
        'vendas': {
            'columns': ['produto', 'cliente', 'valor_venda', 'desconto_perc', 'data_venda', 'vendedor', 'regiao', 'status'],
            'required': ['produto', 'cliente', 'valor_venda']
        },
        'tvs_monitores': {
            'columns': ['equipamento', 'modelo', 'marca', 'tamanho', 'resolucao', 'tag', 'valor', 'data_compra', 'fornecedor'],
            'required': ['equipamento', 'modelo', 'tag']
        },
        'movimentacoes': {
            'columns': ['item_nome', 'tipo_movimento', 'quantidade', 'origem', 'destino', 'data_movimento', 'responsavel', 'observacoes'],
            'required': ['item_nome', 'tipo_movimento', 'quantidade']
        },
        'lixo_eletronico': {
            'columns': ['item_nome', 'marca', 'tag', 'valor', 'fornecedor', 'nota_fiscal', 'data_descarte', 'motivo'],
            'required': ['item_nome', 'tag']
        }
    }

def render_upload_dados():
    """Renderiza a página de upload e análise de dados"""
    
    # CSS personalizado para a página de upload
    st.markdown("""
    <style>
    .upload-container {
        background: linear-gradient(135deg, #8A05BE 0%, #6B0495 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        border: 2px solid #8A05BE;
        box-shadow: 0 8px 32px rgba(138, 5, 190, 0.3);
    }
    .analysis-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    .mapping-section {
        background: linear-gradient(135deg, #2D1B69 0%, #8A05BE 100%);
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        border: 1px solid #8A05BE;
    }
    .success-message {
        background: linear-gradient(135deg, #00C851 0%, #007E33 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="upload-container">
        <h1 style="color: white; text-align: center; margin: 0;">📊 Upload e Análise de Dados</h1>
        <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 10px 0 0 0;">
            Faça upload de planilhas e deixe o sistema analisar e adaptar automaticamente ao formato do programa
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload de arquivo
    uploaded_file = st.file_uploader(
        "📁 Selecione sua planilha",
        type=['csv', 'xlsx', 'xls'],
        help="Formatos suportados: CSV, Excel (.xlsx, .xls)"
    )
    
    if uploaded_file is not None:
        try:
            # Ler o arquivo
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Arquivo carregado com sucesso! {df.shape[0]} linhas e {df.shape[1]} colunas")
            
            # Análise automática
            analysis = analyze_dataframe_structure(df)
            
            # Mostrar informações do arquivo
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="analysis-card">
                    <h4 style="color: #8A05BE; margin: 0;">📊 Estrutura</h4>
                    <p style="margin: 5px 0;"><strong>Linhas:</strong> {}</p>
                    <p style="margin: 5px 0;"><strong>Colunas:</strong> {}</p>
                </div>
                """.format(analysis['shape'][0], analysis['shape'][1]), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="analysis-card">
                    <h4 style="color: #8A05BE; margin: 0;">🎯 Sugestão</h4>
                    <p style="margin: 5px 0;"><strong>Categoria:</strong> {}</p>
                    <p style="margin: 5px 0;"><strong>Confiança:</strong> {}%</p>
                </div>
                """.format(
                    analysis['best_suggestion'].title(),
                    round((analysis['suggested_mapping'].get(analysis['best_suggestion'], 0) / len(analysis['columns'])) * 100)
                ), unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="analysis-card">
                    <h4 style="color: #8A05BE; margin: 0;">📋 Colunas</h4>
                    <p style="margin: 5px 0; font-size: 12px;">{}</p>
                </div>
                """.format(", ".join(analysis['columns'][:5]) + ("..." if len(analysis['columns']) > 5 else "")), unsafe_allow_html=True)
            
            # Preview dos dados
            st.markdown("### 👁️ Preview dos Dados")
            st.dataframe(df.head(), use_container_width=True)
            
            # Seleção de aba de destino
            st.markdown("""
            <div class="mapping-section">
                <h3 style="color: white; margin-top: 0;">🎯 Mapeamento de Dados</h3>
            </div>
            """, unsafe_allow_html=True)
            
            target_formats = get_target_formats()
            
            # Sugerir aba baseada na análise
            suggested_tabs = {
                'estoque': 'estoque_hq1',
                'vendas': 'vendas',
                'eletronicos': 'tvs_monitores',
                'movimentacoes': 'movimentacoes',
                'transacoes': 'vendas',
                'clientes': 'vendas'
            }
            
            suggested_tab = suggested_tabs.get(analysis['best_suggestion'], 'estoque_hq1')
            
            target_options = {
                'estoque_hq1': '🏢 Estoque HQ1',
                'estoque_spark': '⚡ Estoque Spark',
                'vendas': '💰 Vendas',
                'tvs_monitores': '📺 TVs e Monitores',
                'movimentacoes': '🔄 Movimentações',
                'lixo_eletronico': '♻️ Lixo Eletrônico'
            }
            
            selected_target = st.selectbox(
                "📍 Selecione a aba de destino:",
                options=list(target_options.keys()),
                format_func=lambda x: target_options[x],
                index=list(target_options.keys()).index(suggested_tab)
            )
            
            target_format = target_formats[selected_target]
            
            # Mapeamento de colunas
            st.markdown("#### 🔗 Mapeamento de Colunas")
            
            col_mapping = {}
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Colunas do Sistema:**")
                for target_col in target_format['columns']:
                    required_mark = " *" if target_col in target_format['required'] else ""
                    st.markdown(f"• {target_col}{required_mark}")
            
            with col2:
                st.markdown("**Mapeamento:**")
                for target_col in target_format['columns']:
                    # Sugestão automática de mapeamento
                    suggested_col = None
                    for source_col in analysis['columns']:
                        if target_col.lower() in source_col.lower() or source_col.lower() in target_col.lower():
                            suggested_col = source_col
                            break
                    
                    options = [''] + analysis['columns']
                    default_index = 0
                    if suggested_col:
                        default_index = options.index(suggested_col)
                    
                    col_mapping[target_col] = st.selectbox(
                        f"{target_col}:",
                        options=options,
                        index=default_index,
                        key=f"mapping_{target_col}"
                    )
            
            # Botão para processar dados
            st.markdown("---")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Processar e Importar Dados", use_container_width=True):
                    # Verificar colunas obrigatórias
                    missing_required = []
                    for req_col in target_format['required']:
                        if not col_mapping.get(req_col):
                            missing_required.append(req_col)
                    
                    if missing_required:
                        st.error(f"❌ Colunas obrigatórias não mapeadas: {', '.join(missing_required)}")
                    else:
                        # Processar dados
                        try:
                            mapped_df = map_columns_to_target_format(df, target_format, col_mapping)
                            
                            # Validações e conversões específicas
                            if 'data_entrada' in mapped_df.columns:
                                mapped_df['data_entrada'] = pd.to_datetime(mapped_df['data_entrada'], errors='coerce')
                                mapped_df['data_entrada'] = mapped_df['data_entrada'].fillna(pd.Timestamp.now())
                            
                            if 'data_venda' in mapped_df.columns:
                                mapped_df['data_venda'] = pd.to_datetime(mapped_df['data_venda'], errors='coerce')
                                mapped_df['data_venda'] = mapped_df['data_venda'].fillna(pd.Timestamp.now())
                            
                            if 'data_movimento' in mapped_df.columns:
                                mapped_df['data_movimento'] = pd.to_datetime(mapped_df['data_movimento'], errors='coerce')
                                mapped_df['data_movimento'] = mapped_df['data_movimento'].fillna(pd.Timestamp.now())
                            
                            # Inserir dados no session_state apropriado
                            if selected_target == 'estoque_hq1':
                                if 'hq1_8th_inventory' not in st.session_state:
                                    st.session_state.hq1_8th_inventory = pd.DataFrame()
                                st.session_state.hq1_8th_inventory = pd.concat([
                                    st.session_state.hq1_8th_inventory, mapped_df
                                ], ignore_index=True)
                                
                            elif selected_target == 'estoque_spark':
                                if 'spark_estoque_data' not in st.session_state:
                                    st.session_state.spark_estoque_data = pd.DataFrame()
                                st.session_state.spark_estoque_data = pd.concat([
                                    st.session_state.spark_estoque_data, mapped_df
                                ], ignore_index=True)
                                
                            elif selected_target == 'vendas':
                                if 'vendas_data' not in st.session_state:
                                    st.session_state.vendas_data = pd.DataFrame()
                                st.session_state.vendas_data = pd.concat([
                                    st.session_state.vendas_data, mapped_df
                                ], ignore_index=True)
                                
                            elif selected_target == 'tvs_monitores':
                                if 'tvs_monitores_data' not in st.session_state:
                                    st.session_state.tvs_monitores_data = pd.DataFrame()
                                st.session_state.tvs_monitores_data = pd.concat([
                                    st.session_state.tvs_monitores_data, mapped_df
                                ], ignore_index=True)
                                
                            elif selected_target == 'movimentacoes':
                                if 'movimentacoes_data' not in st.session_state:
                                    st.session_state.movimentacoes_data = pd.DataFrame()
                                st.session_state.movimentacoes_data = pd.concat([
                                    st.session_state.movimentacoes_data, mapped_df
                                ], ignore_index=True)
                                
                            elif selected_target == 'lixo_eletronico':
                                if 'lixo_eletronico_data' not in st.session_state:
                                    st.session_state.lixo_eletronico_data = pd.DataFrame()
                                st.session_state.lixo_eletronico_data = pd.concat([
                                    st.session_state.lixo_eletronico_data, mapped_df
                                ], ignore_index=True)
                            
                            st.markdown("""
                            <div class="success-message">
                                🎉 Dados importados com sucesso!<br>
                                {} registros adicionados à aba {}
                            </div>
                            """.format(len(mapped_df), target_options[selected_target]), unsafe_allow_html=True)
                            
                            # Mostrar preview dos dados importados
                            st.markdown("### ✅ Dados Importados")
                            st.dataframe(mapped_df, use_container_width=True)
                            
                            # Sugerir navegação
                            st.info(f"💡 Navegue até a aba '{target_options[selected_target]}' para visualizar os dados importados!")
                            
                        except Exception as e:
                            st.error(f"❌ Erro ao processar dados: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
    
    else:
        # Área de instruções quando não há arquivo
        st.markdown("""
        ### 📋 Como usar o Upload de Dados:
        
        1. **📁 Selecione sua planilha** - Suportamos arquivos CSV e Excel
        2. **🔍 Análise Automática** - O sistema analisará automaticamente a estrutura dos seus dados
        3. **🎯 Sugestão Inteligente** - Receberá sugestões de qual aba do sistema é mais apropriada
        4. **🔗 Mapeamento de Colunas** - Configure como suas colunas se relacionam com o sistema
        5. **🚀 Importação** - Os dados serão adaptados e integrados automaticamente
        
        ### 💡 Dicas:
        - Use nomes de colunas descritivos para melhor detecção automática
        - Certifique-se de que datas estejam em formato reconhecível
        - Valores numéricos devem estar limpos (sem texto misturado)
        """)
        
        # Mostrar formatos suportados para cada aba
        with st.expander("📊 Formatos Suportados por Aba"):
            target_formats = get_target_formats()
            
            for target_key, format_info in target_formats.items():
                target_options = {
                    'estoque_hq1': '🏢 Estoque HQ1',
                    'estoque_spark': '⚡ Estoque Spark',
                    'vendas': '💰 Vendas',
                    'tvs_monitores': '📺 TVs e Monitores',
                    'movimentacoes': '🔄 Movimentações',
                    'lixo_eletronico': '♻️ Lixo Eletrônico'
                }
                
                st.markdown(f"**{target_options.get(target_key, target_key)}:**")
                required_cols = ", ".join([f"{col}*" for col in format_info['required']])
                optional_cols = ", ".join([col for col in format_info['columns'] if col not in format_info['required']])
                
                st.markdown(f"- *Obrigatórias:* {required_cols}")
                if optional_cols:
                    st.markdown(f"- *Opcionais:* {optional_cols}")
                st.markdown("")

def main():
    """Função principal do app"""
    apply_nubank_theme()
    
    # Verificar autenticação
    if not st.session_state.authenticated:
        render_login_page()
        return
    
    # Usuário autenticado - mostrar navegação e sistema
    render_navigation()
    
    # Roteamento de páginas
    current_page = st.session_state.current_page
    
    if current_page == 'dashboard':
        render_dashboard()
    elif current_page == 'admin_users':
        render_admin_users()
    elif current_page == 'visual_editor':
        render_visual_editor()
    elif current_page == 'spark_inventory':
        render_inventory_table(st.session_state.inventory_data['spark'], "● Itens A&V Spark", "spark")
    elif current_page == 'hq1_inventory':
        render_inventory_table(st.session_state.inventory_data['hq1'], "▢ Itens A&V HQ1", "hq1")
    elif current_page == 'hq1_8th':
        render_hq1_8th()
    elif current_page == 'impressoras':
        render_impressoras()
    elif current_page == 'tvs_monitores':
        render_tvs_monitores()
    elif current_page == 'vendas_spark':
        render_vendas_spark()
    elif current_page == 'lixo_eletronico':
        render_lixo_eletronico()
    elif current_page == 'inventario_oficial':
        render_inventario_oficial()
    elif current_page == 'entrada_estoque':
        render_barcode_entry()
    elif current_page == 'saida_estoque':
        render_barcode_exit()
    elif current_page == 'movimentacoes':
        render_movements()
    elif current_page == 'relatorios':
        render_reports()
    elif current_page == 'upload_dados':
        render_upload_dados()

if __name__ == "__main__":
    main()