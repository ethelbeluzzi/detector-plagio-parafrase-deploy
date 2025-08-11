import pytest
from src.combine_scores import combine_scores


def test_combine_scores_basic():
    top_lex = [("doc_a", 0.9), ("doc_b", 0.4)]
    top_sem = [("doc_a", 0.8), ("doc_b", 0.95)]

    result = combine_scores(top_lex, top_sem, k_final=2, alpha=0.5)

    # Verifica tamanho e campos
    assert len(result) == 2
    assert all("doc_id" in r for r in result)

    # Reproduz exatamente a lógica interna de combine_scores para calcular ordem esperada
    lex_dict = dict(top_lex)
    sem_dict = dict(top_sem)

    ids_list = list(set(lex_dict.keys()) | set(sem_dict.keys()))
    raw_lex = [float(lex_dict.get(doc_id, 0.0)) for doc_id in ids_list]
    raw_sem = [float(sem_dict.get(doc_id, 0.0)) for doc_id in ids_list]

    # Normalização
    def norm(scores):
        if not scores:
            return []
        min_s, max_s = min(scores), max(scores)
        if max_s == min_s:
            return [0.0] * len(scores)
        return [(s - min_s) / (max_s - min_s) for s in scores]

    norm_lex = norm(raw_lex)
    norm_sem = norm(raw_sem)

    scores_final = [0.5 * l + 0.5 * s for l, s in zip(norm_lex, norm_sem)]
    expected_order = [doc for _, doc in sorted(zip(scores_final, ids_list), reverse=True)]

    assert [r["doc_id"] for r in result] == expected_order


def test_combine_scores_empty_inputs():
    assert combine_scores([], [], k_final=3) == []


def test_combine_scores_detect_plagio_literal():
    top_lex = [("doc_a", 0.95)]
    top_sem = [("doc_a", 0.9)]

    result = combine_scores(top_lex, top_sem, k_final=1, tau_lex=0.9, tau_sem=0.85)
    assert "plagio_literal" in result[0]["flags"]
    assert result[0]["match_type"] == "plagio_literal"


def test_combine_scores_detect_parafrase():
    top_lex = [("doc_a", 0.5)]
    top_sem = [("doc_a", 0.9)]

    result = combine_scores(top_lex, top_sem, k_final=1, tau_lex=0.9, tau_sem=0.85, delta_para=0.3)
    assert "parafrase" in result[0]["flags"]
    assert result[0]["match_type"] == "parafrase"


def test_combine_scores_min_gate_filter():
    top_lex = [("doc_a", 0.05)]
    top_sem = [("doc_a", 0.04)]  # ambos abaixo de min_gate padrão (0.1)

    result = combine_scores(top_lex, top_sem, k_final=1)
    assert result[0]["flags"] == []
    assert result[0]["match_type"] is None

