import numpy as np
from scipy import sparse
import src.pipeline_build_index as pipeline

# Mock de modelo semântico
class FakeModel:
    def encode(self, texts, convert_to_numpy=True, normalize_embeddings=True):
        return np.array([[0.1, 0.2], [0.3, 0.4]])

# Mock de modelo léxico
class FakeTFIDF:
    def fit_transform(self, texts):
        return sparse.csr_matrix([[1, 0], [0, 1]])


def test_pipeline_build_index_creates_indexes(tmp_path, monkeypatch):
    # Prepara estrutura: tmp/data/raw com dois arquivos .txt
    data_dir = tmp_path / "data"
    raw_dir = data_dir / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "doc1.txt").write_text("Texto de teste A", encoding="utf-8")
    (raw_dir / "doc2.txt").write_text("Texto de teste B", encoding="utf-8")

    # Direciona paths relativos do pipeline (data/...) para tmp usando chdir
    monkeypatch.chdir(tmp_path)

    # Mocka SentenceTransformer e TfidfVectorizer
    monkeypatch.setattr(pipeline, "SentenceTransformer", lambda *_a, **_kw: FakeModel())
    monkeypatch.setattr(pipeline, "TfidfVectorizer", lambda: FakeTFIDF())

    # Executa o pipeline
    pipeline.main()

    # Verifica se os índices foram salvos
    lexical_dir = data_dir / "indexes" / "lexical"
    semantic_dir = data_dir / "indexes" / "semantic"

    assert lexical_dir.exists()
    assert semantic_dir.exists()
    assert any(lexical_dir.iterdir())
    assert any(semantic_dir.iterdir())
