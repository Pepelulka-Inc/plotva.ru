from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from user_service.domain.repositories.user_repository import IUserRepository
from user_service.domain.repositories.cart_repository import ICartRepository


class BaseUseCase(ABC):
    @abstractmethod
    async def __call__(self, *args):
        result = await self.execute(*args)
        return result


class IUnitOfWork(ABC):
    session: AsyncSession
    user_repo: "IUserRepository"
    cart_repo: "ICartRepository"

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, *args):
        raise NotImplementedError

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError
