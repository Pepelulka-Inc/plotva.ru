from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List

from domain.entities.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def delete_by_id(self, user_id: UUID):
        raise NotImplementedError

    @abstractmethod
    async def get_all_users(self) -> List[Optional[User]]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: UUID) -> None:
        raise NotImplementedError
