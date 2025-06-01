import uuid

from attr import dataclass


@dataclass(slots=True, frozen=True)
class Cart:
    entry_id: int
    product_id: uuid.UUID
    user_id: uuid.UUID
    quantity: int
