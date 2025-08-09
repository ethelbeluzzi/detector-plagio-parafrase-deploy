from src.config import settings
from src import io_utils, compare_lexical, compare_semantic, combine_scores


# Compara um texto usando índices léxico e semântico pré-carregados
def compare(query: str):
    if not query or not query.strip():
        return []

    # Carrega índice léxico e calcula similaridade
    tfidf_model, tfidf_matrix, id_map_lex = io_utils.load_index_lexical(settings.INDEX_LEX_DIR)
    top_lex = compare_lexical.compare_with_index(
        query=query,
        tfidf_model=tfidf_model,
        tfidf_matrix=tfidf_matrix,
        id_map=id_map_lex,
        top_n=settings.K_LEX,
    )

    # Carrega índice semântico e calcula similaridade
    embeddings, id_map_sem, model_name = io_utils.load_index_semantic(settings.INDEX_SEM_DIR)
    top_sem = compare_semantic.semantic_top_k(
        query=query,
        embeddings=embeddings,
        id_map=id_map_sem,
        model_name=model_name,
        k=settings.K_SEM,
    )

    # Combina os resultados
    combined = combine_scores.combine_scores(
        top_lex=top_lex,
        top_sem=top_sem,
        k_final=settings.K_FINAL,
        alpha=settings.ALPHA,
        tau_lex=settings.TAU_LEX,
        tau_sem=settings.TAU_SEM,
    )

    return combined
