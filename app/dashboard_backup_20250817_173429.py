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
import hashlib
import secrets

# Imports para email (opcionais)
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    from email.mime.base import MimeBase
    from email import encoders
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

# Imports para scanner de código de barras
try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration  # type: ignore
    import cv2  # type: ignore
    import numpy as np  # type: ignore
    from pyzbar import pyzbar  # type: ignore
    from PIL import Image  # type: ignore
    import pytesseract  # type: ignore
except ImportError:
    BARCODE_SCANNER_AVAILABLE = False

# Scanner sempre ativo se bibliotecas disponíveis
if 'BARCODE_SCANNER_AVAILABLE' not in locals():
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
            except Exception as e:
                pass  # Ignorar erros de OCR

        return detected_codes
    except Exception as e:
        st.error(f"Erro ao processar imagem: {str(e)}")
        return []

# ========================================================================================
# TEMA NUBANK - CORES E ESTILOS
# ========================================================================================

def apply_nubank_theme():
    """Aplica o tema customizável avançado baseado nas configurações do admin"""
    # Usar configurações personalizadas se existirem, senão usar padrão
    theme = getattr(st.session_state, 'theme_config', DEFAULT_THEME.copy())

    # Extrair configurações principais
    primary_color = theme.get('primary_color', DEFAULT_THEME['primary_color'])
    background_color = theme.get('background_color', DEFAULT_THEME['background_color'])
    text_color = theme.get('text_color', DEFAULT_THEME['text_color'])
    accent_color = theme.get('accent_color', DEFAULT_THEME['accent_color'])
    custom_css = theme.get('custom_css', '')

    # Novas configurações visuais
    font_family = theme.get('font_family', DEFAULT_THEME.get('font_family', 'Inter'))
    font_size = theme.get('font_size', DEFAULT_THEME.get('font_size', '16px'))
    heading_font = theme.get('heading_font', DEFAULT_THEME.get('heading_font', 'Inter'))
    heading_size = theme.get('heading_size', DEFAULT_THEME.get('heading_size', '2.5rem'))
    border_radius = theme.get('border_radius', DEFAULT_THEME.get('border_radius', '8px'))
    gradient_enabled = theme.get('gradient_enabled', DEFAULT_THEME.get('gradient_enabled', False))
    background_image = theme.get('background_image')
    background_image_opacity = theme.get('background_image_opacity', 0.1)
    background_position = theme.get('background_position', 'center')
    logo_image = theme.get('logo_image')
    logo_position = theme.get('logo_position', 'sidebar')
    logo_size = theme.get('logo_size', 150)
    text_shadow = theme.get('text_shadow', True)
    hover_effects = theme.get('hover_effects', True)
    shadow_intensity = theme.get('shadow_intensity', 'medium')

    # Configurar cores de gradiente se habilitado
    if gradient_enabled:
        gradient_start = theme.get('gradient_start', primary_color)
        gradient_end = theme.get('gradient_end', accent_color)
        gradient_direction = theme.get('gradient_direction', '90deg')
        primary_bg = f"linear-gradient({gradient_direction}, {gradient_start}, {gradient_end})"
    else:
        primary_bg = primary_color

    # Configurar imagem de fundo
    background_style = f"background-color: {background_color};"
    if background_image:
        background_style += f"""
        background-image: url('{background_image}');
            background-size: {background_position};
            background-repeat: no-repeat;
            background-position: center;
            background-attachment: fixed;
            """
        background_style += f"background-color: rgba({background_color}, {1 - background_image_opacity});"

    # Configurar sombras baseado na intensidade
    shadow_config = {
    'none': '0 0 0 rgba(0,0,0,0)',
        'light': '0 2px 4px rgba(0,0,0,0.1)',
        'medium': '0 4px 8px rgba(0,0,0,0.2)',
        'heavy': '0 8px 16px rgba(0,0,0,0.3)'
        }
    box_shadow = shadow_config.get(shadow_intensity, shadow_config['medium'])

    # Configurar efeitos de hover
    hover_transform = "transform: translateY(-2px);" if hover_effects else ""
    hover_shadow = "box-shadow: 0 6px 12px rgba(0,0,0,0.3);" if hover_effects else ""

    # Configurar sombra de texto
    text_shadow_css = "text-shadow: 1px 2px 4px rgba(0,0,0,0.4);" if text_shadow else ""

    # Adicionar logo se configurado
    logo_html = ""
    if logo_image and logo_position in ['header', 'both']:
        logo_html = f"""
        <div style="text-align: center; margin-bottom: 2rem;">
        <img src="{logo_image}" style="max-width: {logo_size}px; height: auto;" alt="Logo"/>
            </div>
        """

    # Adicionar logo na sidebar se configurado
    if logo_image and logo_position in ['sidebar', 'both']:
        st.sidebar.markdown(f"""
        <div style="text-align: center; margin: 1rem 0;">
        <img src="{logo_image}" style="max-width: {min(logo_size, 200)}px; height: auto;" alt="Logo"/>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    {logo_html}
    <style>
    /* Importar fontes do Google */
    @import url('https://fonts.googleapis.com/css2?family={font_family.replace(" ", "+")}:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family={heading_font.replace(" ", "+")}:wght@300;400;500;600;700;800&display=swap');

    .stApp {{
    {background_style}
        font-family: '{font_family}', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: {font_size} !important;
        color: {text_color} !important;
        }}

    .main-header {{
    background: {primary_bg} !important;
        padding: 2rem 1rem;
        border-radius: {border_radius};
        color: {text_color} !important;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: {box_shadow};
        transition: all 0.3s ease;
        }}

    .main-header:hover {{
    {hover_transform}
        {hover_shadow}
        }}

    .main-header * {{
    {text_shadow_css}
        }}

    .main-title {{
    font-family: '{heading_font}' !important;
        font-size: {heading_size} !important;
        font-weight: 700 !important;
        color: {text_color} !important;
        margin-bottom: 0.5rem !important;
        {text_shadow_css}
        }}

    .main-subtitle {{
    font-family: '{font_family}' !important;
        font-size: 1.2rem !important;
        color: {text_color} !important;
        opacity: 0.9 !important;
        {text_shadow_css}
        }}

    h1, h2, h3, h4, h5, h6 {{
    font-family: '{heading_font}' !important;
        {text_shadow_css}
        }}

    .stButton > button {{
    background: {primary_bg} !important;
        color: {text_color} !important;
        border: none !important;
        border-radius: {border_radius} !important;
        padding: 0.75rem 1.5rem !important;
        font-family: '{font_family}' !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: {box_shadow} !important;
        {text_shadow_css}
        }}

    .stButton > button:hover {{
    {hover_transform}
        {hover_shadow}
        {text_shadow_css}
        }}

    .stContainer, .element-container {{
    background: {primary_bg} !important;
        border-left: 4px solid {accent_color};
        border-radius: {border_radius};
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: {box_shadow};
        transition: all 0.3s ease;
        }}

    .stDataFrame {{
    background: {primary_bg} !important;
        border-radius: {border_radius};
        border-left: 4px solid {accent_color};
        overflow: hidden;
        box-shadow: {box_shadow};
        }}

    .stDataFrame th {{
    background: {primary_bg} !important;
        color: {text_color} !important;
        font-family: '{font_family}' !important;
        font-weight: 600 !important;
        {text_shadow_css}
        }}

    .stDataFrame td {{
    background: {primary_bg} !important;
        color: {text_color} !important;
        border-color: {accent_color} !important;
        font-family: '{font_family}' !important;
        }}

    .stTextInput > div > div > input, .stSelectbox > div > div,
    .stNumberInput > div > div > input, .stTextArea > div > div > textarea {{
    background: {primary_bg} !important;
        border: 2px solid {accent_color} !important;
        border-radius: {border_radius} !important;
        padding: 0.75rem !important;
        font-family: '{font_family}' !important;
        font-size: {font_size} !important;
        color: {text_color} !important;
        {text_shadow_css}
        }}

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {{
    color: rgba(255, 255, 255, 0.7) !important;
        opacity: 1 !important;
        }}

    .stExpander > div {{
    background: {primary_bg} !important;
        border: 2px solid {accent_color} !important;
        border-radius: {border_radius} !important;
        overflow: hidden;
        }}

    .stExpander summary {{
    background: {primary_bg} !important;
        color: {text_color} !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        font-family: '{font_family}' !important;
        }}

    .stSuccess {{
    background: {primary_bg} !important;
        color: {text_color} !important;
        border-radius: {border_radius} !important;
        {text_shadow_css}
        }}

    .stError {{
    background: linear-gradient(90deg, #DC3545 0%, #E74C3C 100%) !important;
        color: white !important;
        border-radius: {border_radius} !important;
        {text_shadow_css}
        }}

    .stWarning {{
    background: linear-gradient(90deg, #FFC107 0%, #F39C12 100%) !important;
        color: #333333 !important;
        border-radius: {border_radius} !important;
        text-shadow: 1px 2px 3px rgba(255, 255, 255, 0.6);
        }}

    .stInfo {{
    background: linear-gradient(90deg, #17A2B8 0%, #3498DB 100%) !important;
        color: white !important;
        border-radius: {border_radius} !important;
        {text_shadow_css}
        }}

    .metric-card {{
    background: {primary_bg} !important;
        border-radius: {border_radius};
        padding: 1.5rem;
        margin: 0.5rem 0;
        box-shadow: {box_shadow};
        border-left: 4px solid {accent_color};
        transition: all 0.3s ease;
        }}

    .metric-card:hover {{
    {hover_transform}
        {hover_shadow}
        }}

    .metric-value {{
    font-family: '{heading_font}' !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: {text_color} !important;
        {text_shadow_css}
        }}

    .metric-label {{
    font-family: '{font_family}' !important;
        font-size: 0.9rem !important;
        color: {text_color} !important;
        opacity: 0.9 !important;
        font-weight: 500 !important;
        {text_shadow_css}
        }}

    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6, .stText, label,
    .stSubheader, .stCaption {{
    color: {text_color} !important;
        font-family: '{font_family}' !important;
        }}

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stSubheader {{
    font-family: '{heading_font}' !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        margin-top: 1.5rem !important;
        {text_shadow_css}
        }}

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{
    background: {primary_bg} !important;
        border-radius: {border_radius} !important;
        padding: 0.5rem !important;
        }}

    .stTabs [data-baseweb="tab"] {{
    background: transparent !important;
        color: {text_color} !important;
        font-family: '{font_family}' !important;
        border-radius: {border_radius} !important;
        padding: 1rem 2rem !important;
        margin: 0 0.5rem !important;
        transition: all 0.3s ease !important;
        }}

    .stTabs [aria-selected="true"] {{
    background: {accent_color} !important;
        color: {text_color} !important;
        {text_shadow_css}
        }}

    /* File uploader */
    .stFileUploader {{
    background: {primary_bg} !important;
        border: 2px solid {accent_color} !important;
        border-radius: {border_radius} !important;
        padding: 1rem !important;
        }}

    .stFileUploader > div {{
    color: {text_color} !important;
        font-family: '{font_family}' !important;
        }}

    /* Sidebar customizations */
    .css-1d391kg {{
    background: {primary_bg} !important;
        border-right: 2px solid {accent_color} !important;
        }}

    .css-1d391kg .stMarkdown {{
    color: {text_color} !important;
        font-family: '{font_family}' !important;
        }}

    /* All form labels */
    .stSelectbox label, .stNumberInput label, .stTextInput label,
    .stTextArea label, .stColorPicker label, .stCheckbox label,
    .stRadio label, .stSlider label, .stDateInput label,
    .stTimeInput label, .stMultiSelect label {{
    color: {text_color} !important;
        font-family: '{font_family}' !important;
        font-weight: 600 !important;
        {text_shadow_css}
        }}

    /* Custom icons integration */
    .icon-dashboard::before {{ content: "{theme.get('custom_icons', {}).get('dashboard', '📊')}"; }}
    .icon-inventory::before {{ content: "{theme.get('custom_icons', {}).get('inventory', '📦')}"; }}
    .icon-users::before {{ content: "{theme.get('custom_icons', {}).get('users', '👥')}"; }}
    .icon-settings::before {{ content: "{theme.get('custom_icons', {}).get('settings', '⚙️')}"; }}
    .icon-logout::before {{ content: "{theme.get('custom_icons', {}).get('logout', '🚪')}"; }}
    .icon-add::before {{ content: "{theme.get('custom_icons', {}).get('add', '➕')}"; }}
    .icon-edit::before {{ content: "{theme.get('custom_icons', {}).get('edit', '✏️')}"; }}
    .icon-delete::before {{ content: "{theme.get('custom_icons', {}).get('delete', '🗑️')}"; }}
    .icon-save::before {{ content: "{theme.get('custom_icons', {}).get('save', '💾')}"; }}
    .icon-cancel::before {{ content: "{theme.get('custom_icons', {}).get('cancel', '❌')}"; }}

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
    'custom_css': '',
    # Novas configurações visuais
    'background_image': None,
    'background_image_opacity': 0.1,
    'font_family': 'Inter',
    'font_size': '16px',
    'heading_font': 'Inter',
    'heading_size': '2.5rem',
    'button_style': 'rounded',
    'border_radius': '8px',
    'shadow_intensity': 'medium',
    'custom_icons': {},
    'logo_image': None,
    'logo_position': 'sidebar'
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
        <p style="color: #666; font-size: 16px; margin-top: 0.5rem;">Sistema de Controle de Inventário</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Dados", "Gráficos"])


    with tab1:
        # Centralizar o formulário de login
                col1, col2, col3 = st.columns([1, 2, 1])

                with col2:
                    st.markdown("""
                    <div style='text-align: center; margin-bottom: 2rem;'>
                        <h2 style='color: white; margin: 0; font-size: 2rem; font-weight: 600;'>
                            Área de Login
                        </h2>
                        <p style='color: white; font-size: 14px; margin-top: 0.5rem;'>
                            Acesse sua conta com segurança
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

            # CSS para layout limpo sem ícones
            st.markdown("""
            <style>
            .password-help {
                position: absolute;
                    left: 50%;
                    top: 50%;
                    transform: translate(-50%, -50%);
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 12px;
                    font-style: italic;
                    pointer-events: none;
                    z-index: 10;
                    background: transparent;
                    padding: 4px 8px;
                    border-radius: 4px;
                    white-space: nowrap;
                    }
                .password-field-container {
                position: relative;
                    display: block;
                    }
                .password-field-container input {
                position: relative;
                    z-index: 1;
                    }
                /* Cores brancas para labels e textos */
                label {
                margin-bottom: 0.3rem !important;
                    color: white !important;
                    }
                /* Customizar cores de seleção para branco - removendo vermelho */
                .stTextInput input:focus,
                .stTextArea textarea:focus {
                border-color: white !important;
                    box-shadow: 0 0 0 1px white !important;
                    outline: none !important;
                    }
                .stTextInput input::selection,
                .stTextArea textarea::selection {
                background-color: white !important;
                    color: #333 !important;
                    }
                /* Remover cores vermelhas de clique/hover/active */
                .stTextInput input:active,
                .stTextArea textarea:active,
                .stButton button:active,
                .stTab button:active {
                border-color: white !important;
                    box-shadow: 0 0 0 1px white !important;
                    background-color: rgba(255, 255, 255, 0.1) !important;
                    }
                /* Tabs com cores brancas */
                .stTabs [data-baseweb="tab-list"] button {
                color: white !important;
                    }
                .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
                color: white !important;
                    border-bottom-color: white !important;
                    }
                /* Remover cores roxas de elementos interativos */
                .stMarkdown, .stText {
                color: white !important;
                    }
                /* Cores dos placeholders e textos - removendo backgrounds roxos */
                .stTextInput input {
                color: white !important;
                    background-color: transparent !important;
                    border: 1px solid rgba(255, 255, 255, 0.3) !important;
                    }
                .stTextInput input::placeholder {
                color: rgba(255, 255, 255, 0.6) !important;
                    }
                .stTextArea textarea {
                color: white !important;
                    background-color: transparent !important;
                    border: 1px solid rgba(255, 255, 255, 0.3) !important;
                    }
                .stTextArea textarea::placeholder {
                color: rgba(255, 255, 255, 0.6) !important;
                    }
                /* Remover backgrounds roxos de botões e elementos */
                .stButton button {
                background: #333 !important;
                    border: 1px solid rgba(255, 255, 255, 0.3) !important;
                    color: white !important;
                    }
                .stButton button:hover {
                background: #444 !important;
                    border: 1px solid rgba(255, 255, 255, 0.5) !important;
                    }
                /* Remover qualquer background roxo de containers */
                .stForm {
                background: transparent !important;
                    }
                .stContainer {
                background: transparent !important;
                    }
                /* Remover todos os elementos roxos vazios */
                .stTabs [data-baseweb="tab-list"] {
                background: transparent !important;
                    }
                .stTabs [data-baseweb="tab-panel"] {
                background: transparent !important;
                    }
                /* Garantir que nenhum elemento tenha cor roxa */
                * {
                color: inherit !important;
                    }
                /* Remover backgrounds roxos do Streamlit */
                .stApp > header {
                background: transparent !important;
                    }
                .stApp [data-testid="stSidebar"] {
                background: transparent !important;
                    }
                /* Cores específicas para evitar vermelho em cliques */
                input:focus, textarea:focus, button:focus {
                border-color: white !important;
                    box-shadow: 0 0 0 1px white !important;
                    }
                button:active, input:active, textarea:active {
                background-color: rgba(255, 255, 255, 0.1) !important;
                    border-color: white !important;
                    }
                </style>
            """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("<div style='text-align: center; margin: 1rem 0;'><p style='color: white; font-size: 13px;'>Entre com suas credenciais para acessar o sistema</p></div>", unsafe_allow_html=True)

                # Campos simples sem ícones
                st.markdown("<label style='font-size: 14px; color: white; font-weight: 500;'>Email</label>", unsafe_allow_html=True)
                email = st.text_input("Email", placeholder="seu.email@empresa.com", help="Digite seu email corporativo", label_visibility="collapsed", key="email_input")

                st.markdown("<label style='font-size: 14px; color: white; font-weight: 500; margin-top: 1rem; display: block;'>Senha</label>", unsafe_allow_html=True)

                # Container para campo de senha com frase no meio
                st.markdown('<div class="password-field-container">', unsafe_allow_html=True)
                password = st.text_input("Senha", type="password", placeholder="Digite aqui sua senha de acesso", help="", label_visibility="collapsed", key="password_input")
                st.markdown('<div class="password-help">Pressione Enter para enviar o formulário</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                if st.form_submit_button("Entrar no Sistema", use_container_width=True):
                    if not email or not password:
                        st.error("× Digite seu email e senha")
                    elif email in st.session_state.usuarios_pendentes:
                    st.warning("⧖ Sua solicitação está pendente de aprovação pelo administrador")
                    else:
                    success, message = authenticate_user(email, password)
                    if success:
                            st.success(f"✓ {message} Bem-vindo(a), {st.session_state.users_db[email]['nome']}")
                            st.rerun()
                        else:
                            st.error(f"× {message}")

with with with with with with tab2:
    # Centralizar o formulário de registro
    col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
                    st.markdown("""<div></div>""")  # Fixed string
                    <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='color: white; margin: 0; font-size: 2rem; font-weight: 600;'>
                Solicitar Acesso
                    </h2>
                <p style='color: white; font-size: 14px; margin-top: 0.5rem;'>
                Solicite aprovação do administrador
                    </p>
                </div>
            """, unsafe_allow_html=True)

        with st.form("registro_form"):
            st.markdown("<div style='text-align: center; margin: 1rem 0;'><p style='color: white; font-size: 13px;'>Preencha os dados para solicitar acesso</p></div>", unsafe_allow_html=True)

                # Campos simples sem ícones
                st.markdown("<label style='font-size: 14px; color: white; font-weight: 500;'>Nome Completo</label>", unsafe_allow_html=True)
                nome = st.text_input("Nome", placeholder="Seu nome completo", help="Digite seu nome completo", label_visibility="collapsed", key="nome_input")

                st.markdown("<label style='font-size: 14px; color: white; font-weight: 500; margin-top: 1rem; display: block;'>Email Corporativo</label>", unsafe_allow_html=True)
                email = st.text_input("Email", placeholder="seu.email@empresa.com", help="Use seu email corporativo", label_visibility="collapsed", key="email_registro_input")

                st.markdown("<label style='font-size: 14px; color: white; font-weight: 500; margin-top: 1rem; display: block;'>Senha</label>", unsafe_allow_html=True)
                password = st.text_input("Senha", type="password", placeholder="Crie uma senha segura aqui",
                help="Mínimo 6 caracteres - Use letras, números e símbolos", label_visibility="collapsed", key="senha_registro_input")

                                       st.markdown("<label style='font-size: 14px; color: white; font-weight: 500; margin-top: 1rem; display: block;'>Confirmar Senha</label>", unsafe_allow_html=True)
                password_confirm = st.text_input("Confirmar", type="password", placeholder="Confirme sua senha novamente", help="Digite a mesma senha novamente", label_visibility="collapsed", key="confirma_senha_input")

                st.markdown("<label style='font-size: 14px; color: white; font-weight: 500; margin-top: 1rem; display: block;'>Justificativa</label>", unsafe_allow_html=True)
                justificativa = st.text_area("Justificativa",
                placeholder="Explique por que precisa acessar o sistema de estoque...",
                                       help="Descreva sua função e motivo para acessar o sistema (mínimo 20 caracteres)", label_visibility="collapsed", key="justificativa_input")

                st.markdown("<div style='text-align: center; margin: 1rem 0; padding: 0.5rem; background: transparent; border-radius: 6px; color: white; font-size: 12px; font-style: italic;'>Pressione Enter para enviar a solicitação</div>", unsafe_allow_html=True)

                if st.form_submit_button("Solicitar Acesso ao Sistema", use_container_width=True):
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

def upload_image_to_base64(uploaded_file):
    """Converte arquivo de imagem para base64"""
    if uploaded_file is not None:
        import base64
        bytes_data = uploaded_file.getvalue()
        base64_str = base64.b64encode(bytes_data).decode()
        return f"data:{uploaded_file.type};base64,{base64_str}"
        return None

def render_visual_editor():
    """Renderiza o editor visual avançado para customização completa do tema (apenas admin)"""
    if not is_admin(st.session_state.current_user):
        st.error("× Acesso negado. Apenas administradores podem acessar esta área.")
        return

    st.markdown('<div class="main-header"><h1 class="main-title">🎨 Editor Visual Avançado</h1><p class="main-subtitle">Personalize completamente a aparência do sistema</p></div>', unsafe_allow_html=True)

    # Tabs para organizar as configurações
    tab1, tab2 = st.tabs(["Dados", "Gráficos"])
    with tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🎨 Cores & Gradientes",
        "🖼️ Imagens & Logos",
        "🔤 Tipografia",
        "🎯 Ícones",
        "🎪 Efeitos Visuais",
        "👁️ Preview"
        ])

    with tab1:  # Cores & Gradientes
        st.subheader("🎨 Configurações de Cores")

        col1, col2 = st.columns(2)
        with col1:
            primary_color = st.color_picker(
                    "🟣 Cor Primária",
                value=st.session_state.theme_config.get('primary_color', DEFAULT_THEME['primary_color']),
                help="Cor principal do tema (botões, destaques)"
                )

            background_color = st.color_picker(
            "⬛ Cor de Fundo",
                value=st.session_state.theme_config.get('background_color', DEFAULT_THEME['background_color']),
                help="Cor de fundo principal do app"
                )

            accent_color = st.color_picker(
            "💎 Cor de Destaque",
                value=st.session_state.theme_config.get('accent_color', DEFAULT_THEME['accent_color']),
                help="Cor para elementos de destaque (bordas, foco)"
                )

        with col2:
                    text_color = st.selectbox(
                    "📝 Cor do Texto",
                options=["white", "black", "#333333", "#555555", "#777777"],
                index=0 if st.session_state.theme_config.get('text_color', 'white') == 'white' else 1,
                help="Cor principal do texto"
                )

            secondary_color = st.color_picker(
            "🔸 Cor Secundária",
                value=st.session_state.theme_config.get('secondary_color', '#444444'),
                help="Cor secundária para elementos menos importantes"
                )

            success_color = st.color_picker(
            "✅ Cor de Sucesso",
                value=st.session_state.theme_config.get('success_color', '#28a745'),
                help="Cor para mensagens de sucesso"
                )

        st.subheader("🌈 Configurações de Gradiente")
        col3, col4 = st.columns(2)
        with col3:
            gradient_enabled = st.checkbox(
            "🎨 Habilitar Gradientes",
                value=st.session_state.theme_config.get('gradient_enabled', False),
                help="Adicionar efeitos de gradiente aos elementos"
                )

            if gradient_enabled:
                gradient_direction = st.selectbox(
                "📐 Direção do Gradiente",
                    options=["90deg", "45deg", "135deg", "180deg", "270deg"],
                    index=0,
                    help="Direção do gradiente"
                    )

        with col4:
            if gradient_enabled:
                gradient_start = st.color_picker(
                "🎯 Cor Inicial do Gradiente",
                    value=st.session_state.theme_config.get('gradient_start', primary_color),
                    help="Cor inicial do gradiente"
                    )

                gradient_end = st.color_picker(
                "🏁 Cor Final do Gradiente",
                    value=st.session_state.theme_config.get('gradient_end', accent_color),
                    help="Cor final do gradiente"
                    )

    with with with with with with tab2:  # Imagens & Logos
        st.subheader("🖼️ Imagem de Fundo")

        background_image_file = st.file_uploader(
        "📷 Upload de Imagem de Fundo",
            type=['png', 'jpg', 'jpeg', 'gif', 'webp'],
            help="Faça upload de uma imagem para usar como fundo"
            )

        if background_image_file:
            background_image_data = upload_image_to_base64(background_image_file)
            if background_image_data:
                st.image(background_image_file, caption="Preview da Imagem de Fundo", width=300)

                background_opacity = st.slider(
                "🔍 Opacidade da Imagem de Fundo",
                    min_value=0.0,
                    max_value=1.0,
                    value=st.session_state.theme_config.get('background_image_opacity', 0.1),
                    step=0.05,
                    help="Transparência da imagem de fundo"
                    )

                background_position = st.selectbox(
                "📍 Posição da Imagem",
                    options=["center", "top", "bottom", "left", "right", "cover", "contain"],
                    index=0,
                    help="Como posicionar a imagem de fundo"
                    )

        st.subheader("🏢 Logo da Empresa")

        logo_file = st.file_uploader(
        "🎯 Upload do Logo",
            type=['png', 'jpg', 'jpeg', 'svg'],
            help="Faça upload do logo da empresa"
            )

        if logo_file:
            logo_data = upload_image_to_base64(logo_file)
            if logo_data:
                st.image(logo_file, caption="Preview do Logo", width=200)

                col_logo1, col_logo2 = st.columns(2)
                with col_logo1:
                    logo_position = st.selectbox(
                    "📍 Posição do Logo",
                        options=["sidebar", "header", "both", "none"],
                        index=0,
                        help="Onde exibir o logo"
                        )

                with col_logo2:
                    logo_size = st.slider(
                    "📏 Tamanho do Logo",
                        min_value=50,
                        max_value=300,
                        value=st.session_state.theme_config.get('logo_size', 150),
                        step=10,
                        help="Tamanho do logo em pixels"
                        )

    with tab3:  # Tipografia
        st.subheader("🔤 Configurações de Fonte")

        col_font1, col_font2 = st.columns(2)
        with col_font1:
            font_family = st.selectbox(
            "🔤 Família da Fonte Principal",
                options=[
                "Inter", "Roboto", "Open Sans", "Lato", "Montserrat",
                    "Poppins", "Source Sans Pro", "Arial", "Helvetica", "Georgia"
                    ],
                index=0,
                help="Fonte principal do sistema"
                )

            font_size = st.selectbox(
            "📏 Tamanho da Fonte Base",
                options=["12px", "14px", "16px", "18px", "20px"],
                index=2,
                help="Tamanho base da fonte"
                )

            line_height = st.selectbox(
            "📐 Altura da Linha",
                options=["1.2", "1.4", "1.5", "1.6", "1.8"],
                index=2,
                help="Espaçamento entre linhas"
                )

        with col_font2:
            heading_font = st.selectbox(
            "📰 Fonte dos Títulos",
                options=[
                "Inter", "Roboto", "Montserrat", "Poppins", "Playfair Display",
                    "Oswald", "Merriweather", "Source Sans Pro"
                    ],
                index=0,
                help="Fonte para títulos e cabeçalhos"
                )

            heading_size = st.selectbox(
            "📏 Tamanho dos Títulos",
                options=["1.8rem", "2rem", "2.2rem", "2.5rem", "3rem"],
                index=3,
                help="Tamanho dos títulos principais"
                )

            font_weight = st.selectbox(
            "💪 Peso da Fonte",
                options=["300", "400", "500", "600", "700", "800"],
                index=3,
                help="Espessura da fonte"
                )

        st.subheader("🎭 Efeitos de Texto")
        col_text1, col_text2 = st.columns(2)
        with col_text1:
            text_shadow = st.checkbox(
            "🌟 Sombra no Texto",
                value=st.session_state.theme_config.get('text_shadow', True),
                help="Adicionar sombra ao texto"
                )

        with col_text2:
            text_transform = st.selectbox(
            "🔄 Transformação do Texto",
                options=["none", "uppercase", "lowercase", "capitalize"],
                index=0,
                help="Transformação automática do texto"
                )

    with tab4:  # Ícones
        st.subheader("🎯 Personalização de Ícones")

        st.info("💡 Aqui você pode personalizar os ícones usados em todo o sistema")

        # Ícones padrão do sistema
        default_icons = {
        "dashboard": "📊",
            "inventory": "📦",
            "users": "👥",
            "settings": "⚙️",
            "logout": "🚪",
            "add": "➕",
            "edit": "✏️",
            "delete": "🗑️",
            "save": "💾",
            "cancel": "❌"
            }

        st.subheader("🔧 Ícones do Sistema")
        col_icon1, col_icon2 = st.columns(2)

        custom_icons = st.session_state.theme_config.get('custom_icons', {})

        for idx, (icon_key, default_icon) in enumerate(default_icons.items()):
            col = col_icon1 if idx % 2 == 0 else col_icon2
            with col:
                current_icon = custom_icons.get(icon_key, default_icon)
                new_icon = st.text_input(
                f"{default_icon} {icon_key.title()}",
                    value=current_icon,
                    max_chars=4,
                    help=f"Ícone para {icon_key}"
                    )
                custom_icons[icon_key] = new_icon

        # Upload de ícones personalizados
        st.subheader("📤 Upload de Ícones Personalizados")
        uploaded_icon = st.file_uploader(
        "🎨 Upload de Ícone Personalizado",
            type=['png', 'jpg', 'jpeg', 'svg'],
            help="Faça upload de ícones personalizados"
            )

        if uploaded_icon:
            icon_data = upload_image_to_base64(uploaded_icon)
            if icon_data:
                st.image(uploaded_icon, caption="Preview do Ícone", width=100)
                icon_name = st.text_input("Nome do Ícone", placeholder="nome_do_icone")
                if icon_name and st.button("💾 Salvar Ícone"):
                    if 'uploaded_icons' not in st.session_state.theme_config:
                        st.session_state.theme_config['uploaded_icons'] = {}
                        st.session_state.theme_config['uploaded_icons'][icon_name] = icon_data
                    st.success(f"✅ Ícone '{icon_name}' salvo!")

    with tab5:  # Efeitos Visuais
        st.subheader("🎪 Efeitos e Animações")

        col_effect1, col_effect2 = st.columns(2)
        with col_effect1:
            border_radius = st.slider(
            "🔘 Raio das Bordas",
                min_value=0,
                max_value=30,
                value=int(st.session_state.theme_config.get('border_radius', '8px').replace('px', '')),
                help="Arredondamento das bordas dos elementos"
                )

            shadow_intensity = st.selectbox(
            "🌫️ Intensidade das Sombras",
                options=["none", "light", "medium", "heavy"],
                index=2,
                help="Intensidade das sombras dos elementos"
                )

            animation_speed = st.selectbox(
            "⚡ Velocidade das Animações",
                options=["slow", "normal", "fast"],
                index=1,
                help="Velocidade das transições e animações"
                )

        with col_effect2:
            button_style = st.selectbox(
            "🔲 Estilo dos Botões",
                options=["rounded", "square", "pill", "outline"],
                index=0,
                help="Estilo visual dos botões"
                )

            hover_effects = st.checkbox(
            "✨ Efeitos de Hover",
                value=st.session_state.theme_config.get('hover_effects', True),
                help="Ativar efeitos ao passar o mouse"
                )

            blur_backgrounds = st.checkbox(
            "🌀 Backgrounds Desfocados",
                value=st.session_state.theme_config.get('blur_backgrounds', False),
                help="Aplicar efeito de desfoque aos fundos"
                )

    with tab6:  # Preview
        st.subheader("👁️ Preview em Tempo Real")

        # Aplicar configurações temporárias para preview
        preview_config = {
        'primary_color': primary_color,
            'background_color': background_color,
            'accent_color': accent_color,
            'text_color': text_color,
            'gradient_enabled': gradient_enabled,
            'font_family': font_family,
            'font_size': font_size,
            'heading_font': heading_font,
            'heading_size': heading_size,
            'border_radius': f"{border_radius}px",
            'custom_icons': custom_icons
            }

        if 'gradient_start' in locals() and gradient_enabled:
            preview_config.update({
            'gradient_direction': gradient_direction,
                'gradient_start': gradient_start,
                'gradient_end': gradient_end
                })

        if 'background_image_file' in locals() and background_image_file:
            preview_config.update({
            'background_image': upload_image_to_base64(background_image_file),
                'background_image_opacity': background_opacity,
                'background_position': background_position
                })

        # Mostrar preview
        st.markdown("### 🎨 Preview do Tema")
        with st.container():
            st.markdown(f"""
            <div style="
            background: {'linear-gradient(' + preview_config.get('gradient_direction', '90deg') + ', ' + preview_config.get('gradient_start', primary_color) + ', ' + preview_config.get('gradient_end', accent_color) + ')' if gradient_enabled else primary_color};
                color: {text_color};
                padding: 2rem;
                border-radius: {border_radius}px;
                font-family: {font_family};
                font-size: {font_size};
                margin: 1rem 0;
                box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                ">
            <h2 style="font-family: {heading_font}; font-size: {heading_size}; margin: 0 0 1rem 0;">
                {custom_icons.get('dashboard', '📊')} Dashboard Preview
                    </h2>
                <p>Este é um preview do seu tema personalizado em tempo real!</p>
                <button style="
                background: {primary_color};
                    color: {text_color};
                    border: none;
                    padding: 0.5rem 1rem;
                    border-radius: {border_radius}px;
                    font-family: {font_family};
                    cursor: pointer;
                    ">
                {custom_icons.get('save', '💾')} Botão de Exemplo
                    </button>
                </div>
            """, unsafe_allow_html=True)

    # Botões de ação na parte inferior
    st.divider()
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

    with col_btn1:
        if st.button("💾 Salvar Configurações", use_container_width=True):
            # Salvar todas as configurações
            new_config = {
            'primary_color': primary_color,
                'background_color': background_color,
                'accent_color': accent_color,
                'text_color': text_color,
                'gradient_enabled': gradient_enabled,
                'font_family': font_family,
                'font_size': font_size,
                'heading_font': heading_font,
                'heading_size': heading_size,
                'border_radius': f"{border_radius}px",
                'shadow_intensity': shadow_intensity,
                'button_style': button_style,
                'custom_icons': custom_icons,
                'hover_effects': hover_effects if 'hover_effects' in locals() else True,
                'blur_backgrounds': blur_backgrounds if 'blur_backgrounds' in locals() else False,
                'text_shadow': text_shadow if 'text_shadow' in locals() else True,
                'text_transform': text_transform if 'text_transform' in locals() else 'none',
                'line_height': line_height if 'line_height' in locals() else '1.5',
                'font_weight': font_weight if 'font_weight' in locals() else '600',
                'animation_speed': animation_speed if 'animation_speed' in locals() else 'normal'
                }

            # Adicionar configurações condicionais
            if gradient_enabled and 'gradient_start' in locals():
                new_config.update({
                'gradient_direction': gradient_direction,
                    'gradient_start': gradient_start,
                    'gradient_end': gradient_end
                    })

            if 'background_image_file' in locals() and background_image_file:
                new_config.update({
                'background_image': upload_image_to_base64(background_image_file),
                    'background_image_opacity': background_opacity,
                    'background_position': background_position
                    })

            if 'logo_file' in locals() and logo_file:
                new_config.update({
                'logo_image': upload_image_to_base64(logo_file),
                    'logo_position': logo_position,
                    'logo_size': logo_size
                    })

            if 'secondary_color' in locals():
                new_config['secondary_color'] = secondary_color

            if 'success_color' in locals():
                new_config['success_color'] = success_color

            st.session_state.theme_config.update(new_config)
            st.success("✅ Todas as configurações visuais foram salvas!")
            st.rerun()

    with col_btn2:
        if st.button("🔄 Aplicar Tema", use_container_width=True):
            st.success("🎨 Tema aplicado! Recarregando...")
            st.rerun()

    with col_btn3:
        if st.button("↩️ Restaurar Padrão", use_container_width=True):
            st.session_state.theme_config = DEFAULT_THEME.copy()
            st.success("🔧 Tema restaurado para o padrão!")
            st.rerun()

    with col_btn4:
        if st.button("📥 Exportar Tema", use_container_width=True):
            theme_json = json.dumps(st.session_state.theme_config, indent=2)
            st.download_button(
            label="💾 Download do Tema",
                data=theme_json,
                file_name="tema_personalizado.json",
                mime="application/json",
                use_container_width=True
                )

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
        'tvs_monitores': '▢ TVs e Monitores',
        'impressoras_status': '🖨️ Status Impressoras',
        'grab_and_go': '🎯 Grab & Go Perdas',
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

        st.plotly_chart(fig, use_container_width=True))

    with col2:
                    st.subheader("📊 Status de Conferência")

        # Calcular percentuais para cada local
        percentual_spark = (conferidos_spark / total_spark * 100) if total_spark > 0 else 0
        percentual_hq1 = (conferidos_hq1 / total_hq1 * 100) if total_hq1 > 0 else 0

        # Gráfico de barras modernizado com gradientes e animações
        status_data = pd.DataFrame({
        'Local': ['SPARK', 'HQ1'],
            'Conferidos': [conferidos_spark, conferidos_hq1],
            'Pendentes': [total_spark - conferidos_spark, total_hq1 - conferidos_hq1],
            'Total': [total_spark, total_hq1],
            'Percentual': [percentual_spark, percentual_hq1]
            })

        fig = go.Figure()

        # Barras com gradiente e hover melhorado
        fig.add_trace(go.Bar(
        name='✅ Conferidos',
            x=status_data['Local'],
            y=status_data['Conferidos'],
            marker=dict(
            color='rgba(34, 197, 94, 0.8)',
                line=dict(color='rgba(34, 197, 94, 1)', width=2)
                ),
            text=[f'{val}<br>({perc:.1f}%)' for val, perc in zip(status_data['Conferidos'], status_data['Percentual'])],
            textposition='inside',
            textfont=dict(color='white', size=12, family='Arial Black'),
            hovertemplate='<b>%{x}</b><br>' +
            'Conferidos: <b>%{y}</b><br>' +
                         'Percentual: <b>%{customdata:.1f}%</b><br>' +
                         '<extra></extra>',
                         customdata=status_data['Percentual']
            ))

        fig.add_trace(go.Bar(
        name='⏳ Pendentes',
            x=status_data['Local'],
            y=status_data['Pendentes'],
            marker=dict(
            color='rgba(239, 68, 68, 0.8)',
                line=dict(color='rgba(239, 68, 68, 1)', width=2)
                ),
            text=[f'{val}' if val > 0 else '' for val in status_data['Pendentes']],
            textposition='inside',
            textfont=dict(color='white', size=12, family='Arial Black'),
            hovertemplate='<b>%{x}</b><br>' +
            'Pendentes: <b>%{y}</b><br>' +
                         'Restante: <b>%{customdata:.1f}%</b><br>' +
                         '<extra></extra>',
                         customdata=[100-perc for perc in status_data['Percentual']]
            ))

        # Layout modernizado com animações e estilo profissional
        fig.update_layout(
        title=dict(
            text='📊 Status de Conferência por Local',
                x=0.5,
                font=dict(size=18, color='white', family='Arial Black')
                ),
            xaxis=dict(
            title=dict(text='Local', font=dict(size=14, color='white')),
                tickfont=dict(size=13, color='white'),
                showgrid=False,
                zeroline=False
                ),
            yaxis=dict(
            title=dict(text='Quantidade de Itens', font=dict(size=14, color='white')),
                tickfont=dict(size=12, color='white'),
                showgrid=True,
                gridcolor='rgba(255, 255, 255, 0.1)',
                zeroline=False
                ),
            barmode='stack',
            height=400,
            font=dict(size=14, color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(
            orientation='h',
                x=0.5,
                y=-0.1,
                xanchor='center',
                font=dict(size=12, color='white')
                ),
            margin=dict(t=60, b=80, l=60, r=40),
            # Adicionar animações
            transition=dict(duration=500, easing='cubic-in-out')
            )

        # Adicionar anotações com insights
        if percentual_conferido > 80:
            fig.add_annotation(
            x=0.5, y=1.05,
                xref='paper', yref='paper',
                text='🎯 Excelente taxa de conferência!',
                showarrow=False,
                font=dict(size=12, color='#22C55E'),
                bgcolor='rgba(34, 197, 94, 0.2)',
                bordercolor='#22C55E',
                borderwidth=1
                )
        elif percentual_conferido < 50:
            fig.add_annotation(
            x=0.5, y=1.05,
                xref='paper', yref='paper',
                text='⚠️ Atenção: Baixa taxa de conferência',
                showarrow=False,
                font=dict(size=12, color='#EF4444'),
                bgcolor='rgba(239, 68, 68, 0.2)',
                bordercolor='#EF4444',
                borderwidth=1
                )

        st.plotly_chart(fig, use_container_width=True))

        # Adicionar mini cards com estatísticas
        col_stat1, col_stat2 = st.columns(2)

        with col_stat1:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #22C55E, #16A34A); padding: 15px; border-radius: 10px; text-align: center; color: white; margin: 5px;'>
            <div style='font-size: 24px; font-weight: bold;'>{total_conferidos}</div>
                <div style='font-size: 12px; opacity: 0.9;'>Total Conferidos</div>
                <div style='font-size: 14px; font-weight: bold;'>{percentual_conferido:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

        with col_stat2:
            total_pendentes = total_items - total_conferidos
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #EF4444, #DC2626); padding: 15px; border-radius: 10px; text-align: center; color: white; margin: 5px;'>
            <div style='font-size: 24px; font-weight: bold;'>{total_pendentes}</div>
                <div style='font-size: 12px; opacity: 0.9;'>Pendentes</div>
                <div style='font-size: 14px; font-weight: bold;'>{100-percentual_conferido:.1f}%</div>
                </div>
            """, unsafe_allow_html=True)

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
    st.markdown("""<div></div>""")  # Fixed string
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
        st.markdown("""<div></div>""")  # Fixed string
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
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
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
                    st.markdown("""<div></div>""")  # Fixed string
                    <div class="metric-card">
        <div class="metric-value">92%</div>
            <div class="metric-label">✓ Itens Conferidos</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
                    st.markdown("""<div></div>""")  # Fixed string
                    <div class="metric-card">
        <div class="metric-value">15/03/2024</div>
            <div class="metric-label">⎙ Última Atualização</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""<div></div>""")  # Fixed string
        <div class="metric-card">
        <div class="metric-value">◐ Aprovado</div>
            <div class="metric-label">✓ Status Auditoria</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""<div></div>""")  # Fixed string
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
    st.markdown("""<div></div>""")  # Fixed string
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
        st.markdown("""<div></div>""")  # Fixed string
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
                except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
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
    st.markdown("""<div></div>""")  # Fixed string
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
        st.markdown("""<div></div>""")  # Fixed string
        <div style="text-align: center; padding: 1rem 0;">
        <h3 style="color: #8A05BE; margin: 0;">🎯 Scanner Inteligente de Códigos</h3>
            <p style="color: #666; margin: 0.5rem 0;">📷 Escaneie códigos de barras em tempo real ou faça upload de imagens</p>
            </div>
        """, unsafe_allow_html=True)

        # Mostrar status do scanner - sempre ativo
        st.markdown("""<div></div>""")  # Fixed string
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
                    except Exception as e:
                                st.error(f"❌ Erro: {str(e)}")
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
                    st.markdown("""<div></div>""")  # Fixed string
                    <div class="metric-card">
        <div class="metric-value">127</div>
            <div class="metric-label">▤ Total Movimentações</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
                    st.markdown("""<div></div>""")  # Fixed string
                    <div class="metric-card">
        <div class="metric-value">85</div>
            <div class="metric-label">↘ Entradas</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""<div></div>""")  # Fixed string
        <div class="metric-card">
        <div class="metric-value">42</div>
            <div class="metric-label">↗ Saídas</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""<div></div>""")  # Fixed string
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
                    st.markdown("""<div></div>""")  # Fixed string
                    <div class="metric-card">
            <div class="metric-value">247</div>
                <div class="metric-label">■ Total de Itens</div>
                </div>
            """, unsafe_allow_html=True)

        with col2:
                    st.markdown("""<div></div>""")  # Fixed string
                    <div class="metric-card">
            <div class="metric-value">R$ 1.2M</div>
                <div class="metric-label">$ Valor Total</div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
        st.markdown("""<div></div>""")  # Fixed string
        <div class="metric-card">
            <div class="metric-value">89%</div>
                <div class="metric-label">✓ Taxa Conferência</div>
                </div>
            """, unsafe_allow_html=True)

        with col4:
        st.markdown("""<div></div>""")  # Fixed string
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
        csv_content = f"Relatório,Data,Valor
        {tipo_relatorio},{datetime.now().strftime('%Y-%m-%d')},R$ 1.200.000"
st.download_button(
        label="📥 Download CSV",
            data=csv_content,
            file_name=f"relatorio_{tipo_relatorio.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
            )

def render_impressoras_status():
    """Renderiza a página de monitoramento de status das impressoras"""
    import subprocess
    import platform
    import time
    import re

    st.markdown("## 🖨️ Status de Impressoras")
    st.markdown("### 📍 Monitoramento em Tempo Real - Porta 43 dos Switches")

    # Inicializar dados das impressoras no session_state
    if 'impressoras_data' not in st.session_state:
        st.session_state.impressoras_data = {
        "HQ1": {
            "info": {"login": "admin", "senha": "Ultravioleta"},
                "impressoras": [
                {"id": "hq1_001", "local": "Térreo - Recepção", "ip": "172.25.61.53", "serial": "X3B7034483", "papercut": False, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "hq1_002", "local": "2º Andar - L Maior", "ip": "172.25.61.20", "serial": "X3B7034452", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "hq1_003", "local": "2º Andar - L Menor", "ip": "172.25.61.21", "serial": "X3B703447320", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "hq1_004", "local": "4º Andar - L Maior", "ip": "172.25.61.40", "serial": "X3B7034450", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "hq1_005", "local": "4º Andar - L Menor", "ip": "172.25.61.41", "serial": "X3B7034746", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "hq1_006", "local": "6º Andar - L Maior", "ip": "172.25.61.50", "serial": "X3B7034471", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "hq1_007", "local": "6º Andar - L Menor", "ip": "172.25.61.60", "serial": "X3B7034438", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "hq1_008", "local": "8º Andar - L Maior", "ip": "172.25.61.48", "serial": "X3B7034440", "papercut": False, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "hq1_009", "local": "8º Andar - L Menor", "ip": "172.25.61.81", "serial": "X3B7034468", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "hq1_010", "local": "MTEAM", "ip": "172.25.61.66", "serial": "X3B7034448", "papercut": False, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "hq1_011", "local": "MENSAGERIA", "ip": "172.25.61.11", "serial": "X3B7034486", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"}
                    ]
                },
            "HQ2": {
            "info": {"login": "admin", "senha": "Ultravioleta"},
                "impressoras": [
                {"id": "hq2_001", "local": "2º Andar", "ip": "172.26.61.20", "serial": "X3B7034750", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "hq2_002", "local": "4º Andar", "ip": "172.26.61.40", "serial": "X3B7034444", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "hq2_003", "local": "8º Andar", "ip": "172.26.61.80", "serial": "X3B7034488", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "hq2_004", "local": "9º Andar - Ambulatório", "ip": "172.26.61.90", "serial": "X3B7034477", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "hq2_005", "local": "12º Andar", "ip": "172.26.61.120", "serial": "X3B7034481", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "hq2_006", "local": "15º Andar", "ip": "172.26.61.150", "serial": "X3B7034752", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "hq2_007", "local": "16º Andar", "ip": "172.26.61.160", "serial": "X3B7034479", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"}
                    ]
                },
            "SPARK": {
            "info": {"login": "admin", "senha": "Ultravioleta"},
                "impressoras": [
                {"id": "spark_001", "local": "Térreo - Recepção", "ip": "172.30.139.8", "serial": "X3B7034704", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "spark_002", "local": "Térreo - Enfermaria", "ip": "172.30.139.5", "serial": "X3B7034620", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "spark_003", "local": "Térreo - Mensageria", "ip": "172.30.139.19", "serial": "X3B7034989", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "spark_004", "local": "1º Andar - Lado A", "ip": "172.30.139.10", "serial": "X3B7034959", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "spark_005", "local": "1º Andar - Lado B", "ip": "172.30.139.11", "serial": "X3B7034624", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "spark_006", "local": "2º Andar - Lado A", "ip": "172.30.139.20", "serial": "X3B7034733", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "spark_007", "local": "2º Andar - Lado B", "ip": "172.30.139.41", "serial": "X3B7034691", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "spark_008", "local": "3º Andar - MTEAM Lado A", "ip": "172.30.139.40", "serial": "X3B7034698", "papercut": False, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "spark_009", "local": "3º Andar - Lado A", "ip": "172.30.139.30", "serial": "X3B7035080", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"},
                    {"id": "spark_010", "local": "3º Andar - Lado B", "ip": "172.30.139.35", "serial": "X3B7034696", "papercut": True, "modelo": "HP LaserJet", "status_manual": "Ativo"}
                    ]
                }
            }

    # Usar dados do session_state
    impressoras_data = st.session_state.impressoras_data

    def ping_ip(ip):
        """Testa conectividade com o IP"""
        try:
            param = "-n" if platform.system().lower() == "windows" else "-c"
            result = subprocess.run(
            ["ping", param, "1", ip],
                capture_output=True,
                text=True,
                timeout=3
                )
            return result.returncode == 0
        except:
            return False

    def validate_ip(ip):
        """Valida formato do IP"""
        pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return re.match(pattern, ip) is not None

    # Atualizar status se solicitado
    if 'printer_status_cache' not in st.session_state:
        st.session_state.printer_status_cache = {}

    # Verificar impressoras offline e exibir alertas
    offline_printers = []
    for local_name, local_data in impressoras_data.items():
        for printer in local_data["impressoras"]:
            if printer["ip"] in st.session_state.printer_status_cache:
                if not st.session_state.printer_status_cache[printer["ip"]]:
                    offline_printers.append(f"{printer['local']} ({printer['ip']}) - {local_name}")

    # Alertas de impressoras offline
    if offline_printers and len(st.session_state.printer_status_cache) > 0:
        st.error("🚨 **ALERTAS - Impressoras Offline Detectadas:**")
        for offline in offline_printers:
            st.warning(f"🔴 {offline}")
            st.divider()

    # Botões de controle
    col_header1, col_header2, col_header3, col_header4 = st.columns([2, 1, 1, 1])

    with col_header1:
        st.markdown("#### 🔍 Controles de Monitoramento")

    with col_header2:
        if st.button("🔄 Atualizar Status", use_container_width=True):
            with st.spinner("🔍 Testando conectividade..."):
                st.session_state.printer_status_cache = {}
                for local_name, local_data in impressoras_data.items():
                    for printer in local_data["impressoras"]:
                        status = ping_ip(printer["ip"])
                        st.session_state.printer_status_cache[printer["ip"]] = status
                        st.success("✅ Status atualizado!")
                st.rerun()

    with col_header3:
        auto_refresh = st.checkbox("⚡ Auto-refresh (30s)", help="Atualização automática a cada 30 segundos")

        with col_header4:
        if st.button("➕ Adicionar Impressora", use_container_width=True):
            st.session_state.show_add_printer_form = True
            st.rerun()

    if auto_refresh:
        time.sleep(30)
        st.rerun()

    # Upload CSV de Impressoras
    st.markdown("### 📁 Import/Export de Impressoras")

    col_upload, col_download = st.columns(2)

    with col_upload:
        st.markdown("#### 📥 Upload CSV")
        uploaded_csv_printers = st.file_uploader(
        "Carregar arquivo CSV com dados das impressoras",
            type=['csv'],
            help="O arquivo deve conter as colunas: local, descricao_local, ip, serial, modelo, papercut, status_manual",
            key="printer_csv_upload"
            )

        if uploaded_csv_printers is not None:
            try:
                # Ler o CSV
                df_printers = pd.read_csv(uploaded_csv_printers)

                st.markdown("#### 👁️ Preview dos Dados:")
                st.dataframe(df_printers.head(), use_container_width=True)

                # Verificar colunas obrigatórias
                required_cols = ['local', 'descricao_local', 'ip', 'serial', 'modelo', 'papercut', 'status_manual']
                missing_cols = [col for col in required_cols if col not in df_printers.columns]

                if missing_cols:
                    st.error(f"❌ Colunas obrigatórias faltando: {', '.join(missing_cols)}")
                    st.info("📋 **Formato esperado do CSV:**")
                    st.code("""local,descricao_local,ip,serial,modelo,papercut,status_manual
                    HQ1,Térreo - Recepção,172.25.61.53,X3B7034483,HP LaserJet,False,Ativo
