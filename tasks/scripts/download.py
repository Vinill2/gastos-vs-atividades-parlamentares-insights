import io
import os
import time
import zipfile

import requests
from prefect import get_run_logger

HORAS_CACHE = 24


def e_csv(nome_arquivo):
    return nome_arquivo.lower().endswith(".csv")


def encontrar_csv_no_zip(arquivo_zip):
    for nome in arquivo_zip.namelist():
        if e_csv(nome):
            return nome

    raise ValueError("Arquivo ZIP não contém nenhum CSV.")


def validar_arquivo(destino):
    if not os.path.isfile(destino):
        raise FileNotFoundError(
            f"Arquivo não foi criado: {destino}"
        )

    if os.path.getsize(destino) == 0:
        raise ValueError(
            f"Arquivo está vazio: {destino}"
        )


def arquivo_recente(destino, horas=HORAS_CACHE):
    """True se o arquivo existe, não está vazio e foi modificado há menos de `horas`."""
    if not os.path.isfile(destino) or os.path.getsize(destino) == 0:
        return False

    idade_horas = (time.time() - os.path.getmtime(destino)) / 3600

    return idade_horas < horas


def baixar_arquivo(url, destino, compactado=False):
    logger = get_run_logger()

    # Reaproveita o arquivo local se ele foi baixado há pouco tempo
    if arquivo_recente(destino):
        logger.info(
            "Arquivo atualizado nas últimas %s horas. "
            "Usando arquivo existente: %s",
            HORAS_CACHE,
            destino,
        )

        validar_arquivo(destino)

        return destino

    logger.info("Arquivo não encontrado ou desatualizado.")
    logger.info("Iniciando download: %s", url)

    resposta = requests.get(url, timeout=1200)
    resposta.raise_for_status()

    diretorio = os.path.dirname(destino)

    if diretorio:
        os.makedirs(diretorio, exist_ok=True)

    if compactado:
        logger.info("Arquivo compactado. Procurando CSV.")

        with zipfile.ZipFile(
            io.BytesIO(resposta.content)
        ) as arquivo_zip:

            nome_csv = encontrar_csv_no_zip(arquivo_zip)

            with (
                arquivo_zip.open(nome_csv) as origem,
                open(destino, "wb") as saida,
            ):
                saida.write(origem.read())

    else:
        with open(destino, "wb") as saida:
            saida.write(resposta.content)

    validar_arquivo(destino)

    logger.info(
        "Arquivo baixado com sucesso: %s",
        destino,
    )

    return destino