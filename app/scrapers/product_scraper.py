import re
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.security.url_policy import Resolver, UnsafeUrlError, validate_outbound_url


class ScraperError(Exception):
    """Erro genérico ao tentar coletar dados de uma página."""


@dataclass
class ScrapedProduct:
    name: str
    price: float
    available: bool


class ProductScraper:
    REDIRECT_STATUS_CODES = frozenset({301, 302, 303, 307, 308})
    ALLOWED_CONTENT_TYPES = frozenset({"text/html", "application/xhtml+xml"})

    def __init__(
        self,
        timeout: int = 10,
        connect_timeout: float = 3.05,
        max_response_bytes: int = 2 * 1024 * 1024,
        max_redirects: int = 3,
        allowed_hosts: set[str] | frozenset[str] | None = None,
        resolver: Resolver | None = None,
        session: requests.Session | None = None,
    ):
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.max_response_bytes = max_response_bytes
        self.max_redirects = max_redirects
        self.allowed_hosts = allowed_hosts
        self.resolver = resolver
        self.session = session or requests.Session()
        # Evita que variáveis HTTP_PROXY/HTTPS_PROXY alterem o destino real da conexão.
        self.session.trust_env = False
        self.headers = {
            "User-Agent": "PriceWatchBot/0.2 (+https://github.com/Lucas-Bonatto/price-watch-api)",
            "Accept": "text/html,application/xhtml+xml",
        }

    def scrape(
        self,
        url: str,
        name_selector: str = "h1",
        price_selector: str = ".price_color",
        availability_selector: str = ".availability",
    ) -> ScrapedProduct:
        html = self._fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        name = self._extract_text(soup, name_selector, "nome do produto")
        price_text = self._extract_text(soup, price_selector, "preço do produto")
        availability_text = self._extract_text(
            soup,
            availability_selector,
            "disponibilidade do produto",
        )

        price = self._parse_price(price_text)
        available = self._parse_availability(availability_text)

        return ScrapedProduct(
            name=name,
            price=price,
            available=available,
        )

    def _fetch_html(self, url: str) -> str:
        current_url = url

        for redirect_count in range(self.max_redirects + 1):
            validate_outbound_url(
                current_url,
                allowed_hosts=self.allowed_hosts,
                resolver=self.resolver,
            )

            response: requests.Response | None = None

            try:
                response = self.session.get(
                    current_url,
                    headers=self.headers,
                    timeout=(self.connect_timeout, self.timeout),
                    allow_redirects=False,
                    stream=True,
                )

                if response.status_code in self.REDIRECT_STATUS_CODES:
                    if redirect_count >= self.max_redirects:
                        raise ScraperError(
                            f"A página excedeu o limite de {self.max_redirects} redirecionamentos."
                        )

                    location = response.headers.get("Location")

                    if not location:
                        raise ScraperError(
                            "A página retornou um redirecionamento sem destino."
                        )

                    current_url = urljoin(current_url, location)
                    continue

                response.raise_for_status()
                self._validate_response_headers(response)
                response_body = self._read_limited_body(response)
                encoding = response.encoding or "utf-8"

                return response_body.decode(encoding, errors="replace")
            except UnsafeUrlError:
                raise
            except requests.RequestException as error:
                raise ScraperError(f"Erro ao acessar a página: {error}") from error
            finally:
                if response is not None:
                    response.close()

        raise ScraperError("Não foi possível concluir a coleta da página.")

    def _validate_response_headers(self, response: requests.Response) -> None:
        content_type = response.headers.get("Content-Type", "")
        media_type = content_type.split(";", maxsplit=1)[0].strip().lower()

        if media_type not in self.ALLOWED_CONTENT_TYPES:
            raise ScraperError("A página retornou um tipo de conteúdo não permitido.")

        content_length = response.headers.get("Content-Length")

        if content_length is None:
            return

        try:
            declared_size = int(content_length)
        except ValueError as error:
            raise ScraperError(
                "A página retornou um tamanho de conteúdo inválido."
            ) from error

        if declared_size < 0 or declared_size > self.max_response_bytes:
            raise ScraperError(
                f"A página excede o limite de {self.max_response_bytes} bytes."
            )

    def _read_limited_body(self, response: requests.Response) -> bytes:
        body = bytearray()

        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue

            body.extend(chunk)

            if len(body) > self.max_response_bytes:
                raise ScraperError(
                    f"A página excede o limite de {self.max_response_bytes} bytes."
                )

        return bytes(body)

    def _extract_text(
        self,
        soup: BeautifulSoup,
        selector: str,
        field_name: str,
    ) -> str:
        element = soup.select_one(selector)

        if element is None:
            raise ScraperError(
                f"Não foi possível encontrar o campo '{field_name}' "
                f"usando o seletor CSS '{selector}'."
            )

        text = element.get_text(strip=True)

        if not text:
            raise ScraperError(
                f"O campo '{field_name}' foi encontrado, mas está vazio."
            )

        return text

    def _parse_price(self, price_text: str) -> float:
        clean_price = re.sub(r"[^\d,.-]", "", price_text)

        if not clean_price:
            raise ScraperError(f"Preço inválido: {price_text}")

        has_comma = "," in clean_price
        has_dot = "." in clean_price

        if has_comma and has_dot:
            last_comma = clean_price.rfind(",")
            last_dot = clean_price.rfind(".")

            if last_comma > last_dot:
                clean_price = clean_price.replace(".", "").replace(",", ".")
            else:
                clean_price = clean_price.replace(",", "")
        elif has_comma:
            clean_price = clean_price.replace(",", ".")

        try:
            return float(clean_price)
        except ValueError as error:
            raise ScraperError(
                f"Não foi possível converter o preço: {price_text}"
            ) from error

    def _parse_availability(self, availability_text: str) -> bool:
        text = availability_text.lower()

        unavailable_terms = [
            "out of stock",
            "indisponível",
            "indisponivel",
            "sem estoque",
            "esgotado",
        ]

        available_terms = [
            "in stock",
            "available",
            "disponível",
            "disponivel",
            "em estoque",
            "estoque",
        ]

        if any(term in text for term in unavailable_terms):
            return False

        return any(term in text for term in available_terms)
