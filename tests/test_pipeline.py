import pandas as pd
import pytest

from scripts.pipeline import unir_dataframes


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
