from fastapi import APIRouter, HTTPException, Depends
from app.api.auth.schemas import (
    RegisterRequest, LoginRequest, InviteRequest,
    AcceptInviteRequest, RedeemPromoRequest
)
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.api.auth.service import (
    login_user,register
)

router = APIRouter(prefix='/api/auth', tags=['auth'])

@router.post('/register')
def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    email = req.email
    password = req.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="Please fill all the fields")

    try:
        return register(email, password, db)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        # print(f"Error during registration: {e}")
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


# @router.get('/profile/{user_id}')
# def getProfile(user_id: str, db: Session = Depends(get_db)):
#     try:
#         return get_user_profile(user_id, db)
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal Server Error")


# @router.post('/invite')
# def invite_members(req: InviteRequest, db: Session = Depends(get_db)):
#     try:
#         return invite_member(req.sender_email, req.email, db)
#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="Internal Server Error")


# @router.post('/accept-invite')
# def accept_invite(req: AcceptInviteRequest, db: Session = Depends(get_db)):
#     try:
#         return accept_invitation(req.email, req.password, req.token, db)
#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="Internal Server Error")


# @router.post('/redeem-promo')
# def redeem_promo(req: RedeemPromoRequest, db: Session = Depends(get_db)):
#     try:
#         return redeem_promo_code(req.code, req.org_id, db)
#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="Internal Server Error")