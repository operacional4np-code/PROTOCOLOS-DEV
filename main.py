import streamlit as st
import pandas as pd
import requests
import io
import re
import os
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
@st.cache_data(ttl=5) 
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
    
    # Busca do Logo
    caminho_logo = None
    opcoes_nome = ["logo.png.JPG", "logo.png", "logo.jpg", "logo.jpeg", "logo.png.jpg", "LOGO.JPG", "LOGO.PNG"]
    for opcao in opcoes_nome:
        if os.path.exists(opcao):
            caminho_logo = opcao
            break
            
    if caminho_logo:
        pdf.drawImage(caminho_logo, 45, y_offset + 5, width=110, height=30, preserveAspectRatio=True, mask='auto')
    else:
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(45, y_offset + 15, "[ LOGO NEW POST ]")
    
    # Título do Bloco
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(45, y_offset - 25, "PROTOCOLO DE DEVOLUÇÃO")
    
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(380, y_offset - 25, "PROTOCOLO Nº:")
    pdf.setFont("Helvetica", 11)
    p_num = f"MG-{limpar_float(dados['protocolo'])}"
    pdf.drawString(485, y_offset - 25, p_num)
    
    # Cliente e CTE
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(45, y_offset - 55, "CLIENTE:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(105, y_offset - 55, str(dados['cliente']).upper())
    
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(380, y_offset - 55, "Nº CTE:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(430, y_offset - 55, limpar_float(dados['cte']))
    
    # Nota Fiscal e Protocolo Cliente
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(45, y_offset - 80, "Nº NOTA FISCAL:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(145, y_offset - 80, limpar_float(dados['nota_fiscal']))
    
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(380, y_offset - 80, "Nº PROTOCOLO CLIENTE:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(530, y_offset - 80, limpar_float(dados['protocolo']))
    
    # Campos de preenchimento manual
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(45, y_offset - 110, "DATA:")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(85, y_offset - 110, "______ / ______ / __________")
    
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(45, y_offset - 140, "DADOS DO RECEBEDOR:")
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(185, y_offset - 140, "(Nome legível e RG)")
    
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(45, y_offset - 170, "ASSINATURA:")
    pdf.setLineWidth(0.8)
    pdf.line(125, y_offset - 170, 450, y_offset - 170)
    
    # Linha pontilhada de recorte
    pdf.setLineWidth(0.5)
    pdf.setDash(2, 2)
    pdf.line(30, y_offset - 200, 580, y_offset - 200)
    pdf.setDash(1, 0)

def gerar_pdf_memoria(dados_filtrados):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    y_positions = [730, 490, 250]
    bloco_atual = 0
    
    for _, row in dados_filtrados.iterrows():
        info_nota = {
            'protocolo': row.get('protocolo', '---'),
            'cliente': row.get('nome', '---'),
            'nota_fiscal': row.get('nota fiscal', '---'),
            'cte': row.get('cte', '---')
        }
        
        if bloco_atual > 2:
            c.showPage()
            bloco_atual = 0
            
        desenhar_bloco_final_mg(c, y_positions[bloco_atual], info_nota)
        bloco_atual += 1
        
    c.save()
    buffer.seek(0)
    return buffer

# --- INTERFACE DO USUÁRIO ---
with st.form("formulario_notas"):
    input_notas = st.text_area(
        "Digite ou cole as Notas Fiscais aqui:",
        placeholder="Pode usar espaços, quebras de linha ou vírgulas.\nExemplo:\n1599605\n1609405 1609406"
    )
    botao_enviar = st.form_submit_button("🔍 Buscar Notas e Gerar PDF")

if botao_enviar and input_notas:
    lista_notas = re.findall(r'\d+', input_notas)
    
    if lista_notas:
        st.info(f"🔍 Buscando as seguintes notas no sistema: {', '.join(lista_notas)}")
        df = baixar_dados_google_sheets()
        
        if df is not None:
            if 'nota fiscal' in df.columns:
                df['nota fiscal'] = df['nota fiscal'].astype(str).fillna('')
                mascara = df['nota fiscal'].apply(lambda x: any(nota in x for nota in lista_notas))
                dados_encontrados = df[mascara]
                
                if not dados_encontrados.empty:
                    st.success(f"🎉 Pronto! Localizamos {len(dados_encontrados)} registro(s).")
                    pdf_pronto = gerar_pdf_memoria(dados_encontrados)
                    
                    st.download_button(
                        label="📥 CLIQUE AQUI PARA BAIXAR O PDF",
                        data=pdf_pronto,
                        file_name="protocolos_devolucao_mg.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("❌ Nenhuma dessas notas foi encontrada na planilha do Google.")
            else:
                st.error("❌ Erro de estrutura: Não achei a coluna 'nota fiscal' na sua planilha.")
    else:
        st.warning("⚠ Digite pelo menos um número de nota fiscal válido.")
