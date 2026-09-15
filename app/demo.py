from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.price_history import PriceHistory
from app.models.product import Product


DEMO_PRODUCTS = (
    {
        "url": (
            "https://books.toscrape.com/catalogue/"
            "a-light-in-the-attic_1000/index.html"
        ),
        "name": "A Light in the Attic",
        "target_price": 40.0,
        "created_at": datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc),
        "history": (
            (51.77, True, datetime(2026, 9, 1, 12, 5, tzinfo=timezone.utc)),
            (46.90, True, datetime(2026, 9, 5, 12, 5, tzinfo=timezone.utc)),
            (39.99, True, datetime(2026, 9, 10, 12, 5, tzinfo=timezone.utc)),
        ),
    },
    {
        "url": (
            "https://books.toscrape.com/catalogue/"
            "tipping-the-velvet_999/index.html"
        ),
        "name": "Tipping the Velvet",
        "target_price": 30.0,
        "created_at": datetime(2026, 9, 2, 15, 0, tzinfo=timezone.utc),
        "history": (
            (53.74, True, datetime(2026, 9, 2, 15, 5, tzinfo=timezone.utc)),
            (49.90, True, datetime(2026, 9, 8, 15, 5, tzinfo=timezone.utc)),
        ),
    },
)


def seed_demo_data(db: Session) -> None:
    """Create the public demo dataset once for the current database."""
    try:
        for sample in DEMO_PRODUCTS:
            product = db.query(Product).filter(Product.url == sample["url"]).first()

            if product is None:
                product = Product(
                    url=sample["url"],
                    name=sample["name"],
                    target_price=sample["target_price"],
                    created_at=sample["created_at"],
                    updated_at=sample["created_at"],
                )
                db.add(product)
                db.flush()

            history_exists = (
                db.query(PriceHistory)
                .filter(PriceHistory.product_id == product.id)
                .first()
            )

            if history_exists is None:
                db.add_all(
                    PriceHistory(
                        product_id=product.id,
                        price=price,
                        available=available,
                        checked_at=checked_at,
                    )
                    for price, available, checked_at in sample["history"]
                )

        db.commit()
    except Exception:
        db.rollback()
        raise
