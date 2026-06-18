from fastapi import FastAPI, HTTPException, Request, Depends, WebSocket, WebSocketException, status, WebSocketDisconnect
from datetime import datetime
import os, json, logging, jwt, uuid
from kafka import KafkaProducer
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from database import sessionLocal, History
from redis import Redis
from datetime import datetime, timedelta
from langchain_groq import ChatGroq
from kafka import KafkaProducer
llm=ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
load_dotenv()
app = FastAPI()
redis_client=Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), password=os.getenv("REDIS_PASSWORD"), decode_responses=True)
BOOTSTRAP_SERVER=""  #TODO: fill it after kafka helm chart installation
producer=KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER, value_serializer= lambda v: json.dumps(v).encode("utf-8"))
class WebSchema(BaseModel):
    text: str
    molecule: Optional[str]=None
    tasks: Optional[List[str]]=None
    region: Optional[str]=None
    timeframe: Optional[int]=5

def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()
active_jobs={}
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("bffservice")
@app.get("/")
def chek():
    return {"status": "Running"}

@app.post("/fileinfo")
async def file_info(request: Request, db:Session=Depends(get_db)):
    try:
        body= await request.json()
        username=body.get("username")
        file_key=body.get("file_key")
        job_id=body.get("job_id")
        db_note=History(user=username, file_key=file_key, job_id=job_id, mode="internal_mode", timestamp=datetime.utcnow())
        db.add(db_note)
        try:
            db.commit()
            logger.info(json.dumps({"event": "event_added", "job_id": job_id}))
        except Exception as e:
            db.rollback()
            logger.error(json.dumps({"event": "db_error", "error": str(e)}))
            raise HTTException(status_code=500, detail=f"error: {str(e)}")
        db.refresh(db_note)
        redis_client.setex(f"job:{job_id}", 86400, json.dumps({"username": username, "file_key": file_key}))
        logger.info(json.dumps({"event": "redis_publish", "job_id": job_id}))
        return {"message": "successfully queued", "job_id": job_id}
    except Exception as e:
        logger.error(json.dumps({"event": "bff_service_error", "error": str(e)}))
        raise HTTPException(status_code=500, detail="error fetching")

@app.websocket("/ws/inp")
async def exin(db:Session=Depends(get_db), websocket: WebSocket):
    token = websocket.headers["Authorization"]
    if not token:
        await websocket.close(code=1008)
        return 
    try:
        schema, token=token.split()
        if schema.lower() != "bearer":
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="invalid token format")
        pay=jwt.decode(token, "supersecret", algorithms=["HS256"])
        username, iss=pay["sub"], pay["iss"]
        if iss != "auth-service":
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="invalid issuer")
        await websocket.accept()
        while True:
            raw = await websocket.receive_json()
            payl = WebSchema.model_validate(raw)
            text = payl.text
            prompt=f"""
              You are the master agent for a pharma research platform.
              Your job:
                  1. Understand user's query
                  2. Decide whether it requires:
                    - external market/clinical/patent/web intelligence
                    - none 
                  3. Select suitable workers
              AVAILABLE WORKERS:
                  - "iqvia"     → market size, growth, competition trends
                  - "exim"      → export/import trends, dependency tables
                  - "patent"    → patent filings, expiry, FTO flags
                  - "clinical"  → clinical trials, sponsors, MoA pipelines
                  - "web"       → guidelines, publications, scientific news
               USER QUERY:
                   {text}
                STRICT RESPONSE FORMAT:
                    Return ONLY a JSON object, no extra text.
                EXAMPLE OUTPUTS:
                    1) For orchestrator:
                            {{
                                "route": "orchestrator",
                                "subtasks": ["iqvia", "clinical", "web"]
                            }}

                    2) For none:
                        {{
                            "route": "none",
                            "subtasks": []
                        }}
            """
            res = llm.invoke(prompt)
            raw_llm = res.content
            job_id=str(uuid.uuid4())
            try:
                data = json.loads(raw_llm)
            except Exception as e:
                data= {"route": "orchestrator", "subtasks": ["iqvia", "clinical", "web"]}
            route=data.get("route")
            if route != "orchestrator":
                await websocket.send_json({"job_id": job_id, "status": "rejected", "message": "query does not require worker agents"})
                continue
            subtasks=data.get("subtasks")
            if not subtasks:
                await websocket.send_json({"job_id": job_id, "status": "rejected", "message": "no workers found"})
                continue
            active_jobs[job_id]=websocket
            redis_client.hset(f"task:{job_id}", mapping={"username": username, "query": text, "status": "running", "iqvia_status": "pending", "exim_status": "pending", "patent_status": "pending", "clinical_status": "pending", "web_status": "pending", "report_status": "pending", "created_at": datetime.utcnow().isoformat()})
            event = {"user_input": text, "job_id": job_id}
            if "iqvia" in subtasks:
                producer.send("iqvia-topic", key=job_id.encode(), value=event)
                producer.flush()
            if "exim" in subtasks:
                producer.send("exim-topic", key=job_id.encode(), value=event)
                producer.flush()
            if "patent" in subtasks:
                producer.send("patent-topic", key=job_id.encode(), value=event)
                producer.flush()
            if "clinical" in subtasks:
                producer.send("clinical-topic", key=job_id.encode(), value=event)
                producer.flush()
            if "web" in subtasks:
                producer.send("web-topic", key=job_id.encode(), value=event)
                producer.flush()
            await websocket.send_json({"job_id": job_id, "status": "queued", "workers": subtasks})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception:
            pass
    finally:
        jobs_rem =[]
        for job_id, ws in active_jobs.items():
            if ws==websocket:
                jobs_rem.append(job_id)
        for job_id in jobs_rem:
            active_jobs.pop(job_id, None)

