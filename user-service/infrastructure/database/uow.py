from sqlalchemy.ext.asyncio import AsyncSession
from domain.base import IUnitOfWork
from infrastructure.database.repositories.user_repository import UserRepository
from infrastructure.database.repositories.cart_repository import CartRepository


class UnitOfWork(IUnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session: AsyncSession = None
        self.user_repo = None
        self.cart_repo = None

    async def __aenter__(self):
        self.session = self.session_factory()
        self.user_repo = UserRepository(self.session)
        self.cart_repo = CartRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
