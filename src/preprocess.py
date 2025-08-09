import re
import unicodedata

# Normaliza texto: remove acentos, converte para minúsculas, remove HTML e espaços extras
def normalize(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.category(c).startswith("M"))
    text = text.lower()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text
