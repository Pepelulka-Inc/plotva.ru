from typing import Optional

from attr import dataclass

from user_service.domain.base import IUnitOfWork, BaseUseCase
from user_service.domain.entities.user import User


@dataclass(slots=True)
class GetUserByEmailUseCase(BaseUseCase):
    uow: IUnitOfWork

    async def __call__(self, user_email: str) -> Optional[User]:
        async with self.uow:
            result = await self.uow.user_repo.get_by_email(user_email)
            return result
