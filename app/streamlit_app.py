# app/streamlit_app.py
import streamlit as st
from src.compare_service import compare

# Renderiza a interface principal
def main():
    st.set_page_config(page_title="Plágio Similarity", layout="wide")
    st.title("🔍 Comparador de Similaridade de Textos")

    # Caixa de texto para entrada do usuário
    query = st.text_area("Cole o texto para análise:", height=200)

    # Botão para rodar a comparação
    if st.button("Comparar"):
        if not query.strip():
            st.warning("Digite um texto antes de comparar.")
            return

        # Executa a comparação
        with st.spinner("Processando..."):
            results = compare(query)

        # Exibe resultados
        if results:
            st.subheader("Resultados")
            st.write("doc_id | score_final | score_lex | score_sem | flags")
            for doc_id, score_final, score_lex, score_sem, flags in results:
                st.write(f"{doc_id} | {score_final:.3f} | {score_lex:.3f} | {score_sem:.3f} | {', '.join(flags) or '-'}")
        else:
            st.info("Nenhum resultado encontrado.")


if __name__ == "__main__":
    main()
