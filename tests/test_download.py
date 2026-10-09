import io
import os
import time
import zipfile

import pytest
import requests

from scripts import download
from scripts.download import (
    arquivo_recente,
    baixar_arquivo,
    encontrar_csv_no_zip,
    validar_arquivo,
)


def criar_zip(arquivos):
    """Cria um ZIP em memória. arquivos = {nome: conteudo}."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for nome, conteudo in arquivos.items():
            zf.writestr(nome, conteudo)
    return buffer.getvalue()


class RespostaFalsa:
    """Substitui o retorno de requests.get."""

    def __init__(self, content=b"", status_code=200):
        self.content = content
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"Erro HTTP {self.status_code}")


def definir_idade(arquivo, horas):
    """Faz o arquivo parecer ter sido modificado há `horas` horas."""
    antigo = time.time() - horas * 3600
    os.utime(str(arquivo), (antigo, antigo))


def simular_get(monkeypatch, resposta):
    monkeypatch.setattr(
        download.requests, "get", lambda url, **kwargs: resposta
    )


# --- encontrar_csv_no_zip ---

def test_encontrar_csv_no_zip_acha_csv():
    dados = criar_zip({"leia-me.txt": "x", "Ano-2026.csv": "a;b"})

    with zipfile.ZipFile(io.BytesIO(dados)) as zf:
        assert encontrar_csv_no_zip(zf) == "Ano-2026.csv"


def test_encontrar_csv_no_zip_extensao_maiuscula():
    dados = criar_zip({"DADOS.CSV": "a;b"})

    with zipfile.ZipFile(io.BytesIO(dados)) as zf:
        assert encontrar_csv_no_zip(zf) == "DADOS.CSV"


def test_encontrar_csv_no_zip_sem_csv():
    dados = criar_zip({"leia-me.txt": "x"})

    with zipfile.ZipFile(io.BytesIO(dados)) as zf:
        with pytest.raises(ValueError, match="nenhum CSV"):
            encontrar_csv_no_zip(zf)


def test_encontrar_csv_no_zip_vazio():
    dados = criar_zip({})

    with zipfile.ZipFile(io.BytesIO(dados)) as zf:
        with pytest.raises(ValueError):
            encontrar_csv_no_zip(zf)


# --- validar_arquivo ---

def test_validar_arquivo_ok(tmp_path):
    arquivo = tmp_path / "dados.csv"
    arquivo.write_text("a;b\n1;2\n")

    validar_arquivo(str(arquivo))  # não deve lançar erro


def test_validar_arquivo_inexistente(tmp_path):
    with pytest.raises(FileNotFoundError):
        validar_arquivo(str(tmp_path / "nao_existe.csv"))


def test_validar_arquivo_vazio(tmp_path):
    arquivo = tmp_path / "vazio.csv"
    arquivo.write_bytes(b"")

    with pytest.raises(ValueError, match="vazio"):
        validar_arquivo(str(arquivo))


# --- baixar_arquivo (requests mockado) ---

def test_baixar_arquivo_csv_simples(tmp_path, monkeypatch):
    conteudo = b"a;b\n1;2\n"
    simular_get(monkeypatch, RespostaFalsa(content=conteudo))
    destino = str(tmp_path / "subpasta" / "dados.csv")

    resultado = baixar_arquivo("http://teste/dados.csv", destino)

    assert resultado == destino
    with open(destino, "rb") as f:
        assert f.read() == conteudo


def test_baixar_arquivo_compactado(tmp_path, monkeypatch):
    conteudo = "a;b\n1;2\n"
    zip_bytes = criar_zip({"Ano-2026.csv": conteudo})
    simular_get(monkeypatch, RespostaFalsa(content=zip_bytes))
    destino = str(tmp_path / "Ano-2026.csv")

    baixar_arquivo("http://teste/Ano-2026.csv.zip", destino, compactado=True)

    with open(destino, encoding="utf-8") as f:
        assert f.read() == conteudo


def test_baixar_arquivo_zip_sem_csv(tmp_path, monkeypatch):
    zip_bytes = criar_zip({"leia-me.txt": "x"})
    simular_get(monkeypatch, RespostaFalsa(content=zip_bytes))

    with pytest.raises(ValueError, match="nenhum CSV"):
        baixar_arquivo(
            "http://teste/x.zip", str(tmp_path / "x.csv"), compactado=True
        )


def test_baixar_arquivo_erro_http(tmp_path, monkeypatch):
    simular_get(monkeypatch, RespostaFalsa(status_code=404))
    destino = tmp_path / "dados.csv"

    with pytest.raises(requests.HTTPError):
        baixar_arquivo("http://teste/dados.csv", str(destino))

    assert not destino.exists()


def test_baixar_arquivo_resposta_vazia(tmp_path, monkeypatch):
    simular_get(monkeypatch, RespostaFalsa(content=b""))

    with pytest.raises(ValueError, match="vazio"):
        baixar_arquivo("http://teste/dados.csv", str(tmp_path / "dados.csv"))


# --- arquivo_recente (cache de download) ---

def test_arquivo_recente_arquivo_novo(tmp_path):
    arquivo = tmp_path / "dados.csv"
    arquivo.write_text("a;b\n1;2\n")

    assert arquivo_recente(str(arquivo), horas=5) is True


def test_arquivo_recente_arquivo_antigo(tmp_path):
    arquivo = tmp_path / "dados.csv"
    arquivo.write_text("a;b\n1;2\n")
    definir_idade(arquivo, horas=10)

    assert arquivo_recente(str(arquivo), horas=5) is False


def test_arquivo_recente_inexistente(tmp_path):
    assert arquivo_recente(str(tmp_path / "nao_existe.csv")) is False


def test_arquivo_recente_vazio_nao_conta(tmp_path):
    arquivo = tmp_path / "vazio.csv"
    arquivo.write_bytes(b"")

    assert arquivo_recente(str(arquivo)) is False


def test_baixar_arquivo_reutiliza_arquivo_recente(tmp_path, monkeypatch):
    arquivo = tmp_path / "dados.csv"
    arquivo.write_text("conteudo antigo")

    def nao_deve_baixar(url, **kwargs):
        raise AssertionError("Não deveria baixar: arquivo é recente")

    monkeypatch.setattr(download.requests, "get", nao_deve_baixar)

    resultado = baixar_arquivo("http://teste/dados.csv", str(arquivo))

    assert resultado == str(arquivo)
    assert arquivo.read_text() == "conteudo antigo"


def test_baixar_arquivo_baixa_de_novo_se_antigo(tmp_path, monkeypatch):
    arquivo = tmp_path / "dados.csv"
    arquivo.write_text("conteudo antigo")
    definir_idade(arquivo, horas=download.HORAS_CACHE + 1)
    simular_get(monkeypatch, RespostaFalsa(content=b"conteudo novo"))

    baixar_arquivo("http://teste/dados.csv", str(arquivo))

    assert arquivo.read_text() == "conteudo novo"