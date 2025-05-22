import os
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool

class DataBase():
    driver = 'postgresql+asyncpg'
    username = os.getenv('db_username')
    password = os.getenv('db_password')
    host = os.getenv('db_host')
    port = os.getenv('db_port')
    name = os.getenv('db_name')

    def __init__(self):
        self._sessionmaker = None
        self.async_engine = None

    def get_db_uri(self):
        return f'{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}'
    
    def create_database(self):
        self.async_engine = create_async_engine(
            self.get_db_uri(),
            poolclass=AsyncAdaptedQueuePool,
            echo=False,
            pool_pre_ping=True,
            pool_size=20,
            max_overflow=10,
            pool_timeout=30
        )
        self._sessionmaker = async_sessionmaker(
            autocommit=False, 
            autoflush=False,
            bind=self.async_engine
        )

    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("База данных не инициализирована")
        
        async with self._sessionmaker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

db = DataBase()

async def get_db_session():
    async for session in db.session():
        yield session

        