from src import combine_scores


def test_combine_scores_basic():
    # Resultados léxicos simulados (doc_id, score)
    top_lex = [
        ("doc1", 0.9),
        ("doc2", 0.5),
        ("doc3", 0.2)
    ]

    # Resultados semânticos simulados (doc_id, score)
    top_sem = [
        ("doc1", 0.4),
        ("doc2", 0.8),
        ("doc3", 0.3)
    ]

    # Executa combinação
    results = combine_scores.combine_scores(
        top_lex, top_sem, k_final=3, alpha=0.5, tau_lex=0.8, tau_sem=0.7
    )

    # Deve retornar exatamente k_final elementos
    assert len(results) == 3

    # Estrutura: (doc_id, score_final, score_lex, score_sem, flags)
    for item in results:
        assert isinstance(item[0], str)       # doc_id
        assert isinstance(item[1], float)     # score_final
        assert isinstance(item[2], float)     # score_lex normalizado
        assert isinstance(item[3], float)     # score_sem normalizado
        assert isinstance(item[4], list)      # flags

    # Flags aplicados corretamente
    flags_doc1 = [r[4] for r in results if r[0] == "doc1"][0]
    assert "plagio_literal" in flags_doc1
    # doc2 tem alto score semântico normalizado, então deve ter "parafrase"
    flags_doc2 = [r[4] for r in results if r[0] == "doc2"][0]
    assert "parafrase" in flags_doc2

    # Ordenação por score_final decrescente
    scores = [r[1] for r in results]
    assert scores == sorted(scores, reverse=True)
