from collections.abc import Iterable

import pytest
import requests

from app.scrapers.product_scraper import ProductScraper, ScraperError
from app.security.url_policy import UnsafeUrlError
from tests.test_url_policy import resolver_for


VALID_HTML = b"""
<html>
  <body>
    <h1>Produto seguro</h1>
    <p class="price_color">R$ 1.234,56</p>
    <p class="availability">Em estoque</p>
  </body>
</html>
"""


class FakeResponse:
    def __init__(
        self,
        *,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        chunks: Iterable[bytes] = (VALID_HTML,),
        encoding: str | None = "utf-8",
    ):
        self.status_code = status_code
        self.headers = headers or {"Content-Type": "text/html; charset=utf-8"}
        self.chunks = list(chunks)
        self.encoding = encoding
        self.closed = False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def iter_content(self, chunk_size: int):
        del chunk_size
        yield from self.chunks

    def close(self):
        self.closed = True


class FakeSession:
    def __init__(self, responses: list[FakeResponse]):
        self.responses = responses
        self.calls: list[dict] = []
        self.trust_env = True

    def get(self, url: str, **kwargs):
        self.calls.append({"url": url, **kwargs})
        return self.responses.pop(0)


def build_scraper(session: FakeSession, **kwargs) -> ProductScraper:
    return ProductScraper(
        allowed_hosts={"shop.example"},
        resolver=resolver_for("93.184.216.34"),
        session=session,
        **kwargs,
    )


def test_should_scrape_valid_html_with_hardened_request():
    response = FakeResponse()
    session = FakeSession([response])
    scraper = build_scraper(session)

    product = scraper.scrape("https://shop.example/produto")

    assert product.name == "Produto seguro"
    assert product.price == 1234.56
    assert product.available is True
    assert session.trust_env is False
    assert session.calls[0]["allow_redirects"] is False
    assert session.calls[0]["stream"] is True
    assert session.calls[0]["timeout"] == (3.05, 10)
    assert response.closed is True


def test_should_revalidate_and_block_unsafe_redirect_before_second_request():
    response = FakeResponse(
        status_code=302,
        headers={"Location": "https://127.0.0.1/admin"},
        chunks=(),
    )
    session = FakeSession([response])
    scraper = build_scraper(session)

    with pytest.raises(UnsafeUrlError, match="IP literais"):
        scraper.scrape("https://shop.example/produto")

    assert len(session.calls) == 1
    assert response.closed is True


def test_should_reject_disallowed_content_type():
    session = FakeSession([FakeResponse(headers={"Content-Type": "application/json"})])
    scraper = build_scraper(session)

    with pytest.raises(ScraperError, match="tipo de conteúdo"):
        scraper.scrape("https://shop.example/produto")


def test_should_reject_declared_oversized_response():
    session = FakeSession(
        [
            FakeResponse(
                headers={
                    "Content-Type": "text/html",
                    "Content-Length": "101",
                }
            )
        ]
    )
    scraper = build_scraper(session, max_response_bytes=100)

    with pytest.raises(ScraperError, match="excede o limite"):
        scraper.scrape("https://shop.example/produto")


def test_should_stop_streaming_when_actual_body_exceeds_limit():
    session = FakeSession([FakeResponse(chunks=[b"a" * 60, b"b" * 41])])
    scraper = build_scraper(session, max_response_bytes=100)

    with pytest.raises(ScraperError, match="excede o limite"):
        scraper.scrape("https://shop.example/produto")
