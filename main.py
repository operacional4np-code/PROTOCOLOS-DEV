import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os

# --- CONFIGURAÇÃO DE CAMINHOS ---
# Pega a pasta onde o script está rodando
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Nomes exatos dos arquivos (conforme vimos no seu terminal)
NOME_PLANILHA = "dados.xlsx"
NOME_IMAGEM = "modelo_protocolo.png"

INPUT_EXCEL = os.path.join(BASE_DIR, NOME_PLANILHA)
MODELO_PATH = os.path.join(BASE_DIR, NOME_IMAGEM)

# Pasta onde os protocolos prontos serão colocados
OUTPUT_DIR = os.path.join(BASE_DIR, "protocolos_prontos")

def gerar_protocolos():
    # Cria a pasta de saída se ela não existir
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. Verificação de segurança: a planilha existe?
    if not os.path.exists(INPUT_EXCEL):
        print(f"❌ Erro: Não encontrei a planilha '{NOME_PLANILHA}' na pasta.")
        return

    # 2. Verificação de segurança: a imagem existe?
    if not os.path.exists(MODELO_PATH):
        print(f"❌ Erro: Não encontrei a imagem '{NOME_IMAGEM}' na pasta.")
        return

    try:
        print(f"⏳ Lendo dados de {NOME_PLANILHA}...")
        df = pd.read_excel(INPUT_EXCEL)
        
        for index, row in df.iterrows():
            # Abre a imagem
            with Image.open(MODELO_PATH).convert("RGB") as img:
                draw = ImageDraw.Draw(img)
                
                # Usa a fonte padrão do sistema (funciona em qualquer lugar)
                fonte = ImageFont.load_default()

                # --- PREENCHIMENTO DOS CAMPOS ---
                # Importante: Os nomes entre [' '] devem ser iguais aos do topo da sua planilha
                draw.text((800, 48),  str(row['protocolo']), fill="black", font=fonte)
                draw.text((100, 145), str(row['cliente']), fill="black", font=fonte)
                draw.text((150, 242), str(row['nota_fiscal']), fill="black", font=fonte)
                draw.text((550, 242), str(row['cte']), fill="black", font=fonte)
                draw.text((100, 310), str(row['data']), fill="black", font=fonte)
                draw.text((100, 450), str(row['nome_recebedor']), fill="black", font=fonte)

                # --- SALVAR O ARQUIVO ---
                nome_saida = f"Protocolo_{row['protocolo']}.png"
                img.save(os.path.join(OUTPUT_DIR, nome_saida))
                print(f"✅ Gerado com sucesso: {nome_saida}")

        print(f"\n🚀 Tudo pronto! Seus arquivos estão na pasta: {OUTPUT_DIR}")

    except Exception as e:
        print(f"❌ Ocorreu um erro durante o processamento: {e}")

if __name__ == "__main__":
    gerar_protocolos()
