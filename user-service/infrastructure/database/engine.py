import os
import asyncio

from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from infrastructure.database.models import Base


load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_async_engine(DB_URL, echo=True)
Session = async_sessionmaker(engine)


async def init_db_and_tables():
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            return
        except Exception as e:
            if attempt < max_attempts - 1:
                print(
                    f"Попытка {attempt + 1} не удалась. Повторная попытка через 2 секунды..."
                )
                await asyncio.sleep(2)
            else:
                raise e
