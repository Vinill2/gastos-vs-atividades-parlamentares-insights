import pandas as pd
import pandas_gbq

from scripts.config import BQ_PROJECT, BQ_DATASET

from prefect import get_run_logger


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
    pandas_gbq.to_gbq(
        dataframe=df,
        destination_table=f"{BQ_DATASET}.{tabela}",
        project_id=BQ_PROJECT,
        if_exists="replace",
        table_schema=schema,
    )

    logger.info("Tabela '%s' atualizada com sucesso", tabela)