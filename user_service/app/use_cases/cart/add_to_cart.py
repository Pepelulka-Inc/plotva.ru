import random

from attr import dataclass

from user_service.app.dtos.cart_dtos import AddProductToCartDTO
from user_service.domain.base import IUnitOfWork, BaseUseCase
from user_service.domain.entities.cart import Cart


@dataclass(slots=True)
class AddProductToCartUseCase(BaseUseCase):
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
                    entry_id=random.randint(1, 99999),
                    user_id=dto.user_id,
                    product_id=dto.product_id,
                    quantity=dto.quantity,
                )
                await self.uow.cart_repo.add_product(cart)

            await self.uow.commit()
