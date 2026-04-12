from fastapi import APIRouter, HTTPException, Depends
from app.api.auth.schemas import (
    RegisterRequest, LoginRequest, InviteRequest,
<<<<<<< HEAD
<<<<<<< HEAD
    AcceptInviteRequest, OrgMembersRequest, RedeemPromoRequest
=======
    AcceptInviteRequest, RedeemPromoRequest
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)
=======
    RedeemPromoRequest
>>>>>>> f2b3fc1 (member feature plus some route changes)
)
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.api.auth.service import (
<<<<<<< HEAD
<<<<<<< HEAD
    register_user, login_user, get_user_profile,
    invite_member, accept_invitation,
    get_org_members, redeem_promo_code
=======
    login_user,register
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)
=======
    login_user, register, invite_member,
    get_members, redeem_promo_code
>>>>>>> f2b3fc1 (member feature plus some route changes)
)
from app.core.middleware import require_owner, protect
from app.db.models import User, Organization

router = APIRouter(prefix='/auth', tags=['auth'])

@router.post('/register')
<<<<<<< HEAD
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    email = req.email
    password = req.password
<<<<<<< HEAD
    domain = req.domain
    name = req.name

    if not name or not email or not password or not domain:
        raise HTTPException(status_code=400, detail="Please fill all the fields")

    try:
        # 1. Check if user exists
        existing_user = db.query(User).filter(
            User.email == email.lower()
        ).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        # 2. Create new user
        hashed_password = hashPassword(password)
        user_id = str(uuid.uuid4())

        new_user = User(
            user_id=user_id,
            name=name.strip(),
            email=email.lower(),
            password=hashed_password,
            domain=domain.lower().strip()
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "Registration successful"}

=======
    domain = req.domain.lower().strip()
    org_name = req.org_name.strip()

    if not email or not password or not domain or not org_name:
        raise HTTPException(status_code=400, detail="Please fill all the fields")

    try:
        return register_user(email, password, domain, org_name, db)
>>>>>>> 95ca74d (invite members to org via email, org-wise history, promo code generateion, redeem code, smtp email added plus some minor changes)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post('/login')
def login(req: LoginRequest, db: Session = Depends(get_db)):
=======
def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)
    email = req.email
    password = req.password
    domain = req.domain

    if not email or not password:
        raise HTTPException(status_code=400, detail="Please fill all the fields")

    try:
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
        user = db.query(User).filter(
            User.email == email.lower()
        ).first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if not verifyPassword(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        return {
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "domain": user.domain,
            "token": generateToken(user.user_id)
        }

=======
        return login_user(email, password, db)
>>>>>>> 95ca74d (invite members to org via email, org-wise history, promo code generateion, redeem code, smtp email added plus some minor changes)
=======
        return register(email, password, db)
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)
=======
        return register(email, password, domain, db)
>>>>>>> f2b3fc1 (member feature plus some route changes)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


<<<<<<< HEAD
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
=======
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


<<<<<<< HEAD
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
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)
=======
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
>>>>>>> f2b3fc1 (member feature plus some route changes)
