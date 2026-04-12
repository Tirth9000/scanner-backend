from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, Depends, HTTPException
from app.api.webhooks.schemas import ScannerWebhookRequest, ScannerWebhookResultRequest
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.db.base import get_db
from app.db.models import ScanResult

connections = {}

router = APIRouter(prefix='/webhooks')
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()

    connections[user_id] = websocket

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.pop(user_id, None)

@router.post("/scan/notification")
async def scanner_webhook(request: ScannerWebhookRequest):
    payload = {
        "event": request.event,
        "user_id": request.scan_id,
        "target": request.target,
        "status": request.status
    }
    ws = connections.get(request.scan_id)
    if ws:
        await ws.send_json(payload)
    return {"status": "received"}


@router.post("/scan/result")
async def scan_result_webhook(
    request: ScannerWebhookResultRequest,
    db: Session = Depends(get_db)
):
    try:
        target = request.target
        raw_data = request.data
        if not target:
            raise HTTPException(status_code=400, detail="target missing")
        scan = db.query(ScanResult).filter(
            ScanResult.domain == target.strip().lower()
        ).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
<<<<<<< HEAD

        if "status" not in body:
            body["status"] = "completed"
        
        scan.results = body
=======
        scan.results = raw_data
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)
        db.commit()
        return {"status": "ok"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
