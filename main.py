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
@st.cache_data(ttl=30) # Cache curto de 30 segundos para garantir dados frescos
def baixar_dados_google_sheets():
    """Busca os dados atualizados diretamente do Google Sheets"""
    try:
        response = requests.get(URL_CSV)
        response.raise_for_status()
        
        csv_data = io.StringIO(response.content.decode('utf-8'))
        df = pd.read_csv(csv_data)
        
        # Cria uma cópia com colunas em minúsculo para busca interna
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

# --- INTERFACE DO USUÁRIO (STREAMLIT) ---

# Caixa de texto isolada no topo para garantir que ela sempre apareça
input_notas = st.text_area(
    "Digite as Notas Fiscais:",
    placeholder="Pode colar as notas aqui separadas por espaço, quebra de linha ou vírgula.\nExemplo: 123456 789101"
)

if input_notas:
    # REGEX MÁGICO: Ele encontra sequências de números isoladas, 
    # ignorando se o separador é espaço, quebra de linha, vírgula ou traço.
    lista_notas = re.findall(r'\d+', input_notas)
    
    if lista_notas:
        st.info(f"🔍 Notas identificadas para busca: {', '.join(lista_notas)}")
        
        if st.button("⚡ Gerar e Preparar PDF"):
            df = baixar_dados_google_sheets()
            
            if df is not None:
                # Tratamento preventivo das colunas do dataframe
                # Remove espaços em branco e garante que a comparação ocorra como texto puro (String)
                if 'nota fiscal' in df.columns:
                    df['nota fiscal'] = df['nota fiscal'].astype(str).str.strip()
                    
                    # Filtra a planilha buscando qualquer uma das notas capturadas
                    dados_encontrados = df[df['nota fiscal'].isin(lista_notas)]
                    
                    if not dados_encontrados.empty:
                        st.success(f"🎉 Sucesso! Encontramos {len(dados_encontrados)} registro(s) correspondente(s).")
                        
                        pdf_pronto = gerar_pdf_memoria(dados_encontrados)
                        
                        st.download_button(
                            label="📥 Clique aqui para Baixar o PDF",
                            data=pdf_pronto,
                            file_name="protocolos_devolucao_mg.pdf",
                            mime="application/pdf"
                        )
                        
                        st.markdown("### 📋 Conferência dos Dados Localizados:")
                        st.dataframe(dados_encontrados[['protocolo', 'nome', 'nota fiscal', 'cte']])
                    else:
                        st.error("❌ Nenhuma dessas notas foi encontrada na base de dados da planilha.")
                else:
                    st.error("❌ Erro estrutural: A coluna 'nota fiscal' não foi localizada na planilha.")
    else:
        st.warning("⚠ Nenhum número de nota fiscal válido foi identificado no texto digitado.")
