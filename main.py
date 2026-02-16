import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os

# --- CONFIGURAÇÃO DE CAMINHOS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOME_PLANILHA = "dados.xlsx"
NOME_IMAGEM = "modelo_protocolo.png"

INPUT_EXCEL = os.path.join(BASE_DIR, NOME_PLANILHA)
MODELO_PATH = os.path.join(BASE_DIR, NOME_IMAGEM)
OUTPUT_DIR = os.path.join(BASE_DIR, "protocolos_prontos")

def gerar_protocolos():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if not os.path.exists(INPUT_EXCEL) or not os.path.exists(MODELO_PATH):
        print(f"❌ Erro: Verifique se '{NOME_PLANILHA}' e '{NOME_IMAGEM}' estão na pasta.")
        return

    try:
        print(f"⏳ Lendo dados de {NOME_PLANILHA}...")
        df = pd.read_excel(INPUT_EXCEL)
        
        # Ajuste para ignorar maiúsculas/minúsculas e espaços nos nomes das colunas
        df.columns = df.columns.astype(str).str.strip().str.upper()
        
        print(f"📋 Colunas lidas: {list(df.columns)}")

        for index, row in df.iterrows():
            with Image.open(MODELO_PATH).convert("RGB") as img:
                draw = ImageDraw.Draw(img)
                fonte = ImageFont.load_default()

                # --- MAPEAMENTO DAS SUAS COLUNAS ---
                # O .get() busca o nome em MAIÚSCULO conforme transformamos acima
                protocolo    = str(row.get('PROTOCOLO', '---'))
                destinatario = str(row.get('DESTINATÁRIO', '---'))
                nota_fiscal  = str(row.get('N.FISCAL', '---'))
                minuta_cte   = str(row.get('MINUTACTE', '---'))
                
                # Se houver colunas de data ou recebedor, o script tentará ler também
                data         = str(row.get('DATA', '---'))
                recebedor    = str(row.get('NOME_RECEBEDOR', '---'))

                # --- PREENCHIMENTO NA IMAGEM (Coordenadas X, Y) ---
                draw.text((800, 48),  protocolo,    fill="black", font=fonte)
                draw.text((100, 145), destinatario, fill="black", font=fonte)
                draw.text((150, 242), nota_fiscal,  fill="black", font=fonte)
                draw.text((550, 242), minuta_cte,   fill="black", font=fonte)
                draw.text((100, 310), data,         fill="black", font=fonte)
                draw.text((100, 450), recebedor,    fill="black", font=fonte)

                # --- SALVAMENTO ---
                nome_saida = f"Protocolo_{protocolo}.png"
                img.save(os.path.join(OUTPUT_DIR, nome_saida))
                print(f"✅ Gerado: {nome_saida}")

        print(f"\n🚀 Sucesso! Pasta de saída: {OUTPUT_DIR}")

    except Exception as e:
        print(f"❌ Erro no processamento: {e}")

if __name__ ==
