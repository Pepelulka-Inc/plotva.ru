# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from order_service.database.connection import db
from order_service.routing.api import api_router
from order_service.tracing import tracer_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.create_database()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

tracer_manager.init_tracer(service_name="order_service", app=app)

if __name__ == "__main__":
    uvicorn.run(app="main:app", loop="asyncio")
