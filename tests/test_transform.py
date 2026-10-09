from decimal import Decimal

import pandas as pd

from scripts.transform import (
    converter_decimal,
    converter_data,
    converter_numero,
    extrair_id,
    normalizar_nulos,
)


def test_converter_decimal():
    df = pd.DataFrame({"valor": ["10.50", "20.00", None]})
    resultado = converter_decimal(df, ["valor"])

    assert resultado["valor"][0] == Decimal("10.50")
    assert resultado["valor"][1] == Decimal("20.00")
    assert resultado["valor"][2] is None


def test_extrair_id():
    df = pd.DataFrame({"uri": [
        "http://api.exemplo.com/proposicoes/12345",
        "http://api.exemplo.com/deputados/67890",
        None,
    ]})

    resultado = extrair_id(df, {"origem": "uri", "destino": "id"})

    assert resultado["id"][0] == 12345
    assert resultado["id"][1] == 67890
    assert pd.isna(resultado["id"][2])


def test_converter_data():
    df = pd.DataFrame({"data": ["2026-01-15", "data-invalida", None]})
    resultado = converter_data(df, ["data"])

    assert str(resultado["data"][0]) == "2026-01-15"
    assert pd.isna(resultado["data"][1])
    assert pd.isna(resultado["data"][2])


def test_normalizar_nulos():
    df = pd.DataFrame({"descricao": ["texto", float("nan"), None]})
    resultado = normalizar_nulos(df, ["descricao"])

    assert resultado["descricao"][0] == "texto"
    assert resultado["descricao"][1] is None
    assert resultado["descricao"][2] is None


def test_converter_numero():
    df = pd.DataFrame({"numero": ["10", "3.5", "abc", None]})
    resultado = converter_numero(df, ["numero"])

    assert resultado["numero"][0] == 10
    assert resultado["numero"][1] == 3.5
    assert pd.isna(resultado["numero"][2])
    assert pd.isna(resultado["numero"][3])