import streamlit as st
import pandas as pd
import requests
import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
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
@st.cache_data(ttl=10)
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

def limpar_float(valor):
    """Remove o '.0' caso o número venha formatado como float da planilha"""
    texto = str(valor).strip()
    if texto.endswith('.0'):
        return texto[:-2]
    return texto

def desenhar_bloco_protocolo(pdf, y_offset, dados):
    """Desenha um dos blocos de protocolo no PDF idêntico ao modelo de referência"""
    
    # --- 1. TÍTULOS E CABEÇALHO ---
    pdf.setFillColor(black)
    
    # Título Principal (Esquerda)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(45, y_offset, "PROTOCOLO DE DEVOLUÇÃO")
    
    # Protocolo Geral (Direita)
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(380, y_offset, "PROTOCOLO Nº:")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(485, y_offset, f"MG-{limpar_float(dados['protocolo'])}")
    
    # --- 2. TABELA DE DADOS (Duas Colunas Perfeitas) ---
    # Montamos a estrutura idêntica à foto de referência
    col_esquerda = [
        f"CLIENTE:   {str(dados['cliente']).upper()}",
        f"Nº NOTA FISCAL:   {limpar_float(dados['nota_fiscal'])}",
        "DATA:   ______ / ______ / __________"
    ]
    
    col_direita = [
        f"Nº CTE:   {limpar_float(dados['cte'])}",
        f"Nº PROTOCOLO CLIENTE:   {limpar_float(dados['protocolo'])}",
        "" # Espaço em branco para alinhar com a Data
    ]
    
    dados_tabela = [
        [col_esquerda[0], col_direita[0]],
        [col_esquerda[1], col_direita[1]],
        [col_esquerda[2], col_direita[2]]
    ]
    
    # Criamos a tabela definindo as larguras exatas das colunas (Esquerda: 335pt, Direita: 200pt)
    tabela = Table(dados_tabela, colWidths=[335, 200])
    tabela.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10), # Dá o espaçamento vertical entre as linhas
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    # Renderiza a tabela na coordenada correta
    tabela.wrapOn(pdf, 45, y_offset - 80)
    tabela.drawOn(pdf, 45, y_offset - 80)
    
    # --- 3. CAMPOS INFERIORES (RECEBEDOR E ASSINATURA) ---
    # Campo Recebedor
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(45, y_offset - 110, "DADOS DO RECEBEDOR:")
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(185, y_offset - 110, "(Nome legível e RG)")
    
    # Campo Assinatura com Linha Contínua Longa
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(45, y_offset - 145, "ASSINATURA:")
    pdf.setLineWidth(0.8)
    pdf.line(130, y_offset - 147, 450, y_offset - 147)
    
    # --- 4. LINHA PONTEADA DE RECORTE ---
    pdf.setLineWidth(0.5)
    pdf.setDash(2, 2)
    pdf.line(30, y_offset - 175, 580, y_offset - 175)
    pdf.setDash(1, 0) # Reseta para linha normal

def gerar_pdf_memoria(dados_filtrados):
    """Gera o PDF em memória (BytesIO) com distribuição de 3 blocos por página"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Coordenadas y ajustadas milimetricamente para o novo espaçamento dos blocos
    y_positions = [735, 480, 225]
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
                    
                    st.markdown("### 📋 Tabela de Conferência:")
                    st.dataframe(dados_encontrados[['protocolo', 'nome', 'nota fiscal', 'cte']])
                else:
                    st.error("❌ Nenhuma dessas notas foi encontrada na planilha do Google.")
            else:
                st.error("❌ Erro de estrutura: Não achei a coluna 'nota fiscal' na sua planilha.")
    else:
        st.warning("⚠ Digite pelo menos um número de nota fiscal válido.")
