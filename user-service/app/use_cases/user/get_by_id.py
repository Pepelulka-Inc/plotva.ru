from uuid import UUID
from typing import Optional
from attr import dataclass

from domain.base import IUnitOfWork, BaseUseCase
from domain.entities.user import User


@dataclass(slots=True)
class GetUserById(BaseUseCase):
    uow: IUnitOfWork

    async def __call__(self, user_id: UUID) -> Optional[User]:
        async with self.uow:
            result = await self.uow.user_repo.get_by_id(user_id)
            return result