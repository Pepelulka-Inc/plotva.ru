from uuid import UUID
from typing import List, Optional

from sqlalchemy import insert, delete, select
from sqlalchemy.orm import Session

from user_service.domain.entities.cart import Cart
from user_service.infrastructure.database.models import ShoppingCartEntry
from user_service.domain.repositories.cart_repository import ICartRepository


class CartRepository(ICartRepository):
    def __init__(self, session: Session):
        self.session = session

    async def get_by_user_id(self):
        await print("lol")

    async def get_item_from_user_cart(
        self, user_id: UUID, product_id: UUID
    ) -> Optional[Cart]:
        stmt = select(ShoppingCartEntry).where(
            ShoppingCartEntry.user_id == user_id,
            ShoppingCartEntry.product_id == product_id,
        )
        result = await self.session.execute(stmt)
        records = result.scalar_one_or_none()
        return records

    async def get_cart_items(self, user_id: UUID) -> List[Cart]:
        stmt = select(ShoppingCartEntry).where(ShoppingCartEntry.user_id == user_id)
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return list(records)

    async def add_product(self, cart: Cart) -> None:
        stmt = insert(ShoppingCartEntry).values(
            entry_id=cart.entry_id,
            product_id=cart.product_id,
            user_id=cart.user_id,
            quantity=cart.quantity,
        )
        await self.session.execute(stmt)

    async def delete_product(self, cart: Cart) -> None:
        stmt = delete(ShoppingCartEntry).where(
            Cart.product_id == cart.product_id, Cart.user_id == cart.user_id
        )
        await self.session.execute(stmt)

    async def delete_all_products(self, cart: Cart) -> None:
        stmt = delete(ShoppingCartEntry).where(Cart.user_id == cart.user_id)
        await self.session.execute(stmt)
