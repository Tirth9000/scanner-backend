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

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.pop(scan_id, None)

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

        # Trigger the analyzer to create the ScanSummary exactly when scan is finished
        try:
            from app.api.analyzer.controller import calculate_score
            calculate_score(scan_id, db)
        except Exception as e:
            print(f"Error calculating score for {scan_id} in webhook: {e}")

        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
