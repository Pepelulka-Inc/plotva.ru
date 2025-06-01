from uuid import uuid4

from attr import dataclass

from domain.base import IUnitOfWork, BaseUseCase
from infrastructure.database.models import UserModel
from app.dtos.user_dtos import CreateUserDTO


@dataclass(slots=True)
class CreateUserUseCase(BaseUseCase):
    uow: IUnitOfWork

    async def __call__(self, dto: CreateUserDTO) -> UserModel:
        async with self.uow:
            user = UserModel(**dto.model_dump(), user_id=uuid4())
            await self.uow.user_repo.create(user)
            await self.uow.commit()
            return user
