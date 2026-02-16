import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os

# --- CONFIGURAÇÃO ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOME_PLANILHA = "dados.xlsx"
NOME_IMAGEM = "modelo_protocolo.png"
OUTPUT_DIR = os.path.join(BASE_DIR, "protocolos_prontos")

def gerar_protocolos():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    caminho_excel = os.path.join(BASE_DIR, NOME_PLANILHA)
    caminho_img = os.path.join(BASE_DIR, NOME_IMAGEM)

    try:
        print(f"⏳ Lendo {NOME_PLANILHA}...")
        # Lemos o Excel (se houver linhas vazias no topo, o pandas ignora)
        df = pd.read_excel(caminho_excel)
        
        # LIMPEZA TOTAL DE COLUNAS: tira espaços, remove acentos (opcional) e põe em MAIÚSCULO
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        colunas_encontradas = list(df.columns)
        print(f"📋 Colunas que o Python encontrou: {colunas_encontradas}")

        if not colunas_encontradas:
            print("❌ Erro: A planilha parece estar vazia!")
            return

        for index, row in df.iterrows():
            # Abrindo a imagem modelo
            with Image.open(caminho_img).convert("RGB") as img:
                draw = ImageDraw.Draw(img)
                fonte = ImageFont.load_default()

                # USAMOS .get() PARA NUNCA MAIS DAR O ERRO DE 'KEYERROR'
                # Se não achar a coluna, ele escreve "Não encontrado" em vez de travar
                p_protocolo = str(row.get('PROTOCOLO', 'Sem_ID'))
                p_destin    = str(row.get('DESTINATÁRIO', '---'))
                p_fiscal    = str(row.get('N.FISCAL', '---'))
                p_cte       = str(row.get('MINUTACTE', '---'))

                # Escrevendo na imagem
                draw.text((800, 48),  p_protocolo, fill="black", font=fonte)
                draw.text((100, 145), p_destin,    fill="black", font=fonte)
                draw.text((150, 242), p_fiscal,    fill="black", font=fonte)
                draw.text((550, 242), p_cte,       fill="black", font=fonte)

                # Nome do arquivo de saída (usa o protocolo ou o número da linha se falhar)
                nome_saida = f"Protocolo_{p_protocolo}_{index}.png"
                img.save(os.path.join(OUTPUT_DIR, nome_saida))
                print(f"✅ {nome_saida} gerado!")

        print(f"\n🚀 Finalizado! Verifique a pasta: {OUTPUT_DIR}")

    except Exception as e:
        # Aqui ele vai te dizer exatamente onde foi o erro
        print(f"❌ Erro crítico: {e}")

if __name__ == "__main__":
    gerar_protocolos()
