from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ProductCreate(BaseModel):
    model_config = ConfigDict(
        title="Dados para cadastro de produto",
        json_schema_extra={
            "example": {
                "url": "https://example.com/produto-teste",
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


class ProductResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        title="Produto cadastrado",
    )

    id: int = Field(description="Identificador único do produto.")
    url: str = Field(description="URL do produto monitorado.")
    name: str = Field(description="Nome do produto.")
    target_price: float = Field(description="Preço desejado para alerta.")
    is_active: bool = Field(description="Indica se o produto está ativo para monitoramento.")
    created_at: datetime = Field(description="Data e hora de cadastro do produto.")
    updated_at: datetime = Field(description="Data e hora da última atualização do produto.")