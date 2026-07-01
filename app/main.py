from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.schemas.price_history import PriceHistoryResponse
from app.schemas.product import ProductCreate, ProductResponse
from app.schemas.scraper import ScrapedProductResponse
from app.scrapers.product_scraper import ProductScraper, ScraperError

Base.metadata.create_all(bind=engine)

tags_metadata = [
    {
        "name": "Produtos",
        "description": "Operações para cadastro, consulta, remoção e coleta de dados de produtos monitorados.",
    },
    {
        "name": "Histórico",
        "description": "Operações para consultar o histórico de preços coletados.",
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


@app.get(
    "/",
    tags=["Sistema"],
    summary="Página inicial da API",
    description="Retorna uma mensagem simples informando que a API está funcionando.",
)
def root():
    return {
        "message": "API de Monitoramento de Preços está funcionando!",
        "docs": "/docs",
    }


@app.get(
    "/health",
    tags=["Sistema"],
    summary="Verificar saúde da API",
    description="Verifica se a aplicação está ativa e respondendo corretamente.",
)
def health_check():
    return {
        "status": "ok",
    }


@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Produtos"],
    summary="Cadastrar produto",
    description=(
        "Cadastra um novo produto para monitoramento. "
        "A URL deve ser única e o preço-alvo deve ser maior que zero."
    ),
)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
):
    product = Product(
        url=str(product_data.url),
        name=product_data.name,
        target_price=product_data.target_price,
    )

    db.add(product)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um produto cadastrado com essa URL.",
        )

    db.refresh(product)

    return product


@app.get(
    "/products",
    response_model=list[ProductResponse],
    tags=["Produtos"],
    summary="Listar produtos",
    description="Retorna todos os produtos cadastrados para monitoramento.",
)
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.id).all()

    return products


@app.get(
    "/products/{product_id}",
    response_model=ProductResponse,
    tags=["Produtos"],
    summary="Buscar produto por ID",
    description="Retorna os dados de um produto específico a partir do seu identificador.",
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    return product


@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Produtos"],
    summary="Remover produto",
    description="Remove um produto cadastrado a partir do seu identificador.",
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    db.query(PriceHistory).filter(PriceHistory.product_id == product_id).delete()
    db.delete(product)
    db.commit()

    return None


@app.post(
    "/products/{product_id}/scrape",
    response_model=ScrapedProductResponse,
    tags=["Produtos"],
    summary="Coletar dados atuais do produto",
    description=(
        "Acessa a URL cadastrada para o produto, coleta nome, preço e disponibilidade, "
        "e salva o preço encontrado no histórico."
    ),
)
def scrape_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    scraper = ProductScraper()

    try:
        scraped_product = scraper.scrape(product.url)
    except ScraperError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    price_history = PriceHistory(
        product_id=product.id,
        price=scraped_product.price,
        available=scraped_product.available,
    )

    db.add(price_history)
    db.commit()
    db.refresh(price_history)

    return ScrapedProductResponse(
        source_url=product.url,
        scraped_name=scraped_product.name,
        current_price=scraped_product.price,
        available=scraped_product.available,
        history_id=price_history.id,
        checked_at=price_history.checked_at,
    )


@app.get(
    "/products/{product_id}/history",
    response_model=list[PriceHistoryResponse],
    tags=["Histórico"],
    summary="Listar histórico de preços do produto",
    description="Retorna todos os preços já coletados para um produto específico.",
)
def list_product_price_history(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    histories = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.checked_at.desc())
        .all()
    )

    return histories