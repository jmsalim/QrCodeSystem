# ==============================================================================
# COPYRIGHT NOTICE & LICENSE TERMS
# ==============================================================================
#  Software: QUANTIX Inventory System
#  Owner:    Wildfire Consulting Services LLC
#  Author:   Joao de Mendonca Salim
#  Copyright (c) 2026 Wildfire Consulting Services LLC. All Rights Reserved.
#
#  LICENSE TERMS:
#  This software is provided under a revocable, non-exclusive, non-transferable
#  free license granted by Wildfire Consulting Services LLC.
# ==============================================================================

import streamlit as st
import pandas as pd
import cv2
import numpy as np
import os
import glob as globmod
import qrcode
import barcode
import base64
import requests
import json
import zipfile
import io
import urllib.parse
import streamlit.components.v1 as components
from barcode.writer import ImageWriter
from datetime import datetime, timedelta
from PIL import Image
import time
import socket
import random
import uuid
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False

# ==========================================
# 1. LICENSE SYSTEM
# ==========================================
LICENSE_MASTER_URL = "https://gist.githubusercontent.com/jmsalim/d0968ab09f347be10c671ace248e9140/raw/licenses.json"

def get_machine_id():
    return str(uuid.getnode())

def check_license(user_key):
    try:
        fresh_url = f"{LICENSE_MASTER_URL}?v={random.randint(1, 1000000)}"
        response = requests.get(fresh_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            remote_status = data.get(user_key, "INVALID")
            local_hwid = get_machine_id()
            
            if remote_status == "ACTIVE": return True, "Valid"
            elif remote_status == "SUSPENDED": return False, "SUSPENDED"
            elif remote_status == local_hwid: return True, "Valid"
            elif remote_status != "INVALID": return False, "USED_ELSEWHERE"
            else: return False, "INVALID"
        return False, "CONNECTION_ERROR"
    except:
        return False, "CONNECTION_ERROR"

# ==========================================
# 2. TRANSLATIONS
# ==========================================
LANG = {
    'PT': {
        'lic_suspended': "🚫 LICENÇA SUSPENSA",
        'lic_used': "🚫 ESTA LICENÇA JÁ ESTÁ EM USO",
        'lic_msg': "Esta chave de licença foi desativada.",
        'lic_msg_used': "Esta chave está vinculada a outro computador.",
        'lic_invalid': "❌ Chave Inválida",
        'recover_title': "🔐 Ativação Necessária",
        'recover_desc': "Insira uma chave válida.",
        'recover_btn': "🔄 Validar",
        'setup_title': "Instalação QUANTIX",
        'setup_sub': "Ativação de Software",
        'step1': "Passo 1: Solicitar Ativação",
        'step2': "Passo 2: Configurar Acesso",
        'your_id': "Seu ID de Máquina:",
        'email_btn': "📧 Enviar ID para Suporte",
        'comp_name': "Nome da Empresa",
        'lic_key_label': "Chave de Licença Recebida",
        'comp_placeholder': "Ex: Pontual Leather",
        'logo_opt': "Logo (Opcional)",
        'start_btn': "🚀 Ativar e Iniciar",
        'name_required': "Campos obrigatórios.",
        'success_restart': "Ativado! Reiniciando...",
        'settings': "⚙️ Configurações",
        'connect': "📱 Conectar",
        'save': "Salvar Alterações",
        'tab_dash': "📊 Dashboard",
        'tab_scan': "⚡ Leitura",
        'tab_create': "➕ Criar Item",
        'tab_data': "🗃️ Base de Dados",
        'config_header': "⚙️ Configuração",
        'method': "Método de Entrada:",
        'cam_mode': "📹 Webcam / Celular",
        'usb_mode': "🔌 Scanner USB",
        'man_mode': "👆 Seleção Manual",
        'mobile_compat': "📱 Modo Compatibilidade",
        'action': "Ação:",
        'act_add': "📥 ADICIONAR (+)",
        'act_remove': "📤 REMOVER (-)",
        'act_sell': "💸 VENDER ($)",
        'qty': "Qtd:",
        'wait_usb': "Aguardando Scanner...",
        'input': "Input:",
        'take_photo': "Tirar Foto do QR",
        'sel_prod': "Selecione o Produto:",
        'exec_btn': "✅ EXECUTAR AÇÃO",
        'err_not_found': "❌ Não encontrado",
        'err_error': "Erro",
        'warn_no_qr': "Nada detectado",
        'low_stock': "⚠️ BAIXO ESTOQUE",
        'sold': "VENDIDO",
        'added': "ADICIONADO",
        'removed': "REMOVIDO",
        'new_item': "Cadastrar Item",
        'name': "Nome",
        'id_barcode': "ID / Barcode",
        'initial_stock': "Estoque Inicial",
        'min_alert': "⚠️ Alerta Mínimo",
        'cost': "Custo Unitário",
        'price': "Preço Venda",
        'image': "Imagem",
        'saved': "Salvo!",
        'gen_new_id': "Gerar Novo ID",
        'id_exists': "ID já existe",
        'dash_header': "📊 Análise de Performance",
        'data_header': "🗃️ Gerenciamento de Estoque",
        'items': "Itens",
        'pieces': "Peças",
        'stock_val': "Valor Estoque",
        'pot_sales': "Potencial Venda",
        'profit': "Lucro",
        'refresh': "🔄 Atualizar Tabela",
        'hist_header': "📜 Histórico (Logs)",
        'lang_sel': "🌐 Idioma / Language",
        'no_img_text': "SEM FOTO",
        'vs_prev': "vs anterior",
        'ana_period': "📅 Período de Análise",
        'p_7d': "7 Dias",
        'p_30d': "30 Dias",
        'p_3m': "3 Meses",
        'p_6m': "6 Meses",
        'p_1y': "1 Ano",
        'p_all': "Todo o Período",
        'g_daily': "📊 Lucro Diário",
        'g_cum': "📈 Crescimento Acumulado",
        'g_vol': "📉 Volume de Vendas",
        'edit_item': "📝 Editar Item Completo",
        'edit_sel': "Selecione um Produto para Editar:",
        'regen_assets': "🔄 Regenerar QR & Barcode",
        'assets_ok': "Assets regenerados!",
        'item_updated': "Item atualizado com sucesso!",
        'desc_dash': "Visão geral financeira.",
        'desc_scan': "Processe vendas.",
        'desc_create': "Cadastre novos produtos.",
        'desc_data': "Tabela completa.",
        'h_method': "Escolha como você vai ler.",
        'h_action': "Ação.",
        'h_qty': "Qtd.",
        'h_backup': "Baixar Backup (.zip)",
        'backup_btn': "📥 Baixar Backup",
        'backup_ok': "Backup gerado!",
        'delete_item': "🗑️ Excluir Item",
        'delete_confirm': "Tem certeza que deseja excluir este item? Esta ação não pode ser desfeita.",
        'delete_ok': "Item excluído com sucesso!",
        'auto_backup_ok': "Backup automático criado.",
        'cloud_warning': "⚠️ Dados em nuvem são temporários e podem ser perdidos ao reiniciar."
    },
    'EN': {
        'lic_suspended': "🚫 LICENSE SUSPENDED",
        'lic_used': "🚫 LICENSE ALREADY IN USE",
        'lic_msg': "License deactivated.",
        'lic_msg_used': "Key bound to another machine.",
        'lic_invalid': "❌ Invalid Key",
        'recover_title': "🔐 Activation Required",
        'recover_desc': "Enter valid key.",
        'recover_btn': "🔄 Validate",
        'setup_title': "QUANTIX Setup",
        'setup_sub': "Software Activation",
        'step1': "Step 1: Request Activation",
        'step2': "Step 2: Configure Access",
        'your_id': "Your Machine ID:",
        'email_btn': "📧 Send ID to Support",
        'comp_name': "Company Name",
        'lic_key_label': "License Key",
        'comp_placeholder': "Ex: Pontual Leather",
        'logo_opt': "Logo (Optional)",
        'start_btn': "🚀 Activate & Start",
        'name_required': "All fields required.",
        'success_restart': "Activated! Restarting...",
        'settings': "⚙️ Settings",
        'connect': "📱 Connect",
        'save': "Save Changes",
        'tab_dash': "📊 Dashboard",
        'tab_scan': "⚡ Scan",
        'tab_create': "➕ Create Item",
        'tab_data': "🗃️ Database",
        'config_header': "⚙️ Configuration",
        'method': "Input Method:",
        'cam_mode': "📹 Webcam / Mobile",
        'usb_mode': "🔌 USB Scanner",
        'man_mode': "👆 Manual Selection",
        'mobile_compat': "📱 Mobile Mode",
        'action': "Action:",
        'act_add': "📥 ADD (+)",
        'act_remove': "📤 REMOVE (-)",
        'act_sell': "💸 SELL ($)",
        'qty': "Qty:",
        'wait_usb': "Waiting for Scanner...",
        'input': "Input:",
        'take_photo': "Take QR Photo",
        'sel_prod': "Select Product:",
        'exec_btn': "✅ EXECUTE ACTION",
        'err_not_found': "❌ Not Found",
        'err_error': "Error",
        'warn_no_qr': "Nothing detected",
        'low_stock': "⚠️ LOW STOCK",
        'sold': "SOLD",
        'added': "ADDED",
        'removed': "REMOVED",
        'new_item': "Register New Item",
        'name': "Name",
        'id_barcode': "ID / Barcode",
        'initial_stock': "Initial Stock",
        'min_alert': "⚠️ Min Alert",
        'cost': "Unit Cost",
        'price': "Sell Price",
        'image': "Image",
        'saved': "Saved!",
        'gen_new_id': "Generate New ID",
        'id_exists': "ID already exists",
        'dash_header': "📊 Performance Analytics",
        'data_header': "🗃️ Inventory Management",
        'items': "Items",
        'pieces': "Units",
        'stock_val': "Stock Value",
        'pot_sales': "Potential Sales",
        'profit': "Profit",
        'refresh': "🔄 Refresh Table",
        'hist_header': "📜 History (Logs)",
        'lang_sel': "🌐 Language",
        'no_img_text': "NO IMAGE",
        'vs_prev': "vs previous",
        'ana_period': "📅 Analysis Period",
        'p_7d': "7 Days",
        'p_30d': "30 Days",
        'p_3m': "3 Months",
        'p_6m': "6 Months",
        'p_1y': "1 Year",
        'p_all': "All Time",
        'g_daily': "📊 Daily Profit",
        'g_cum': "📈 Cumulative Growth",
        'g_vol': "📉 Sales Volume",
        'edit_item': "📝 Edit Full Item",
        'edit_sel': "Select Product to Edit:",
        'regen_assets': "🔄 Regenerate QR & Barcode",
        'assets_ok': "Assets regenerated!",
        'item_updated': "Item updated successfully!",
        'desc_dash': "Financial overview.",
        'desc_scan': "Process sales.",
        'desc_create': "Register products.",
        'desc_data': "Full inventory table.",
        'h_method': "Choose input.",
        'h_action': "Action.",
        'h_qty': "Qty.",
        'h_backup': "Download Backup (.zip)",
        'backup_btn': "📥 Download Backup",
        'backup_ok': "Backup generated!",
        'delete_item': "🗑️ Delete Item",
        'delete_confirm': "Are you sure you want to delete this item? This action cannot be undone.",
        'delete_ok': "Item deleted successfully!",
        'auto_backup_ok': "Auto-backup created.",
        'cloud_warning': "⚠️ Cloud data is ephemeral and may be lost on restart."
    },
    'ES': {
        'lic_suspended': "🚫 LICENCIA SUSPENDIDA",
        'lic_used': "🚫 LICENCIA EN USO",
        'lic_msg': "Clave desactivada.",
        'lic_msg_used': "Clave vinculada a otro equipo.",
        'lic_invalid': "❌ Clave Inválida",
        'recover_title': "🔐 Activación Requerida",
        'recover_desc': "Ingrese una clave válida.",
        'recover_btn': "🔄 Validar",
        'setup_title': "Instalación QUANTIX",
        'setup_sub': "Activación de Software",
        'step1': "Paso 1: Solicitar Activación",
        'step2': "Paso 2: Configurar Acceso",
        'your_id': "Su ID de Máquina:",
        'email_btn': "📧 Enviar ID a Soporte",
        'comp_name': "Nombre de la Empresa",
        'lic_key_label': "Clave de Licencia",
        'comp_placeholder': "Ej: Pontual Leather",
        'logo_opt': "Logo (Opcional)",
        'start_btn': "🚀 Activar e Iniciar",
        'name_required': "Campos obligatorios.",
        'success_restart': "¡Activado! Reiniciando...",
        'settings': "⚙️ Configuraciones",
        'connect': "📱 Conectar",
        'save': "Guardar Cambios",
        'tab_dash': "📊 Tablero",
        'tab_scan': "⚡ Escanear",
        'tab_create': "➕ Crear Artículo",
        'tab_data': "🗃️ Base de Datos",
        'config_header': "⚙️ Configuración",
        'method': "Método de Entrada:",
        'cam_mode': "📹 Cámara / Móvil",
        'usb_mode': "🔌 Escáner USB",
        'man_mode': "👆 Selección Manual",
        'mobile_compat': "📱 Modo Compatibilidad",
        'action': "Acción:",
        'act_add': "📥 AGREGAR (+)",
        'act_remove': "📤 QUITAR (-)",
        'act_sell': "💸 VENDER ($)",
        'qty': "Cant:",
        'wait_usb': "Esperando Escáner...",
        'input': "Entrada:",
        'take_photo': "Tomar Foto QR",
        'sel_prod': "Seleccionar Producto:",
        'exec_btn': "✅ EJECUTAR ACCIÓN",
        'err_not_found': "❌ No Encontrado",
        'err_error': "Error",
        'warn_no_qr': "Nada detectado",
        'low_stock': "⚠️ BAJO STOCK",
        'sold': "VENDIDO",
        'added': "AGREGADO",
        'removed': "QUITADO",
        'new_item': "Registrar Artículo",
        'name': "Nombre",
        'id_barcode': "ID / Código",
        'initial_stock': "Stock Inicial",
        'min_alert': "⚠️ Alerta Mín",
        'cost': "Costo Unitario",
        'price': "Precio Venta",
        'image': "Imagen",
        'saved': "¡Guardado!",
        'gen_new_id': "Generar Nuevo ID",
        'id_exists': "ID ya existe",
        'dash_header': "📊 Análisis de Rendimiento",
        'data_header': "🗃️ Gestión de Inventario",
        'items': "Artículos",
        'pieces': "Unidades",
        'stock_val': "Valor Stock",
        'pot_sales': "Ventas Potenc.",
        'profit': "Ganancia",
        'refresh': "🔄 Actualizar Tabla",
        'hist_header': "📜 Historial (Logs)",
        'lang_sel': "🌐 Idioma",
        'no_img_text': "SIN FOTO",
        'vs_prev': "vs anterior",
        'ana_period': "📅 Período de Análisis",
        'p_7d': "7 Días",
        'p_30d': "30 Días",
        'p_3m': "3 Meses",
        'p_6m': "6 Meses",
        'p_1y': "1 Año",
        'p_all': "Todo el Tiempo",
        'g_daily': "📊 Ganancia Diaria",
        'g_cum': "📈 Crecimiento Acumulado",
        'g_vol': "📉 Volumen de Ventas",
        'edit_item': "📝 Editar Artículo",
        'edit_sel': "Seleccione Producto:",
        'regen_assets': "🔄 Regenerar QR y Barcode",
        'assets_ok': "¡Regenerado!",
        'item_updated': "¡Artículo actualizado!",
        'desc_dash': "Visión financiera.",
        'desc_scan': "Procesar ventas.",
        'desc_create': "Registrar nuevos.",
        'desc_data': "Tabla completa.",
        'h_method': "Elija entrada.",
        'h_action': "Acción.",
        'h_qty': "Cantidad.",
        'h_backup': "Descargar Backup (.zip)",
        'backup_btn': "📥 Descargar Backup",
        'backup_ok': "¡Backup generado!",
        'delete_item': "🗑️ Eliminar Artículo",
        'delete_confirm': "¿Está seguro de eliminar este artículo? Esta acción no se puede deshacer.",
        'delete_ok': "¡Artículo eliminado!",
        'auto_backup_ok': "Backup automático creado.",
        'cloud_warning': "⚠️ Los datos en la nube son temporales y pueden perderse al reiniciar."
    }
}

# --- 1. HELPER TO GET TRANSLATION ---
def t(key):
    lang = st.session_state.get('lang', 'PT')
    return LANG[lang].get(key, key)

# --- 3. CONFIGURATION & PATHS ---
CONFIG_FILE = 'config.json'
DATA_FILE = 'inventory.csv'
HISTORY_FILE = 'history.csv'
QR_FOLDER = 'qr_codes'
BARCODE_FOLDER = 'barcodes'
IMG_FOLDER = 'product_images'
LOGO_FILE = 'logo.png'
PLACEHOLDER_FILE = 'placeholder.png'
APP_ICON_FILE = 'app.jpg' 

BACKUP_FOLDER = 'backups'
BACKUP_MAX = 10

for folder in [QR_FOLDER, BARCODE_FOLDER, IMG_FOLDER, BACKUP_FOLDER]:
    if not os.path.exists(folder): os.makedirs(folder)

def convert_uploaded_image_to_png(uploaded_file, save_path):
    """Convert any uploaded image (including HEIC/HEIF) to PNG and save it."""
    img = Image.open(uploaded_file)
    img = img.convert("RGB")
    img.save(save_path, "PNG")

def auto_backup():
    """Create an auto-backup ZIP on startup if data has changed. Keep last N backups."""
    if not os.path.exists(DATA_FILE):
        return
    existing = sorted(globmod.glob(os.path.join(BACKUP_FOLDER, "backup_*.zip")))
    if existing:
        last_backup_time = os.path.getmtime(existing[-1])
        data_mod_time = os.path.getmtime(DATA_FILE)
        if data_mod_time <= last_backup_time:
            return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_FOLDER, f"backup_{timestamp}.zip")
    with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in [DATA_FILE, HISTORY_FILE, CONFIG_FILE, LOGO_FILE, PLACEHOLDER_FILE]:
            if os.path.exists(f): z.write(f)
        for folder in [IMG_FOLDER, QR_FOLDER, BARCODE_FOLDER]:
            if os.path.exists(folder):
                for root, _, files in os.walk(folder):
                    for file in files: z.write(os.path.join(root, file))
    existing = sorted(globmod.glob(os.path.join(BACKUP_FOLDER, "backup_*.zip")))
    while len(existing) > BACKUP_MAX:
        os.remove(existing.pop(0))

