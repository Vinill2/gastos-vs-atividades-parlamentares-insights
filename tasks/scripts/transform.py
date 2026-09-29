import re
from decimal import Decimal

import pandas as pd

from prefect import get_run_logger    



def selecionar(df, colunas):
    return df[colunas].copy()


def selecionar_existentes(df, colunas):
    existentes = [coluna for coluna in colunas if coluna in df.columns]
    return df[existentes].copy()


def converter_data(df, colunas):
    for coluna in colunas:
        df[coluna] = pd.to_datetime(df[coluna], errors="coerce").dt.date
    return df


def converter_datetime(df, colunas):
    for coluna in colunas:
        df[coluna] = pd.to_datetime(df[coluna], errors="coerce")
    return df


def converter_numero(df, colunas):
    for coluna in colunas:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    return df


def converter_decimal(df, colunas):
    for coluna in colunas:
        df[coluna] = df[coluna].apply(
            lambda x: Decimal(str(x)) if pd.notnull(x) else None
        )
    return df


def normalizar_nulos(df, colunas):
    for coluna in colunas:
        df[coluna] = df[coluna].astype(object)
        df[coluna] = df[coluna].where(df[coluna].notna(), None)
    return df


def extrair_id(df, config):
    origem = config["origem"]
    destino = config["destino"]

    def extrair(uri):
        if pd.isna(uri):
            return None
        match = re.search(r"/(\d+)$", str(uri))
        return int(match.group(1)) if match else None

    df[destino] = df[origem].apply(extrair)
    return df


ETAPAS = {
    "selecionar": selecionar,
    "selecionar_existentes": selecionar_existentes,
    "converter_data": converter_data,
    "converter_datetime": converter_datetime,
    "converter_numero": converter_numero,
    "converter_decimal": converter_decimal,
    "normalizar_nulos": normalizar_nulos,
    "extrair_id": extrair_id,
}


def aplicar_etapas(df, etapas):
    logger = get_run_logger()
    for nome, parametro in etapas:
        logger.info("Aplicando etapa '%s'", nome)
        funcao = ETAPAS[nome]
        df = funcao(df, parametro)
        logger.info("Etapa '%s' concluida. Shape atual: %s", nome, df.shape)
    return df
