from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.security.url_policy import UnsafeUrlError, validate_url_structure


class ProductCreate(BaseModel):
    model_config = ConfigDict(
        title="Dados para cadastro de produto",
        json_schema_extra={
            "example": {
                "url": "https://books.toscrape.com/produto-teste",
                "name": "Notebook Gamer",
                "target_price": 3500,
            }
        },
    )

    url: HttpUrl = Field(
        description="URL do produto que será monitorado.",
    )
    name: str = Field(
        min_length=2,
        max_length=255,
        description="Nome do produto.",
    )
    target_price: float = Field(
        gt=0,
        description="Preço desejado para disparar o alerta.",
    )

    @field_validator("url")
    @classmethod
    def validate_monitored_url(cls, url: HttpUrl) -> HttpUrl:
        try:
            validate_url_structure(str(url))
        except UnsafeUrlError as error:
            raise ValueError(str(error)) from error

        return url


class ProductUpdate(BaseModel):
    model_config = ConfigDict(
        title="Dados para atualização de produto",
        json_schema_extra={
            "example": {
                "name": "Livro de teste atualizado",
                "target_price": 60,
                "is_active": True,
            }
        },
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
        description="Novo nome do produto.",
    )
    target_price: float | None = Field(
        default=None,
        gt=0,
        description="Novo preço-alvo para disparar o alerta.",
    )
    is_active: bool | None = Field(
        default=None,
        description="Indica se o produto continuará ativo para monitoramento.",
    )


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Identificador único do produto.")
    url: str = Field(description="URL do produto monitorado.")
    name: str = Field(description="Nome do produto.")
    target_price: float = Field(description="Preço desejado para alerta.")
    is_active: bool = Field(
        description="Indica se o produto está ativo para monitoramento."
    )
    created_at: datetime = Field(description="Data e hora de cadastro do produto.")
    updated_at: datetime = Field(
        description="Data e hora da última atualização do produto."
    )
