import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from src import io_utils, preprocess


# Executa o pipeline offline para gerar índices léxicos e semânticos
def main():
    path_raw = "data/raw"
    path_processed = "data/processed"
    path_indexes = "data/indexes"

    # 1. Carregar corpus (usa processed se existir, senão raw)
    corpus = io_utils.load_corpus(path_raw, path_processed)
    texts = [preprocess.normalize_text(doc["text"]) for doc in corpus]
    id_map = [doc["doc_id"] for doc in corpus]

    # 2. Índice léxico (TF-IDF)
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(texts)
    io_utils.save_index_lexical(os.path.join(path_indexes, "lexical"), tfidf, tfidf_matrix, id_map)

    # 3. Índice semântico (embeddings)
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    io_utils.save_index_semantic(os.path.join(path_indexes, "semantic"), embeddings, id_map, model_name)

    print(f"✅ Índices salvos em: {path_indexes}")


if __name__ == "__main__":
    main()
