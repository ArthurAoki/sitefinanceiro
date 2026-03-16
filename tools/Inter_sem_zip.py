import pdfplumber
import os
import re
import shutil
from datetime import datetime
import time

def limpar_nome(nome):
    nome = nome.strip()
    nome = re.sub(r"[\\/*?:\"<>|]", "", nome)
    nome = re.sub(r"\s+", " ", nome)
    return nome.replace(" ", "_")

def identificar_tipo(texto):
    if "Pix enviado" in texto:
        return "pix"
    elif "PREFEITURA DO MUNICÍPIO DE SÃO PAULO" in texto:
        return "nf_sp"
    elif "PREFEITURA DE SÃO JOSÉ DOS CAMPOS" in texto:
        return "nf_sjc"
    elif "PREFEITURA MUNICIPAL DE SERRANA" in texto:
        return "nf_serrana"
    elif "PREFEITURA MUNICIPAL DE SANTOS" in texto:
        return "nf_santos"
    elif "DANFSe" in texto or "Documento Auxiliar da NFS-e" in texto:
        return "danfse"
    else:
        return "desconhecido"

def processar_inter(caminho_entrada, pasta_saida):
    """
    Processa PDF do Inter e salva renomeado em pasta_saida.
    Retorna a pasta onde os arquivos foram salvos.
    """
    try:
        # Espera arquivo terminar de copiar
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

        tipo = identificar_tipo(texto)

        # Extrair nome e valor dependendo do tipo
        nome = "DESCONHECIDO"
        valor = "0,00"

        if tipo == "pix":
            nome_match = re.search(r"Nome\s+(.+)", texto)
            valor_match = re.search(r"R\$\s*([\d\.,]+)", texto)
            if nome_match:
                nome = nome_match.group(1)
            if valor_match:
                valor = valor_match.group(1)
        elif tipo == "nf_sp":
            nome_match = re.search(r"Nome/Razão Social:\s*(.+)", texto)
            valor_match = re.search(r"VALOR TOTAL DO SERVIÇO\s*=\s*R\$\s*([\d\.,]+)", texto)
            if nome_match:
                nome = nome_match.group(1)
            if valor_match:
                valor = valor_match.group(1)
        elif tipo == "nf_sjc":
            nome_match = re.search(r"\n([A-Z &]+LTDA)", texto)
            valor_match = re.search(r"VALOR TOTAL DA NOTA.*?([\d\.,]{4,})", texto, re.S)
            if nome_match:
                nome = nome_match.group(1)
            if valor_match:
                valor = valor_match.group(1)
        elif tipo == "danfse":
            nome_match = re.search(r"Nome\s*/\s*Nome Empresarial\s*\n(.+)", texto)
            valor_match = re.search(r"Valor do Serviço\s*R?\$?\s*([\d\.,]+)", texto)
            if nome_match:
                nome = nome_match.group(1)
            if valor_match:
                valor = valor_match.group(1)
        elif tipo == "nf_serrana":
            nome_match = re.search(r"Nome/Razão Social\s+CPF/CNPJ\s*\n(.+?)\s+\d{2}\.", texto)
            valor_match = re.search(r"Valor do Serviço\s*R?\$?\s*([\d\.,]+)", texto)
            if nome_match:
                nome = nome_match.group(1)
            if valor_match:
                valor = valor_match.group(1)
        elif tipo == "nf_santos":
            nome_match = re.search(r"Nome/Razão Social:\s*(.+)", texto)
            valor_match = re.search(r"Valor do Serviço\s*([\d\.,]+)", texto)
            if nome_match:
                nome = nome_match.group(1)
            if valor_match:
                valor = valor_match.group(1)

        nome_limpo = limpar_nome(nome)
        os.makedirs(pasta_saida, exist_ok=True)
        novo_nome = f"{nome_limpo}_R${valor}.pdf"
        novo_caminho = os.path.join(pasta_saida, novo_nome)
        shutil.move(caminho_entrada, novo_caminho)

        return pasta_saida

    except Exception as e:
        print(f"Erro Inter: {e}")
        return pasta_saida