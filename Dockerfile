FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHERUSAGESTATS=false

WORKDIR /app

# libs mínimas; libgomp1 evita erro de OpenMP em wheels de ML
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgomp1 git \
  && rm -rf /var/lib/apt/lists/*

# instala PyTorch CPU-only primeiro para evitar versão GPU pesada
RUN pip install torch==2.0.1+cpu --extra-index-url https://download.pytorch.org/whl/cpu

# instala demais dependências (melhor uso de cache)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copia código e dados
COPY src/ /app/src/
COPY app/ /app/app/
COPY data/ /app/data/

EXPOSE 8501

CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=localhost"]


