import os

from dotenv import load_dotenv

from scripts.schemas import (
    SCHEMA_PROPOSICOES,
    SCHEMA_PROPOSICOES_AUTORES,
    SCHEMA_GASTOS_PARLAMENTARES,
    SCHEMA_DEPUTADOS,
)

from scripts.etapas_transform import (
    TRANSFORM_PROPOSICOES,
    TRANSFORM_PROPOSICOES_AUTORES,
    TRANSFORM_GASTOS_PARLAMENTARES,
    TRANSFORM_DEPUTADOS,
)

load_dotenv()

BQ_PROJECT = os.environ["BQ_PROJECT"]
BQ_DATASET = os.environ["BQ_DATASET"]
DADOS_DIR = os.getenv("DADOS_DIR", "./data/camara_leg_csv")
URL_BASE = os.getenv(
    "URL_BASE", "https://dadosabertos.camara.leg.br/arquivos"
)

MAX_ANOS = 4


def validar_anos(anos):
    anos = [str(ano).strip() for ano in anos]

    if not 1 <= len(anos) <= MAX_ANOS:
        raise ValueError(
            f"Informe de 1 a {MAX_ANOS} anos. Recebido: {len(anos)}."
        )

    if len(set(anos)) != len(anos):
        raise ValueError(f"Anos duplicados: {anos}")

    for ano in anos:
        if not (ano.isdigit() and len(ano) == 4):
            raise ValueError(f"Ano inválido: '{ano}'")

    return sorted(anos)


def montar_datasets(ano):
    return {
        "proposicoes": {
            "url": f"{URL_BASE}/proposicoes/csv/proposicoes-{ano}.csv",
            "compactado": False,
            "arquivo": f"{DADOS_DIR}/proposicoes-{ano}.csv",
            "tabela": "proposicoes",
            "etapas_transform": TRANSFORM_PROPOSICOES,
            "schema": SCHEMA_PROPOSICOES,
            "por_ano": True,
        },

        "proposicoes_autores": {
            "url": (
                f"{URL_BASE}/proposicoesAutores/csv/"
                f"proposicoesAutores-{ano}.csv"
            ),
            "compactado": False,
            "arquivo": f"{DADOS_DIR}/proposicoesAutores-{ano}.csv",
            "tabela": "proposicoes_autores",
            "etapas_transform": TRANSFORM_PROPOSICOES_AUTORES,
            "schema": SCHEMA_PROPOSICOES_AUTORES,
            "por_ano": True,
        },

        "gastos_parlamentares": {
            "url": f"{URL_BASE}/cotas/Ano-{ano}.csv.zip",
            "compactado": True,
            "arquivo": f"{DADOS_DIR}/Ano-{ano}.csv",
            "tabela": "gastos_parlamentares",
            "etapas_transform": TRANSFORM_GASTOS_PARLAMENTARES,
            "schema": SCHEMA_GASTOS_PARLAMENTARES,
            "por_ano": True,
        },

        "deputados": {
            "url": f"{URL_BASE}/deputados/csv/deputados.csv",
            "compactado": False,
            "arquivo": f"{DADOS_DIR}/deputados.csv",
            "tabela": "deputados",
            "etapas_transform": TRANSFORM_DEPUTADOS,
            "schema": SCHEMA_DEPUTADOS,
            "por_ano": False,
        },
    }