from uuid import UUID
from typing import Optional

from attr import dataclass

from domain.base import IUnitOfWork, BaseUseCase
from domain.entities.user import User


@dataclass(slots=True)
class DeleteUserByIdUseCase(BaseUseCase):
    uow: IUnitOfWork

    async def __call__(self, user_id: UUID) -> Optional[User]:
        async with self.uow:
            deleted_user = await self.uow.user_repo.get_by_id(user_id)
            if not deleted_user:
                return None

            await self.uow.user_repo.delete_by_id(user_id)
            await self.uow.commit()
            return deleted_user
