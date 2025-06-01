from uuid import uuid4
from attr import dataclass

from domain.base import IUnitOfWork
from infrastructure.database.models import User
from app.dtos.user.user_dtos import CreateUserDTO


@dataclass(slots=True)
class CreateUserUseCase:
    uow: IUnitOfWork

    async def __call__(self, dto: CreateUserDTO) -> User:
        async with self.uow:
            user = User(**dto.model_dump(), user_id=uuid4())
            await self.uow.user_repo.create(user)
            await self.uow.commit()
            return user
