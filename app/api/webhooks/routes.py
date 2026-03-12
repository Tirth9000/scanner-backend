from fastapi import APIRouter, Request
from app.api.webhooks.schemas import ScannerWebhookRequest, ScannerWebhookResultRequest
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from app.db.base import get_db
from app.db.models import ScanResult

router = APIRouter(prefix='/webhooks')

@router.post("/scan/notification")
def scanner_webhook(request: ScannerWebhookRequest):
    print(f"Received scanner webhook: {request.data}")
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

        scan.results = body  # JSONB auto-handled
        db.commit()

        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print("WEBHOOK ERROR:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")