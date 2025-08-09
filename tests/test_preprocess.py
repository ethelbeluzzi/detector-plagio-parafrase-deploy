from src.preprocess import normalize

# Deve remover acentos, colocar em minúsculas, tirar HTML e espaços extras
def test_normalize_removes_accents_and_html():
    texto = "  Eu <b>AMO</b> escrever épicos da literatura!   "
    esperado = "eu amo escrever epicos da literatura!"
    assert normalize(texto) == esperado
