from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PriceHistoryResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        title="Registro de histórico de preço",
    )

    id: int = Field(description="Identificador único do registro de histórico.")
    product_id: int = Field(description="Identificador do produto relacionado.")
    price: float = Field(description="Preço encontrado na coleta.")
    available: bool = Field(description="Indica se o produto estava disponível na coleta.")
    checked_at: datetime = Field(description="Data e hora em que o preço foi coletado.")