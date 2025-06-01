from abc import ABC, abstractmethod
from domain.repositories.user_repository import IUserRepository
from domain.repositories.cart_repository import ICartRepository


class BaseUseCase(ABC):
    async def __call__(self, *args, **kwargs):
        result = await self.execute(*args, **kwargs)
        return result

    @abstractmethod
    def execute(self, *args, **kwargs):
        raise NotImplementedError


class IUnitOfWork(ABC):
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
