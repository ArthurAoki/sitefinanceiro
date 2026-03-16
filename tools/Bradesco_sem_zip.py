import pdfplumber
import os
import re
import shutil
from datetime import datetime
import time

def limpar_nome(nome):
    nome = nome.strip()
    nome = nome.replace("/", "")
    nome = nome.replace("\\", "")
    nome = re.sub(r"\s+", " ", nome)
    return nome.replace(" ", "_")

def processar_bradesco(caminho_entrada, pasta_saida):
    """
    Processa PDF do Bradesco e salva renomeado em pasta_saida.
    Retorna a pasta onde os arquivos foram salvos.
    """
    try:
        # Espera o arquivo terminar de copiar
        tamanho_anterior = -1
        while True:
            tamanho_atual = os.path.getsize(caminho_entrada)
            if tamanho_atual == tamanho_anterior:
                break
            tamanho_anterior = tamanho_atual
            time.sleep(0.5)

        # Ler PDF
        texto = ""
        with pdfplumber.open(caminho_entrada) as pdf:
            for pagina in pdf.pages:
                txt = pagina.extract_text()
                if txt:
                    texto += txt + "\n"

        linhas = [l.strip() for l in texto.split("\n") if l.strip()]
        nome = None
        valor = "0,00"

        # Pegar nome
        for linha in linhas:
            linha_upper = linha.upper()
            if "RAZÃO SOCIAL" in linha_upper:
                nome = re.sub("(?i)RAZÃO SOCIAL", "", linha).strip()
                break
            if "NOME FANTASIA" in linha_upper:
                nome = re.sub("(?i)NOME FANTASIA", "", linha).strip()
                break
        if not nome:
            nome = "NOME_NAO_ENCONTRADO"

        # Pegar valor
        for linha in linhas:
            if "VALOR TOTAL" in linha.upper():
                match = re.search(r"R\$\s*([\d\.,]+)", linha)
                if match:
                    valor = match.group(1)
                break

        nome_limpo = limpar_nome(nome)

        os.makedirs(pasta_saida, exist_ok=True)
        novo_nome = f"{nome_limpo}_R${valor}.pdf"
        novo_caminho = os.path.join(pasta_saida, novo_nome)
        shutil.move(caminho_entrada, novo_caminho)

        return pasta_saida

    except Exception as e:
        print(f"Erro Bradesco: {e}")
        return pasta_saida