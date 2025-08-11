import os
import sys
import base64
import requests
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd
import streamlit as st
from github import Github

# --- Caminho do projeto ---
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.compare_service import compare
from src.config import settings


# ========= LLM Sidebar (categorias + modos + GitHub) =========

@st.cache_resource
@st.cache_resource
@st.cache_resource
def get_contextos() -> Dict[str, str]:
    """Carrega todos os .txt da pasta contextos/ (na raiz do projeto)."""
    contextos: Dict[str, str] = {}
    pasta = ROOT / "contextos"

    if not pasta.exists():
        return contextos

    for arquivo in os.listdir(pasta):
        if arquivo.lower().endswith(".txt"):
            nome = os.path.splitext(arquivo)[0]
            nome_formatado = nome.replace("_", " ").title()  # deixa bonito
            try:
                with open(pasta / arquivo, "r", encoding="utf-8", errors="ignore") as f:
                    contextos[nome_formatado] = f.read().strip()
            except Exception:
                pass

    return contextos

def salvar_no_github(area: str, modo: str, pergunta: str, resposta: str) -> None:
    """Salva o histórico diretamente no GitHub em CSV (append)."""
    token = st.secrets["GITHUB_TOKEN"]
    repo_name = st.secrets["REPO_NAME"]
    file_path = st.secrets["HISTORICO_PATH"]  # ex.: "logs/chat_history.csv"

    g = Github(token)
    repo = g.get_repo(repo_name)
    # Escapa quebras de linha e vírgulas básicas
    def _clean(s) -> str:
        if s is None:
            return ""
        return str(s).replace("\n", " ").replace("\r", " ").replace(",", " ").strip()

    nova_linha = f"{_clean(area)},{_clean(modo)},{_clean(pergunta)},{_clean(resposta)}\n"

    try:
        contents = repo.get_contents(file_path)
        novo_conteudo = contents.decoded_content.decode() + nova_linha
        repo.update_file(file_path, "append chat history", novo_conteudo, contents.sha)
    except Exception:
        repo.create_file(file_path, "create chat history", "area,modo,pergunta,resposta\n" + nova_linha)

