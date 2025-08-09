import os
from dataclasses import dataclass
from typing import Mapping, Optional

try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv())
except Exception:
    pass


def _to_int(val: Optional[str], default: int) -> int:
    try:
        return int(str(val)) if val is not None else default
    except Exception:
        return default


def _to_float(val: Optional[str], default: float) -> float:
    try:
        return float(str(val)) if val is not None else default
    except Exception:
        return default


@dataclass(frozen=True)
class Settings:
    DATA_RAW_DIR: str
    DATA_PROCESSED_DIR: str
    DATA_INDEXES_DIR: str
    INDEX_LEX_DIR: str
    INDEX_SEM_DIR: str

    K_LEX: int
    K_SEM: int
    K_FINAL: int

    ALPHA: float
    TAU_LEX: float
    TAU_SEM: float

    SEM_MODEL_NAME: str


def get_settings(environ: Optional[Mapping[str, str]] = None) -> Settings:
    env = os.environ if environ is None else environ

    data_raw = env.get("DATA_RAW_DIR", "data/raw")
    data_processed = env.get("DATA_PROCESSED_DIR", "data/processed")
    data_indexes = env.get("DATA_INDEXES_DIR", "data/indexes")

    idx_lex = env.get("INDEX_LEX_DIR") or os.path.join(data_indexes, "lexical")
    idx_sem = env.get("INDEX_SEM_DIR") or os.path.join(data_indexes, "semantic")

    k_lex = _to_int(env.get("K_LEX"), 10)
    k_sem = _to_int(env.get("K_SEM"), 10)
    k_final = _to_int(env.get("K_FINAL"), 5)

    alpha = _to_float(env.get("ALPHA"), 0.5)
    tau_lex = _to_float(env.get("TAU_LEX"), 0.8)
    tau_sem = _to_float(env.get("TAU_SEM"), 0.75)

    model_name = env.get("SEM_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

    return Settings(
        DATA_RAW_DIR=data_raw,
        DATA_PROCESSED_DIR=data_processed,
        DATA_INDEXES_DIR=data_indexes,
        INDEX_LEX_DIR=idx_lex,
        INDEX_SEM_DIR=idx_sem,
        K_LEX=k_lex,
        K_SEM=k_sem,
        K_FINAL=k_final,
        ALPHA=alpha,
        TAU_LEX=tau_lex,
        TAU_SEM=tau_sem,
        SEM_MODEL_NAME=model_name,
    )


settings = get_settings()
