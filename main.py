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

def desenhar_bloco_final(c, y, dados):
    # 1. Borda do Bloco
    c.rect(40, y, 520, 180, stroke=1, fill=0)
    
    # 2. LOGO (Tenta buscar logo.png.JPG)
    if os.path.exists("logo.png.JPG"):
        c.drawImage("logo.png.JPG", 45, y + 152, width=80, height=25, preserveAspectRatio=True, mask='auto')
    else:
        # Se não achar, escreve "LOGO" apenas para não quebrar
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(45, y + 160, "(Sem Logo)")
        
    # 3. Cabeçalho e Título
    c.line(40, y + 150, 560, y + 150) # Linha divisória topo
    c.setFont("Helvetica-Bold", 14)
    c.drawString(140, y + 160, "PROTOCOLO DE DEVOLUÇÃO")
    
    c.setFont("Helvetica", 9)
    c.drawString(430, y + 165, "PROTOCOLO Nº:")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(430, y + 153, f"PE-{limpar_float(dados['protocolo'])}")
    
    # 4. Campos Organizados
    c.setFont("Helvetica-Bold", 10)
    # Cliente
    c.drawString(45, y + 130, "CLIENTE:")
    c.setFont("Helvetica", 10)
    c.drawString(100, y + 130, str(dados['cliente']).upper())
    
    # NF e CTE
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 105, "Nº NOTA FISCAL:")
    c.setFont("Helvetica", 10)
    c.drawString(135, y + 105, limpar_float(dados['nota_fiscal']))
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(350, y + 105, "Nº CTE:")
    c.setFont("Helvetica", 10)
    c.drawString(400, y + 105, str(dados['cte']))
    
    # Rodapé
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 80, "DATA:")
    c.drawString(200, y + 80, "Nº PROTOCOLO CLIENTE:")
    c.setFont("Helvetica", 10)
    c.drawString(330, y + 80, limpar_float(dados['protocolo']))
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 50, "DADOS DO RECEBEDOR:")
    c.line(160, y + 48, 550, y + 48)
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 20, "ASSINATURA:")
    c.line(120, y + 18, 550, y + 18)

def gerar_pdf(dados):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    posicoes = [550, 310, 70]
    
    for i, (_, row) in enumerate(dados.iterrows()):
        bloco = i % 3
        if i > 0 and bloco == 0:
            c.showPage()
        
        info = {
            'protocolo': row.get('protocolo', '---'),
            'cliente': row.get('nome', '---'),
            'nota_fiscal': row.get('nota fiscal', '---'),
            'cte': row.get('cte', '---')
        }
        desenhar_bloco_final(c, posicoes[bloco], info)
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
            st.download_button("📥 Baixar PDF", data=pdf, file_name="protocolo.pdf", mime="application/pdf")
        else:
            st.error("Notas não encontradas.")
