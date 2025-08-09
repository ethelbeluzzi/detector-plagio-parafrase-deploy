# src/compare_lexical.py
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.preprocess import normalize_text


# Compara um texto com um corpus gerando TF-IDF na hora
def compare_lexical(query: str, corpus: List[str], top_n: int = 5) -> List[Tuple[int, float]]:
    if not query or not corpus:
        return []

    corpus_norm = [normalize_text(doc) for doc in corpus]
    query_norm = normalize_text(query)

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus_norm + [query_norm])

    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
    top_indices = cosine_sim.argsort()[::-1][:top_n]
    return [(idx, float(cosine_sim[idx])) for idx in top_indices]


# Compara um texto usando índice TF-IDF pré-carregado
def compare_with_index(
    query: str,
    tfidf_model: TfidfVectorizer,
    tfidf_matrix,
    id_map: List[str],
    top_n: int = 5
) -> List[Tuple[str, float]]:
    if not query:
        return []

    query_norm = normalize_text(query)
    query_vec = tfidf_model.transform([query_norm])

    scores = cosine_similarity(query_vec, tfidf_matrix)[0]
    top_indices = scores.argsort()[::-1][:top_n]
    return [(id_map[i], float(scores[i])) for i in top_indices]

