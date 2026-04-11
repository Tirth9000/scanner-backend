from fastapi import APIRouter, HTTPException, Depends
from app.api.auth.schemas import (
    RegisterRequest, LoginRequest, InviteRequest,
    RedeemPromoRequest
)
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.api.auth.service import (
    login_user, register, invite_member,
    get_members, redeem_promo_code
)
from app.core.middleware import require_owner, protect
from app.db.models import User, Organization

router = APIRouter(prefix='/auth', tags=['auth'])

@router.post('/register')
def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    email = req.email
    password = req.password
    domain = req.domain

    if not email or not password:
        raise HTTPException(status_code=400, detail="Please fill all the fields")

    try:
        return register(email, password, domain, db)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post('/login')
def login(req: LoginRequest, db: Session = Depends(get_db)):
    email = req.email
    password = req.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="Please fill all the fields")

    try:
        return login_user(email, password, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error"+str(e))


@router.post('/invite')
def invite_members(
    req: InviteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    try:
        return invite_member(current_user, req.email, db)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get('/members')
def list_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_owner)
):
    try:
        return get_members(current_user, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get('/profile')
def get_profile(
    current_user: User = Depends(protect),
    db: Session = Depends(get_db)
):
    org = db.query(Organization).filter(Organization.org_id == current_user.org_id).first()
    return {
        "user_id": current_user.user_id,
        "org_id": current_user.org_id,
        "email": current_user.email,
        "role": current_user.role,
        "domain": org.domain if org else None,
        "max_domains": org.max_domains if org else 0
    }


@router.post('/redeem-promo')
def redeem_promo(
    req: RedeemPromoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(protect)
):
    try:
        return redeem_promo_code(current_user.user_id, req.code, db)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")