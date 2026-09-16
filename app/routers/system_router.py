from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse

router = APIRouter(tags=["Sistema"])
LANDING_PAGE = Path(__file__).resolve().parents[1] / "static" / "index.html"


@router.get(
    "/",
    include_in_schema=False,
    response_class=FileResponse,
)
def landing_page() -> FileResponse:
    return FileResponse(LANDING_PAGE, media_type="text/html")


@router.get(
    "/api",
    summary="Informações básicas da API",
    description="Retorna os links e o estado básico da API.",
)
def api_info(request: Request):
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
