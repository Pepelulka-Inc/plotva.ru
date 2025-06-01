from uuid import UUID
from typing import Optional

from attr import dataclass

from domain.base import IUnitOfWork, BaseUseCase
from domain.entities.cart import Cart


@dataclass(slots=True)
class GetUserCartByIdUseCase(BaseUseCase):
    uow: IUnitOfWork

    async def __call__(self, user_id: UUID) -> Optional[Cart]:
        async with self.uow:
            result = await self.uow.cart_repo.get_cart_items(user_id)
            return result
