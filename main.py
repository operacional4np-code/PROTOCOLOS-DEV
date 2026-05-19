import streamlit as st
import pandas as pd
import requests
import io
import re
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black

SHEET_ID = "1f_NDUAezh4g0ztyHVUO_t33QxGai9TYcWOD-IAoPcuE"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

st.set_page_config(page_title="Gerador de Protocolos - MG", page_icon="📄", layout="centered")

st.title("📄 Gerador de Protocolos de Devolução")
st.markdown("Insira as Notas Fiscais abaixo para gerar e baixar os protocolos correspondentes.")

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
        st.error(f"Erro ao carregar dados do Google Sheets: {e}")
        return None

def limpar_float(valor):
    texto = str(valor).strip()
    if texto.endswith('.0'):
        return texto[:-2]
    return texto

def desenhar_bloco_final_mg(pdf, y_offset, dados):
    pdf.setFillColor(black)
    
    caminho_logo = None
    opcoes_nome = ["logo.png.JPG", "logo.png", "logo.jpg", "logo.jpeg", "logo.png.jpg", "LOGO.JPG", "LOGO.PNG"]
    for opcao in opcoes_nome:
        if os.path.exists(opcao):
            caminho_logo = opcao
            break
            
    if caminho_logo:
        pdf.drawImage(caminho_logo, 45, y_offset + 10, width=100, height=30, preserveAspectRatio=True, mask='auto')
    else:
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(45, y_offset + 20, "NEW POST")
    
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(380, y_offset + 20, "PROTOCOLO Nº:")
    pdf.setFont("Helvetica", 11)
    p_num = f"MG-{limpar_float(dados['protocolo'])}"
    pdf.drawString(485, y_offset + 20, p_num)
    
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(45, y_offset - 15, "PROTOCOLO DE DEVOLUÇÃO")
    
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(45, y_offset - 45, "CLIENTE:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(105, y_offset - 45, str(dados['cliente']).upper())
    
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(380, y_offset - 45, "Nº CTE:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(430, y_offset - 45, limpar_float(dados['cte']))
    
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(45, y_offset - 70, "Nº NOTA FISCAL:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(145, y_offset - 70, limpar_float(dados['nota_fiscal']))
    
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(380, y_offset - 70, "Nº PROTOCOLO CLIENTE:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(530, y_offset - 70, limpar_float(dados['protocolo']))
    
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(45, y_offset - 95, "DATA:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(85, y_offset - 95, "______ / ______ / __________")
    
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(45, y_offset - 125, "DADOS DO RECEBEDOR:")
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(185, y_offset - 125, "(Nome legível e RG)")
    
    pdf.setFont("Helvetica
