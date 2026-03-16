import os
import re
import time
import pdfplumber
from unidecode import unidecode
from pypdf import PdfReader, PdfWriter

CC_VALIDOS = [
    "ALESP",
    "EQUIPE",
    "COMPRAS",
    "FINANCEIRO",
    "INPE",
    "MINISTERIO",
    "MPF",
    "OPERACOES"
]

def criar_estrutura_lote(nome_lote, pasta_base):
    pasta_lote = os.path.join(pasta_base, nome_lote)
    os.makedirs(pasta_lote, exist_ok=True)
    for cc in CC_VALIDOS:
        os.makedirs(os.path.join(pasta_lote, cc), exist_ok=True)
    os.makedirs(os.path.join(pasta_lote, "OUTROS"), exist_ok=True)
    pasta_temp = os.path.join(pasta_lote, "temp")
    os.makedirs(pasta_temp, exist_ok=True)
    return pasta_lote, pasta_temp

def separar_pdf_em_paginas(pdf_path, pasta_temp):
    reader = PdfReader(pdf_path)
    paginas = []
    for i, pagina in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(pagina)
        caminho_saida = os.path.join(pasta_temp, f"pagina_{i+1}.pdf")
        with open(caminho_saida, "wb") as f:
            writer.write(f)
        paginas.append(caminho_saida)
    return paginas

def extrair_texto_pdf(caminho_pdf):
    texto = ""
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            t = pagina.extract_text()
            if t:
                texto += t + "\n"
    return texto

def extrair_dados(pdf_path):
    texto = extrair_texto_pdf(pdf_path)
    cc_match = re.search(r"CC:\s*([A-Z0-9]+)", texto)
    cc = cc_match.group(1).upper() if cc_match else "SEMCC"
    nome = "SEMNOME"
    linhas = texto.split("\n")
    for i, linha in enumerate(linhas):
        if "Nome do Funcionário" in linha:
            if i + 1 < len(linhas):
                linha_nome = linhas[i + 1].strip()
                if i + 2 < len(linhas):
                    linha_nome += " " + linhas[i + 2].strip()
                match = re.search(r"\d+\s+(.+?)\s+\d+\s+\d+", linha_nome)
                if match:
                    nome_extraido = match.group(1).strip()
                    nome = unidecode(nome_extraido.upper())
            break
    return cc, nome

def obter_pasta_cc(pasta_lote, cc):
    if cc in CC_VALIDOS:
        return os.path.join(pasta_lote, cc)
    return os.path.join(pasta_lote, "OUTROS")

def renomear_pdf(caminho_pdf, pasta_lote):
    try:
        nome_atual = os.path.basename(caminho_pdf)
        cc, nome = extrair_dados(caminho_pdf)
        pasta_destino = obter_pasta_cc(pasta_lote, cc)
        if nome == "SEMNOME":
            contador = 1
            while True:
                novo_nome = f"{cc}_SEMNOME{contador}.pdf"
                destino = os.path.join(pasta_destino, novo_nome)
                if not os.path.exists(destino):
                    break
                contador += 1
        else:
            novo_nome_base = f"{cc}_{nome}.pdf"
            destino = os.path.join(pasta_destino, novo_nome_base)
            if not os.path.exists(destino):
                novo_nome = novo_nome_base
            else:
                contador = 1
                while True:
                    novo_nome = f"{cc}_{nome}_{contador}.pdf"
                    destino = os.path.join(pasta_destino, novo_nome)
                    if not os.path.exists(destino):
                        break
                    contador += 1
        os.rename(caminho_pdf, destino)
        print(f"Renomeado: {nome_atual} -> {novo_nome}")
    except Exception as e:
        print(f"Erro ao processar {caminho_pdf}: {e}")

def organizar_pagamento(pdf_path, pasta_base):
    nome_lote = os.path.splitext(os.path.basename(pdf_path))[0]
    pasta_lote, pasta_temp = criar_estrutura_lote(nome_lote, pasta_base)
    paginas = separar_pdf_em_paginas(pdf_path, pasta_temp)
    for pagina in paginas:
        renomear_pdf(pagina, pasta_lote)
    os.remove(pdf_path)
    return pasta_lote