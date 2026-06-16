from fastapi import FastAPI, HTTPException, Request, Depends
import os, json, logging
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from database import sessionLocal, History
from redis import Redis
from datetime import datetime, timedelta
load_dotenv()
app = FastAPI()
redis_client=Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), password=os.getenv("REDIS_PASSWORD"), decode_responses=True)
def get_db():
    db=sessionLocal()
    try:
        yield db
    finally:
        db.close()

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


        
        
        
        