if not os.path.exists(PLACEHOLDER_FILE):
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    img.fill(220)
    cv2.line(img, (50, 50), (250, 250), (150, 150, 150), 5)
    cv2.line(img, (250, 50), (50, 250), (150, 150, 150), 5)
    cv2.rectangle(img, (0,0), (300,300), (100,100,100), 5)
    cv2.imwrite(PLACEHOLDER_FILE, img)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f: return json.load(f)
        except: return None
    return None

def save_config(name):
    current = load_config()
    if current:
        current['company_name'] = name
        with open(CONFIG_FILE, 'w') as f: json.dump(current, f)

def create_backup_zip():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for f in [DATA_FILE, HISTORY_FILE, CONFIG_FILE, LOGO_FILE, PLACEHOLDER_FILE]:
            if os.path.exists(f): z.write(f)
        for folder in [IMG_FOLDER, QR_FOLDER, BARCODE_FOLDER]:
            if os.path.exists(folder):
                for root, _, files in os.walk(folder):
                    for file in files: z.write(os.path.join(root, file))
    return buffer.getvalue()

# --- 4. FIRST RUN SETUP & LICENSE CHECK ---
if 'lang' not in st.session_state: st.session_state.lang = 'PT'

config = load_config()
page_icon_to_use = APP_ICON_FILE if os.path.exists(APP_ICON_FILE) else "💎"

