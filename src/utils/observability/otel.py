import os
import logging

from opentelemetry import trace
from opentelemetry.metrics import set_meter_provider, get_meter
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

from utils.common import is_enabled

_otel_tracer = trace.get_tracer(__name__)
_otel_collector_endpoint = os.getenv('OTEL_COLLECTOR_ENDPOINT')
_otel_service_name = os.getenv('CWCLOUD_API_NODE_NAME', "cwcloud-api")
_otel_service_version = os.getenv('VERSION', '0.1')

_otel_meter = get_meter(_otel_service_name, version=_otel_service_version)
_otel_resource = Resource.create(attributes={
    ResourceAttributes.SERVICE_NAME: _otel_service_name,
})

_logger_provider = LoggerProvider(_otel_resource)
set_logger_provider(_logger_provider)

def init_otel_tracer():
    trace.set_tracer_provider(TracerProvider(resource=_otel_resource))

    if is_enabled(_otel_collector_endpoint):
        trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=_otel_collector_endpoint, insecure=True)))

def init_otel_metrics():
    if is_enabled(_otel_collector_endpoint):
        otlp_exporter = OTLPMetricExporter(endpoint=_otel_collector_endpoint, insecure=True)
        set_meter_provider(MeterProvider(resource=_otel_resource, metric_readers=[PeriodicExportingMetricReader(otlp_exporter, export_interval_millis=5000)]))

def init_otel_logger():
    if is_enabled(_otel_collector_endpoint):
        otlp_exporter = OTLPLogExporter(endpoint=_otel_collector_endpoint, insecure=True)
        _logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_exporter))
        handler = LoggingHandler(level=logging.NOTSET, logger_provider=_logger_provider)
        logging.getLogger().addHandler(handler)

def get_otel_tracer():
    return _otel_tracer

def get_otel_meter():
    return _otel_meter
