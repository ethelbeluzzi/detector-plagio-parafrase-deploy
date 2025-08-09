# tests/test_pipeline_build_index.py
import os
import numpy as np
from scipy import sparse
from src import io_utils
import src.pipeline_build_index as pipeline


# Garante que o pipeline gera índices com corpus mínimo,
# sem dependências externas (mock de modelo e vetorizador),
# escrevendo na árvore relativa data/ sob um diretório temporário.
def test_pipeline_build_index_creates_indexes(tmp_path, monkeypatch):
    # Prepara estrutura: tmp/data/raw com dois arquivos .txt
    data_dir = tmp_path / "data"
    raw_dir = data_dir / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "doc1.txt").write_text("Texto de teste A", encoding="utf-8")
    (raw_dir / "doc2.txt").write_text("Texto de teste B", encoding="utf-8")

    # Direciona paths relativos do pipeline (data/...) para tmp usando chdir
    monkeypatch.chdir(tmp_path)

    # Mocka SentenceTransformer para evitar download de modelo
    class FakeModel:
        def encode(self, texts, convert_to_numpy=True, normalize_embeddings=True):
            return np.array([[0.1, 0.2], [0.3, 0.4]])
    monkeypatch.setattr(pipeline, "SentenceTransformer", lambda *_args, **_kwargs: FakeModel())

    # Mocka TfidfVectorizer para acelerar o teste e evitar dependências
    class FakeTFIDF:
        def fit_transform(self, texts):
            return sparse.csr_matrix([[1, 0], [0, 1]])
    monkeypatch.setattr(pipeline, "TfidfVectorizer", lambda: FakeTFIDF())

    # Executa o pipeline
    pipeline.main()

    # Verifica artefatos criados
    indexes_dir = data_dir / "indexes"
    lex_dir = indexes_dir / "lexical"
    sem_dir = indexes_dir / "semantic"

    assert (lex_dir / "tfidf_model.joblib").exists()
    assert (lex_dir / "tfidf_matrix.npz").exists()
    assert (lex_dir / "id_map.json").exists()

    assert (sem_dir / "embeddings.npy").exists()
    assert (sem_dir / "meta.json").exists()

    # Carrega e valida conteúdo básico
    _, tfidf_matrix, id_map_lex = io_utils.load_index_lexical(str(lex_dir))
    assert tfidf_matrix.shape == (2, 2)
    assert id_map_lex == ["doc1", "doc2"]

    embeddings, id_map_sem, model_name = io_utils.load_index_semantic(str(sem_dir))
    assert embeddings.shape == (2, 2)
    assert id_map_sem == ["doc1", "doc2"]
    assert isinstance(model_name, str) and len(model_name) > 0
