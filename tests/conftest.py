import logging
import os

import pytest

os.environ.setdefault("BQ_PROJECT", "projeto-teste")
os.environ.setdefault("BQ_DATASET", "dataset_teste")


@pytest.fixture(autouse=True)
def logger_sem_prefect(monkeypatch):
    
    logger = logging.getLogger("teste")

    for modulo in ("transform", "download", "pipeline"):
        monkeypatch.setattr(
            f"scripts.{modulo}.get_run_logger",
            lambda: logger,
        )
