from typing import List, Tuple


# Normaliza uma lista de scores para o intervalo [0, 1]
def normalize_scores(scores: List[float]) -> List[float]:
    min_s, max_s = min(scores), max(scores)
    if max_s == min_s:
        return [0.0 for _ in scores]
    return [(s - min_s) / (max_s - min_s) for s in scores]


# Combina resultados léxicos e semânticos usando média ponderada
# Retorna lista de (doc_id, score_final, score_lex, score_sem, flags)
def combine_scores(top_lex: List[Tuple[str, float]],
                   top_sem: List[Tuple[str, float]],
                   k_final: int,
                   alpha: float = 0.5,
                   tau_lex: float = 0.8,
                   tau_sem: float = 0.8) -> List[Tuple[str, float, float, float, List[str]]]:
    sem_dict = dict(top_sem)

    # Normaliza scores
    lex_ids, lex_scores = zip(*top_lex)
    sem_scores = [sem_dict.get(doc_id, 0.0) for doc_id in lex_ids]
    norm_lex = normalize_scores(list(lex_scores))
    norm_sem = normalize_scores(list(sem_scores))

    results = []
    for doc_id, s_lex, s_sem in zip(lex_ids, norm_lex, norm_sem):
        score_final = alpha * s_lex + (1 - alpha) * s_sem
        flags = []
        if s_lex >= tau_lex:
            flags.append("plagio_literal")
        if s_sem >= tau_sem:
            flags.append("parafrase")
        results.append((doc_id, score_final, s_lex, s_sem, flags))

    # Ordena pelo score final e retorna top k
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:k_final]
