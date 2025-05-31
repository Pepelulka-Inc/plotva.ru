from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from database.connection import db
from routing.api import api_router

@asynccontextmanager
async def lifespan(app:FastAPI):
    db.create_database()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

if __name__ == '__main__':
    uvicorn.run(app='main:app',loop='asyncio')