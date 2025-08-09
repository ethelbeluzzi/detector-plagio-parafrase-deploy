import os
import json
import tempfile
import numpy as np
import joblib
from scipy import sparse
from src import io_utils


def test_ensure_dir_and_load_corpus(tmp_path):
    # Cria diretório e arquivo fictício
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    file_path = raw_dir / "doc1.txt"
    file_path.write_text("Texto de teste", encoding="utf-8")

    # Testa ensure_dir
    new_dir = tmp_path / "new_dir"
    io_utils.ensure_dir(new_dir)
    assert new_dir.exists()

    # Testa load_corpus
    corpus = io_utils.load_corpus(str(raw_dir))
    assert len(corpus) == 1
    assert corpus[0]["text"] == "Texto de teste"


def test_save_and_load_index_lexical(tmp_path):
    path_out = tmp_path / "lexical"
    model = {"vocab": ["a", "b"]}
    matrix = sparse.csr_matrix([[1, 0], [0, 1]])
    id_map = ["doc1", "doc2"]

    # Salva e carrega
    io_utils.save_index_lexical(str(path_out), model, matrix, id_map)
    loaded_model, loaded_matrix, loaded_id_map = io_utils.load_index_lexical(str(path_out))

    assert loaded_model["vocab"] == model["vocab"]
    assert (loaded_matrix != matrix).nnz == 0  # Mesma matriz
    assert loaded_id_map == id_map


def test_save_and_load_index_semantic(tmp_path):
    path_out = tmp_path / "semantic"
    embeddings = np.array([[0.1, 0.2], [0.3, 0.4]])
    id_map = ["doc1", "doc2"]
    model_name = "test-model"

    # Salva e carrega
    io_utils.save_index_semantic(str(path_out), embeddings, id_map, model_name)
    loaded_embeddings, loaded_id_map, loaded_model_name = io_utils.load_index_semantic(str(path_out))

    assert np.allclose(loaded_embeddings, embeddings)
    assert loaded_id_map == id_map
    assert loaded_model_name == model_name
