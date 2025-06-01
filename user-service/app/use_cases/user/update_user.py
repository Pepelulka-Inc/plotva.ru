from uuid import UUID
from typing import Optional

from attr import dataclass

from domain.base import IUnitOfWork, BaseUseCase
from infrastructure.database.models import UserModel
from app.dtos.user_dtos import UpdateUserDTO


@dataclass(slots=True)
class UpdateUserUseCase(BaseUseCase):
    uow: IUnitOfWork

    async def __call__(self, user_id: UUID, dto: UpdateUserDTO) -> Optional[UserModel]:
        async with self.uow:
            user = await self.uow.user_repo.get_by_id(user_id)
            if not user:
                return None

            updated_user = UserModel(
                user_id=user.user_id,
                name=dto.name if dto.name is not None else user.name,
                surname=dto.surname if dto.surname is not None else user.surname,
                photo_url=dto.photo_url
                if dto.photo_url is not None
                else user.photo_url,
                phone_number=dto.phone_number
                if dto.phone_number is not None
                else user.phone_number,
                email=dto.email if dto.email is not None else user.email,
                hashed_password_base64=user.hashed_password_base64,
            )

            await self.uow.user_repo.update(updated_user)
            await self.uow.commit()

            return updated_user
