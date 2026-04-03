from fastapi import APIRouter, HTTPException, Depends
from app.api.auth.schemas import (
    RegisterRequest, LoginRequest, InviteRequest,
    AcceptInviteRequest, OrgMembersRequest, RedeemPromoRequest
)
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.api.auth.service import (
    register_user, login_user, get_user_profile,
    invite_member, accept_invitation,
    get_org_members, redeem_promo_code
)

router = APIRouter(prefix='/api/auth', tags=['auth'])

@router.post('/register')
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    email = req.email
    password = req.password
    domain = req.domain.lower().strip()
    org_name = req.org_name.strip()

    if not email or not password or not domain or not org_name:
        raise HTTPException(status_code=400, detail="Please fill all the fields")

    try:
        return register_user(email, password, domain, org_name, db)
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
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get('/profile/{user_id}')
def getProfile(user_id: str, db: Session = Depends(get_db)):
    try:
        return get_user_profile(user_id, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post('/invite')
def invite_members(req: InviteRequest, db: Session = Depends(get_db)):
    try:
        return invite_member(req.sender_email, req.email, db)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post('/accept-invite')
def accept_invite(req: AcceptInviteRequest, db: Session = Depends(get_db)):
    try:
        return accept_invitation(req.email, req.password, req.token, db)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")




@router.post('/org-members')
def list_org_members(req: OrgMembersRequest, db: Session = Depends(get_db)):
    return get_org_members(req.org_id, db)


@router.post('/redeem-promo')
def redeem_promo(req: RedeemPromoRequest, db: Session = Depends(get_db)):
    try:
        return redeem_promo_code(req.code, req.org_id, db)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")