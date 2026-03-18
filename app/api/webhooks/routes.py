from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, Depends, HTTPException
from app.api.webhooks.schemas import ScannerWebhookRequest, ScannerWebhookResultRequest
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.db.base import get_db
from app.db.models import ScanRequest,ScanResult

router = APIRouter(prefix='/webhooks')

connections = {}
@router.websocket("/ws/{scan_id}")
async def websocket_endpoint(websocket: WebSocket, scan_id: str):
    await websocket.accept()

    connections[scan_id] = websocket
    print(f"WebSocket connected: {scan_id}")

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.pop(scan_id, None)
        print(f"WebSocket disconnected: {scan_id}")

@router.post("/scan/notification")
async def scanner_webhook(request: ScannerWebhookRequest):
    scan_id = request.scan_id
    payload = {
        "event": request.event,
        "scan_id": request.scan_id,
        "target": request.target,
        "status": request.status
    }
    ws = connections.get(scan_id)
    if ws:
        await ws.send_json(payload)
    return {"status": "received"}


@router.post("/scan/result")
async def scan_result_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        body = await request.json()
        scan_id = body.get("scan_id")

        if not scan_id:
            raise HTTPException(status_code=400, detail="scan_id missing")

        scan = db.query(ScanResult).filter(
            ScanResult.scan_id == scan_id
        ).first()

        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")

        scan.results = body
        db.commit()

        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
