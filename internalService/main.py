from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import  History, sessionLocal
from redis import Redis
import os, json, jwt, boto3, logging
from dotenv import load_dotenv
from utils.extractor import extract, extract_ocr
from metric import TOTAL_ASKS, TOTAL_SUMMARIZERS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from utils.vec_help import build_vector_store
load_dotenv()
app = FastAPI()
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from datetime import datetime, timedelta
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (OTLPSpanExporter)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry import trace
resource = Resource.create({"service.name": "auth-service"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)
otlp_exporter = OTLPSpanExporter( endpoint="jaeger.tracing.svc.cluster.local:4317",insecure=True,)
provider.add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)
FastAPIInstrumentor.instrument_app(app)
tracer = trace.get_tracer(__name__)
redis_client=Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), password=os.getenv("REDIS_PASSWORD"), decode_responses=False)
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("internal")
s3= boto3.client('s3', region_name=os.getenv("S3_REGION"), aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))
bucket=os.getenv("S3_BUCKET_NAME")
def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()

class SumSchema(BaseModel):
    job_id: str

class AskSchema(BaseModel):
    job_id: str
    question: str
llm = ChatGroq(model="llama-3.3-70b-versatile",api_key=os.getenv("GROQ_API_KEY"))
POD_NAME=os.getenv("HOSTNAME")

@app.on_event("startup")
def startup():
    logger.info(json.dumps({"event": "internal_service_start", "pod": POD_NAME}))

@app.get("/")
def chek():
    return {"status": "Running"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/summarize")
def summar(payload: SumSchema, request: Request, db:Session=Depends(get_db)):
    TOTAL_SUMMARIZERS.inc()
    token=request.headers["Authorization"]
    if not token:
        logger.warning(json.dumps({"event": "token_not_found"}))
        raise HTTPException(status_code=401, detail="no token found")
    schema, token=token.split()
    if schema.lower() != "bearer":
        logger.warning(json.dumps({"event": "invalid_token_format"}))
        raise HTTPException(status_code=401, detail="invalid token format")
    pay = jwt.decode(token, "supersecret", algorithms=["HS256"])
    username=pay["sub"]
    job_id=payload.job_id
    key=f"job:{job_id}"
    dt=redis_client.get(key)
    if not dt:
        logger.warning(json.dumps({"event": "empty_cache", "key": job_id}))
        raise HTTPException(status_code=404, detail="no data found, please upload again")
    data=json.loads(dt)
    if data["username"] != username:
        logger.warning(json.dumps({"event": "bypass_attempt", "username": username}))
        raise HTTPException(status_code=401, detail="nah broski, this file ain't yours")
    file_key=data["file_key"]
    resp=s3.get_object(Bucket=bucket, Key=file_key)
    if not resp:
        logger.warning(json.dumps({"event": "file_not_found", "key": file_key}))
        raise HTTPException(status_code=404, detail="no file found")
    file_bytes=resp["Body"].read()
    text=extract(file_bytes)
    if len(text.strip()) < 100:
        logger.info(json.dumps({"event": "ocr_invoked"}))
        text=extract_ocr(file_bytes)
    vector_store = build_vector_store(text,job_id)
    prompt = ChatPromptTemplate.from_template(
    """
    Create a professional executive summary.
    Include:
    - Main purpose
    - Key findings
    - Risks
    - Action items
    - Important conclusions
    DOCUMENT:
    {text}
    """
)
    chain = prompt | llm
    summary = chain.invoke({ "text": text[:15000]})
    summary_text = summary.content
    his=db.query(History).filter(History.job_id==job_id, History.user==username).first()
    if not his:
        logger.warning(json.dumps({"event": "no_record_found"}))
        raise HTTPException(status_code=404, detail="no related history found")
    his.content=summary_text
    try:
        db.commit()
        logger.info(json.dumps({"event": "db_updated"}))
    except Exception as e:
        db.rollback()
        logger.error(json.dumps({"error": "db_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail=f"error: {str(e)}")
    return {"job_id": job_id,"summary": summary_text}

@app.post("/ask")
def ask_ai(payload: AskSchema, request: Request):
    TOTAL_ASKS.inc()
    token=request.headers["Authorization"]
    if not token:
        logger.warning(json.dumps({"event": "token_not_found"}))
        raise HTTPException(status_code=401, detail="no token found")
    schema, token=token.split()
    if schema.lower() != "bearer":
        logger.warning(json.dumps({"event": "invalid_token_format"}))
        raise HTTPException(status_code=401, detail="invalid token format")
    pay=jwt.decode(token, "supersecret", algorithms=["HS256"])
    username=pay["sub"]
    embedding_model = HuggingFaceEmbeddings( model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.load_local(f"vector_indexes/{payload.job_id}",embedding_model,allow_dangerous_deserialization=True)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    docs = retriever.invoke(payload.question)
    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )
    qa_prompt = ChatPromptTemplate.from_template(
        """
        Answer ONLY using the context.
        If answer does not exist
        say:
        "Not found in document."
        CONTEXT:
        {context}

        QUESTION:
        {question}
        """
    )
    chain = qa_prompt | llm
    response = chain.invoke({"context": context,"question": payload.question})
    return {"question": payload.question,"answer": response.content}











