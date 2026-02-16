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

    # Verifica se os arquivos básicos existem
    if not os.path.exists(INPUT_EXCEL):
        print(f"❌ Erro: Arquivo '{NOME_PLANILHA}' não encontrado na pasta {BASE_DIR}")
        return
    if not os.path.exists(MODELO_PATH):
        print(f"❌ Erro: Imagem '{NOME_IMAGEM}' não encontrada na pasta {BASE_DIR}")
        return

    try:
        print(f"⏳ Lendo dados de {NOME_PLANILHA}...")
        df = pd.read_excel(INPUT_EXCEL)
        
        # Limpa os nomes das colunas (tira espaços extras e deixa em maiúsculo)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        print(f"📋 Colunas identificadas na sua planilha: {list(df.columns)}")

        for index, row in df.iterrows():
            # Tenta abrir o modelo de imagem
            with Image.open(MODELO_PATH).convert("RGB") as img:
                draw = ImageDraw.Draw(img)
                fonte = ImageFont.load_default()

                # --- BUSCA EXATA PELAS SUAS COLUNAS ---
                # Usamos .get para que, se o nome estiver errado, o script não trave
                val_protocolo = str(row.get('PROTOCOLO', 'S-ID'))
                val_destin    = str(row.get('DESTINATÁRIO', '---'))
                val_nf        = str(row.get('N.FISCAL', '---'))
                val_cte       = str(row.get('MINUTACTE', '---'))

                # --- ESCREVENDO NO PROTOCOLO (Coordenadas X, Y) ---
                draw.text((800, 48),  val_protocolo, fill="black", font=fonte)
                draw.text((100, 145), val_destin,    fill="black", font=fonte)
                draw.text((150, 242), val_nf,        fill="black", font=fonte)
                draw.text((550, 242), val_cte,       fill="black", font=fonte)

                # --- SALVAMENTO ---
                # Salva com o número do protocolo para facilitar a busca
                nome_arquivo = f"Protocolo_{val_protocolo}.png"
                caminho_salvamento = os.path.join(OUTPUT_DIR, nome_arquivo)
                
                img.save(caminho_salvamento)
                print(f"✅ Sucesso: {nome_arquivo} gerado.")

        print(f"\n🚀 Finalizado! Todos os protocolos estão na pasta: {OUTPUT_DIR}")

    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    gerar_protocolos()
