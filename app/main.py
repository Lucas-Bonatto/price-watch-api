from fastapi import FastAPI

from app.database import Base, engine
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.routers.alert_router import router as alert_router
from app.routers.history_router import router as history_router
from app.routers.product_router import router as product_router
from app.routers.system_router import router as system_router

# Garante que os modelos sejam carregados antes de criar as tabelas.
MODELS = (Product, PriceHistory)

Base.metadata.create_all(bind=engine)

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

app = FastAPI(
    title="API de Monitoramento de Preços",
    description=(
        "API para cadastrar produtos, monitorar preços, armazenar histórico "
        "e futuramente enviar alertas quando o preço cair abaixo do valor desejado."
    ),
    version="0.1.0",
    openapi_tags=tags_metadata,
)

app.include_router(system_router)
app.include_router(product_router)
app.include_router(history_router)
app.include_router(alert_router)