import os

import pandas as pd
import pandas_gbq
import pyarrow as pa
from google.oauth2 import service_account
from prefect import get_run_logger

from scripts.config import BQ_DATASET, BQ_PROJECT


def obter_credenciais():
    caminho = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not caminho:
        raise EnvironmentError(
            "Defina GOOGLE_APPLICATION_CREDENTIALS com o caminho "
            "do credenciais.json."
        )

    return service_account.Credentials.from_service_account_file(caminho)


def extrair(arquivo):
    logger = get_run_logger()
    logger.info("Lendo arquivo: %s", arquivo)
    df = pd.read_csv(arquivo, sep=";")
    if df.empty:
        raise ValueError(f"Arquivo {arquivo} não contém registros.")

    logger.info("Arquivo lido com sucesso. Shape: %s", df.shape)
    return df


def unir_dataframes(dfs):
    logger = get_run_logger()

    if not dfs:
        raise ValueError("Nenhum DataFrame para unir.")

    df = pd.concat(dfs, ignore_index=True) if len(dfs) > 1 else dfs[0]

    logger.info("Unidos %s arquivo(s). Shape final: %s", len(dfs), df.shape)

    return df


def validar_conversao_pyarrow(df):
    """Testa coluna por coluna se o PyArrow consegue converter (usado pelo to_gbq)."""
    logger = get_run_logger()

    for coluna in df.columns:
        try:
            pa.array(df[coluna])
            logger.info("OK: %s | pandas=%s", coluna, df[coluna].dtype)

        except Exception as e:
            logger.error(
                "ERRO: %s | pandas=%s | erro=%s",
                coluna,
                df[coluna].dtype,
                e,
            )
            raise

    logger.info("Todas as colunas passaram no teste PyArrow.")


def carregar_bigquery(df, tabela, schema):
    logger = get_run_logger()

    validar_conversao_pyarrow(df)

    pandas_gbq.to_gbq(
        dataframe=df,
        destination_table=f"{BQ_DATASET}.{tabela}",
        project_id=BQ_PROJECT,
        if_exists="replace",
        table_schema=schema,
        credentials=obter_credenciais(),
    )

    logger.info("Tabela '%s' atualizada com sucesso", tabela)