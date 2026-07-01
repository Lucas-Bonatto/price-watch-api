from pydantic import BaseModel, Field


class PriceAlertResponse(BaseModel):
    alert_triggered: bool = Field(
        description="Indica se o preço atual atingiu ou ficou abaixo do preço-alvo."
    )
    alert_message: str = Field(description="Mensagem explicando o resultado da verificação.")
    product_id: int = Field(description="Identificador do produto monitorado.")
    product_name: str = Field(description="Nome cadastrado do produto.")
    target_price: float = Field(description="Preço-alvo cadastrado para o produto.")
    current_price: float = Field(description="Preço atual coletado.")