from fastapi import FastAPI, HTTPException, Response, Depends
from sqlalchemy.orm import Session
import os, logging, json, boto3
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (OTLPSpanExporter)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("report")
resource = Resource.create({"service.name": "report-service"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)
otlp_exporter = OTLPSpanExporter( endpoint="jaeger.tracing.svc.cluster.local:4317",insecure=True,)
provider.add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)
FastAPIInstrumentor.instrument_app(app)
tracer = trace.get_tracer(__name__)
from datebase import Reports, sessionLocal
def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup():
    logger.info(json.dumps({"event": "report_service_start", "pod": os.getenv("HOSTNAME")}))

@app.get("/")
def chek():
    return {"status": "Running"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)




