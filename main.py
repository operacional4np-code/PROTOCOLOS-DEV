def gerar_pdf_com_fundo(dados_filtrados):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Alturas iniciais para cada bloco (o primeiro é o mais alto)
    # Se precisar mover tudo para cima/baixo, mude estes números
    posicoes = [550, 310, 70] 
    
    for i, (_, row) in enumerate(dados_filtrados.iterrows()):
        bloco = i % 3
        if i > 0 and bloco == 0:
            c.showPage()
            
        # 1. Carimba o modelo de fundo
        if os.path.exists("modelo_protocolo.png"):
            # O Y aqui deve casar com o posicoes[bloco]
            c.drawImage("modelo_protocolo.png", 30, posicoes[bloco], width=550, height=200, preserveAspectRatio=True, mask='auto')
        
        # 2. ESCREVE OS DADOS (Ajuste fino)
        c.setFont("Helvetica-Bold", 11)
        # Protocolo (MG-XXXX) - Canto superior direito do bloco
        c.drawString(485, posicoes[bloco] + 165, f"MG-{limpar_float(row.get('protocolo', ''))}")
        
        c.setFont("Helvetica", 11)
        # Cliente - Primeira linha
        c.drawString(100, posicoes[bloco] + 135, str(row.get('nome', '')).upper()) 
        # Nota Fiscal - Segunda linha
        c.drawString(150, posicoes[bloco] + 105, limpar_float(row.get('nota fiscal', ''))) 
        # Protocolo Cliente - Segunda linha à direita
        c.drawString(500, posicoes[bloco] + 105, limpar_float(row.get('protocolo', ''))) 
        # CTE - Segunda linha
        c.drawString(430, posicoes[bloco] + 105, limpar_float(row.get('cte', ''))) 

    c.save()
    buffer.seek(0)
    return buffer
