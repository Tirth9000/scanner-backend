from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from app.api.webhooks.schemas import ScannerWebhookRequest, ScannerWebhookResultRequest
from app.api.analyzer.controller import calculate_and_store_summary
from app.core.websocket_manager import ws_manager
from sqlalchemy.orm import Session
from app.db.base import get_db

router = APIRouter(prefix='/webhooks')


@router.websocket("/ws/{org_id}")
async def websocket_endpoint(websocket: WebSocket, org_id: str):
    await websocket.accept()
    ws_manager.connect(org_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(org_id)


@router.post("/scan/notification")
async def scanner_webhook(request: ScannerWebhookRequest):
    
    event_map = {
        "subdomain_discovery_completed": "subdomain_discovery",
        "subdomain_filter_completed": "subdomain_filter",
        "subdomain_collection_completed": "data_collection",
    }

    payload = {
        "event": event_map.get(request.event, request.event),
        "org_id": request.scan_id,
        "domain": request.target,
    }
    await ws_manager.send(request.scan_id, payload)
    return {"status": "received"}


@router.post("/scan/result")
async def scan_result_webhook(
    request: ScannerWebhookResultRequest,
    db: Session = Depends(get_db)
):
    
    try:
        target = request.target
        raw_data = request.data
        org_id = request.scan_id

        if not target:
            raise HTTPException(status_code=400, detail="target missing")
        if not org_id:
            raise HTTPException(status_code=400, detail="scan_id missing")

        calculate_and_store_summary(db, org_id, target.strip().lower(), raw_data)

        await ws_manager.send(org_id, {
            "event": "scan_complete",
            "org_id": org_id,
            "domain": target.strip().lower(),
        })

        return {"status": "ok"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
