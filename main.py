import streamlit as st
import pandas as pd
import requests
import io
import re
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# --- CONFIGURAÇÕES ---
SHEET_ID = "1f_NDUAezh4g0ztyHVUO_t33QxGai9TYcWOD-IAoPcuE"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

st.set_page_config(page_title="Gerador de Protocolos", page_icon="📄")

@st.cache_data(ttl=2)
def baixar_dados_google_sheets():
    try:
        response = requests.get(URL_CSV)
        response.raise_for_status()
        csv_data = io.StringIO(response.content.decode('utf-8'))
        df = pd.read_csv(csv_data)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

def limpar_float(valor):
    texto = str(valor).strip()
    return texto[:-2] if texto.endswith('.0') else texto

def desenhar_bloco_final(c, y, row):
    # 1. Borda do Bloco (Retângulo principal)
    c.rect(40, y, 520, 180, stroke=1, fill=0)
    
    # 2. LOGO - Ajustado para o nome "logo.png.JPG"
    logo_filename = "logo.png.JPG"
    logo_path = os.path.join(os.path.dirname(__file__), logo_filename)
    
    if os.path.exists(logo_path):
        # Aumentamos um pouco a altura para ficar visível
        c.drawImage(logo_path, 45, y + 155, width=80, height=20, preserveAspectRatio=True, mask='auto')
    
    # Cabeçalho (Linha divisória topo)
    c.line(40, y + 150, 560, y + 150)
    c.line(420, y + 150, 420, y + 180) # Divisor do protocolo
    
    # Título Principal
