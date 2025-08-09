import numpy as np
from src import compare_semantic


def test_semantic_top_k_with_mock(monkeypatch):
    # Embeddings fictícios do corpus (3 docs, vetores normalizados)
    embeddings = np.array([
        [1.0, 0.0],   # doc1
        [0.0, 1.0],   # doc2
        [0.7, 0.7]    # doc3
    ])
    id_map = ["doc1", "doc2", "doc3"]

    # Embedding fictício da query
    fake_query_vec = np.array([[1.0, 0.0]])

    # Mock de embed_query para evitar carregamento real do modelo
    monkeypatch.setattr(compare_semantic, "embed_query", lambda text, model_name: fake_query_vec)

    # Executa o cálculo
    results = compare_semantic.semantic_top_k("texto de teste", embeddings, id_map, "fake-model", k=2)

    # Verifica se retorna os dois mais próximos
    assert len(results) == 2
    assert results[0][0] == "doc1"  # mais próximo
    assert results[0][1] > results[1][1]  # score do primeiro maior que o do segundo
