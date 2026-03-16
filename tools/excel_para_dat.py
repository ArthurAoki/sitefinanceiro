import pandas as pd
import os

def excel_para_dat(caminho_excel, pasta_saida):
    """
    Converte um arquivo Excel em .dat
    Retorna o caminho do arquivo .dat criado
    """

    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)

    # Ler o Excel
    df = pd.read_excel(caminho_excel)

    # Nome base do arquivo
    nome_base = os.path.splitext(os.path.basename(caminho_excel))[0]
    caminho_dat = os.path.join(pasta_saida, nome_base + ".dat")

    # Gerar .dat
    with open(caminho_dat, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            # transformar cada campo em string, remover | se houver
            campos = [str(campo).replace("|","") for campo in row]
            linha = "|".join(campos)
            f.write(linha + "\n")

    return caminho_dat