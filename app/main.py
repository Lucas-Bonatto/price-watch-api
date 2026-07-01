from fastapi import FastAPI

app = FastAPI(
    title="Price Watch API",
    description="API para monitoramento de preços com histórico e alertas.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Price Watch API está funcionando!",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
    }