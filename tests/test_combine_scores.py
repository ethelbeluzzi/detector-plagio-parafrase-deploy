import pytest
from src.combine_scores import combine_scores


# 🔹 Testa a combinação e ordenação básica dos scores
# Aqui doc_b deve ser o primeiro pois tem melhor média ponderada
def test_combine_scores_basic():
    top_lex = [("doc_a", 0.9), ("doc_b", 0.4)]
    top_sem = [("doc_a", 0.8), ("doc_b", 0.95)]

    result = combine_scores(top_lex, top_sem, k_final=2, alpha=0.5)

    assert len(result) == 2
    assert result[0]["doc_id"] == "doc_b"
    assert result[1]["doc_id"] == "doc_a"
    # Garante que os campos básicos estão presentes
    for r in result:
        assert all(k in r for k in ["score_final", "score_lex_raw", "score_sem_raw", "flags"])


# 🔹 Testa retorno vazio quando não há entradas
def test_combine_scores_empty_inputs():
    assert combine_scores([], [], k_final=3) == []


# 🔹 Testa detecção de plágio literal (altos em ambos eixos)
def test_combine_scores_detect_plagio_literal():
    top_lex = [("doc_a", 0.95)]
    top_sem = [("doc_a", 0.9)]

    result = combine_scores(top_lex, top_sem, k_final=1, tau_lex=0.9, tau_sem=0.85)
    assert "plagio_literal" in result[0]["flags"]
    assert result[0]["match_type"] == "plagio_literal"


# 🔹 Testa detecção de paráfrase (semântico alto, léxico relativamente baixo)
def test_combine_scores_detect_parafrase():
    top_lex = [("doc_a", 0.5)]
    top_sem = [("doc_a", 0.9)]

    result = combine_scores(top_lex, top_sem, k_final=1, tau_lex=0.9, tau_sem=0.85, delta_para=0.3)
    assert "parafrase" in result[0]["flags"]
    assert result[0]["match_type"] == "parafrase"


# 🔹 Testa que o min_gate filtra candidatos fracos
def test_combine_scores_min_gate_filter():
    top_lex = [("doc_a", 0.05)]
    top_sem = [("doc_a", 0.04)]  # ambos abaixo de min_gate padrão (0.1)

    result = combine_scores(top_lex, top_sem, k_final=1)
    assert result[0]["flags"] == []
    assert result[0]["match_type"] is None