# === CASE A: NO CONFIG (FIRST RUN) ===
if config is None:
    st.set_page_config(page_title="QUANTIX Setup", page_icon=page_icon_to_use)
    st.session_state.lang = st.selectbox("Language / Idioma", ['PT', 'EN', 'ES'], index=0)
    
    col_img, col_txt = st.columns([1, 5])
    with col_img:
        if os.path.exists(APP_ICON_FILE): st.image(APP_ICON_FILE, width=100)
    with col_txt:
        st.title(t('setup_title'))
        st.caption(f"*{t('setup_sub')}*")
    st.markdown("---")
    
    # === STEP 1: GET ID ===
    with st.container(border=True):
        st.subheader(t('step1'))
        c1, c2 = st.columns([2, 1])
        my_hwid = get_machine_id()
        with c1:
            st.info(f"**{t('your_id')}** `{my_hwid}`")
        with c2:
            email_subject = "License Activation Request"
            email_body_raw = f"Hello, please activate my license.\n\nMachine ID: {my_hwid}"
            email_body_enc = urllib.parse.quote(email_body_raw)
            mailto_link = f"mailto:info@wildfireservices.us?subject={email_subject}&body={email_body_enc}"
            
            st.markdown(f'''
                <a href="{mailto_link}" style="text-decoration: none;">
                    <div style="
                        width: 100%;
                        background: linear-gradient(90deg, #6200EA 0%, #7C4DFF 100%);
                        color: white;
                        padding: 14px;
                        border-radius: 8px;
                        text-align: center;
                        font-weight: bold;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                        transition: 0.3s;
                        cursor: pointer;">
                        {t('email_btn')}
                    </div>
                </a>
            ''', unsafe_allow_html=True)

    # === STEP 2: FORM ===
    with st.container(border=True):
        st.subheader(t('step2'))
        with st.form("setup"):
            c_name = st.text_input(t('comp_name'), placeholder=t('comp_placeholder'))
            lic_key = st.text_input(t('lic_key_label'), placeholder="XXXX-XXXX-XXXX")
            c_logo = st.file_uploader(t('logo_opt'), type=['png', 'jpg'])
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button(t('start_btn'), type="primary", use_container_width=True):
                if c_name and lic_key:
                    is_valid, status = check_license(lic_key.strip())
                    if is_valid:
                        data = {"company_name": c_name, "license_key": lic_key.strip()}
                        with open(CONFIG_FILE, 'w') as f: json.dump(data, f)
                        if c_logo:
                            with open(LOGO_FILE, "wb") as f: f.write(c_logo.getbuffer())
                        st.success(t('success_restart'))
                        time.sleep(1)
                        st.rerun()
                    else:
                        if status == "SUSPENDED": st.error(t('lic_suspended'))
                        elif status == "USED_ELSEWHERE": st.error(t('lic_used'))
                        elif status == "INVALID": st.error(t('lic_invalid'))
                        else: st.error(t('lic_error'))
                else:
                    st.error(t('name_required'))
    st.stop()

