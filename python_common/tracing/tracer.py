from opentelemetry import trace

from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from fastapi import FastAPI


class Tracer:
    def __init__(self, service_name: str, app: FastAPI, otlp_endpoint: str = "http://alloy:4317/v1/traces"):
        resource = Resource.create(attributes={
            SERVICE_NAME: service_name
        })

        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)
        
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)

        span_processor = BatchSpanProcessor(
            span_exporter=otlp_exporter,
            max_export_batch_size=1
        )
        tracer_provider.add_span_processor(span_processor)

        self.opentelemetry_tracer = trace.get_tracer(__name__)

        FastAPIInstrumentor().instrument_app(app)
        RequestsInstrumentor().instrument()