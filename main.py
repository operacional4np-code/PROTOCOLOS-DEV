import streamlit as st
import pandas as pd
import requests
import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black

# --- CONFIGURAÇÕES DA PLANILHA ---
SHEET_ID = "1f_NDUAezh4g0ztyHVUO_t33QxGai9TYcWOD-IAoPcuE"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# --- CONFIGURAÇÃO DA PÁGINA WEB ---
st.set_page_config(page_title="Gerador de Protocolos - MG", page_icon="📄", layout="centered")

st.title("📄 Gerador de Protocolos de Devolução")
st.markdown("Insira as Notas Fiscais abaixo para gerar e baixar os protocolos correspondentes.")

# --- FUNÇÕES DE BACKEND ---
@st.cache_data(ttl=30)
def baixar_dados_google_sheets():
    """Busca os dados atualizados diretamente do Google Sheets"""
    try:
        response = requests.get(URL_CSV)
        response.raise_for_status()
        
        csv_data = io.StringIO(response.content.decode('utf-8'))
        df = pd.read_csv(csv_data)
        
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados do Google Sheets: {e}")
        return None

def desenhar_bloco_protocolo(pdf, y_offset, dados):
    """Desenha um dos blocos de protocolo no PDF baseado no modelo de MG"""
    pdf.setStrokeColor(black)
    pdf.setLineWidth(1)
    
    # Cabeçalho do Bloco
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y_offset, "PROTOCOLO DE DEVOLUÇÃO")
    
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(400, y_offset, "PROTOCOLO Nº:")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(500, y_offset, f"MG-{dados['protocolo']}")
    
    # Coluna da Esquerda
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y_offset - 30, "CLIENTE:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(110, y_offset - )
