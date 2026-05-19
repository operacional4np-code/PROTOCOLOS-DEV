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
st.markdown("Insira as Notas Fiscais abaixo para gerar e baixar os protocolos.")

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

def desenhar_bloco_do_zero(c, y, dados):
    # Desenha o cabeçalho e linhas
    c.setFont("Helvetica-Bold", 14)
    c.drawString(45, y + 160, "PROTOCOLO DE DEVOLUÇÃO")
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(420, y + 160, f"PROTOCOLO Nº: MG-{limpar_float(dados['protocolo'])}")
    
    # Linhas de Informação
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 130, "CLIENTE:")
    c.setFont("Helvetica", 10)
    c.drawString(100, y + 130, str(dados['cliente']).upper())
    
    c.drawString(420, y + 130, f"Nº CTE: {limpar_float(dados['cte'])}")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 105, "Nº NOTA FISCAL:")
    c.setFont("Helvetica", 10)
    c.drawString(130, y + 105, limpar_float(dados['nota_fiscal']))
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(250, y + 105, "Nº PROTOCOLO CLIENTE:")
    c.setFont("Helvetica", 10)
    c.drawString(370, y + 105, limpar_float(dados['protocolo']))
    
    # Rodapé do bloco
    c.drawString(45, y + 70, "DATA: ______ / ______ / __________")
    c.drawString(45, y + 45, "DADOS DO RECEBEDOR: __________________________________________")
    c.drawString(45, y + 20, "ASSINATURA: __________________________________________________")
    
    # Linha pontilhada de separação
    c.setDash(2, 2)
    c.line(30, y, 580, y)
    c.setDash(1, 0)

def gerar_pdf_puro(dados_filtrados):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Y começa lá em cima e desce para caber 3 por página
    posicoes = [550, 280, 10]
    
    for i, (_, row) in enumerate(dados_filtrados.iterrows()):
        bloco = i % 3
        if i > 0 and bloco == 0:
            c.showPage()
        
        info = {
            'protocolo': row.get('protocolo', '---'),
            'cliente': row.get('nome', '---'),
            'nota_fiscal': row.get('nota fiscal', '---'),
            'cte': row.get('cte', '---')
        }
        desenhar_bloco_do_zero(c, posicoes[bloco], info)
        
    c.save()
    buffer.seek(0)
    return buffer

# Interface
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
            pdf = gerar_pdf_puro(dados)
            st.success("PDF gerado!")
            st.download_button("📥 Baixar PDF", data=pdf, file_name="protocolo.pdf", mime="application/pdf")
        else:
            st.error("Notas não encontradas.")
