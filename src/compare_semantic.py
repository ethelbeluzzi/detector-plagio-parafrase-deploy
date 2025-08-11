import functools
from typing import List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Carregamento lazy + cache do modelo local
@functools.lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("/app/models/paraphrase-multilingual-MiniLM-L12-v2")

def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Gera embeddings normalizados (L2) para uma lista de textos usando o modelo local.
    """
    model = _get_model()
    emb = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return emb

def semantic_top_k(
    query_block: str,
    embeddings: np.ndarray,
    id_map: List[str],
    k: int = 10
) -> List[Tuple[str, float]]:
    """
    Compara UM bloco de texto (query_block) contra embeddings indexados (de blocos).
    Retorna [(block_id_map_entry, score_cosine), ...] ordenado por score desc.
    """
    if not query_block:
        return []

    query_vec = embed_texts([query_block])  # shape (1, d)
    scores = cosine_similarity(query_vec, embeddings)[0]
    top_indices = np.argsort(scores)[::-1][:k]
    return [(id_map[i]["uid"], float(scores[i])) for i in top_indices]

