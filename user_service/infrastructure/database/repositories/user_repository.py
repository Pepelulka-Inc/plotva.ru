from typing import Optional
from uuid import UUID

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.domain.entities.user import User
from user_service.domain.repositories.user_repository import IUserRepository
from user_service.infrastructure.database.models import UserModel


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def delete_by_id(self, user_id: UUID):
        stmt = delete(UserModel).where(UserModel.user_id == user_id)
        result = await self.session.execute(stmt)
        if result.rowcount == 0:
            raise ValueError(f"User with ID {user_id} not found")

    async def get_all_users(self):
        stmt = select(UserModel)
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        return records

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.user_id == user_id)
        result = await self.session.execute(stmt)
        records = result.scalar_one_or_none()
        return records

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        records = result.scalar_one_or_none()
        return records

    async def create(self, user: UserModel) -> None:
        stmt = insert(UserModel).values(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            photo_url=user.photo_url,
            phone_number=user.phone_number,
            email=user.email,
            hashed_password_base64=user.hashed_password_base64,
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def update(self, user: User) -> None:
        stmt = (
            update(UserModel)
            .where(UserModel.user_id == user.user_id)
            .values(
                name=user.name,
                surname=user.surname,
                photo_url=user.photo_url,
                phone_number=user.phone_number,
                email=user.email,
                hashed_password_base64=user.hashed_password_base64,
            )
        )
        await self.session.execute(stmt)

    async def delete(self, user_id: UUID) -> None:
        stmt = delete(UserModel).where(UserModel.user_id == user_id)
        await self.session.execute(stmt)
