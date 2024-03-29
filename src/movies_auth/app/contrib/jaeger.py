from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from movies_auth.app.settings import app_settings, jaeger_settings


class JaegerManager:
    def __init__(self, app: Flask = None, host: str | None = None, port: int | None = None) -> None:
        self.host = host or "localhost"
        self.port = port or 6831
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        self.configure_tracer()
        FlaskInstrumentor().instrument_app(app)

    def configure_tracer(self) -> None:
        trace.set_tracer_provider(
            TracerProvider(resource=Resource.create({SERVICE_NAME: app_settings.PROJECT_NAME}))
        )
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(
                JaegerExporter(
                    agent_host_name=self.host,
                    agent_port=self.port,
                )
            )
        )

        # Чтобы видеть трейсы в консоли
        # trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


jaeger = JaegerManager(host=jaeger_settings.JAEGER_HOST, port=jaeger_settings.JAEGER_UDP_PORT)
