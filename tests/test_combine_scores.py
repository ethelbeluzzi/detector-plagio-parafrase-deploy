import pytest
from src.combine_scores import combine_scores


# 🔹 Testa a combinação e ordenação básica dos scores
# Aqui doc_b deve ser o primeiro pois tem melhor média ponderada
def test_combine_scores_basic():
    top_lex = [("doc_a", 0.9), ("doc_b", 0.4)]
    top_sem = [("doc_a", 0.8), ("doc_b", 0.95)]

    result = combine_scores(top_lex, top_sem, k_final=2, alpha=0.5)

    # Verifica tamanho e campos
    assert len(result) == 2
    assert all("doc_id" in r for r in result)

    # Calcula o esperado para validar ordem
    # Normalização léxica
    lex_scores = [0.9, 0.4]
    norm_lex = [(s - min(lex_scores)) / (max(lex_scores) - min(lex_scores)) for s in lex_scores]
    # Normalização semântica
    sem_scores = [0.8, 0.95]
    norm_sem = [(s - min(sem_scores)) / (max(sem_scores) - min(sem_scores)) for s in sem_scores]
    # Score final
    scores_final = [0.5 * l + 0.5 * s for l, s in zip(norm_lex, norm_sem)]

    # Ordena manualmente
    expected_order = [x for _, x in sorted(zip(scores_final, ["doc_a", "doc_b"]), reverse=True)]

    assert [r["doc_id"] for r in result] == expected_order

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

