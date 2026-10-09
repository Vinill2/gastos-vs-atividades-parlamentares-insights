from types import SimpleNamespace

import pandas as pd
import pyarrow as pa
import pytest

from scripts import pipeline
from scripts.pipeline import (
    carregar_bigquery,
    obter_credenciais,
    unir_dataframes,
    validar_conversao_pyarrow,
)


def test_unir_dataframes_um_df():
    df = pd.DataFrame({"id": [1, 2], "ano": [2026, 2026]})

    resultado = unir_dataframes([df])

    assert len(resultado) == 2
    assert list(resultado["id"]) == [1, 2]


def test_unir_dataframes_varios_anos():
    df_2025 = pd.DataFrame({"id": [1, 2], "ano": [2025, 2025]})
    df_2026 = pd.DataFrame({"id": [3], "ano": [2026]})

    resultado = unir_dataframes([df_2025, df_2026])

    assert len(resultado) == 3
    assert list(resultado["ano"]) == [2025, 2025, 2026]
    assert list(resultado.index) == [0, 1, 2]  # índice reiniciado


def test_unir_dataframes_quatro_anos():
    dfs = [
        pd.DataFrame({"id": [i], "ano": [2023 + i]}) for i in range(4)
    ]

    resultado = unir_dataframes(dfs)

    assert len(resultado) == 4
    assert list(resultado["ano"]) == [2023, 2024, 2025, 2026]


def test_unir_dataframes_colunas_diferentes():
    df_a = pd.DataFrame({"id": [1], "extra": ["x"]})
    df_b = pd.DataFrame({"id": [2]})

    resultado = unir_dataframes([df_a, df_b])

    assert len(resultado) == 2
    assert set(resultado.columns) == {"id", "extra"}
    assert pd.isna(resultado["extra"][1])


def test_unir_dataframes_lista_vazia():
    with pytest.raises(ValueError, match="Nenhum DataFrame"):
        unir_dataframes([])


# --- credenciais e carga no BigQuery (tudo mockado) ---

def test_obter_credenciais_sem_variavel(monkeypatch):
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)

    with pytest.raises(EnvironmentError, match="GOOGLE_APPLICATION_CREDENTIALS"):
        obter_credenciais()


def test_obter_credenciais_usa_caminho_da_variavel(monkeypatch):
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/qualquer/cred.json")
    recebido = []

    def credencial_falsa(caminho):
        recebido.append(caminho)
        return "credenciais-falsas"

    monkeypatch.setattr(
        pipeline,
        "service_account",
        SimpleNamespace(
            Credentials=SimpleNamespace(
                from_service_account_file=credencial_falsa
            )
        ),
    )

    assert obter_credenciais() == "credenciais-falsas"
    assert recebido == ["/qualquer/cred.json"]


def test_validar_conversao_pyarrow_ok():
    df = pd.DataFrame({"id": [1, 2], "nome": ["a", "b"]})

    validar_conversao_pyarrow(df)  # não deve lançar erro


def test_validar_conversao_pyarrow_coluna_com_tipos_misturados():
    df = pd.DataFrame({"misto": [1, "texto"]})

    with pytest.raises((pa.ArrowInvalid, pa.ArrowTypeError)):
        validar_conversao_pyarrow(df)


def test_carregar_bigquery_chama_to_gbq_uma_vez(monkeypatch):
    chamadas = []
    monkeypatch.setattr(
        pipeline.pandas_gbq, "to_gbq", lambda **kwargs: chamadas.append(kwargs)
    )
    monkeypatch.setattr(pipeline, "obter_credenciais", lambda: "cred-falsa")

    df = pd.DataFrame({"id": [1, 2]})
    schema = [{"name": "id", "type": "INT64"}]

    carregar_bigquery(df, "minha_tabela", schema)

    assert len(chamadas) == 1
    chamada = chamadas[0]
    assert chamada["destination_table"] == f"{pipeline.BQ_DATASET}.minha_tabela"
    assert chamada["project_id"] == pipeline.BQ_PROJECT
    assert chamada["if_exists"] == "replace"
    assert chamada["table_schema"] == schema
    assert chamada["credentials"] == "cred-falsa"


def test_carregar_bigquery_nao_chama_to_gbq_se_pyarrow_falhar(monkeypatch):
    chamadas = []
    monkeypatch.setattr(
        pipeline.pandas_gbq, "to_gbq", lambda **kwargs: chamadas.append(kwargs)
    )
    monkeypatch.setattr(pipeline, "obter_credenciais", lambda: "cred-falsa")

    df = pd.DataFrame({"misto": [1, "texto"]})

    with pytest.raises((pa.ArrowInvalid, pa.ArrowTypeError)):
        carregar_bigquery(df, "minha_tabela", [])

    assert chamadas == []