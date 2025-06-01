from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List

from user_service.domain.entities.cart import Cart


class ICartRepository(ABC):
    @abstractmethod
    async def get_item_from_user_cart(
        self, user_id: UUID, product_id: UUID
    ) -> Optional[Cart]:
        raise NotImplementedError

    @abstractmethod
    async def get_cart_items(self, user_id: UUID) -> List[Cart]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Optional[Cart]:
        raise NotImplementedError

    @abstractmethod
    async def delete_product(self, cart: Cart) -> None:
        raise NotImplementedError

    @abstractmethod
    async def add_product(self, cart: Cart) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_all_products(self, cart: Cart) -> None:
        raise NotImplementedError
