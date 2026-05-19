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
    
    # Linha tracejada para corte
    pdf.setDash(2, 2)
    pdf.line(30, y_offset - 165, 580, y_offset - 165)
    pdf.setDash(1, 0)

def gerar_pdf_memoria(dados_filtrados):
    """Gera o PDF em memória (BytesIO)"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    y_positions = [730, 480, 230]
    bloco_atual = 0
    
    for _, row in dados_filtrados.iterrows():
        # Linha 103 TOTALMENTE CORRIGIDA E REVISADA AQUI:
        info_nota = {
            'protocolo': row.get('protocolo', '---'),
            'cliente': row.get('nome', '---'),
            'nota_fiscal': row.get('nota fiscal', '---'),
            'cte': row.get('cte', '---')
        }
        
        if bloco_atual > 2:
            c.showPage()
            bloco_atual = 0
            
        desenhar_bloco_protocolo(c, y_positions[bloco_atual], info_nota)
        bloco_atual += 1
        
    c.save()
    buffer.seek(0)
    return buffer

# --- INTERFACE DO USUÁRIO EM FORMATO DE FORMULÁRIO ---

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
                df['nota fiscal'] = df['nota fiscal'].astype(str).str.strip()
                dados_encontrados = df[df['nota fiscal'].isin(lista_notas)]
                
                if not dados_encontrados.empty:
                    st.success(f"🎉 Pronto! Localizamos {len(dados_encontrados)} registro(s).")
                    
                    pdf_pronto = gerar_pdf_memoria(dados_encontrados)
                    
                    st.download_button(
                        label="📥 CLIQUE AQUI PARA BAIXAR O PDF",
                        data=pdf_pronto,
                        file_name="protocolos_devolucao_mg.pdf",
                        mime="application/pdf"
                    )
                    
                    st.markdown("### 📋 Tabela de Conferência:")
                    st.dataframe(dados_encontrados[['protocolo', 'nome', 'nota fiscal', 'cte']])
                else:
                    st.error("❌ Nenhuma dessas notas foi encontrada na planilha do Google.")
            else:
                st.error("❌ Erro de estrutura: Não achei a coluna 'nota fiscal' na sua planilha.")
    else:
        st.warning("⚠ Digite pelo menos um número de nota fiscal válido.")
