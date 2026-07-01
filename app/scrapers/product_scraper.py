import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


class ScraperError(Exception):
    """Erro genérico ao tentar coletar dados de uma página."""


@dataclass
class ScrapedProduct:
    name: str
    price: float
    available: bool


class ProductScraper:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "PriceWatchBot/0.1"
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
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as error:
            raise ScraperError(f"Erro ao acessar a página: {error}") from error

        return response.text

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
            raise ScraperError(f"O campo '{field_name}' foi encontrado, mas está vazio.")

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
            raise ScraperError(f"Não foi possível converter o preço: {price_text}") from error

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