# === CASE B: CONFIG EXISTS (NORMAL RUN) ===
else:
    saved_key = config.get('license_key', '')
    is_valid, status = check_license(saved_key)
    
    if not is_valid:
        st.set_page_config(page_title="Access Denied", page_icon="🚫")
        
        if status == "SUSPENDED":
            st.error(t('lic_suspended')); st.warning(t('lic_msg'))
        elif status == "USED_ELSEWHERE":
            st.error(t('lic_used')); st.warning(t('lic_msg_used')); st.caption(f"{t('your_id')} {get_machine_id()}")
        else:
            st.error(t('lic_invalid')); st.info(t('recover_desc'))
        
        st.markdown("---")
        st.subheader(t('recover_title'))
        
        with st.form("recover_form"):
            new_key = st.text_input(t('lic_key_label'), placeholder="XXXX-XXXX-XXXX")
            if st.form_submit_button(t('recover_btn'), type="primary"):
                if new_key:
                    val, stat = check_license(new_key.strip())
                    if val:
                        config['license_key'] = new_key.strip()
                        with open(CONFIG_FILE, 'w') as f: json.dump(config, f)
                        st.success(t('success_restart'))
                        time.sleep(1)
                        st.rerun()
                    else: st.error(t('lic_invalid'))
                else: st.warning("Input required.")
        st.stop()

