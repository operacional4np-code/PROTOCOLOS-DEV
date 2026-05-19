import streamlit as st
import pandas as pd
import requests
import io
import re
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Configurações iniciais
SHEET_ID = "1f_NDUAezh4g0ztyHVUO_t33QxGai9TYcWOD-IAoPcuE"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

st.set_page_config(page_title="Gerador de Protocolos - MG", page_icon="📄")

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

# Função principal que gera o PDF usando o modelo como fundo
def gerar_pdf_com_fundo(dados_filtrados):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Coordenadas aproximadas para preencher o modelo (ajuste fino pode ser necessário)
    posicoes = [725, 480, 235] # Y para cada um dos 3 blocos
    
    for i, (_, row) in enumerate(dados_filtrados.iterrows()):
        bloco = i % 3
        if i > 0 and bloco == 0:
            c.showPage()
            
        # 1. Carimba o modelo de fundo
        if os.path.exists("modelo_protocolo.png"):
            c.drawImage("modelo_protocolo.png", 30, posicoes[bloco], width=550, height=200, preserveAspectRatio=True, mask='auto')
        
        # 2. Escreve os dados por cima (ajuste os valores X e Y conforme necessário)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(480, posicoes[bloco] + 165, f"MG-{limpar_float(row.get('protocolo', ''))}")
        
        c.setFont("Helvetica", 11)
        c.drawString(100, posicoes[bloco] + 135, str(row.get('nome', '')).upper()) # Cliente
        c.drawString(150, posicoes[bloco] + 105, limpar_float(row.get('nota fiscal', ''))) # Nota
        c.drawString(500, posicoes[bloco] + 105, limpar_float(row.get('protocolo', ''))) # Prot Cliente
        c.drawString(460, posicoes[bloco] + 105, limpar_float(row.get('cte', ''))) # CTE

    c.save()
    buffer.seek(0)
    return buffer

# Interface
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
        dados_encontrados = df[mask]
        
        if not dados_encontrados.empty:
            pdf_final = gerar_pdf_com_fundo(dados_encontrados)
            st.download_button("📥 Baixar PDF", data=pdf_final, file_name="protocolo.pdf", mime="application/pdf")
        else:
            st.error("Notas não encontradas.")
