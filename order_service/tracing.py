from fastapi import FastAPI
from src.plotva.common.tracing.tracer import Tracer


class TracerManager:
    _instance = None

    def __init__(self):
        self.tracer = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def init_tracer(self, service_name: str, app: FastAPI):
        if self.tracer is not None:
            return self.tracer

        self.tracer = Tracer(service_name=service_name, app=app)
        return self.tracer

    def get_tracer(self):
        if self.tracer is None:
            raise RuntimeError("Tracer not initialized. Call init_tracer() first.")
        return self.tracer


tracer_manager = TracerManager.get_instance()
