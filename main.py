import streamlit as st
import pandas as pd
import requests
import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# --- CONFIGURAÇÕES ---
SHEET_ID = "1f_NDUAezh4g0ztyHVUO_t33QxGai9TYcWOD-IAoPcuE"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

st.set_page_config(page_title="Gerador de Protocolos", page_icon="📄", layout="centered")

# --- FUNÇÕES AUXILIARES ---
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
    # Caixa principal
    c.rect(40, y, 520, 180, stroke=1, fill=0) 
    
    # Linha horizontal do cabeçalho e vertical para o número
    c.line(40, y + 150, 560, y + 150)
    c.line(420, y + 150, 420, y + 180)
    
    # Títulos
    c.setFont("Helvetica-Bold", 14)
    c.drawString(140, y + 160, "PROTOCOLO DE DEVOLUÇÃO")
    
    c.setFont("Helvetica", 10)
    c.drawString(430, y + 165, "PROTOCOLO Nº:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(450, y + 152, f"PE-{limpar_float(dados['protocolo'])}")
    
    # Cliente
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 130, "CLIENTE:")
    c.line(100, y + 128, 550, y + 128) 
    c.setFont("Helvetica", 11)
    c.drawString(100, y + 132, str(dados['cliente']).upper())
    
    # Linha do meio (NF e CTE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 105, "Nº NOTA FISCAL:")
    c.line(130, y + 103, 380, y + 103)
    c.drawString(390, y + 105, "Nº CTE:")
    c.line(440, y + 103, 550, y + 103)
    
    c.setFont("Helvetica", 11)
    c.drawString(140, y + 107, limpar_float(dados['nota_fiscal']))
    c.drawString(445, y + 107, str(dados['cte']))
    
    # Dados Rodapé
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 80, "DATA:")
    c.line(80, y + 78, 250, y + 78)
    c.drawString(270, y + 80, "Nº PROTOCOLO CLIENTE:")
    c.line(400, y + 78, 550, y + 78)
    
    c.setFont("Helvetica", 11)
    c.drawString(410, y + 82, limpar_float(dados['protocolo']))
    
    # Recebedor e Assinatura
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 50, "DADOS DO RECEBEDOR:")
    c.line(160, y + 48, 550, y + 48)
    c.setFont("Helvetica", 8)
    c.drawString(350, y + 38, "Nome legível e RG")
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y + 20, "ASSINATURA:")
    c.line(120, y + 18, 550, y + 18)

def gerar_pdf_puro(dados_filtrados):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Posicionamento Y para 3 blocos por página
    posicoes = [550, 310, 70]
    
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

# --- INTERFACE ---
st.title("📄 Gerador de Protocolos")

with st.form("form_busca"):
    input_notas = st.text_area("Cole as Notas Fiscais aqui:")
    submitted = st.form_submit_button("Gerar PDF")

# Lógica fora do formulário para evitar erros de state
if submitted:
    if input_notas:
        lista_notas = re.findall(r'\d+', input_notas)
        df = baixar_dados_google_sheets()
        
        if df is not None:
            df['nota fiscal'] = df['nota fiscal'].astype(str).fillna('')
            # Filtra os dados que batem com as notas inseridas
            mask = df['nota fiscal'].apply(lambda x: any(n in x for n in lista_notas))
            dados = df[mask]
            
            if not dados.empty:
                st.success(f"Encontramos {len(dados)} protocolos!")
                pdf_final = gerar_pdf_puro(dados)
                st.download_button("📥 Baixar PDF", data=pdf_final, file_name="protocolos.pdf", mime="application/pdf")
            else:
                st.error("Nenhuma nota encontrada.")
    else:
        st.warning("Por favor, digite as notas.")
