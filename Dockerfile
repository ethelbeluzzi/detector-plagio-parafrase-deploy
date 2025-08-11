# ============ 1) Builder ============ 
FROM python:3.11-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /install

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgomp1 git \
  && rm -rf /var/lib/apt/lists/*

# PyTorch CPU-only primeiro (compatível com transformers recentes)
RUN pip install --no-cache-dir torch==2.2.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu

# Dependências do projeto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Congela o ambiente exato que funcionou
RUN pip freeze > /install/requirements.lock

# ============ 2) Runtime ============ 
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHERUSAGESTATS=false

WORKDIR /app

# Copia TUDO que foi instalado no builder
COPY --from=builder /usr/local /usr/local
COPY --from=builder /install/requirements.lock /app/requirements.lock

# Copia o código e dados necessários
COPY src/ /app/src/
COPY app/ /app/app/
COPY data/ /app/data/

EXPOSE 8501
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=localhost"]




