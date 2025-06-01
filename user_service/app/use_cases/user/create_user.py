import base64
from uuid import uuid4
import logging

from attr import dataclass

from user_service.domain.base import IUnitOfWork, BaseUseCase
from user_service.infrastructure.database.models import UserModel
from user_service.app.dtos.user_dtos import CreateUserDTO
from src.plotva.plugins.s3 import CephStorage

logger = logging.getLogger(__name__)


def parse_base64_image(data_uri: str) -> bytes:
    if not data_uri.startswith("data:image"):
        raise ValueError("Неверный формат изображения")

    try:
        header, encoded = data_uri.split(",", 1)
        return base64.b64decode(encoded)
    except Exception as e:
        raise ValueError(f"Ошибка парсинга base64: {e}")


@dataclass(slots=True)
class CreateUserUseCase(BaseUseCase):
    uow: IUnitOfWork
    s3_storage: CephStorage

    async def __call__(self, dto: CreateUserDTO) -> UserModel:
        async with self.uow:
            user = UserModel(**dto.model_dump(), user_id=uuid4())
            if user.photo_url and user.photo_url.startswith("data:image"):
                try:
                    image_data = parse_base64_image(user.photo_url)
                    filename = f"users/{user.user_id}/photo.jpg"
                    await self.s3_storage.write_file(filename, image_data)
                    user = UserModel(
                        user_id=user.user_id,
                        name=user.name,
                        surname=user.surname,
                        email=user.email,
                        hashed_password_base64=user.hashed_password_base64,
                        photo_url=filename,
                        phone_number=user.phone_number,
                    )
                except Exception as e:
                    logger.error(f"Ошибка загрузки фото: {e}")
                    raise ValueError("Не удалось загрузить фото") from e
            await self.uow.user_repo.create(user)
            await self.uow.commit()
            return user