# --- 5. MAIN APP UI ---
st.set_page_config(page_title=f"QUANTIX | {config.get('company_name')}", page_icon=page_icon_to_use, layout="wide")

# Auto-backup on startup
auto_backup()

# Style the native file uploader drop zones
st.markdown("""<style>
    [data-testid="stFileUploader"] section {
        border: 2px dashed #6200EA !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: #7C4DFF !important;
        background-color: rgba(98, 0, 234, 0.04) !important;
    }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    if os.path.exists(LOGO_FILE): st.image(LOGO_FILE, width='stretch')
    st.markdown(f"## {config.get('company_name')}")
    st.caption("Powered by **QUANTIX**")
    st.markdown("---")
    
    lang_choice = st.selectbox(t('lang_sel'), ['PT', 'EN', 'ES'], index=['PT','EN','ES'].index(st.session_state.lang))
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

    with st.expander(t('settings')):
        with st.form("settings"):
            new_n = st.text_input(t('name'), value=config.get('company_name'))
            new_l = st.file_uploader("Logo", type=['png','jpg'])
            if st.form_submit_button(t('save')):
                save_config(new_n)
                if new_l:
                    with open(LOGO_FILE, "wb") as f: f.write(new_l.getbuffer())
                st.rerun()
        
        st.markdown("---")
        st.markdown(f"**{t('h_backup')}**")
        zip_data = create_backup_zip()
        st.download_button(label=t('backup_btn'), data=zip_data, file_name=f"quantix_backup_{datetime.now().strftime('%Y%m%d')}.zip", mime="application/zip", help=t('h_backup'))
    
    st.markdown("---")
    st.header(t('connect'))
    def get_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]; s.close(); return ip
        except: return "127.0.0.1"
    ip = get_ip()
    st.image(qrcode.make(f"http://{ip}:8501").get_image(), width=150)
    st.caption(f"http://{ip}:8501")

st.title(f"📦 {config.get('company_name')}")

# --- DEFINING COLUMNS (THE MISSING PIECE) ---
EXPECTED_COLS = ['product_id', 'product_name', 'quantity', 'min_stock', 'cost_price', 'sell_price', 'last_updated', 'image_path', 'qr_path', 'barcode_path']

def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=EXPECTED_COLS)
        df.to_csv(DATA_FILE, index=False)
        return df
    df = pd.read_csv(DATA_FILE)
    df['product_id'] = df['product_id'].astype(str)
    changed = False
    for col in EXPECTED_COLS:
        if col not in df.columns:
            df[col] = 0.0 if 'price' in col else None
            changed = True
    for i, row in df.iterrows():
        pid = str(row['product_id'])
        found_img = False
        current_path = str(row.get('image_path'))
        if pd.isna(current_path) or not os.path.exists(current_path) or current_path == 'nan':
            for ext in ['.png', '.jpg', '.jpeg']:
                p = os.path.join(IMG_FOLDER, f"{pid}{ext}")
                if os.path.exists(p): 
                    df.at[i, 'image_path'] = p; found_img = True; changed = True; break
            if not found_img: df.at[i, 'image_path'] = PLACEHOLDER_FILE; changed = True
        qp = os.path.join(QR_FOLDER, f"{pid}.png")
        if (pd.isna(row.get('qr_path')) or row.get('qr_path') != qp) and os.path.exists(qp): df.at[i, 'qr_path'] = qp; changed = True
        bp = os.path.join(BARCODE_FOLDER, f"{pid}.png")
        if (pd.isna(row.get('barcode_path')) or row.get('barcode_path') != bp) and os.path.exists(bp): df.at[i, 'barcode_path'] = bp; changed = True
    if changed: df.to_csv(DATA_FILE, index=False)
    return df

def save_data(df): df.to_csv(DATA_FILE, index=False)

def log_trans(pid, name, change, total, custom_action=None):
    if not os.path.exists(HISTORY_FILE): pd.DataFrame(columns=['timestamp', 'product_id', 'product_name', 'action', 'amount', 'new_total']).to_csv(HISTORY_FILE, index=False)
    if custom_action: action = custom_action
    else: action = "ADD" if change > 0 else "REMOVE"
    pd.DataFrame([{'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'product_id': pid, 'product_name': name, 'action': action, 'amount': abs(change), 'new_total': total}]).to_csv(HISTORY_FILE, mode='a', header=False, index=False)

def path_to_image_html(path):
    if pd.isna(path) or not os.path.exists(str(path)): return None
    try:
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            ext = path.split('.')[-1]
            return f"data:image/{ext};base64,{encoded}"
    except: return None

tab_dash, tab_scan, tab_gen, tab_data_ui = st.tabs([t('tab_dash'), t('tab_scan'), t('tab_create'), t('tab_data')])

with tab_dash:
    st.header(t('dash_header'), help=t('desc_dash'))
    df = load_data()
    df['cost_price'] = pd.to_numeric(df['cost_price'], errors='coerce').fillna(0)
    df['sell_price'] = pd.to_numeric(df['sell_price'], errors='coerce').fillna(0)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(t('items'), len(df))
    m2.metric(t('pieces'), int(df['quantity'].sum()))
    tot_cost = (df['quantity'] * df['cost_price']).sum()
    tot_sell = (df['quantity'] * df['sell_price']).sum()
    m3.metric(t('stock_val'), f"R$ {tot_cost:,.2f}")
    m4.metric(t('pot_sales'), f"R$ {tot_sell:,.2f}", delta=f"{t('profit')}: {tot_sell-tot_cost:,.2f}")
    st.markdown("---")
    if os.path.exists(HISTORY_FILE):
        hist = pd.read_csv(HISTORY_FILE)
        df_prices = df[['product_id', 'cost_price', 'sell_price']]
        hist['product_id'] = hist['product_id'].astype(str)
        merged = pd.merge(hist, df_prices, on='product_id', how='left')
        sales = merged[merged['action'] == 'SALE'].copy()
        if not sales.empty:
            sales['profit'] = (sales['sell_price'] - sales['cost_price']) * sales['amount']
            sales['timestamp'] = pd.to_datetime(sales['timestamp']); sales['date'] = sales['timestamp'].dt.date; now = datetime.now().date()
            st.subheader(t('ana_period'))
            period_opt = st.selectbox("Selecione:", [t('p_7d'), t('p_30d'), t('p_3m'), t('p_6m'), t('p_1y'), t('p_all')], label_visibility="collapsed")
            days_map = {t('p_7d'): 7, t('p_30d'): 30, t('p_3m'): 90, t('p_6m'): 180, t('p_1y'): 365, t('p_all'): 36500}
            days = days_map[period_opt]
            curr_mask = (sales['date'] > now - timedelta(days=days)) & (sales['date'] <= now)
            prev_mask = (sales['date'] > now - timedelta(days=days*2)) & (sales['date'] <= now - timedelta(days=days))
            val_curr = sales[curr_mask]['profit'].sum(); val_prev = sales[prev_mask]['profit'].sum(); delta = val_curr - val_prev
            st.metric(f"💰 Lucro ({period_opt})", f"R$ {val_curr:,.2f}", delta=f"{delta:,.2f} {t('vs_prev')}")
            g_tab1, g_tab2, g_tab3 = st.tabs([t('g_daily'), t('g_cum'), t('g_vol')])
            chart_data = sales[curr_mask].copy()
            if not chart_data.empty:
                grouped_day = chart_data.groupby('date')['profit'].sum()
                grouped_cum = chart_data.groupby('date')['profit'].sum().cumsum()
                grouped_vol = chart_data.groupby('date')['amount'].sum()
                with g_tab1: st.bar_chart(grouped_day)
                with g_tab2: st.line_chart(grouped_cum)
                with g_tab3: st.area_chart(grouped_vol)
            else: st.info("Sem dados para este período.")
    if st.button("🔄 Refresh Data"): st.rerun()

with tab_scan:
    st.header(t('tab_scan'), help=t('desc_scan'))
    c1, c2 = st.columns([1, 2])
    with c1:
        st.write(f"### {t('config_header')}")
        method = st.radio(t('method'), [t('cam_mode'), t('usb_mode'), t('man_mode')], help=t('h_method'))
        mobile = False
        if method == t('cam_mode'): 
            st.write(""); mobile = st.checkbox(t('mobile_compat'), value=True)
        st.markdown("---")
        mode_label = st.radio(t('action'), [t('act_add'), t('act_remove'), t('act_sell')], help=t('h_action'))
        qty = st.number_input(t('qty'), min_value=1, value=1, help=t('h_qty'))
    with c2:
        def update_stock(code):
            df = pd.read_csv(DATA_FILE); df['product_id'] = df['product_id'].astype(str)
            if code in df['product_id'].values:
                row = df.loc[df['product_id'] == code].iloc[0]
                curr, lim, name = row['quantity'], row['min_stock'], row['product_name']
                if mode_label == t('act_add'): change = qty; action_code = "ADD"; msg_verb = t('added')
                elif mode_label == t('act_sell'): change = -qty; action_code = "SALE"; msg_verb = t('sold')
                else: change = -qty; action_code = "REMOVE"; msg_verb = t('removed')
                new_q = max(0, curr + change)
                df.loc[df['product_id'] == code, 'quantity'] = new_q
                df.loc[df['product_id'] == code, 'last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.to_csv(DATA_FILE, index=False)
                log_trans(code, name, change, new_q, custom_action=action_code)
                if new_q <= lim: st.error(f"{t('low_stock')}: {name} ({new_q})!"); st.toast(f"⚠️ {name}", icon="🚨")
                else: st.toast(f"✅ {msg_verb}: {name} ({new_q})", icon="💰" if action_code == "SALE" else "📦")
                return True
            return False
        if method == t('man_mode'):
            st.info(t('man_mode'))
            df_man = load_data()
            if not df_man.empty:
                df_man['label'] = df_man['product_name'] + " (" + df_man['product_id'].astype(str) + ")"
                options = df_man['label'].tolist(); selected_label = st.selectbox(t('sel_prod'), options)
                selected_id = selected_label.split('(')[-1].replace(')', '')
                row = df_man.loc[df_man['product_id'] == selected_id].iloc[0]
                img_path = row['image_path']
                if img_path and os.path.exists(img_path): st.image(img_path, width=200, caption=row['product_name'])
                if st.button(t('exec_btn'), use_container_width=True): update_stock(selected_id)
            else: st.warning("Nenhum produto cadastrado.")
        elif method == t('usb_mode'):
            st.info(t('wait_usb')); label_name = t('input')
            components.html(f"""<script>var input = window.parent.document.querySelector('input[aria-label="{label_name}"]'); if (input) {{ input.focus(); input.addEventListener('blur', function() {{ setTimeout(function(){{ input.focus(); }}, 50); }}); }}</script>""", height=0)
            components.html(f"""<script>const doc = window.parent.document; const input = doc.querySelector('input[aria-label="{label_name}"]'); if (input) {{ var timer = null; input.addEventListener('input', function() {{ if (timer) clearTimeout(timer); timer = setTimeout(() => {{ input.blur(); }}, 300); }}); }}</script>""", height=0)
            if "usb" not in st.session_state: st.session_state.usb = ""
            def usb_cb():
                c = str(st.session_state.usb_in).strip()
                if c: 
                    if not update_stock(c): st.toast(t('err_not_found'), icon="⚠️")
                    st.session_state.usb_in = ""
            st.text_input(t('input'), key="usb_in", on_change=usb_cb)
        elif mobile:
            st.info(t('take_photo')); img = st.file_uploader("QR", type=['png','jpg','heic','heif'], key="mob", label_visibility="collapsed")
            if img:
                pil_img = Image.open(img).convert("RGB")
                cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                d, _, _ = cv2.QRCodeDetector().detectAndDecode(cv_img)
                if d: 
                    if update_stock(d): st.success(f"Lido: {d}")
                    else: st.error(t('err_error'))
                else: st.warning(t('warn_no_qr'))
        else:
            class VideoProcessor:
                def recv(self, frame):
                    img = frame.to_ndarray(format="bgr24"); d, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
                    return av.VideoFrame.from_ndarray(img, format="bgr24")
            webrtc_streamer(key="cam", mode=WebRtcMode.SENDRECV, video_processor_factory=VideoProcessor, async_processing=True)

with tab_gen:
    st.header(t('new_item'), help=t('desc_create'))
    # Full-screen drag & drop overlay that redirects files to the uploader
    components.html("""
    <style>
        #drop-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100vw; height: 100vh;
            background: rgba(98, 0, 234, 0.15);
            border: 4px dashed #6200EA;
            z-index: 999999;
            justify-content: center;
            align-items: center;
            pointer-events: none;
        }
        #drop-overlay.active { display: flex; pointer-events: auto; }
        #drop-overlay .drop-text {
            font-size: 2rem; font-weight: bold; color: #6200EA;
            background: rgba(255,255,255,0.9); padding: 30px 60px;
            border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
    </style>
    <div id="drop-overlay"><div class="drop-text">📷 Drop image here</div></div>
    <script>
    const doc = window.parent.document;
    const overlay = document.getElementById('drop-overlay');
    let dragCounter = 0;

    doc.addEventListener('dragenter', function(e) {
        e.preventDefault();
        dragCounter++;
        if (e.dataTransfer && e.dataTransfer.types && e.dataTransfer.types.indexOf('Files') !== -1) {
            overlay.classList.add('active');
        }
    });
    doc.addEventListener('dragleave', function(e) {
        e.preventDefault();
        dragCounter--;
        if (dragCounter <= 0) { overlay.classList.remove('active'); dragCounter = 0; }
    });
    doc.addEventListener('dragover', function(e) { e.preventDefault(); });
    doc.addEventListener('drop', function(e) {
        e.preventDefault();
        overlay.classList.remove('active');
        dragCounter = 0;
        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            // Find the file uploader input in the Criar Item tab
            const uploaders = doc.querySelectorAll('input[type="file"]');
            for (const input of uploaders) {
                const accept = input.getAttribute('accept') || '';
                if (accept.includes('heic') || accept.includes('image')) {
                    const dt = new DataTransfer();
                    dt.items.add(e.dataTransfer.files[0]);
                    input.files = dt.files;
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    break;
                }
            }
        }
    });
    overlay.addEventListener('drop', function(e) {
        e.preventDefault();
        overlay.classList.remove('active');
        dragCounter = 0;
        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            const uploaders = doc.querySelectorAll('input[type="file"]');
            for (const input of uploaders) {
                const accept = input.getAttribute('accept') || '';
                if (accept.includes('heic') || accept.includes('image')) {
                    const dt = new DataTransfer();
                    dt.items.add(e.dataTransfer.files[0]);
                    input.files = dt.files;
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    break;
                }
            }
        }
    });
    </script>
    """, height=0)
    if 'gen_id' not in st.session_state: st.session_state.gen_id = str(random.randint(10000000, 99999999))
    with st.form("new"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input(t('name'))
            pid = st.text_input(t('id_barcode'), value=st.session_state.generated_id if 'generated_id' in st.session_state else st.session_state.gen_id)
            q = st.number_input(t('initial_stock'), min_value=0)
            lim = st.number_input(t('min_alert'), value=5)
            cost = st.number_input(t('cost'), min_value=0.0, format="%.2f")
            sell = st.number_input(t('price'), min_value=0.0, format="%.2f")
        with c2:
            up_img = st.file_uploader(t('image'), type=['png','jpg','jpeg','heic','heif'])
            if up_img:
                st.image(up_img, caption=up_img.name, width='stretch')
            else:
                st.image(PLACEHOLDER_FILE, caption=t('no_img_text'), width='stretch')
        if st.form_submit_button(t('save')):
            if name and pid:
                df = load_data()
                if pid in df['product_id'].values: st.error(t('id_exists'))
                else:
                    ipath = PLACEHOLDER_FILE
                    if up_img:
                        ipath = os.path.join(IMG_FOLDER, f"{pid}.png")
                        convert_uploaded_image_to_png(up_img, ipath)
                    qp = os.path.join(QR_FOLDER, f"{pid}.png"); qrcode.make(pid).save(qp)
                    bp = os.path.join(BARCODE_FOLDER, f"{pid}.png"); barcode.get('code128', pid, writer=ImageWriter()).save(os.path.join(BARCODE_FOLDER, pid))
                    pd.concat([df, pd.DataFrame([{'product_id': pid, 'product_name': name, 'quantity': q, 'min_stock': lim, 'cost_price': cost, 'sell_price': sell, 'last_updated': datetime.now().strftime("%Y-%m-%d"), 'image_path': ipath, 'qr_path': qp, 'barcode_path': f"{bp}.png"}])], ignore_index=True).to_csv(DATA_FILE, index=False)
                    st.success(t('saved')); st.session_state.gen_id = str(random.randint(10000000, 99999999)); st.rerun()
    if st.button(t('gen_new_id')): st.session_state.gen_id = str(random.randint(10000000, 99999999)); st.rerun()

with tab_data_ui:
    st.header(t('data_header'), help=t('desc_data')); 
    if st.button(t('refresh')): st.rerun()
    df = load_data()
    with st.expander(t('edit_item'), expanded=False):
        if not df.empty:
            st.info(t('edit_sel'))
            df['display_label'] = df['product_name'] + " (" + df['product_id'].astype(str) + ")"
            opts = df['display_label'].tolist(); sel_item = st.selectbox("Product", opts, label_visibility="collapsed")
            sel_id = sel_item.split('(')[-1].replace(')', '')
            row = df.loc[df['product_id'] == sel_id].iloc[0]
            with st.form("edit_form"):
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    new_name = st.text_input(t('name'), value=row['product_name'])
                    new_qty = st.number_input(t('qty'), value=int(row['quantity']), min_value=0)
                    new_lim = st.number_input(t('min_alert'), value=int(row['min_stock']), min_value=0)
                with col_b:
                    new_cost = st.number_input(t('cost'), value=float(row['cost_price']), min_value=0.0, format="%.2f")
                    new_sell = st.number_input(t('price'), value=float(row['sell_price']), min_value=0.0, format="%.2f")
                    curr_path = row['image_path']
                    if os.path.exists(curr_path): st.image(curr_path, width=100, caption="Atual")
                    new_img_file = st.file_uploader(t('image'), type=['png','jpg','jpeg','heic','heif'], key="edit_img")
                if st.form_submit_button(t('save')):
                    df.loc[df['product_id'] == sel_id, 'product_name'] = new_name
                    df.loc[df['product_id'] == sel_id, 'quantity'] = new_qty
                    df.loc[df['product_id'] == sel_id, 'min_stock'] = new_lim
                    df.loc[df['product_id'] == sel_id, 'cost_price'] = new_cost
                    df.loc[df['product_id'] == sel_id, 'sell_price'] = new_sell
                    if new_img_file:
                        new_path = os.path.join(IMG_FOLDER, f"{sel_id}.png")
                        convert_uploaded_image_to_png(new_img_file, new_path)
                        # Remove old image if it had a different extension
                        for old in globmod.glob(os.path.join(IMG_FOLDER, f"{sel_id}.*")):
                            if old != new_path and os.path.exists(old): os.remove(old)
                        df.loc[df['product_id'] == sel_id, 'image_path'] = new_path
                    save_data(df); st.success(t('item_updated')); time.sleep(1); st.rerun()
            col_regen, col_del = st.columns(2)
            with col_regen:
                if st.button(t('regen_assets'), use_container_width=True):
                    qp = os.path.join(QR_FOLDER, f"{sel_id}.png"); qrcode.make(sel_id).save(qp)
                    bp = os.path.join(BARCODE_FOLDER, f"{sel_id}.png"); barcode.get('code128', sel_id, writer=ImageWriter()).save(os.path.join(BARCODE_FOLDER, sel_id))
                    st.success(t('assets_ok')); time.sleep(1); st.rerun()
            with col_del:
                if st.button(t('delete_item'), type="primary", use_container_width=True):
                    st.session_state['confirm_delete'] = sel_id
            if st.session_state.get('confirm_delete') == sel_id:
                st.warning(t('delete_confirm'))
                cd1, cd2 = st.columns(2)
                with cd1:
                    if st.button("✅ Confirm", key="del_yes", use_container_width=True):
                        # Delete from CSV
                        df = df[df['product_id'] != sel_id]
                        save_data(df)
                        # Delete associated files
                        for pattern in [os.path.join(IMG_FOLDER, f"{sel_id}.*"),
                                        os.path.join(QR_FOLDER, f"{sel_id}.png"),
                                        os.path.join(BARCODE_FOLDER, f"{sel_id}.png")]:
                            for fpath in globmod.glob(pattern):
                                if os.path.exists(fpath): os.remove(fpath)
                        st.session_state.pop('confirm_delete', None)
                        st.success(t('delete_ok')); time.sleep(1); st.rerun()
                with cd2:
                    if st.button("❌ Cancel", key="del_no", use_container_width=True):
                        st.session_state.pop('confirm_delete', None); st.rerun()
        else: st.warning("Sem produtos.")
    disp = df.copy()
    disp['img_d'] = disp['image_path'].apply(path_to_image_html)
    disp['qr_d'] = disp['qr_path'].apply(path_to_image_html)
    disp['bc_d'] = disp['barcode_path'].apply(path_to_image_html)
    disp['Status'] = disp['quantity'].apply(lambda x: "🟢" if x>=25 else "🟡" if x>=5 else "🔴")
    ed = st.data_editor(disp, column_config={"Status": st.column_config.TextColumn("St", width="small"), "img_d": st.column_config.ImageColumn("📸", width="small"), "qr_d": st.column_config.ImageColumn("QR", width="small"), "bc_d": st.column_config.ImageColumn("Bar", width="medium"), "quantity": st.column_config.ProgressColumn("Qtd", max_value=100), "cost_price": st.column_config.NumberColumn(t('cost'), format="R$ %.2f"), "sell_price": st.column_config.NumberColumn(t('price'), format="R$ %.2f"), "image_path": None, "qr_path": None, "barcode_path": None, "display_label": None}, use_container_width=True, num_rows="dynamic", key="editor", column_order=["Status", "img_d", "product_id", "product_name", "quantity", "cost_price", "sell_price", "min_stock", "qr_d", "bc_d"])
    if not disp.equals(ed):
        for c in ['product_name', 'quantity', 'min_stock', 'cost_price', 'sell_price']: df[c] = ed[c]
        if len(df) != len(ed): save_data(ed.drop(columns=['img_d','qr_d','bc_d','Status', 'display_label']))
        else: save_data(df)
        st.toast(t('saved'), icon="💾"); time.sleep(0.5); st.rerun()
    with st.expander(t('hist_header')):
        if os.path.exists(HISTORY_FILE): st.dataframe(pd.read_csv(HISTORY_FILE).sort_values('timestamp', ascending=False), use_container_width=True)