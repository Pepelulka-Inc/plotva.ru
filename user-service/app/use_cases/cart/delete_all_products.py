from uuid import UUID

from attr import dataclass

from domain.base import IUnitOfWork, BaseUseCase
from domain.entities.cart import Cart
from app.dtos.cart_dtos import ClearCartDTO


@dataclass(slots=True)
class ClearCartUseCase(BaseUseCase):
    uow: IUnitOfWork

    async def __call__(self, dto: ClearCartDTO) -> bool:
        async with self.uow:
            cart = Cart(
                entry_id="dummy",
                user_id=dto.user_id,
                product_id=UUID("00000000-0000-0000-0000-000000000000"),
                quantity=0,
            )

            await self.uow.cart_repo.delete_all_products(cart)
            await self.uow.commit()

            return True
