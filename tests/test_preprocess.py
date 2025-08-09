from src.preprocess import normalize

# Deve remover acentos, colocar em minúsculas, tirar HTML e espaços extras
def test_normalize_removes_accents_and_html():
    texto = "  Eu <b>AMO</b> escrever!   "
    esperado = "eu amo escrever!"
    assert normalize(texto) == esperado