HQ2,2º Andar,172.26.61.20,X3B7034750,HP LaserJet,True,Ativo
SPARK,Térreo - Enfermaria,172.30.139.5,X3B7034620,Canon ImageRunner,True,Ativo""")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
                else:
                    col_preview, col_import = st.columns(2)

                    with col_preview:
                        st.success(f"✅ {len(df_printers)} impressoras prontas para importar")
                        st.info(f"📊 Colunas encontradas: {len(df_printers.columns)}")

                    with col_import:
                        if st.button("📥 Importar Impressoras", use_container_width=True, type="primary"):
                            # Processar e importar dados
                            imported_count = 0
                            skipped_count = 0

                            for _, row in df_printers.iterrows():
                                local = row['local'].upper()

                                # Verificar se o local existe
                                if local not in impressoras_data:
                                    st.warning(f"⚠️ Local '{local}' não existe. Ignorando linha.")
                                    skipped_count += 1
                                    continue

                                # Verificar se IP já existe
                                ip_exists = False
                                for local_data in impressoras_data.values():
                                    for printer in local_data["impressoras"]:
                                        if printer["ip"] == row['ip']:
                                            ip_exists = True
                                            break

                                if ip_exists:
                                    st.warning(f"⚠️ IP {row['ip']} já existe. Ignorando linha.")
                                    skipped_count += 1
                                    continue

                                # Gerar ID único
                                next_id = len(impressoras_data[local]["impressoras"]) + 1
                                new_id = f"{local.lower()}_{next_id:03d}"

                                # Converter papercut para boolean
                                papercut_val = str(row['papercut']).lower() in ['true', '1', 'sim', 'yes']

                                # Criar nova impressora
                                new_printer = {
                                "id": new_id,
                                    "local": row['descricao_local'],
                                    "ip": row['ip'],
                                    "serial": row['serial'],
                                    "papercut": papercut_val,
                                    "modelo": row['modelo'],
                                    "status_manual": row['status_manual']
                                    }

                                # Adicionar ao local correto
                                st.session_state.impressoras_data[local]["impressoras"].append(new_printer)
                                imported_count += 1

                            # Mostrar resultado
                            if imported_count > 0:
                                st.success(f"🎉 {imported_count} impressoras importadas com sucesso!")
                                if skipped_count > 0:
                                st.warning(f"⚠️ {skipped_count} impressoras ignoradas (duplicadas ou local inválido)")

                            st.rerun()

                            except Exception as e:
                st.error(f"❌ Erro ao processar arquivo CSV: {str(e)}")
                st.info("💡 Verifique se o arquivo está no formato correto")

    with col_download:
        st.markdown("#### 📤 Download CSV")

        # Criar CSV com dados atuais
        export_data = []
        for local_name, local_data in impressoras_data.items():
            for printer in local_data["impressoras"]:
                export_data.append({
                'local': local_name,
                    'descricao_local': printer['local'],
                    'ip': printer['ip'],
                    'serial': printer['serial'],
                    'modelo': printer.get('modelo', 'HP LaserJet'),
                    'papercut': printer['papercut'],
                    'status_manual': printer.get('status_manual', 'Ativo')
                    })

        if export_data:
            df_export = pd.DataFrame(export_data)
            csv_data = df_export.to_csv(index=False)

            st.download_button(
            label="📥 Baixar CSV Atual",
                data=csv_data,
                file_name=f"impressoras_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
                )

            st.info(f"📊 {len(export_data)} impressoras no arquivo")
        else:
            st.info("📝 Nenhuma impressora cadastrada para exportar")

        # Mostrar formato de exemplo
        st.markdown("#### 📋 Formato CSV Esperado:")
        example_csv = """local,descricao_local,ip,serial,modelo,papercut,status_manual
        HQ1,Térreo - Recepção,172.25.61.53,X3B7034483,HP LaserJet,False,Ativo
