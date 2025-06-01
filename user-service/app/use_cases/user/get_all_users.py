from typing import Optional
from attr import dataclass

from domain.base import IUnitOfWork, BaseUseCase
from domain.entities.user import User


@dataclass(slots=True)
class GetAllUsers(BaseUseCase):
    uow: IUnitOfWork

    async def __call__(self, user_email: str) -> Optional[User]:
        async with self.uow:
            result = await self.uow.user_repo.get_all_users()
            return result