from fastapi import FastAPI, HTTPException, Depends, Response, Request
from database import Users, sessionLocal, RefreshTokens
from sqlalchemy.orm import Session
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from schema import SignupSchema
from utils.otp_gen import otp_generator
from utils.em_send import email_send
from redis import Redis
import hashlib, logging, os
from metric import USERS_CREATED, EMAILS_SENT, USERS_LOGIN, TOTAL_USERS, TOTAL_REFRESH_TOKENS
from dotenv import load_dotenv
load_dotenv()
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt, json
from datetime import datetime, timedelta
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (OTLPSpanExporter)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry import trace
ph = PasswordHasher()
app= FastAPI()
redis_client = Redis(
    host=os.getenv("REDIS_URL"),
    port=int(os.getenv("REDIS_PORT")),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True,
)
resource = Resource.create({"service.name": "auth-service"})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)
otlp_exporter = OTLPSpanExporter( endpoint="jaeger.tracing.svc.cluster.local:4317",insecure=True,)
provider.add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)
FastAPIInstrumentor.instrument_app(app)
tracer = trace.get_tracer(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("auth")
POD_NAME=os.getenv("POD_NAME")

def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup():
    logger.info(json.dumps({"event": "auth_service_start", "pod": POD_NAME}))

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def chek():
    return {"status": "Running"}

@app.post("/create")
def cret(payload: SignupSchema, db:Session=Depends(get_db)):
    email, username=payload.email, payload.username
    password=ph.hash(payload.password)
    db_note=Users(email=email, username=username, password=password, isactive=False)
    db.add(db_note)
    try:
        db.commit()
        logger.info(json.dumps({"event": "user_created", "id": db_note.id}))
    except Exception as e:
        db.rollback()
        logger.error(json.dumps({"event": "db_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail="database error")
    db.refresh(db_note)
    USERS_CREATED.inc()
    otp= otp_generator()
    hashed= hashlib.sha256(otp.encode()).hexdigest()
    redis_client.setex(f"otp:{email}", 600, hashed)
    logger.info(json.dumps({"event": "otp_set", "otp_hash": hashed}))
    email_send(email, otp)
    EMAILS_SENT.inc()
    logger.info(json.dumps({"event": "email_sent", "email": email}))
    return {"message": "Pls verify your email"}

@app.post("/verify")
def veri(payload: EmailSchema, db:Session=Depends(get_db)):
    ot, email=payload.ot, payload.email
    key= f"otp:{email}"
    stored=redis_client.get(key)
    if not stored:
        logger.warning(json.dumps({"event": "otp_not_found", "redis_key": key}))
        return {"message": "OTP expired or invalid"}
    input_hash=hashlib.sha256(ot.encode()).hexdigest()
    if input_hash != stored:
        logger.error(json.dumps({"event": "otp_mismatch", "email": email}))
        return {"message": "OTP does not match"}
    user=db.query(Users).filter(Users.email==email).first()
    user.isactive=True
    try:
        db.commit()
        logger.info(json.dumps({"event": "user_made_active", "username": user.username}))
    except Exception as e:
        db.rollback()
        logger.error(json.dumps({"event": "db_error", "error": str(e)}))
    db.refresh(user)
    redis_client.delete(key)
    return {"message": "OTP verified successfully, proceed to login"}

@app.post("/login")
def logi(payload:LoginSchema,response: Response, db:Session=Depends(get_db)):
    username, password=payload.username, payload.password
    user=db.query(Users).filter(Users.username==username).first()
    if user is None:
        logger.error(json.dumps({"event": "user_not_found", "username": username}))
        raise HTTPException(status_code=404, detail="user not found")
    if user.isactive==True:
        passw=user.password
        try:
            ph.verify(passw, password)
            pay= {"iss": "auth-service", "sub": username, "exp": datetime.utcnow()+timedelta(minutes=15)}
            token=jwt.encode(pay, "supersecret", algorithm="HS256")
            pay1= {"iss": "auth-service", "sub": username, "exp": datetime.utcnow()+timedelta(days=7)}
            refresh_token=jwt.encode(pay1, "supersecret", algorithm="HS256")
            response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="lax", max_age=604800)
            db_no=RefreshTokens(user_username=user.username, token_hash= hashlib.sha256(refresh_token.encode()).hexdigest(), expires_at=datetime.utcnow()+timedelta(days=7), revoked=False)
            db.add(db_no)
            try:
                db.commit()
                logger.info(json.dumps({"event":"refresh_token_added"}))
            except Exception as e:
                db.rollback()
                logger.error(json.dumps({"event": "db_error", "error": str(e)}))
                raise HTTPException(status_code=500, detail="database error")
            db.refresh(db_no)
            USERS_LOGIN.inc()
            TOTAL_REFRESH_TOKENS.inc()
            logger.info(json.dumps({"event": "login_success", "username": username}))
            return {"message": "logged in", "token": token}
        except VerifyMismatchError:
            logger.error(json.dumps({"event": "password_mismatch", "email": user.email, "username": username}))
            raise HTTPException(status_code=401, detail="passwords do not match")
    else:
        logger.error(json.dumps({"event": "inactive_user", "email": user.email}))
        raise HTTPException(status_code=401, detail="verify your email")

@app.post("/refresh")
def refr(request: Request, db:Session=Depends(get_db)):
    refresh_token=request.cookies.get("refresh_token")
    if not refresh_token:
        logger.warning(json.dumps({"event": "missing_token"}))
        raise HTTPException(status_code=401, detail="Missing refresh token")
    payload=jwt.decode(refresh_token, "supersecret", algorithm="HS256")
    username=payload["sub"]
    tok_hash= hashlib.sha256(refresh_token.encode()).hexdigest()
    refr= db.query(RefreshTokens).filter(RefreshTokens.token_hash==tok_hash).first()
    if refr is None:
        logger.warning(json.dumps({"event":"refresh_bypass_attempt", "username": username}))
        raise HTTPException(status_code=404, detail="no corresponding username found")
    if refr.revoked == True:
        logger.warning(json.dumps({"event": "refresh_bypass_attempt", "username": username}))
        raise HTTPException(status_code=401, detail="refresh token revoked")
    if refr.expires_at < datetime.utcnow():
        logger.warning(json.dumps({"event": "refresh_token_expired"}))
        raise HTTPException(status_code=401, detail="refresh token expired")
    pay= {"iss": "auth-service", "sub": username, "exp":datetime.utcnow() + timedelta(minutes=15) }
    token=jwt.encode(pay,"supersecret", algorithm="HS256")
    return {"session_token": token}

@app.delete("/auth/delete")
def dele(request: Request, db: Session=Depends(get_db)):
    token=request.headers["Authorization"]
    schema, token = token.split()
    if schema.lower() != "bearer":
        logger.warning(json.dumps({"event": "invalid_token"}))
        raise HTTPException(status_code=401, detail="invalid token format")
    pay = jwt.decode(token, "supersecret", algorithm="HS256")
    username=pay["sub"]
    user=db.query(Users).filter(Users.username==username).first()
    db.delete(user)
    try:
        db.commit()
        logger.info(json.dumps({"event": "user_delete", "username": username}))
    except Exception as e:
        db.rollback()
        logger.error(json.dumps({"event": "db_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail="database error")
    TOTAL_REFRESH_TOKENS.dec()
    USERS_LOGIN.dec()
    return {"message": "user deleted"}

@app.post("/logout")
def logou(request: Request, db:Session=Depends(get_db), response: Response):
    refresh_token=request.cookies.get("refresh_token")
    hash_token=hashlib.sha256(refresh_token.encode()).hexdigest()
    refr = db.query(RefreshTokens).filter(RefreshTokens.token_hash==hash_token).first()
    if not refr:
        logger.warning(json.dumps({"event": "refresh_token_not_found"}))
        raise HTTPException(status_code=404, detail="no refresh token found")
    refr.revoked=True
    try:
        db.commit()
        logger.info(json.dumps({"event": "refresh_token_revoked"}))
    except Exception as e:
        db.rollback()
        logger.error(json.dumps({"event": "db_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail="database error")
    response.delete_cookie("refresh_token")
    TOTAL_REFRESH_TOKENS.dec()
    USERS_LOGIN.dec()
    return {"message": "successfully logged out"}

@app.get("/admin/users")
def get_users(db: Session=Depends(get_db)):
    users=db.query(Users).count()
    TOTAL_USERS.set(users)
    return {"message": f"total number of users: {users}"}





