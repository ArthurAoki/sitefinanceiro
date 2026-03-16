from flask import Flask, render_template, request, send_from_directory
from tools.pagamentos_por_cc import organizar_pagamento
from tools.BB_sem_zip import processar_bb
from tools.Bradesco_sem_zip import processar_bradesco
from tools.Inter_sem_zip import processar_inter
from tools.excel_para_dat import excel_para_dat

import os
import shutil
from shutil import make_archive

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
DOWNLOAD_FOLDER = "downloads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


# ===============================
# Página inicial
# ===============================
@app.route("/")
def home():
    return render_template("index.html")


# ===============================
# OPÇÃO 1 - ORGANIZAR PDFs
# ===============================
@app.route("/upload", methods=["GET", "POST"])
def upload_file():

    if request.method == "POST":

        arquivo = request.files["arquivo"]

        caminho_entrada = os.path.join(UPLOAD_FOLDER, arquivo.filename)
        arquivo.save(caminho_entrada)

        pasta_saida = os.path.join(DOWNLOAD_FOLDER, os.path.splitext(arquivo.filename)[0])

        if os.path.exists(pasta_saida):
            shutil.rmtree(pasta_saida)

        os.makedirs(pasta_saida)

        pasta_lote = organizar_pagamento(caminho_entrada, pasta_saida)

        nome_zip = os.path.splitext(arquivo.filename)[0]

        caminho_zip_sem_ext = os.path.join(DOWNLOAD_FOLDER, nome_zip)

        make_archive(caminho_zip_sem_ext, 'zip', pasta_lote)

        caminho_zip = nome_zip + ".zip"

        return f"""
        Arquivos organizados com sucesso!<br><br>
        <a href="/download/{caminho_zip}">Clique aqui para baixar (.zip)</a>
        """

    return render_template("upload.html")


# ===============================
# OPÇÃO 2 - CONVERTER COMPROVANTES
# ===============================
@app.route("/converter_comprovantes", methods=["GET", "POST"])
def converter_comprovantes():

    if request.method == "POST":

        banco = request.form.get("banco")

        arquivos = request.files.getlist("arquivos")

        pasta_saida = os.path.join(DOWNLOAD_FOLDER, f"comprovantes_{banco}")

        if os.path.exists(pasta_saida):
            shutil.rmtree(pasta_saida)

        os.makedirs(pasta_saida)

        for arquivo in arquivos:

            caminho_entrada = os.path.join(UPLOAD_FOLDER, arquivo.filename)

            arquivo.save(caminho_entrada)

            if banco == "bb":
                processar_bb(caminho_entrada, pasta_saida)

            elif banco == "bradesco":
                processar_bradesco(caminho_entrada, pasta_saida)

            elif banco == "inter":
                processar_inter(caminho_entrada, pasta_saida)

        nome_zip = f"comprovantes{banco}"

        caminho_zip_sem_ext = os.path.join(DOWNLOAD_FOLDER, nome_zip)

        make_archive(caminho_zip_sem_ext, 'zip', pasta_saida)

        caminho_zip = nome_zip + ".zip"

        return f"""
        Comprovantes convertidos com sucesso!<br><br>
        <a href="/download/{caminho_zip}">Clique aqui para baixar (.zip)</a>
        """

    return render_template("converter_comprovantes.html")

@app.route("/excel", methods=["GET", "POST"])
def excel_para_dat_route():

    if request.method == "POST":

        arquivos = request.files.getlist("arquivos")
        pasta_saida = os.path.join(DOWNLOAD_FOLDER, "dat_files")

        if os.path.exists(pasta_saida):
            shutil.rmtree(pasta_saida)

        os.makedirs(pasta_saida)

        # processar todos os arquivos
        for arquivo in arquivos:
            caminho_entrada = os.path.join(UPLOAD_FOLDER, arquivo.filename)
            arquivo.save(caminho_entrada)
            excel_para_dat(caminho_entrada, pasta_saida)

        # criar zip com todos os .dat
        nome_zip = "DAT_Arquivos"
        caminho_zip_sem_ext = os.path.join(DOWNLOAD_FOLDER, nome_zip)
        make_archive(caminho_zip_sem_ext, 'zip', pasta_saida)
        caminho_zip = nome_zip + ".zip"

        return f"""
        Arquivos .dat criados com sucesso!<br><br>
        <a href="/download/{caminho_zip}">Clique aqui para baixar (.zip)</a>
        """

    return render_template("excel.html")


# ===============================
# DOWNLOAD
# ===============================
@app.route("/download/<nome_arquivo>")
def download_arquivo(nome_arquivo):
    return send_from_directory(DOWNLOAD_FOLDER, nome_arquivo, as_attachment=True)


# ===============================
# RODAR O SERVIDOR
# ===============================
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=10000)