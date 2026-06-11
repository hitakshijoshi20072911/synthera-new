from fastapi import FastAPI, HTTPException, Depends, Request, Response
from database import Files, sessionLocal
from sqlalchemy.orm import Session
import jwt, uuid,os, boto3, logging, json
from datetime import datetime
from dotenv import load_dotenv
from schema import UploadSchema
from metric import FILE_UPLOADED, TOTAL_FILES
from datetime import datetime, timedelta
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (OTLPSpanExporter)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import requests
RequestsInstrumentor().instrument()
from opentelemetry import trace
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
load_dotenv()
s3= boto3.client('s3', region_name=os.getenv("S3_REGION"), aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
bucket_name=os.getenv("S3_BUCKET_NAME")
app =FastAPI()
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("upload")
resource = Resource.create({"service.name": "upload-service"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)
otlp_exporter = OTLPSpanExporter( endpoint="jaeger.tracing.svc.cluster.local:4317",insecure=True,)
provider.add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)
FastAPIInstrumentor.instrument_app(app)
tracer = trace.get_tracer(__name__)
POD_NAME=os.getenv("POD_NAME")

def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def chek():
    return {"status": "Running"}

@app.on_event("startup")
def startup():
    logger.info(json.dumps({"event": "upload_service_start", "pod": POD_NAME}))

@app.post("/upload")
def uplod(payload: UploadSchema,request: Request,  db:Session=Depends(get_db)):
    TOTAL_FILES.set(db.query(Files).count())
    token=request.headers["Authorization"]
    schema, token= token.split()
    if schema.lower() != "bearer":
        logger.warning(json.dumps({"event": "invalid_token_format"}))
        raise HTTPException(status_code=401, detail="invalid token format")
    pay=jwt.decode(token, "supersecret", algorithm="HS256")
    username=pay["sub"]
    file_id=str(uuid.uuid4())
    key=f"docs/{file_id}-{username}-{payload.file_name}"
    pres=s3.generate_presigned_url(
        ClientMethod = 'put_object',
        Params = {
            'Bucket': bucket_name,
            "Key" : key,
            "ContentType": payload.content_type
        },
        ExpiresIn = 600
    )
    logger.info(json.dumps({"event": "presigned_url_gen", "pres": pres}))
    db_note=Files(user=username, file_key=key, timestamp=datetime.utcnow())
    db.add(db_note)
    try:
        db.commit()
        logger.info(json.dumps({"event": "file_added_to_db"}))
    except Exception as e:
        db.rollback()
        logger.error(json.dumps({"event": "db_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail="database error")
    db.refresh(db_note)
    FILE_UPLOADED.inc()
    try:
        resp=requests.post("http://bff-service/fileinfo", json={"username": username, "file_key": key}, timeout=5)
        resp.raise_for_status()
    except Exception as e:
        logger.error(json.dumps({"event": "bff_service_error", "error": str(e)}))
    return {"presigned_url": pres, "file_key": key}

@app.post("/getfiles")
def getfi(request: Request, db:Session=Depends(get_db)):
    token= request.headers["Authorization"]
    schema, token=token.split()
    if schema.lower() != "bearer":
        logger.warning(json.dumps({"event": "invalid_token_format"}))
        raise HTTPException(status_code=401, detail="invalid token format")
    pay=jwt.decode(token, "supersecret", algorithm="HS256")
    username=pay["sub"]
    files= db.query(Files).filter(Files.user==username).all()
    if not files:
        logger.error(json.dumps({"event": "no_files", "username": username}))
        raise HTTPException(status_code=404, detail="no file found")
    res=[]
    for file in files:
        file_key= file.file_key
        pres=s3.generate_presigned_url(ClientMethod = 'get_object',Params = {'Bucket': bucket_name,"Key" : file_key})
        res.append({"file_key": file_key, "pres": pres, "timestamp": file.timestamp})
    return {"files": res}

@app.post("/deletefiles/{file_key}")
def delfi(request: Request, db:Session=Depends(get_db), file_key: str):
    token=request.headers["Authorization"]
    schema, token = token.split()
    if schema.lower() != "bearer":
        logger.warning(json.dumps({"event": "invalid_token_format"}))
        raise HTTPException(status_code=401, detail="invalid token format")
    pay=jwt.decode(token, "supersecret", algorithm="HS256")
    username=pay["sub"]
    file=db.query(Files).filter(Files.user==username, Files.file_key==file_key).first()
    if not file:
        logger.error(json.dumps({"event": "file_not_found", "username": username, "file_key": file_key}))
        raise HTTPException(status_code=404, detail="no file found")
    s3.delete_object(Bucket=bucket_name, Key=file.file_key)
    db.delete(file)
    try:
        db.commit()
        logger.info(json.dumps({"event": "file_deleted", "file_key": file_key, "username": username}))
    except Exception as e:
        db.rollback()
        logger.error(json.dumps({"event": "db_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail="database error")
    TOTAL_FILES.dec()
    return {"message": "file deleted successfully"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

