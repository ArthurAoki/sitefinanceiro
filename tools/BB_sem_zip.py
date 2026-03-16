import pdfplumber
import os
import re
import shutil
from datetime import datetime
import time

def processar_bb(caminho_entrada, pasta_saida):
    """
    Processa o PDF do BB e salva renomeado em pasta_saida.
    Retorna a pasta onde os arquivos foram salvos.
    """
    try:
        # Esperar o arquivo terminar de copiar
        tamanho_anterior = -1
        while True:
            tamanho_atual = os.path.getsize(caminho_entrada)
            if tamanho_atual == tamanho_anterior:
                break
            tamanho_anterior = tamanho_atual
            time.sleep(0.5)

        # Abrir PDF
        texto = ""
        with pdfplumber.open(caminho_entrada) as pdf:
            for pagina in pdf.pages:
                txt = pagina.extract_text()
                if txt:
                    texto += txt + "\n"

        # Extrair dados
        if "COMPROVANTE DE PAGAMENTO DE TITULOS" in texto:
            nome_match = re.search(r"NOME FANTASIA:\s*(.+)", texto)
            valor_match = re.search(r"VALOR DO DOCUMENTO\s*([\d.,]+)", texto)
        elif "COMPROVANTE DE PAGAMENTO" in texto:
            agencia_match = re.search(r"AGÊNCIA DE RECOLHIMENTO:\s*(\d+)", texto)
            valor_match = re.search(r"IPVA.*?(\d+,\d{1,2})", texto)
            if agencia_match and valor_match:
                nome = f"AGENCIA_{agencia_match.group(1)}"
                valor = valor_match.group(1)
                nome = nome.replace(" ", "_")
                novo_nome = f"{nome}_R${valor}.pdf"
                novo_caminho = os.path.join(pasta_saida, novo_nome)
                os.makedirs(pasta_saida, exist_ok=True)
                shutil.move(caminho_entrada, novo_caminho)
                return pasta_saida
            else:
                return pasta_saida
        elif "Comprovante Pix" in texto:
            nome_match = re.search(r"PAGO PARA:\s*(.+)", texto)
            valor_match = re.search(r"VALOR:\s*R\$\s*([\d.,]+)", texto)
        else:
            return pasta_saida

        if not nome_match or not valor_match:
            return pasta_saida

        nome = re.sub(r"[^\w\s-]", "", nome_match.group(1).strip())
        nome = nome.replace(" ", "_")
        valor = valor_match.group(1).strip()

        # Criar pasta de saída
        os.makedirs(pasta_saida, exist_ok=True)
        novo_nome = f"{nome}_R${valor}.pdf"
        novo_caminho = os.path.join(pasta_saida, novo_nome)
        shutil.move(caminho_entrada, novo_caminho)

        return pasta_saida

    except Exception as e:
        print(f"Erro BB: {e}")
        return pasta_saida