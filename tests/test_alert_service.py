from app.services.alert_service import AlertService


def test_should_trigger_alert_when_current_price_is_lower_than_target_price():
    alert_service = AlertService()

    result = alert_service.check_price_alert(
        current_price=50,
        target_price=100,
    )

    assert result.alert_triggered is True
    assert result.alert_message == "O produto atingiu o preço desejado."


def test_should_trigger_alert_when_current_price_is_equal_to_target_price():
    alert_service = AlertService()

    result = alert_service.check_price_alert(
        current_price=100,
        target_price=100,
    )

    assert result.alert_triggered is True
    assert result.alert_message == "O produto atingiu o preço desejado."


def test_should_not_trigger_alert_when_current_price_is_higher_than_target_price():
    alert_service = AlertService()

    result = alert_service.check_price_alert(
        current_price=150,
        target_price=100,
    )

    assert result.alert_triggered is False
    assert result.alert_message == "O produto ainda está acima do preço desejado."