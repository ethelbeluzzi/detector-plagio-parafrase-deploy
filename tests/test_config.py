import os
from src.config import get_settings


def test_config_defaults_isolated(monkeypatch):
    for key in list(os.environ.keys()):
        if key.startswith(("DATA_", "INDEX_", "K_", "ALPHA", "TAU_", "SEM_MODEL_NAME")):
            monkeypatch.delenv(key, raising=False)

    s = get_settings(environ={})

    assert s.DATA_RAW_DIR == "data/raw"
    assert s.DATA_PROCESSED_DIR == "data/processed"
    assert s.DATA_INDEXES_DIR == "data/indexes"
    assert s.INDEX_LEX_DIR.endswith("data/indexes/lexical")
    assert s.INDEX_SEM_DIR.endswith("data/indexes/semantic")

    assert s.K_LEX == 10
    assert s.K_SEM == 10
    assert s.K_FINAL == 5

    assert s.ALPHA == 0.5
    assert s.TAU_LEX == 0.8
    assert s.TAU_SEM == 0.75

    assert s.SEM_MODEL_NAME == "sentence-transformers/all-MiniLM-L6-v2"


def test_config_overrides_and_casts():
    env = {
        "DATA_RAW_DIR": "x/raw",
        "DATA_PROCESSED_DIR": "x/processed",
        "DATA_INDEXES_DIR": "x/indexes",
        "INDEX_LEX_DIR": "custom/lex",
        "INDEX_SEM_DIR": "custom/sem",
        "K_LEX": "7",
        "K_SEM": "9",
        "K_FINAL": "3",
        "ALPHA": "0.33",
        "TAU_LEX": "0.9",
        "TAU_SEM": "0.66",
        "SEM_MODEL_NAME": "test-model",
    }

    s = get_settings(environ=env)

    assert s.DATA_RAW_DIR == "x/raw"
    assert s.DATA_PROCESSED_DIR == "x/processed"
    assert s.DATA_INDEXES_DIR == "x/indexes"
    assert s.INDEX_LEX_DIR == "custom/lex"
    assert s.INDEX_SEM_DIR == "custom/sem"

    assert s.K_LEX == 7
    assert s.K_SEM == 9
    assert s.K_FINAL == 3

    assert abs(s.ALPHA - 0.33) < 1e-9
    assert abs(s.TAU_LEX - 0.9) < 1e-9
    assert abs(s.TAU_SEM - 0.66) < 1e-9

    assert s.SEM_MODEL_NAME == "test-model"


def test_config_derived_index_paths_from_data_indexes():
    env = {
        "DATA_INDEXES_DIR": "root/i",
        "INDEX_LEX_DIR": "",
        "INDEX_SEM_DIR": "",
    }
    s = get_settings(environ=env)
    assert s.INDEX_LEX_DIR == os.path.join("root/i", "lexical")
    assert s.INDEX_SEM_DIR == os.path.join("root/i", "semantic")
