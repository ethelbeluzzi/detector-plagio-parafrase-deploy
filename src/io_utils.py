import os
import json
import glob
import joblib
import numpy as np
from scipy import sparse

# Garante que o diretório existe, criando-o se necessário
def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


# Carrega o corpus a partir de data/processed ou data/raw
# Retorna lista de dicionários: {"doc_id": str, "title": str, "text": str, "meta": dict}
def load_corpus(path_raw: str, path_processed: str = None) -> list[dict]:
    base_path = path_processed if path_processed and os.path.exists(path_processed) and os.listdir(path_processed) else path_raw
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"Diretório não encontrado: {base_path}")

    corpus = []
    for file_path in sorted(glob.glob(os.path.join(base_path, "*.txt"))):
        doc_id = os.path.splitext(os.path.basename(file_path))[0]
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        corpus.append({
            "doc_id": doc_id,
            "title": doc_id,
            "text": text,
            "meta": {}
        })
    return corpus


# Salva índice léxico (TF-IDF) e metadados
def save_index_lexical(path_out: str, tfidf_model, tfidf_matrix, id_map: list[str]) -> None:
    ensure_dir(path_out)
    joblib.dump(tfidf_model, os.path.join(path_out, "tfidf_model.joblib"))
    sparse.save_npz(os.path.join(path_out, "tfidf_matrix.npz"), tfidf_matrix)
    with open(os.path.join(path_out, "id_map.json"), "w", encoding="utf-8") as f:
        json.dump(id_map, f, ensure_ascii=False, indent=2)


# Carrega índice léxico (TF-IDF) e metadados
def load_index_lexical(path_in: str):
    model = joblib.load(os.path.join(path_in, "tfidf_model.joblib"))
    matrix = sparse.load_npz(os.path.join(path_in, "tfidf_matrix.npz"))
    with open(os.path.join(path_in, "id_map.json"), "r", encoding="utf-8") as f:
        id_map = json.load(f)
    return model, matrix, id_map


# Salva índice semântico (embeddings) e metadados
def save_index_semantic(path_out: str, embeddings: np.ndarray, id_map: list[str], model_name: str) -> None:
    ensure_dir(path_out)
    np.save(os.path.join(path_out, "embeddings.npy"), embeddings)
    meta = {"id_map": id_map, "model_name": model_name}
    with open(os.path.join(path_out, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


# Carrega índice semântico (embeddings) e metadados
def load_index_semantic(path_in: str):
    embeddings = np.load(os.path.join(path_in, "embeddings.npy"))
    with open(os.path.join(path_in, "meta.json"), "r", encoding="utf-8") as f:
        meta = json.load(f)
    return embeddings, meta["id_map"], meta["model_name"]
