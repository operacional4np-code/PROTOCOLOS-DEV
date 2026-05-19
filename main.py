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
    # 1. Borda do Bloco
    c.rect(40, y, 520, 180, stroke=1, fill=0)
    
    # 2. LOGO - Ajustado para "logo.png.JPG"
    logo_filename = "logo.png.JPG"
    logo_path = os.path.join(os.path.dirname(__file__), logo_filename)
    
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 45, y + 155, width=80, height=20, preserveAspectRatio=True, mask='auto')
    
    # Cabeçalho e Divisor
    c.line(40, y + 150, 560, y + 150)
    c.line(420, y + 150, 420, y + 180)
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(140, y + 160, "PROTOCOLO DE DEVOLUÇÃO")
    
    # Lógica de Prefixo (MG ou PE)
    destino = str(row.get('destino', '')).upper()
    prefixo = "MG" if "BETIM" in destino else "PE"
    
    c.setFont("Helvetica", 9)
    c.drawString(430, y + 165, "PROTOCOLO Nº:")
    c.setFont("Helvetica-Bold", 12)
    
    # MUDANÇA AQUI: Apenas desenha o prefixo + linha, sem o número
    c.drawString(430, y + 153, f"{prefixo}-")
    c.line(460, y + 153, 540, y + 153) 
    
    # 3. Campos
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 130, "CLIENTE:")
    c.line(100, y + 128, 550, y + 128)
    c.setFont("Helvetica", 10)
    c.drawString(100, y + 132, str(row.get('nome', '')).upper())
    
    # NF e CTE
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 105, "Nº NOTA FISCAL:")
    c.line(130, y + 103, 350, y + 103)
    c.drawString(370, y + 105, "Nº CTE:")
    c.line(420, y + 103, 550, y + 103)
    
    c.setFont("Helvetica", 10)
    c.drawString(140, y + 107, limpar_float(row.get('nota fiscal', '')))
    c.drawString(430, y + 107, str(row.get('cte', '')))
    
    # Rodapé - Dados
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 80, "DATA:")
    c.line(80, y + 78, 250, y + 78)
    
    c.drawString(270, y + 80, "Nº PROTOCOLO CLIENTE:")
    c.line(400, y + 78, 550, y
