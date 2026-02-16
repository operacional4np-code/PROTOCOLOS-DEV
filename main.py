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
        # Lemos a planilha
        df = pd.read_excel(INPUT_EXCEL)
        
        # FORÇA todas as colunas a serem MAIÚSCULAS e sem espaços
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        print(f"📋 Colunas detectadas: {list(df.columns)}")

        for index, row in df.iterrows():
            with Image.open(MODELO_PATH).convert("RGB") as img:
                draw = ImageDraw.Draw(img)
                fonte = ImageFont.load_default()

                # Pegamos os dados usando apenas MAIÚSCULAS
                # Se não encontrar a coluna, ele coloca '---' em vez de dar erro
                v_protocolo    = str(row.get('PROTOCOLO', 'Sem_ID'))
                v_destinatario = str(row.get('DESTINATÁRIO', '---'))
                v_n_fiscal     = str(row.get('N.FISCAL', '---'))
                v_minuta       = str(row.get('MINUTACTE', '---'))
                v_data         = str(row.get('DATA', '---'))
                v_recebedor    = str(row.get('NOME_RECEBEDOR', '---'))

                # --- ESCREVENDO NA IMAGEM ---
                draw.text((800, 48),  v_protocolo,    fill="black", font=fonte)
                draw.text((100, 145), v_destinatario, fill="black", font=fonte)
                draw.text((150, 242), v_n_fiscal,     fill="black", font=fonte)
                draw.text((550, 242), v_minuta,       fill="black", font=fonte)
                draw.text((100, 310), v_data,         fill="black", font=fonte)
                draw.text((100, 450), v_recebedor,    fill="black", font=fonte)

                # --- SALVAMENTO (Usando a variável segura v_protocolo) ---
                nome_saida = f"Protocolo_{index}.png" if v_protocolo == 'Sem_ID' else f"Protocolo_{v_protocolo}.png"
                img.save(os.path.join(OUTPUT_DIR, nome_saida))
                print(f"✅ Gerado: {nome_saida}")

        print(f"\n🚀 Sucesso! Verifique a pasta: {OUTPUT_DIR}")

    except Exception as e:
        print(f"❌ Erro no processamento: {e}")

if __name__ == "__main__":
    gerar_protocolos()
