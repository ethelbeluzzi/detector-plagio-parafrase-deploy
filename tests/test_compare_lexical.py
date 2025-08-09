from src.compare_lexical import compare_lexical

# Deve ranquear por similaridade com normalização de texto
def test_compare_lexical_ranking_basic():
    corpus = [
        "Olá <b>mundo</b> de dados e privacidade",
        "Privacidade de dados pessoais e segurança",
        "Cinema brasileiro e políticas culturais",
    ]
    query = "privacidade e dados pessoais"
    result = compare_lexical(query, corpus, top_n=3)
    assert len(result) == 3
    assert result[0][0] == 1
    assert result[1][0] == 0

# Deve retornar lista vazia para consulta ou corpus vazio
def test_compare_lexical_empty_inputs():
    assert compare_lexical("", ["a"]) == []
    assert compare_lexical("texto", []) == []

# Deve respeitar o parâmetro top_n
def test_compare_lexical_top_n_limit():
    corpus = [
        "dados e privacidade",
        "dados pessoais",
        "segurança da informação",
    ]
    result = compare_lexical("dados pessoais e privacidade", corpus, top_n=1)
    assert len(result) == 1
