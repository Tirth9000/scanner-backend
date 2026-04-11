from fastapi import APIRouter, HTTPException, Depends
import uuid
import string
import random
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.db.models import PromoCode
from app.core.middleware import require_admin
import os

router = APIRouter(prefix="/admin", tags=["admin"])


def _generate_promo_string(length: int = 10) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))

@router.post("/generate-promo")
def generate_promo(
    db: Session = Depends(get_db)
):
    code_str = _generate_promo_string()

    while db.query(PromoCode).filter(PromoCode.code == code_str).first():
        code_str = _generate_promo_string()

    promo = PromoCode(
        code_id=str(uuid.uuid4()),
        code=code_str,
        is_used=False,
    )

    db.add(promo)
    db.commit()
    db.refresh(promo)

    return {
        "message": "Promo code generated successfully",
        "code": promo.code,
    }


@router.get("/promo-codes")
def list_promo_codes(
    db: Session = Depends(get_db)
):
    codes = db.query(PromoCode).all()

    return [
        {
            "code": c.code,
            "is_used": c.is_used,
            "used_at": c.used_at.isoformat() if c.used_at else None,
        }
        for c in codes
    ]
