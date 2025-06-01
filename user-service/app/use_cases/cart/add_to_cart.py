from uuid import uuid4
from attr import dataclass

from app.dtos.cart.cart_dtos import AddProductToCartDTO
from domain.base import IUnitOfWork
from domain.entities.cart import Cart


@dataclass(slots=True)
class AddProductToCartUseCase:
    uow: IUnitOfWork

    async def __call__(self, dto: AddProductToCartDTO) -> None:
        async with self.uow:
            existing_item = await self.uow.cart_repo.get_item_from_user_cart(
                dto.user_id, dto.product_id
            )

            if existing_item:
                existing_item.quantity += dto.quantity
                await self.uow.cart_repo.update_product(existing_item)
            else:
                cart = Cart(
                    entry_id=str(uuid4()),
                    user_id=dto.user_id,
                    product_id=dto.product_id,
                    quantity=dto.quantity,
                )
                await self.uow.cart_repo.add_product(cart)

            await self.uow.commit()
