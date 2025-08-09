from src.preprocess import normalize

# Deve remover acentos, colocar em minúsculas, tirar HTML e espaços extras
def test_normalize_removes_accents_and_html():
    texto = "  Olá <b>Mundo</b>!   "
    esperado = "ola mundo!"
    assert normalize(texto) == esperado
