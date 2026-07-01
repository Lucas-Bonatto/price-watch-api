from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.schemas.price_history import PriceHistoryResponse

router = APIRouter(tags=["Histórico"])


@router.get(
    "/products/{product_id}/history",
    response_model=list[PriceHistoryResponse],
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