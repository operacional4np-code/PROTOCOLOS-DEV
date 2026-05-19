import streamlit as st
import pandas as pd
import requests
import io
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
@st.cache_data(ttl=60) # Atualiza os dados a cada 60 segundos se houver nova busca
def baixar_dados_google_sheets():
    """Busca os dados atualizados diretamente do Google Sheets"""
    try:
        response = requests.get(URL_CSV)
        response.raise_for_status()
        
        # Converte o conteúdo baixado em um DataFrame do Pandas
        csv_data = io.StringIO(response.content.decode('utf-8'))
        df = pd.read_csv(csv_data)
        
        # Padroniza o nome das colunas (remove espaços e põe em minúsculo para evitar erros)
        df.columns = [str(c).strip().lower() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha do Google: {e}")
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
    pdf.drawString(110, y_offset - 30, str(dados['cliente']))
    
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y_offset - 55, "Nº NOTA FISCAL:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(150, y_offset - 55, str(dados['nota_fiscal']))
    
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y_offset - 80, "DATA:")
    pdf.drawString(100, y_offset - 80, "______ / ______ / __________") 
    
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y_offset - 110, "DADOS DO RECEBEDOR:")
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(190, y_offset - 110, "(Nome legível e RG)")
    
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y_offset - 140, "ASSINATURA:")
    pdf.line(130, y_offset - 142, 350, y_offset - 142)
    
    # Coluna da Direita
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(380, y_offset - 30, "Nº CTE:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(430, y_offset - 30, str(dados['cte']))
    
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(380, y_offset - 55, "Nº PROTOCOLO CLIENTE:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(530, y_offset - 55, str(dados['protocolo']))
    
    # Linha tracejada para corte entre os blocos
    pdf.setDash(2, 2)
    pdf.line(30, y_offset - 165, 580, y_offset - 165)
    pdf.setDash(
