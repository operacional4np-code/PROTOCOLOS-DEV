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
    c.setFont("Helvetica-Bold", 14)
    c.drawString(140, y + 160, "PROTOCOLO DE DEVOLUÇÃO")
    
    # Lógica de Prefixo (MG ou PE)
    destino = str(row.get('destino', '')).upper()
    prefixo = "MG" if "BETIM" in destino else "PE"
    
    c.setFont("Helvetica", 9)
    c.drawString(430, y + 165, "PROTOCOLO Nº:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(430, y + 153, f"{prefixo}-{limpar_float(row.get('protocolo', ''))}")
    
    # 3. Campos e Linhas
    c.setFont("Helvetica-Bold", 10)
    
    # Cliente
    c.drawString(45, y + 130, "CLIENTE:")
    c.line(100, y + 128, 550, y + 128)
    c.setFont("Helvetica", 10)
    c.drawString(100, y + 132, str(row.get('nome', '')).upper())
    
    # NF e CTE
    c.drawString(45, y + 105, "Nº NOTA FISCAL:")
    c.line(130, y + 103, 350, y + 103)
    c.drawString(370, y + 105, "Nº CTE:")
    c.line(420, y + 103, 550, y + 103)
    
    c.setFont("Helvetica", 10)
    c.drawString(140, y + 107, limpar_float(row.get('nota fiscal', '')))
    c.drawString(430, y + 107, str(row.get('cte', '')))
    
    # Rodapé - Dados
    c.drawString(45, y + 80, "DATA:")
    c.line(80, y + 78, 250, y + 78)
    
    c.drawString(270, y + 80, "Nº PROTOCOLO CLIENTE:")
    c.line(400, y + 78, 550, y + 78)
    c.setFont("Helvetica", 10)
    c.drawString(420, y + 82, limpar_float(row.get('protocolo', '')))
    
    # Recebedor
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 50, "DADOS DO RECEBEDOR:")
    c.line(160, y + 48, 550, y + 48)
    c.setFont("Helvetica", 8)
    c.drawString(350, y + 38, "Nome legível e RG")
    
    # Assinatura
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 20, "ASSINATURA:")
    c.line(120, y + 18, 550, y + 18)

def gerar_pdf(dados):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    posicoes = [550, 310, 70] # Altura dos 3 blocos
    
    for i, (_, row) in enumerate(dados.iterrows()):
        bloco = i % 3
        if i > 0 and bloco == 0:
            c.showPage()
        
        desenhar_bloco_final(c, posicoes[bloco], row)
    c.save()
    buffer.seek(0)
    return buffer

# --- INTERFACE ---
st.title("📄 Gerador de Protocolos")

with st.form("form_busca"):
    input_notas = st.text_area("Cole as Notas Fiscais:")
    submitted = st.form_submit_button("Gerar PDF")

if submitted and input_notas:
    lista_notas = re.findall(r'\d+', input_notas)
    df = baixar_dados_google_sheets()
    if df is not None:
        df['nota fiscal'] = df['nota fiscal'].astype(str).fillna('')
        mask = df['nota fiscal'].apply(lambda x: any(n in x for n in lista_notas))
        dados = df[mask]
        
        if not dados.empty:
            pdf = gerar_pdf(dados)
            st.success(f"Encontramos {len(dados)} protocolos!")
            st.download_button("📥 Baixar PDF", data=pdf, file_name="protocolo.pdf", mime="application/pdf")
        else:
            st.error("Notas não encontradas.")
