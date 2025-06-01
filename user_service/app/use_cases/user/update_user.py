from uuid import UUID
from typing import Optional
import logging

from attr import dataclass

from user_service.domain.base import IUnitOfWork, BaseUseCase
from user_service.infrastructure.database.models import UserModel
from user_service.app.dtos.user_dtos import UpdateUserDTO
from src.plotva.plugins.s3 import CephStorage
from user_service.app.use_cases.user.create_user import parse_base64_image


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class UpdateUserUseCase(BaseUseCase):
    uow: IUnitOfWork
    s3_storage: CephStorage

    async def __call__(self, user_id: UUID, dto: UpdateUserDTO) -> Optional[UserModel]:
        async with self.uow:
            user = await self.uow.user_repo.get_by_id(user_id)
            if not user:
                return None
            if dto.photo_url and dto.photo_url.startswith("data:image"):
                try:
                    image_data = parse_base64_image(dto.photo_url)
                    filename = f"users/{user_id}/photo.jpg"
                    await self.s3_storage.write_file(filename, image_data)
                    dto = dto.model_copy(update={"photo_url": filename})
                except Exception as e:
                    logger.error(f"Ошибка обновления фото: {e}")
                    raise ValueError("Не удалось загрузить новое фото") from e

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
