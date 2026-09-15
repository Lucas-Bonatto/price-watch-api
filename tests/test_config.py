from app.config import public_demo_enabled


def test_demo_should_be_disabled_by_default(monkeypatch):
    monkeypatch.delenv("PRICE_WATCH_DEMO_READ_ONLY", raising=False)
    monkeypatch.delenv("VERCEL", raising=False)

    assert public_demo_enabled() is False


def test_vercel_deployment_should_enable_demo_by_default(monkeypatch):
    monkeypatch.delenv("PRICE_WATCH_DEMO_READ_ONLY", raising=False)
    monkeypatch.setenv("VERCEL", "1")

    assert public_demo_enabled() is True


def test_explicit_demo_setting_should_override_vercel_default(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("PRICE_WATCH_DEMO_READ_ONLY", "false")

    assert public_demo_enabled() is False
