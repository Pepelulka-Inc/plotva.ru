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


tracer_manager.init_tracer(service_name="order_service", app=None)

app = FastAPI(lifespan=lifespan)

tracer_manager.tracer.instrument_app(app)
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(app="main:app", loop="asyncio")