HQ1,2º Andar - L Maior,172.25.61.20,X3B7034452,HP LaserJet,True,Ativo
HQ2,2º Andar,172.26.61.20,X3B7034750,Canon ImageRunner,True,Ativo
SPARK,Térreo - Enfermaria,172.30.139.5,X3B7034620,HP LaserJet,True,Manutenção"""

        st.code(example_csv, language="csv")

        # Download do template
        st.download_button(
        label="📄 Baixar Template CSV",
            data=example_csv,
            file_name="template_impressoras.csv",
            mime="text/csv",
            use_container_width=True
            )

    st.divider()

    # Formulário de adicionar impressora
    if st.session_state.get('show_add_printer_form', False):
        st.markdown("### ➕ Adicionar Nova Impressora")

        with st.form("add_printer_form"):
            col_form1, col_form2 = st.columns(2)

            with col_form1:
                local_select = st.selectbox("🏢 Local", ["HQ1", "HQ2", "SPARK"])
                local_desc = st.text_input("📍 Descrição do Local", placeholder="Ex: 5º Andar - Lado A")
                ip_address = st.text_input("🌐 Endereço IP", placeholder="Ex: 172.25.61.70")
                serial_number = st.text_input("🔢 Número Serial", placeholder="Ex: X3B7034XXX")

            with col_form2:
                modelo = st.selectbox("🖨️ Modelo", ["HP LaserJet", "Canon ImageRunner", "Epson WorkForce", "Brother MFC", "Outro"])
                if modelo == "Outro":
                    modelo = st.text_input("Especificar modelo:")
                    papercut_enabled = st.checkbox("✅ Papercut Habilitado")
                status_manual = st.selectbox("📊 Status Manual", ["Ativo", "Manutenção", "Inativo"])

            col_submit, col_cancel = st.columns(2)

            with col_submit:
                if st.form_submit_button("✅ Adicionar Impressora", use_container_width=True):
                    if local_desc and ip_address and serial_number:
                        if validate_ip(ip_address):
                            # Verificar se IP já existe
                            ip_exists = False
                            for local_data in impressoras_data.values():
                                for printer in local_data["impressoras"]:
                                    if printer["ip"] == ip_address:
                                        ip_exists = True
                                        break

                            if not ip_exists:
                                # Gerar ID único
                                next_id = len(impressoras_data[local_select]["impressoras"]) + 1
                                new_id = f"{local_select.lower()}_{next_id:03d}"

                                # Adicionar nova impressora
                                new_printer = {
                                "id": new_id,
                                    "local": local_desc,
                                    "ip": ip_address,
                                    "serial": serial_number,
                                    "papercut": papercut_enabled,
                                    "modelo": modelo,
                                    "status_manual": status_manual
                                    }

                                st.session_state.impressoras_data[local_select]["impressoras"].append(new_printer)
                                st.success(f"✅ Impressora adicionada com sucesso em {local_select}!")
                                st.session_state.show_add_printer_form = False
                                st.rerun()
                            else:
                                st.error("❌ IP já existe na base de dados!")
                            else:
                                st.error("❌ Formato de IP inválido!")
                            else:
                                st.error("❌ Preencha todos os campos obrigatórios!")

            with col_cancel:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state.show_add_printer_form = False
                    st.rerun()

        st.divider()

    # Exibir por abas (HQ1, HQ2, SPARK)
    tab_hq1, tab_hq2, tab_spark = st.tabs(["🏢 HQ1", "🏢 HQ2", "⚡ SPARK"])

    for tab, (local_name, local_data) in zip([tab_hq1, tab_hq2, tab_spark], impressoras_data.items()):
    with tab:
            # Informações de login
            st.markdown(f"### 🔑 Credenciais {local_name}")
            col_login, col_senha = st.columns(2)

            with col_login:
                st.info(f"**👤 Login:** {local_data['info']['login']}")

            with col_senha:
                st.info(f"**🔒 Senha:** {local_data['info']['senha']}")

            st.divider()

            # Métricas resumo
            total_impressoras = len(local_data["impressoras"])
            online = sum(1 for p in local_data["impressoras"] if st.session_state.printer_status_cache.get(p["ip"], False))
            offline = total_impressoras - online
            com_papercut = sum(1 for p in local_data["impressoras"] if p["papercut"])

            col_total, col_online, col_offline, col_papercut = st.columns(4)

            with col_total:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #667eea, #764ba2); padding: 15px; border-radius: 10px; text-align: center; color: white;'>
                <div style='font-size: 24px; font-weight: bold;'>{total_impressoras}</div>
                    <div style='font-size: 12px;'>Total</div>
                    </div>
                """, unsafe_allow_html=True)

            with col_online:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #22C55E, #16A34A); padding: 15px; border-radius: 10px; text-align: center; color: white;'>
                <div style='font-size: 24px; font-weight: bold;'>{online}</div>
                    <div style='font-size: 12px;'>Online</div>
                    </div>
                """, unsafe_allow_html=True)

            with col_offline:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #EF4444, #DC2626); padding: 15px; border-radius: 10px; text-align: center; color: white;'>
                <div style='font-size: 24px; font-weight: bold;'>{offline}</div>
                    <div style='font-size: 12px;'>Offline</div>
                    </div>
                """, unsafe_allow_html=True)

            with col_papercut:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #8B5CF6, #7C3AED); padding: 15px; border-radius: 10px; text-align: center; color: white;'>
                <div style='font-size: 24px; font-weight: bold;'>{com_papercut}</div>
                    <div style='font-size: 12px;'>Papercut</div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("### 🖨️ Lista de Impressoras")

            # Tabela de impressoras
            for i, printer in enumerate(local_data["impressoras"]):
                # Verificar status se não estiver no cache
                if printer["ip"] not in st.session_state.printer_status_cache:
                    with st.spinner(f"Testando {printer['ip']}..."):
                        st.session_state.printer_status_cache[printer["ip"]] = ping_ip(printer["ip"])

                is_online = st.session_state.printer_status_cache.get(printer["ip"], False)
                status_icon = "🟢" if is_online else "🔴"
                status_text = "ONLINE" if is_online else "OFFLINE"
                papercut_icon = "✅" if printer["papercut"] else "❌"

                # Card da impressora
                st.markdown(f"""
                <div style='border: 1px solid {"#22C55E" if is_online else "#EF4444"}; border-radius: 10px; padding: 15px; margin: 10px 0; background: rgba({"34, 197, 94" if is_online else "239, 68, 68"}, 0.1);'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <h4 style='margin: 0; color: #333;'>{status_icon} {printer["local"]}</h4>
                            <p style='margin: 5px 0; color: #666;'><strong>IP:</strong> {printer["ip"]} | <strong>Serial:</strong> {printer["serial"]} | <strong>Modelo:</strong> {printer.get("modelo", "N/A")}</p>
                            <p style='margin: 0; color: #666;'><strong>Status:</strong> {status_text} | <strong>Papercut:</strong> {papercut_icon} | <strong>Status Manual:</strong> {printer.get("status_manual", "N/A")}</p>
                            </div>
                        <div style='text-align: right;'>
                        <div style='background: {"#22C55E" if is_online else "#EF4444"}; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 12px;'>
                            {status_text}
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Botões de ação para cada impressora
                col_action1, col_action2, col_action3, col_action4, col_action5 = st.columns(5)

                with col_action1:
                    if st.button(f"🔍 Testar", key=f"test_{local_name}_{i}", use_container_width=True):
                        with st.spinner("Testando..."):
                            result = ping_ip(printer["ip"])
                            st.session_state.printer_status_cache[printer["ip"]] = result
                            if result:
                                st.success(f"✅ {printer['ip']} respondeu!")
                            else:
                                st.error(f"❌ {printer['ip']} não responde!")
                                st.rerun()

                with col_action2:
                    if st.button(f"🌐 Acessar", key=f"access_{local_name}_{i}", use_container_width=True):
                        st.info(f"🔗 Abrir: http://{printer['ip']}")
                        st.markdown(f"[🌐 Abrir Interface Web](http://{printer['ip']})")

                with col_action3:
                    if st.button(f"📋 Copiar IP", key=f"copy_{local_name}_{i}", use_container_width=True):
                        st.success(f"📋 IP copiado: {printer['ip']}")
                        st.code(printer["ip"])

                with col_action4:
                    if st.button(f"✏️ Editar", key=f"edit_{local_name}_{i}", use_container_width=True):
                        st.session_state.edit_printer_id = printer["id"]
                        st.session_state.edit_printer_local = local_name
                        st.rerun()

                with col_action5:
                    if st.button(f"🗑️ Remover", key=f"remove_{local_name}_{i}", use_container_width=True):
                        st.session_state.impressoras_data[local_name]["impressoras"].remove(printer)
                        if printer["ip"] in st.session_state.printer_status_cache:
                            del st.session_state.printer_status_cache[printer["ip"]]
                            st.success(f"🗑️ Impressora {printer['local']} removida!")
                        st.rerun()

                # Formulário de edição inline
                if st.session_state.get('edit_printer_id') == printer["id"]:
                    st.markdown("#### ✏️ Editando Impressora")

                    with st.form(f"edit_form_{printer['id']}"):
                        col_edit1, col_edit2 = st.columns(2)

                        with col_edit1:
                            new_local = st.text_input("📍 Local", value=printer["local"])
                            new_ip = st.text_input("🌐 IP", value=printer["ip"])
                            new_serial = st.text_input("🔢 Serial", value=printer["serial"])

                        with col_edit2:
                            new_modelo = st.text_input("🖨️ Modelo", value=printer.get("modelo", "HP LaserJet"))
                            new_papercut = st.checkbox("✅ Papercut", value=printer["papercut"])
                            new_status = st.selectbox("📊 Status Manual", ["Ativo", "Manutenção", "Inativo"],
                            index=["Ativo", "Manutenção", "Inativo"].index(printer.get("status_manual", "Ativo")))

                        col_save, col_cancel_edit = st.columns(2)

                        with col_save:
                            if st.form_submit_button("💾 Salvar", use_container_width=True):
                                if new_local and new_ip and new_serial:
                                    if validate_ip(new_ip):
                                        # Verificar se novo IP já existe (exceto o atual)
                                        ip_exists = False
                                        if new_ip != printer["ip"]:
                                            for ld in impressoras_data.values():
                                                for p in ld["impressoras"]:
                                                    if p["ip"] == new_ip and p["id"] != printer["id"]:
                                                        ip_exists = True
                                                        break

                                        if not ip_exists:
                                            # Atualizar dados
                                            printer["local"] = new_local
                                            printer["ip"] = new_ip
                                            printer["serial"] = new_serial
                                            printer["modelo"] = new_modelo
                                            printer["papercut"] = new_papercut
                                            printer["status_manual"] = new_status

                                            st.success("💾 Impressora atualizada com sucesso!")
                                            st.session_state.edit_printer_id = None
                                            st.rerun()
                                        else:
                                            st.error("❌ IP já existe!")
                                        else:
                                            st.error("❌ Formato de IP inválido!")
                                        else:
                                            st.error("❌ Preencha todos os campos!")

                        with col_cancel_edit:
                            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                st.session_state.edit_printer_id = None
                                st.rerun()

    # Resumo geral
    st.divider()
    st.markdown("### 📊 Resumo Geral da Rede")

    all_printers = []
    for local_data in impressoras_data.values():
        all_printers.extend(local_data["impressoras"])

    total_geral = len(all_printers)
    online_geral = sum(1 for p in all_printers if st.session_state.printer_status_cache.get(p["ip"], False))
    offline_geral = total_geral - online_geral
    papercut_geral = sum(1 for p in all_printers if p["papercut"])

    col_summary1, col_summary2, col_summary3, col_summary4 = st.columns(4)

    with col_summary1:
        st.metric("🖨️ Total de Impressoras", total_geral)

    with col_summary2:
        st.metric("🟢 Online", online_geral, delta=f"{(online_geral/total_geral*100):.1f}%")

    with col_summary3:
        st.metric("🔴 Offline", offline_geral, delta=f"-{(offline_geral/total_geral*100):.1f}%")

    with col_summary4:
        st.metric("✅ Com Papercut", papercut_geral, delta=f"{(papercut_geral/total_geral*100):.1f}%")

    # Informações técnicas
    st.markdown("### ⚙️ Informações Técnicas")
    st.info("""
    📌 **Configuração de Rede:**
    - Todas as impressoras devem estar conectadas na **porta 43** de seus respectivos switches
    - **HQ1:** Rede 172.25.61.x
    - **HQ2:** Rede 172.26.61.x
    - **SPARK:** Rede 172.30.139.x
    - **Credenciais padrão:** admin / Ultravioleta
    - **Porta de verificação:** 43 (Switch)

    📋 **Funcionalidades:**
    - ➕ Adicionar novas impressoras
    - ✏️ Editar informações existentes
    - 🗑️ Remover impressoras
    - 🚨 Alertas automáticos para impressoras offline
    - 🔄 Monitoramento em tempo real
    """)

# ========================================================================================
# GRAB & GO PERDAS
# ========================================================================================

def render_grab_and_go():
    """Renderiza o dashboard de perdas do Grab & Go com recomendações de compra"""
    st.markdown("## 🎯 Grab & Go - Controle de Perdas")
    st.markdown("### 📊 Sistema de Monitoramento e Recomendações de Compra")

    # Inicializar dados no session_state
    if 'grab_and_go_data' not in st.session_state:
        st.session_state.grab_and_go_data = {
        'perdas': [],
            'produtos': {
            # Dados baseados na planilha fornecida
                'TECLADO E MOUSE MK120': {'codigo': '920-004429', 'valor': 126.90, 'categoria': 'TECLADO'},
                'MOUSE COM FIO USB M90 PRETO': {'codigo': '910-004053', 'valor': 39.90, 'categoria': 'MOUSE'},
                'TECLADO COM FIO USB K120': {'codigo': '920-004423', 'valor': 99.90, 'categoria': 'TECLADO'},
                'HEADSET BLACKWIRE C3220': {'codigo': '209745-101T', 'valor': 209.00, 'categoria': 'HEADSET'},
                'CABO ADAPTADOR MULTIPORTAS USB-C 7 EM 1': {'codigo': 'UCA11 - GEONAV', 'valor': 360.00, 'categoria': 'ADAPTADOR'},
                'LIMPA TELA GEONAV': {'codigo': '-', 'valor': 24.30, 'categoria': 'ACESSORIO'},
                'ESPATULA VONDER': {'codigo': '-', 'valor': 37.90, 'categoria': 'ACESSORIO'},
                'ESPATULA PLÁSTICO CELULAR': {'codigo': '-', 'valor': 22.90, 'categoria': 'ACESSORIO'},
                'PASSADOR DE SLIDE WIRELESS': {'codigo': '910-005216', 'valor': 828.90, 'categoria': 'ACESSORIO'},
                'MICRO SD 128GB': {'codigo': 'SANDISK CLASSE 10', 'valor': 97.90, 'categoria': 'ACESSORIO'},
                'ALCOOL ISOPROPILICO': {'codigo': '500ML - MPLASTEC', 'valor': 46.90, 'categoria': 'ACESSORIO'},
                'FLANELA DE MICROFIBRA KIT': {'codigo': '-', 'valor': 27.90, 'categoria': 'ACESSORIO'},
                'HUB 5 EM 1 COM REDE': {'codigo': 'GORILA-H5R', 'valor': 244.00, 'categoria': 'ADAPTADOR'},
                'HUB 6 EM 1 SEM REDE': {'codigo': 'GORILA-H6', 'valor': 110.00, 'categoria': 'ADAPTADOR'},
                'ADAPTADOR HUB MULTIPORTAS FULL USB + REDE': {'codigo': 'GORILA-HFUR', 'valor': 118.00, 'categoria': 'ADAPTADOR'},
                'ADAPTADOR HUB MULTIPORTAS FULL USB': {'codigo': 'GORILA-HFU', 'valor': 59.00, 'categoria': 'ADAPTADOR'}
                },
            'locais': ['HQ1 - LADO MAIOR', 'HQ1 - LADO MENOR', 'HQ2', 'SPARK - 1º ANDAR', 'SPARK - 2º ANDAR', 'SPARK - 3º ANDAR'],
            'configuracao_email': {
            'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'remetente': '',
                'senha': '',
                'destinatarios': []
                }
            }

    # Tabs principais
    tab_registro, tab_analytics, tab_recomendacoes, tab_config = st.tabs([
    "📝 Registrar Perdas",
        "📊 Analytics",
        "🛒 Recomendações",
        "⚙️ Configurações"
        ])

    with tab_registro:
        st.markdown("### 📝 Registrar Nova Perda")

        col_form1, col_form2 = st.columns(2)

        with col_form1:
            st.markdown("#### 📋 Dados da Perda")
            with st.form("registro_perda"):
                local = st.selectbox("🏢 Local", st.session_state.grab_and_go_data['locais'])
                produto = st.selectbox("📦 Produto", list(st.session_state.grab_and_go_data['produtos'].keys()))
                quantidade = st.number_input("🔢 Quantidade Perdida", min_value=1, value=1)
                data_perda = st.date_input("📅 Data da Perda", value=datetime.now().date())

                col_motivo, col_obs = st.columns(2)
                with col_motivo:
                    motivo = st.selectbox("❓ Motivo", [
                    "Furto/Roubo", "Dano/Quebra", "Perda", "Uso Indevido",
                        "Não Retornado", "Defeito", "Outro"
                        ])

                with col_obs:
                    observacoes = st.text_area("📝 Observações", placeholder="Detalhes adicionais...")

                if st.form_submit_button("📝 Registrar Perda", use_container_width=True):
                    produto_info = st.session_state.grab_and_go_data['produtos'][produto]
                    valor_total = produto_info['valor'] * quantidade

                    nova_perda = {
                    'id': str(uuid.uuid4()),
                        'data': data_perda.strftime('%Y-%m-%d'),
                        'local': local,
                        'produto': produto,
                        'categoria': produto_info['categoria'],
                        'codigo': produto_info['codigo'],
                        'quantidade': quantidade,
                        'valor_unitario': produto_info['valor'],
                        'valor_total': valor_total,
                        'motivo': motivo,
                        'observacoes': observacoes,
                        'timestamp': datetime.now().isoformat()
                        }

                    st.session_state.grab_and_go_data['perdas'].append(nova_perda)
                    st.success(f"✅ Perda registrada! Valor total: R$ {valor_total:,.2f}")
                    st.rerun()

        with col_form2:
            st.markdown("#### 📊 Preview do Produto")
            if produto := st.session_state.get('selected_produto'):
                produto_info = st.session_state.grab_and_go_data['produtos'].get(produto, {})
                if produto_info:
                    st.info(f"""
                    **🏷️ Código:** {produto_info.get('codigo', 'N/A')}
                    **💰 Valor:** R$ {produto_info.get('valor', 0):,.2f}
                    **📂 Categoria:** {produto_info.get('categoria', 'N/A')}
                    """)

            # Últimas perdas registradas
            st.markdown("#### 📋 Últimas Perdas")
            if st.session_state.grab_and_go_data['perdas']:
                df_recent = pd.DataFrame(st.session_state.grab_and_go_data['perdas'][-5:])
                df_recent = df_recent[['data', 'local', 'produto', 'quantidade', 'valor_total']].copy()
                df_recent['valor_total'] = df_recent['valor_total'].apply(lambda x: f"R$ {x:,.2f}")
                st.dataframe(df_recent, use_container_width=True, hide_index=True)
            else:
                st.info("📝 Nenhuma perda registrada ainda")

    with tab_analytics:
        st.markdown("### 📊 Análise de Perdas")

        if not st.session_state.grab_and_go_data['perdas']:
            st.info("📝 Registre algumas perdas para ver as análises")
            return

        df_perdas = pd.DataFrame(st.session_state.grab_and_go_data['perdas'])
        df_perdas['data'] = pd.to_datetime(df_perdas['data'])
        df_perdas['mes'] = df_perdas['data'].dt.to_period('M')
        df_perdas['trimestre'] = df_perdas['data'].dt.to_period('Q')
        df_perdas['ano'] = df_perdas['data'].dt.year

        # Filtros
        col_filter1, col_filter2, col_filter3 = st.columns(3)

        with col_filter1:
            anos_disponiveis = sorted(df_perdas['ano'].unique(), reverse=True)
            ano_selecionado = st.selectbox("📅 Ano", anos_disponiveis)

        with col_filter2:
            locais_disponiveis = ['Todos'] + sorted(df_perdas['local'].unique())
            local_selecionado = st.selectbox("🏢 Local", locais_disponiveis)

        with col_filter3:
            categorias_disponiveis = ['Todas'] + sorted(df_perdas['categoria'].unique())
            categoria_selecionada = st.selectbox("📂 Categoria", categorias_disponiveis)

    # Aplicar filtros
    df_filtered = df_perdas[df_perdas['ano'] == ano_selecionado].copy()
        if local_selecionado != 'Todos':
            df_filtered = df_filtered[df_filtered['local'] == local_selecionado]
            if categoria_selecionada != 'Todas':
            df_filtered = df_filtered[df_filtered['categoria'] == categoria_selecionada]

        # Métricas principais
        col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)

        with col_metric1:
            total_perdas = len(df_filtered)
            st.metric("📊 Total de Perdas", total_perdas)

        with col_metric2:
            valor_total = df_filtered['valor_total'].sum()
            st.metric("💰 Valor Total", f"R$ {valor_total:,.2f}")

        with col_metric3:
            if len(df_filtered) > 0:
                valor_medio = df_filtered['valor_total'].mean()
                st.metric("📈 Valor Médio", f"R$ {valor_medio:,.2f}")
            else:
                st.metric("📈 Valor Médio", "R$ 0,00")

        with col_metric4:
            produto_mais_perdido = df_filtered.groupby('produto')['quantidade'].sum().idxmax() if len(df_filtered) > 0 else "N/A"
            st.metric("🎯 Produto + Perdido", produto_mais_perdido[:20] + "..." if len(produto_mais_perdido) > 20 else produto_mais_perdido)

        # Gráficos
        col_graph1, col_graph2 = st.columns(2)

        with col_graph1:
            st.markdown("#### 📊 Perdas por Trimestre")
            if len(df_filtered) > 0:
                perdas_trimestre = df_filtered.groupby('trimestre').agg({
                'quantidade': 'sum',
                    'valor_total': 'sum'
                    }).reset_index()
                perdas_trimestre['trimestre_str'] = perdas_trimestre['trimestre'].astype(str)

                fig_trim = go.Figure()
                fig_trim.add_trace(go.Bar(
                x=perdas_trimestre['trimestre_str'],
                    y=perdas_trimestre['valor_total'],
                    name='Valor (R$)',
                    marker_color='#EF4444',
                    text=perdas_trimestre['valor_total'].apply(lambda x: f'R$ {x:,.0f}'),
                    textposition='auto'
                    ))

                fig_trim.update_layout(
                title="Perdas por Trimestre (Valor)",
                    xaxis_title="Trimestre",
                    yaxis_title="Valor (R$)",
                    showlegend=False,
                    height=400
                    )
                st.plotly_chart(fig_trim, use_container_width=True)

        with col_graph2:
            st.markdown("#### 🏢 Perdas por Local")
            if len(df_filtered) > 0:
                perdas_local = df_filtered.groupby('local')['valor_total'].sum().reset_index()

                fig_local = px.pie(
                perdas_local,
                    values='valor_total',
                    names='local',
                    title="Distribuição de Perdas por Local"
                    )
                fig_local.update_traces(textposition='inside', textinfo='percent+label')
                fig_local.update_layout(height=400)
                st.plotly_chart(fig_local, use_container_width=True)

        # Tabela detalhada
        st.markdown("#### 📋 Detalhamento das Perdas")
        if len(df_filtered) > 0:
            df_display = df_filtered[['data', 'local', 'produto', 'categoria', 'quantidade', 'valor_total', 'motivo']].copy()
            df_display['data'] = df_display['data'].dt.strftime('%d/%m/%Y')
            df_display['valor_total'] = df_display['valor_total'].apply(lambda x: f"R$ {x:,.2f}")
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # Download CSV
            csv_data = df_display.to_csv(index=False)
            st.download_button(
            label="📥 Baixar Relatório CSV",
                data=csv_data,
                file_name=f"perdas_grab_and_go_{ano_selecionado}.csv",
                mime="text/csv",
                use_container_width=True
                )

    with tab_recomendacoes:
        st.markdown("### 🛒 Recomendações de Compra")

        if not st.session_state.grab_and_go_data['perdas']:
            st.info("📝 Registre algumas perdas para gerar recomendações")
            return

        df_perdas = pd.DataFrame(st.session_state.grab_and_go_data['perdas'])
        df_perdas['data'] = pd.to_datetime(df_perdas['data'])

        # Configurações de recomendação
        col_config1, col_config2 = st.columns(2)

        with col_config1:
            orcamento_min = st.number_input("💰 Orçamento Mínimo", min_value=30000, max_value=45000, value=30000, step=1000)
            orcamento_max = st.number_input("💰 Orçamento Máximo", min_value=30000, max_value=45000, value=45000, step=1000)

        with col_config2:
            periodo_analise = st.selectbox("📅 Período de Análise", [
            "Último Mês", "Últimos 3 Meses", "Últimos 6 Meses", "Último Ano"
                ])
            fator_seguranca = st.slider("🛡️ Fator de Segurança", min_value=1.1, max_value=2.0, value=1.5, step=0.1)

        # Calcular período
        hoje = datetime.now()
        if periodo_analise == "Último Mês":
            data_inicio = hoje - timedelta(days=30)
        elif periodo_analise == "Últimos 3 Meses":
            data_inicio = hoje - timedelta(days=90)
        elif periodo_analise == "Últimos 6 Meses":
            data_inicio = hoje - timedelta(days=180)
        else:
            data_inicio = hoje - timedelta(days=365)

        # Filtrar dados do período
        df_periodo = df_perdas[df_perdas['data'] >= data_inicio].copy()

        if len(df_periodo) == 0:
            st.warning("⚠️ Nenhuma perda registrada no período selecionado")
            return

        # Calcular recomendações
        st.markdown("#### 🔍 Análise de Perdas do Período")

        perdas_produto = df_periodo.groupby('produto').agg({
        'quantidade': 'sum',
            'valor_total': 'sum'
            }).reset_index()

        # Adicionar informações do produto
        for idx, row in perdas_produto.iterrows():
            produto_info = st.session_state.grab_and_go_data['produtos'][row['produto']]
            perdas_produto.loc[idx, 'valor_unitario'] = produto_info['valor']
            perdas_produto.loc[idx, 'categoria'] = produto_info['categoria']

        # Calcular recomendação de quantidade
        perdas_produto['qtd_recomendada'] = (perdas_produto['quantidade'] * fator_seguranca).round().astype(int)
        perdas_produto['valor_recomendado'] = perdas_produto['qtd_recomendada'] * perdas_produto['valor_unitario']

        # Ordenar por valor recomendado (maior para menor)
        perdas_produto = perdas_produto.sort_values('valor_recomendado', ascending=False)

        # Criar lista de compras dentro do orçamento
        st.markdown("#### 🎯 Lista de Compras Recomendada")

        lista_compras = []
        valor_acumulado = 0

        for _, row in perdas_produto.iterrows():
            if valor_acumulado + row['valor_recomendado'] <= orcamento_max:
                lista_compras.append(row)
                valor_acumulado += row['valor_recomendado']

        if lista_compras:
            df_lista = pd.DataFrame(lista_compras)

            # Métricas da recomendação
            col_rec1, col_rec2, col_rec3 = st.columns(3)

            with col_rec1:
                st.metric("📦 Itens Recomendados", len(df_lista))

            with col_rec2:
                st.metric("💰 Valor Total", f"R$ {valor_acumulado:,.2f}")

            with col_rec3:
                percentual_orcamento = (valor_acumulado / orcamento_max) * 100
                st.metric("📊 % do Orçamento", f"{percentual_orcamento:.1f}%")

            # Tabela da lista de compras
            df_lista_display = df_lista[['produto', 'categoria', 'qtd_recomendada', 'valor_unitario', 'valor_recomendado']].copy()
            df_lista_display.columns = ['Produto', 'Categoria', 'Qtd. Recomendada', 'Valor Unitário', 'Valor Total']
            df_lista_display['Valor Unitário'] = df_lista_display['Valor Unitário'].apply(lambda x: f"R$ {x:,.2f}")
            df_lista_display['Valor Total'] = df_lista_display['Valor Total'].apply(lambda x: f"R$ {x:,.2f}")

            st.dataframe(df_lista_display, use_container_width=True, hide_index=True)

            # Gerar email
            col_email1, col_email2 = st.columns(2)

            with col_email1:
                if st.button("📧 Gerar Email de Compra", use_container_width=True):
                    st.session_state.email_gerado = True

                    # Criar conteúdo do email
                    email_content = f"""
                    <h2>🛒 Recomendação de Compra - Grab & Go</h2>
                    <p><strong>Período de Análise:</strong> {periodo_analise}</p>
                    <p><strong>Data do Relatório:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    <p><strong>Orçamento Disponível:</strong> R$ {orcamento_min:,.2f} - R$ {orcamento_max:,.2f}</p>

                    <h3>📊 Resumo da Recomendação</h3>
                    <ul>
                    <li><strong>Total de Itens:</strong> {len(df_lista)}</li>
                        <li><strong>Valor Total:</strong> R$ {valor_acumulado:,.2f}</li>
                        <li><strong>Percentual do Orçamento:</strong> {percentual_orcamento:.1f}%</li>
                        </ul>

                    <h3>🛒 Lista de Compras</h3>
                    <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr style="background-color: #f0f0f0;">
                        <th>Produto</th>
                            <th>Categoria</th>
                            <th>Qtd. Recomendada</th>
                            <th>Valor Unitário</th>
                            <th>Valor Total</th>
                            </tr>
                        """

                    for _, item in df_lista.iterrows():
                        email_content += f"""
                        <tr>
                        <td>{item['produto']}</td>
                            <td>{item['categoria']}</td>
                            <td>{item['qtd_recomendada']}</td>
                            <td>R$ {item['valor_unitario']:,.2f}</td>
                            <td>R$ {item['valor_recomendado']:,.2f}</td>
                            </tr>
                        """

                    email_content += """
                    </table>

                    <h3>📈 Justificativa</h3>
                    <p>Esta recomendação foi baseada na análise das perdas registradas no período selecionado,
                    aplicando um fator de segurança para garantir estoque adequado.</p>

                    <p><em>Relatório gerado automaticamente pelo Sistema Grab & Go</em></p>
                    """

                    st.session_state.email_content = email_content
                    st.success("📧 Email gerado! Configure o envio na aba Configurações.")

            with col_email2:
                # Download da lista em CSV
                csv_lista = df_lista_display.to_csv(index=False)
                st.download_button(
                label="📥 Baixar Lista CSV",
                    data=csv_lista,
                    file_name=f"lista_compras_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                    )

            else:
                    st.warning("⚠️ Nenhum item se encaixa no orçamento disponível. Considere aumentar o orçamento ou reduzir o fator de segurança.")

    with tab_config:
        st.markdown("### ⚙️ Configurações do Sistema")

        # Configuração de email
        st.markdown("#### 📧 Configuração de Email")

        if not EMAIL_AVAILABLE:
            st.warning("⚠️ Bibliotecas de email não disponíveis. Funcionalidade de envio desabilitada.")
            st.info("💡 Para habilitar o envio de emails, instale as bibliotecas necessárias ou use uma versão atualizada do Python.")

        with st.expander("📮 Configurar Envio de Emails", expanded=False):
            col_email_config1, col_email_config2 = st.columns(2)

            with col_email_config1:
                smtp_server = st.text_input("📡 Servidor SMTP", value=st.session_state.grab_and_go_data['configuracao_email']['smtp_server'])
                smtp_port = st.number_input("🔌 Porta SMTP", value=st.session_state.grab_and_go_data['configuracao_email']['smtp_port'])
                remetente = st.text_input("📤 Email Remetente")
                senha = st.text_input("🔒 Senha do Email", type="password")

            with col_email_config2:
                destinatarios_text = st.text_area("📥 Destinatários",
                placeholder="Digite um email por linha:
                        admin@empresa.com
compras@empresa.com",
help="Um email por linha")

                if st.button("💾 Salvar Configuração Email"):
                    st.session_state.grab_and_go_data['configuracao_email'].update({
                    'smtp_server': smtp_server,
                        'smtp_port': smtp_port,
                        'remetente': remetente,
                        'senha': senha,
                        'destinatarios': [email.strip() for email in destinatarios_text.split('
                        ') if email.strip()]
})
                    st.success("✅ Configuração de email salva!")

        # Enviar email se foi gerado
        if st.session_state.get('email_gerado') and st.session_state.get('email_content'):
            st.markdown("#### 📧 Enviar Email Gerado")

            if st.button("📨 Enviar Email de Recomendação", use_container_width=True):
                if not EMAIL_AVAILABLE:
                    st.error("❌ Bibliotecas de email não disponíveis. Funcionalidade desabilitada.")
                    return

                    config = st.session_state.grab_and_go_data['configuracao_email']

                if not config['remetente'] or not config['senha'] or not config['destinatarios']:
                    st.error("❌ Configure o email antes de enviar!")
                else:
                    try:
                        # Criar mensagem
                        msg = MimeMultipart()
                        msg['From'] = config['remetente']
                        msg['To'] = ', '.join(config['destinatarios'])
                        msg['Subject'] = f"Recomendação de Compra Grab & Go - {datetime.now().strftime('%d/%m/%Y')}"

                        # Anexar conteúdo HTML
                        msg.attach(MimeText(st.session_state.email_content, 'html'))

                        # Conectar e enviar
                        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
                        server.starttls()
                        server.login(config['remetente'], config['senha'])
                        text = msg.as_string()
                        server.sendmail(config['remetente'], config['destinatarios'], text)
                        server.quit()

                        st.success("📧 Email enviado com sucesso!")
                        st.session_state.email_gerado = False

                    except Exception as e:
                        st.error(f"❌ Erro ao enviar email: {str(e)}")

        # Gestão de produtos
        st.markdown("#### 📦 Gestão de Produtos")

        with st.expander("➕ Adicionar Novo Produto", expanded=False):
            with st.form("novo_produto"):
                col_prod1, col_prod2 = st.columns(2)

                with col_prod1:
                    nome_produto = st.text_input("📦 Nome do Produto")
                    codigo_produto = st.text_input("🏷️ Código")
                    valor_produto = st.number_input("💰 Valor", min_value=0.0, format="%.2f")

                with col_prod2:
                    categoria_produto = st.selectbox("📂 Categoria", [
                    "TECLADO", "MOUSE", "HEADSET", "ADAPTADOR", "ACESSORIO"
                        ])

                if st.form_submit_button("➕ Adicionar Produto"):
                    if nome_produto and valor_produto > 0:
                        st.session_state.grab_and_go_data['produtos'][nome_produto] = {
                        'codigo': codigo_produto,
                            'valor': valor_produto,
                            'categoria': categoria_produto
                            }
                        st.success(f"✅ Produto '{nome_produto}' adicionado!")
                        st.rerun()
                    else:
                        st.error("❌ Preencha todos os campos obrigatórios!")

        # Lista de produtos atual
        st.markdown("#### 📋 Produtos Cadastrados")
        produtos_df = pd.DataFrame([
        {
            'Produto': nome,
                'Código': info['codigo'],
                'Valor': f"R$ {info['valor']:,.2f}",
                'Categoria': info['categoria']
                }
            for nome, info in st.session_state.grab_and_go_data['produtos'].items()
            ])

        st.dataframe(produtos_df, use_container_width=True, hide_index=True)

        # Download backup dos dados
        st.markdown("#### 💾 Backup de Dados")

        col_backup1, col_backup2 = st.columns(2)

        with col_backup1:
            # Backup completo em JSON
            backup_data = {
            'timestamp': datetime.now().isoformat(),
                'grab_and_go_data': st.session_state.grab_and_go_data
                }
            backup_json = json.dumps(backup_data, indent=2, ensure_ascii=False)

            st.download_button(
            label="📦 Backup Completo (JSON)",
                data=backup_json,
                file_name=f"backup_grab_and_go_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
                )

        with col_backup2:
            # Backup apenas perdas em CSV
            if st.session_state.grab_and_go_data['perdas']:
                perdas_csv = pd.DataFrame(st.session_state.grab_and_go_data['perdas']).to_csv(index=False)
                st.download_button(
                label="📊 Backup Perdas (CSV)",
                    data=perdas_csv,
                    file_name=f"perdas_grab_and_go_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
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
    st.markdown("""<div></div>""")  # Fixed string
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

    st.markdown("""<div></div>""")  # Fixed string
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
                    st.markdown("""<div></div>""")  # Fixed string
                    <div class="analysis-card">
                <h4 style="color: #8A05BE; margin: 0;">📊 Estrutura</h4>
                    <p style="margin: 5px 0;"><strong>Linhas:</strong> {}</p>
                    <p style="margin: 5px 0;"><strong>Colunas:</strong> {}</p>
                    </div>
                """.format(analysis['shape'][0], analysis['shape'][1]), unsafe_allow_html=True)

            with col2:
                    st.markdown("""<div></div>""")  # Fixed string
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
        st.markdown("""<div></div>""")  # Fixed string
        <div class="analysis-card">
                <h4 style="color: #8A05BE; margin: 0;">📋 Colunas</h4>
                    <p style="margin: 5px 0; font-size: 12px;">{}</p>
                    </div>
                """.format(", ".join(analysis['columns'][:5]) + ("..." if len(analysis['columns']) > 5 else "")), unsafe_allow_html=True)

            # Preview dos dados
            st.markdown("### 👁️ Preview dos Dados")
            st.dataframe(df.head(), use_container_width=True)

            # Seleção de aba de destino
            st.markdown("""<div></div>""")  # Fixed string
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

                            st.markdown("""<div></div>""")  # Fixed string
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
                                    st.markdown("""<div></div>""")  # Fixed string
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
    elif current_page == 'tvs_monitores':
        render_tvs_monitores()
    elif current_page == 'impressoras_status':
        render_impressoras_status()
    elif current_page == 'grab_and_go':
        render_grab_and_go()
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