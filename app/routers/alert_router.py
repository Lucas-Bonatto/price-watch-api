from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.schemas.alert import PriceAlertResponse
from app.services.alert_service import AlertService

router = APIRouter(tags=["Alertas"])


@router.get(
    "/products/{product_id}/alert",
    response_model=PriceAlertResponse,
    summary="Verificar alerta de preço do produto",
    description=(
        "Verifica se o último preço coletado para o produto atingiu ou ficou abaixo "
        "do preço-alvo cadastrado."
    ),
)
def get_product_price_alert(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    latest_history = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.checked_at.desc())
        .first()
    )

    if latest_history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum preço foi coletado para este produto ainda.",
        )

    alert_service = AlertService()
    price_alert = alert_service.check_price_alert(
        current_price=latest_history.price,
        target_price=product.target_price,
    )

    return PriceAlertResponse(
        alert_triggered=price_alert.alert_triggered,
        alert_message=price_alert.alert_message,
        product_id=product.id,
        product_name=product.name,
        target_price=product.target_price,
        current_price=latest_history.price,
    )