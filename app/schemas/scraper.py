from pydantic import BaseModel, Field


class ScrapedProductResponse(BaseModel):
    source_url: str = Field(description="URL usada para coletar os dados.")
    scraped_name: str = Field(description="Nome encontrado na página.")
    current_price: float = Field(description="Preço atual encontrado na página.")
    available: bool = Field(description="Indica se o produto está disponível.")