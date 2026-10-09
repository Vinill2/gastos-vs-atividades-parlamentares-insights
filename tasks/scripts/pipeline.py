import pandas as pd
import pandas_gbq
import pyarrow as pa

from scripts.config import BQ_PROJECT, BQ_DATASET

from prefect import get_run_logger
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    "/app/gcp/credenciais.json"
)

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



def carregar_bigquery(df, tabela, schema):
    logger = get_run_logger()

    logger.info("Testando coluna por coluna com PyArrow...")

    for coluna in df.columns:
        try:
            pa.array(df[coluna])

            logger.info(
                "OK: %s | pandas=%s",
                coluna,
                df[coluna].dtype,
            )

        except Exception as e:
            logger.error(
                "ERRO: %s | pandas=%s | erro=%s",
                coluna,
                df[coluna].dtype,
                e,
            )
            raise

    logger.info("Todas as colunas passaram no teste PyArrow.")

    pandas_gbq.to_gbq(
        dataframe=df,
        destination_table=f"{BQ_DATASET}.{tabela}",
        project_id=BQ_PROJECT,
        if_exists="replace",
        credentials=credentials,
    )
    logger = get_run_logger()

    pandas_gbq.to_gbq(
        dataframe=df,
        destination_table=f"{BQ_DATASET}.{tabela}",
        project_id=BQ_PROJECT,
        if_exists="replace",
        table_schema=schema,
        credentials=credentials
    )

    logger.info("Tabela '%s' atualizada com sucesso", tabela)