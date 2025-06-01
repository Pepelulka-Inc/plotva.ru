from uuid import UUID

from pydantic import BaseModel


class AddProductToCartDTO(BaseModel):
    user_id: UUID
    product_id: UUID
    quantity: int = 1


class RemoveProductFromCartDTO(BaseModel):
    user_id: UUID
    product_id: UUID


class ClearCartDTO(BaseModel):
    user_id: UUID
