from fastapi import APIRouter, Depends
from app.api.scanner.service import create_scan_task_to_queue
from app.api.scanner.schemas import RequestScanTask
from app.core.redis_queue import RedisClient
from sqlalchemy.orm import Session
from app.db.base import get_db
import uuid, json
import redis.asyncio as redis

redis_client = RedisClient()

router = APIRouter(prefix='/api/scanner', tags=["scanner"])

@router.post("/register-scan-task")
async def register_scan_task(request: RequestScanTask,db: Session = Depends(get_db)):
    return await create_scan_task_to_queue(db, request)

@router.get("/scanlist")
async def get_scan_list():
    data = await redis_client.redis.lrange("scan_queue", 0, -1)
    return  [json.loads(item) for item in data]

@router.get("/clear")
async def clear_scan_queue(): 
    await redis_client.redis.delete("scan_queue")
    return {"message": "Scan queue cleared"}