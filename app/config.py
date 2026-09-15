import os


TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


def public_demo_enabled() -> bool:
    value = os.getenv("PRICE_WATCH_DEMO_READ_ONLY", "false")

    return value.strip().lower() in TRUE_VALUES


def database_url() -> str:
    configured_url = os.getenv("DATABASE_URL")

    if configured_url:
        return configured_url

    if public_demo_enabled():
        return "sqlite://"

    return "sqlite:///./price_watch.db"
