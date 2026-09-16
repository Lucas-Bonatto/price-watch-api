from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from app.config import public_demo_enabled
from app.database import Base, SessionLocal, engine
from app.demo import seed_demo_data
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.routers.alert_router import router as alert_router
from app.routers.history_router import router as history_router
from app.routers.product_router import router as product_router
from app.routers.system_router import router as system_router

# Garante que os modelos sejam carregados antes de criar as tabelas.
MODELS = (Product, PriceHistory)
STATIC_DIR = Path(__file__).resolve().parent / "static"

tags_metadata = [
    {
        "name": "Produtos",
        "description": "Operações para cadastro, consulta, atualização, remoção e coleta de dados de produtos monitorados.",
    },
    {
        "name": "Histórico",
        "description": "Operações para consultar o histórico de preços coletados.",
    },
    {
        "name": "Alertas",
        "description": "Operações para verificar se um produto atingiu o preço desejado.",
    },
    {
        "name": "Sistema",
        "description": "Rotas básicas para verificar o funcionamento da API.",
    },
]

DEMO_BLOCK_MESSAGE = (
    "Demonstração pública em modo somente leitura. Operações de criação, "
    "atualização, exclusão e coleta externa estão desabilitadas."
)
SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def create_app(*, demo_read_only: bool | None = None) -> FastAPI:
    if demo_read_only is None:
        demo_read_only = public_demo_enabled()

    description = (
        "API para cadastrar produtos, monitorar preços, armazenar histórico "
        "e verificar alertas quando o preço cair abaixo do valor desejado."
    )

    if demo_read_only:
        description += (
            " Esta implantação é uma demonstração pública somente para leitura, "
            "com dados de exemplo e operações mutáveis desabilitadas."
        )

    application = FastAPI(
        title="API de Monitoramento de Preços",
        description=description,
        version="0.3.0",
        openapi_tags=tags_metadata,
    )
    application.state.demo_read_only = demo_read_only
    application.mount(
        "/static",
        StaticFiles(directory=STATIC_DIR),
        name="static",
    )

    @application.middleware("http")
    async def enforce_public_demo_read_only(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if demo_read_only and request.method.upper() not in SAFE_METHODS:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": DEMO_BLOCK_MESSAGE},
                headers={"X-Demo-Mode": "read-only"},
            )

        response = await call_next(request)

        if demo_read_only:
            response.headers["X-Demo-Mode"] = "read-only"

        return response

    application.include_router(system_router)
    application.include_router(product_router)
    application.include_router(history_router)
    application.include_router(alert_router)

    return application


DEMO_READ_ONLY = public_demo_enabled()

Base.metadata.create_all(bind=engine)

if DEMO_READ_ONLY:
    with SessionLocal() as demo_session:
        seed_demo_data(demo_session)

app = create_app(demo_read_only=DEMO_READ_ONLY)
