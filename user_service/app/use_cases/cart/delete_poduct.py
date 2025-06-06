from attr import dataclass

from user_service.domain.base import IUnitOfWork, BaseUseCase
from user_service.app.dtos.cart_dtos import RemoveProductFromCartDTO


@dataclass(slots=True)
class RemoveProductFromCartUseCase(BaseUseCase):
    uow: IUnitOfWork

    async def __call__(self, dto: RemoveProductFromCartDTO) -> bool:
        async with self.uow:
            cart = await self.uow.cart_repo.get_by_product_and_user(
                dto.product_id, dto.user_id
            )

            if not cart:
                return False

            await self.uow.cart_repo.delete_product(cart)
            await self.uow.commit()

            return True
