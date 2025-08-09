from fastapi import FastAPI

# Instancia a aplicação FastAPI
app = FastAPI(
    title="plagio-similarity",
    version="0.1.0",
    description="API para comparação léxica e semântica de textos"
)

@app.get("/health")
def health():
    """
    Endpoint de verificação.
    Retorna status 'ok' quando a API está rodando.
    """
    return {"status": "ok"}
