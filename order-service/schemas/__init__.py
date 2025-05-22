
from sqlalchemy.ext.asyncio import AsyncAttrs, async_session
from sqlalchemy.orm import DeclarativeBase

class BaseModel(AsyncAttrs, DeclarativeBase):

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    @classmethod
    async def insert(
        cls,
        session: async_session,
        *args, **kwargs
    ):
        async with session.begin():
            session.add(
                cls(
                    *args,
                    **kwargs
                )
            )
            await session.commit()
    
    @classmethod
    async def flush_insert(
        cls,
        session: async_session,
        *args, **kwargs
    ):
        """
        метод вызывается только внутри уже открытой сессии
        async with session.begin():
        """
        cls_object = cls(
            **kwargs
        )
        session.add(
            cls_object
        )
        await session.flush()
        return cls_object
    
from schemas.repositories import *