from dataclasses import dataclass


@dataclass
class PriceAlert:
    alert_triggered: bool
    alert_message: str


class AlertService:
    def check_price_alert(
        self,
        current_price: float,
        target_price: float,
    ) -> PriceAlert:
        if current_price <= target_price:
            return PriceAlert(
                alert_triggered=True,
                alert_message="O produto atingiu o preço desejado.",
            )

        return PriceAlert(
            alert_triggered=False,
            alert_message="O produto ainda está acima do preço desejado.",
        )