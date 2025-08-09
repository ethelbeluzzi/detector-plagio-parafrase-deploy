import numpy as np
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Gera o embedding de um texto usando o modelo especificado
def embed_query(text: str, model_name: str) -> np.ndarray:
    model = SentenceTransformer(model_name)
    embedding = model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
    return embedding


# Calcula a similaridade semântica entre a consulta e o corpus
# Retorna uma lista dos top-k documentos mais similares (doc_id, score)
def semantic_top_k(query: str,
                   embeddings: np.ndarray,
                   id_map: List[str],
                   model_name: str,
                   k: int = 10) -> List[Tuple[str, float]]:
    query_vec = embed_query(query, model_name)
    scores = cosine_similarity(query_vec, embeddings)[0]
    top_indices = np.argsort(scores)[::-1][:k]
    return [(id_map[i], float(scores[i])) for i in top_indices]
