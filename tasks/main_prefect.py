import logging

from prefect import flow, task, get_run_logger

from scripts.config import montar_datasets, validar_anos
from scripts.download import baixar_arquivo
from scripts.transform import aplicar_etapas
from scripts.pipeline import extrair, unir_dataframes, carregar_bigquery


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

tarefa_baixar = task(baixar_arquivo, name="Baixar arquivo", retries=2, log_prints=True)
tarefa_extrair = task(extrair, name="Extrair arquivo", retries=1, log_prints=True)
tarefa_unir = task(unir_dataframes, name="Unir anos", log_prints=True)
tarefa_transformar = task(aplicar_etapas, name="Aplicar transformações", retries=1, log_prints=True)
tarefa_carregar = task(carregar_bigquery, name="Carregar no BigQuery", log_prints=True)


@flow(name="Legislativo ETL", description="Pipeline de dados legislativos", log_prints=True)
def pipeline_legislativo(anos: list[str] = ["2026"]):
    logger = get_run_logger()

    anos = validar_anos(anos)
    logger.info("Iniciando pipeline para os anos %s", anos)

    datasets_por_ano = {ano: montar_datasets(ano) for ano in anos}

    # As chaves são iguais para todos os anos; usa o primeiro como referência
    for chave_dataset, config in datasets_por_ano[anos[0]].items():
        logger.info("Processando dataset: %s", chave_dataset)

        # Arquivo único (ex.: deputados) é baixado uma vez só
        anos_dataset = anos if config["por_ano"] else anos[:1]

        dfs = []
        for ano in anos_dataset:
            cfg = datasets_por_ano[ano][chave_dataset]
            logger.info("Baixando %s (%s)", chave_dataset, ano)
            arquivo = tarefa_baixar(cfg["url"], cfg["arquivo"], cfg["compactado"])
            dfs.append(tarefa_extrair(arquivo))

        df = tarefa_unir(dfs)
        df = tarefa_transformar(df, config["etapas_transform"])
        tarefa_carregar(df, config["tabela"], config["schema"])

        logger.info("Dataset %s finalizado com sucesso", chave_dataset)

    logger.info("Pipeline concluído")


if __name__ == "__main__":
    pipeline_legislativo(anos=["2024", "2025", "2026"])
    # pipeline_legislativo.deploy(
    #     name="legislativo-etl",
    #     work_pool_name="processo-local"
    # )