def llm_sidebar_consultation() -> None:
    # ==== CSS para Sidebar mais larga e texto estilizado ====
    st.markdown(
        """
        <style>
            /* Largura maior para a sidebar */
            [data-testid="stSidebar"] {
                min-width: 420px;
                max-width: 420px;
            }
    
            /* Estilo do título da sidebar */
            .sidebar-title {
                font-size: 20px;
                font-weight: bold;
                line-height: 1.3;
                margin-bottom: 8px;
            }
    
            /* Estilo do subtítulo da sidebar */
            .sidebar-subtitle {
                font-size: 16px;
                font-weight: normal;
                color: #444;
                margin-bottom: 16px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    """Sidebar de consulta à LLM com seleção de contexto e modo de resposta."""
    get_contextos.clear()
    contextos = get_contextos()

    # Visual alinhado ao app (fundo branco / separador)
    st.sidebar.markdown(
    """
    <p style="font-size:18px; font-weight:bold; margin-bottom:0;">
        🤖 Tem alguma dúvida?<br>
        <span style="font-weight:normal;">Selecione a área e o tipo de resposta.</span>
    </p>
    """,
    unsafe_allow_html=True
)

    # Categorias (menu suspenso): "geral" no topo, demais em ordem alfabética
    todas = list(contextos.keys())
    if "geral" in todas:
        outras = sorted([c for c in todas if c != "geral"])
        opcoes = ["geral"] + outras
    else:
        opcoes = sorted(todas)  # fallback

    contexto_escolhido = st.sidebar.selectbox("Área:", opcoes, index=0 if "geral" in opcoes else 0)

    # Modo de resposta (rádio)
    modo_resposta = st.sidebar.radio(
        "Formato da resposta:",
        options=["Explicação", "Resposta Técnica"],
        horizontal=False
    )

    # Pergunta
    user_question = st.sidebar.text_area("Digite sua dúvida abaixo:")

    if st.sidebar.button("Enviar pergunta") and user_question.strip():
        with st.spinner("Consultando a LLM..."):
            try:
                hf_token = st.secrets["HF_TOKEN"]
                headers = {"Authorization": f"Bearer {hf_token}", "Content-Type": "application/json"}

                # Prompt por modo
                if modo_resposta == "Explicação":
                    prompt = f"""
Explique de forma clara, didática e acessível, usando apenas o texto abaixo como base:
---
{contextos.get(contexto_escolhido, '')}
---
Pergunta: {user_question}
"""
                else:
                    prompt = f"""
Responda de forma técnica, objetiva e detalhada, como engenheiro de IA, com base apenas no texto abaixo:
---
{contextos.get(contexto_escolhido, '')}
---
Pergunta: {user_question}
"""

                API_URL = "https://router.huggingface.co/together/v1/chat/completions"
                payload = {
                    "model": "Qwen/Qwen2.5-7B-Instruct-Turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 300
                }

                response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

                if response.status_code == 200:
                    result = response.json()
                    reply = result["choices"][0]["message"]["content"]

                    # Salva no GitHub (apenas histórico; nada é exibido ao usuário além da resposta)
                    salvar_no_github(contexto_escolhido, modo_resposta, user_question.strip(), reply.strip())

                    st.sidebar.success("📘 Resposta da LLM:")
                    st.sidebar.markdown(f"> {reply.strip()}")
                elif response.status_code == 429:
                    st.sidebar.error("⚠️ Limite de requisições atingido!")
                else:
                    st.sidebar.error("❌ Erro inesperado ao consultar a LLM.")

            except Exception as e:
                st.sidebar.error(f"❌ Erro técnico: {e}")

    st.sidebar.markdown("---")


# ========= Helpers de UI =========

def _merge_overlaps(ranges: List[Tuple[int, int, str]]) -> List[Tuple[int, int, str]]:
    """
    Mescla intervalos (start, end, tipo) que se sobrepõem.
    Mantém o tipo "mais severo" quando houver conflito (plágio > paráfrase).
    Severidade: plagio_literal > parafrase.
    """
    if not ranges:
        return []

    severity = {"plagio_literal": 2, "parafrase": 1}
    ranges = sorted(ranges, key=lambda x: (x[0], -severity.get(x[2], 0)))

    merged: List[Tuple[int, int, str]] = []
    cur_s, cur_e, cur_t = ranges[0]

    for s, e, t in ranges[1:]:
        if s <= cur_e:  # overlap
            if e > cur_e:
                cur_e = e
            if severity.get(t, 0) > severity.get(cur_t, 0):
                cur_t = t
        else:
            merged.append((cur_s, cur_e, cur_t))
            cur_s, cur_e, cur_t = s, e, t

    merged.append((cur_s, cur_e, cur_t))
    return merged


def _highlight_text(query_text: str, resultados: List[Dict]) -> str:
    """
    Destaca no texto original os blocos suspeitos.
    Usa <mark> com classes CSS diferentes para cada tipo.
    """
    words = query_text.split()
    n = len(words)

    raw_ranges: List[Tuple[int, int, str]] = []
    for r in resultados:
        tipo = r.get("tipo")
        if tipo not in ("plagio_literal", "parafrase"):
            continue
        start_w = max(0, int(r["inicio"]))
        end_w = min(n, int(r["fim"]))
        if end_w > start_w:
            raw_ranges.append((start_w, end_w, tipo))

    if not raw_ranges:
        return "<p>" + " ".join(words) + "</p>"

    ranges = _merge_overlaps(raw_ranges)

    html_parts = []
    cursor = 0
    for s, e, tipo in ranges:
        if s > cursor:
            html_parts.append(" ".join(words[cursor:s]))
        chunk = " ".join(words[s:e])
        if tipo == "plagio_literal":
            html_parts.append(f"<mark class='plagio' title='Plágio literal'>{chunk}</mark>")
        else:
            html_parts.append(f"<mark class='parafrase' title='Paráfrase'>{chunk}</mark>")
        cursor = e
    if cursor < n:
        html_parts.append(" ".join(words[cursor:]))

    return "<p>" + " ".join(part for part in html_parts if part) + "</p>"


def _header_from_best(best_block: Dict) -> str:
    """
    Gera o cabeçalho de veredito a partir do melhor bloco.
    """
    tipo = best_block.get("tipo")
    cand = best_block.get("melhor_candidato", {}) or {}
    ref_doc = cand.get("doc_id", "documento do dataset")

    if tipo == "plagio_literal":
        return f"🚨 Esse texto contém <b>trecho com plágio literal</b> de: <b>{ref_doc}</b>"
    if tipo == "parafrase":
        return f"📝 Esse texto contém <b>trecho parafraseado</b> possivelmente derivado de: <b>{ref_doc}</b>"
    return "✅ Não foram encontrados blocos suspeitos com os thresholds atuais."


def _build_top_blocks_df(resultados: List[Dict], limit: int = 5) -> pd.DataFrame:
    rows = []
    for r in resultados[:limit]:
        cand = r.get("melhor_candidato", {}) or {}
        flags = r.get("tipo")
        if flags == "plagio_literal":
            flag_label = "🚨 plágio literal"
        elif flags == "parafrase":
            flag_label = "📝 paráfrase"
        else:
            flag_label = "—"

        rows.append({
            "🔎 Bloco": f"{r['bloco_id']} ({r['inicio']}-{r['fim']})",
            "📄 Documento base": cand.get("doc_id", "—"),
            "🏷 Classificação": flag_label,
            "📊 Score final": f"{r['scores']['final']:.3f}",
            "🅻 Léxico (bruto)": f"{r['scores']['lex_raw']:.3f}",
            "🅻 Léxico (norm.)": f"{r['scores']['lex_norm']:.3f}",
            "🆂 Semântico (bruto)": f"{r['scores']['sem_raw']:.3f}",
            "🆂 Semântico (norm.)": f"{r['scores']['sem_norm']:.3f}",
            "🧩 Trecho candidato": (cand.get("text", "")[:200] + "…") if cand.get("text") and len(cand["text"]) > 200 else (cand.get("text", "") or "—"),
        })
    return pd.DataFrame(rows)


# ========= App =========

def main():
    st.set_page_config(page_title="Case Tecnico - Ethel", layout="wide")

    # Header visual
    logo_file = ROOT / "app" / "letrus.png"
    with open(logo_file, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()
        
    st.markdown(f"""
    <style>
      .app-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 16px;
        background: white;
        border-bottom: 2px solid #c2c0b8;
      }}
      .left-group {{
        display: flex;
        align-items: center;
        gap: 20px;
      }}
      .app-title {{
        font-family: Georgia, "Times New Roman", serif;
        font-size: 18px;
        font-weight: 600;
        letter-spacing: .2px;
        color: #2b2b2b;
      }}
      .author-box {{
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        background: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 6px;
        padding: 4px 8px;
      }}
      .author-box a {{
        text-decoration: none;
      }}
      .author-box img {{
        vertical-align: middle;
      }}
      .app-logo {{
        height: 44px; /* tamanho fixo como antes */
        object-fit: contain;
      }}
    </style>
    
    <div class="app-header">
      <div class="left-group">
        <div class="app-title">Case Técnico - Ethel Beluzzi</div>
        <div class="author-box">
          <span>Quer saber mais sobre a autora?</span>
          <a href="http://lattes.cnpq.br/8943675734808684" target="_blank" title="Currículo Lattes">📄</a>
          <a href="https://www.linkedin.com/in/ethelpanitsabeluzzi/" target="_blank" title="LinkedIn">
            <img src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/linkedin.svg" width="18" height="18">
          </a>
        </div>
      </div>
      <img class="app-logo" src="data:image/png;base64,{logo_base64}" alt="Logo Letrus" />
    </div>
    """, unsafe_allow_html=True)


    st.title("🔍 Comparador de Similaridade de Textos")

    # CSS leve para os destaques
    st.markdown("""
    <style>
      mark.plagio { background-color: #ffb3b3; padding: 0.15rem 0.25rem; border-radius: 4px; }
      mark.parafrase { background-color: #ffe4a3; padding: 0.15rem 0.25rem; border-radius: 4px; }
      .legend span { display: inline-block; margin-right: 16px; }
      .legend .bullet { display:inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: 6px; vertical-align: -2px; }
      .bullet.plagio { background: #ffb3b3; }
      .bullet.parafrase { background: #ffe4a3; }
    </style>
    """, unsafe_allow_html=True)

    query = st.text_area("Cole o texto para análise:", height=220)

    if st.button("Comparar"):
        if not query.strip():
            st.warning("Digite um texto antes de comparar.")
            return

        with st.spinner("Processando..."):
            resultados = compare(query)

        if not resultados:
            st.info("Nenhum bloco suspeito encontrado com os thresholds atuais.")
            return

        best = resultados[0]
        header = _header_from_best(best)
        st.markdown(f"<h2 style='font-size:26px;'>{header}</h2>", unsafe_allow_html=True)

        with st.expander("Ver blocos e scores detalhados"):
            st.markdown("### 📌 Blocos mais suspeitos")
            st.table(_build_top_blocks_df(resultados))

            st.markdown("### 🖍️ Texto analisado (com destaques)")
            st.markdown(_highlight_text(query, resultados), unsafe_allow_html=True)

            st.markdown("""
            <div class="legend">
              <span><i class="bullet plagio"></i>Plágio literal</span>
              <span><i class="bullet parafrase"></i>Paráfrase</span>
            </div>
            """, unsafe_allow_html=True)

    # Sidebar de LLM (sempre disponível)
    llm_sidebar_consultation()


if __name__ == "__main__":
    main()
