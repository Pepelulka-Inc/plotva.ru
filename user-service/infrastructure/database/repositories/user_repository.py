from typing import Optional
from uuid import UUID
from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import Session
from domain.entities.user import User
from domain.repositories.user_repository import IUserRepository


class UserRepository(IUserRepository):
    def __init__(self, session: Session):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(User).where(User.user_id == user_id)
        result = await self.session.execute(stmt)
        records = result.scalar_one_or_none()
        return records

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        records = result.scalar_one_or_none()
        return records

    async def create(self, user: User) -> None:
        stmt = insert(User).values(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            photo_url=user.photo_url,
            phone_number=user.phone_number,
            email=user.email,
            hashed_password_base64=user.hashed_password_base64,
        )
        await self.session.execute(stmt)
        self.session.flush()

    async def update(self, user: User) -> None:
        stmt = (
            update(User)
            .where(User.user_id == user.user_id)
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
        stmt = delete(User).where(User.user_id == user_id)
        await self.session.execute(stmt)
