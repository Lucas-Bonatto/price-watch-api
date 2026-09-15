from fastapi import APIRouter, Request

router = APIRouter(tags=["Sistema"])


@router.get(
    "/",
    summary="Página inicial da API",
    description="Retorna uma mensagem simples informando que a API está funcionando.",
)
def root(request: Request):
    response = {
        "message": "API de Monitoramento de Preços está funcionando!",
        "docs": "/docs",
    }

    if request.app.state.demo_read_only:
        response["demo_mode"] = "read-only"

    return response


@router.get(
    "/health",
    summary="Verificar saúde da API",
    description="Verifica se a aplicação está ativa e respondendo corretamente.",
)
def health_check(request: Request):
    response = {
        "status": "ok",
    }

    if request.app.state.demo_read_only:
        response["demo_mode"] = "read-only"

    return response
