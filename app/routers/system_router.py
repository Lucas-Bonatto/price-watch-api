from fastapi import APIRouter

router = APIRouter(tags=["Sistema"])


@router.get(
    "/",
    summary="Página inicial da API",
    description="Retorna uma mensagem simples informando que a API está funcionando.",
)
def root():
    return {
        "message": "API de Monitoramento de Preços está funcionando!",
        "docs": "/docs",
    }


@router.get(
    "/health",
    summary="Verificar saúde da API",
    description="Verifica se a aplicação está ativa e respondendo corretamente.",
)
def health_check():
    return {
        "status": "ok",
    }