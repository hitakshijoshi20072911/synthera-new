from fastapi import FastAPI, HTTPException, Depends 
from pydantic import BaseModel
from agents.graph import app
import traceback
from auth import CustomAuth, get_current_user
from fastapi.middleware.cors import CORSMiddleware
from tasks.notification_tasks import send_email
from redis import Redis 
import hashlib
import os
import json
from dotenv import load_dotenv
from database import create_db_and_tables, ChatHistory, User, SessionDep, get_session
load_dotenv()
import boto3

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("COGNITO_REGION")
)
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
redis_client = Redis(
    host=os.getenv("REDIS_URL"),
    port=int(os.getenv("REDIS_PORT")),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

class UserInput(BaseModel):
    user_input: str
fast_app = FastAPI()
@fast_app.on_event("startup")
def on_startup():
    create_db_and_tables()
@fast_app.post("/agent-run")
async def run_agent(payload: UserInput, user=Depends(get_current_user), session:SessionDep= None):
    try:
        content_hash = hashlib.sha256(f"{user['sub']}::{payload.user_input}".encode()).hexdigest()
        cached = redis_client.get(content_hash)
        if cached:
            print("CACHE HIT: ", content_hash)
            cached_json = json.loads(cached)
            new_url = s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": S3_BUCKET_NAME,
                    "Key": cached_json["pdf_s3_key"],
                },
                ExpiresIn=3600
            )
            cached_json["pdf_url"] = new_url
            return {"status": "success", "data" : cached_json}
        print("CACHE MISS: ", content_hash)
        db_user = session.get(User, user["email"])
        if not db_user:
            session.add(User(email=user["email"]))
            session.commit()
        result = app.invoke({"user_input": payload.user_input, "user_email" : user["email"] , "user_id" : user["sub"] })
        send_email.delay(
            to_email=user["email"],
            subject="Your Synthera Intelligence Report",
            body=f"Your report is ready (Note: This link expires in 1 hour).\nDownload here:\n{result['pdf_url']}"
        )
        redis_client.set(content_hash, json.dumps(result), ex=86400)
        history = ChatHistory(user_email=user["email"], file_key=result["pdf_s3_key"], data=result, sources_links=[])
        return {"status": "success", "data": result}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(e)}"
        )

fast_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

