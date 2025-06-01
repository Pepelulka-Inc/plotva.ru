from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from domain.base import IUnitOfWork
from infrastructure.database.repositories.user_repository import UserRepository
from infrastructure.database.repositories.cart_repository import CartRepository


class UnitOfWork(IUnitOfWork):
    def __init__(self, engine):
        self.engine = engine
        self.session: AsyncSession = None
        self.user_repo = None
        self.cart_repo = None

    async def __aenter__(self):
        async_session = async_sessionmaker(self.engine, expire_on_commit=False)
        self.session = async_session()
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