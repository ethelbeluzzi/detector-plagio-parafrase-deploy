from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.preprocess import normalize

# Compara um texto com um corpus usando TF-IDF e retorna os top_n mais similares
def compare_lexical(query: str, corpus: List[str], top_n: int = 5) -> List[Tuple[int, float]]:
    if not query or not corpus:
        return []

    # Normaliza textos
    corpus_norm = [normalize(doc) for doc in corpus]
    query_norm = normalize(query)

    # Cria matriz TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus_norm + [query_norm])

    # Similaridade: última linha (query) contra todas as outras
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

    # Ordena por score
    top_indices = cosine_sim.argsort()[::-1][:top_n]
    return [(idx, float(cosine_sim[idx])) for idx in top_indices]
