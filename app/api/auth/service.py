import bcrypt
import uuid
import secrets
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import os
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.db.models import User, Invitation, PromoCode
from app.utils.email import send_invite_email

JWT_SECRET = os.getenv('JWT_SECRET')

def hashPassword(password: str) -> str:
    # hash password using bycrypt
    salt = bcrypt.gensalt(10)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verifyPassword(entered_password: str, stored_hash: str) -> bool:
    # Verify entered password against the stored hash
    return bcrypt.checkpw(entered_password.encode('utf-8'), stored_hash.encode('utf-8'))


# generate token for user
def generateToken(user_id: str):
    payload = {
        "user_id" : user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }

    if not JWT_SECRET:
        raise ValueError("JWT_SECRET not set")
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_token(token: str):
    if not JWT_SECRET:
        raise ValueError("JWT_SECRET not set")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
def register(email: str, password: str, db: Session):
    existing_user = db.query(User).filter(
        User.email == email.lower()
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    user_id = str(uuid.uuid4())
    hashed_password = hashPassword(password)

    new_user = User(
        user_id=user_id,
        email=email.lower(),
        password=hashed_password,
        role="owner",
    )
    db.add(new_user)
    db.commit()

    return {"message": "Registration successful"}


def login_user(email: str, password: str, db: Session):
    user = db.query(User).filter(
        User.email == email.lower()
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verifyPassword(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = generateToken(user.user_id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role
        }
    }


# def get_user_profile(user_id: str, db: Session):
#     user = db.query(User).filter(User.user_id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     org = db.query(Organization).filter(
#         Organization.org_id == user.organization_id
#     ).first()

#     return {
#         "user_id": user.user_id,
#         "email": user.email,
#         "role": user.role
#     }


# def invite_member(sender_email: str, invite_email: str, db: Session):
#     sender_user = db.query(User).filter(User.email == sender_email.lower()).first()
#     if not sender_user:
#         raise HTTPException(status_code=404, detail="Sender user not found")

#     org_id = sender_user.organization_id
#     user_id = sender_user.user_id

#     existing_invites = db.query(Invitation).filter(
#         Invitation.org_id == org_id,
#         Invitation.status.in_(["pending", "accepted"])
#     ).count()

#     if existing_invites >= 5:
#         raise HTTPException(
#             status_code=400,
#             detail="You have already reached the maximum limit of 5 invited members."
#         )

#     email_lower = invite_email.lower()
#     if not email_lower:
#         raise HTTPException(status_code=400, detail="Please provide an email")

#     org = db.query(Organization).filter(Organization.org_id == org_id).first()

#     existing_user = db.query(User).filter(User.email == email_lower).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail=f"{email_lower} is already a registered user")

#     existing_invite = db.query(Invitation).filter(
#         Invitation.org_id == org_id,
#         Invitation.email == email_lower,
#         Invitation.status == "pending"
#     ).first()
#     if existing_invite:
#         raise HTTPException(status_code=400, detail=f"{email_lower} already has a pending invitation")

#     invite_token = secrets.token_urlsafe(32)
#     invitation = Invitation(
#         invite_id=str(uuid.uuid4()),
#         org_id=org_id,
#         email=email_lower,
#         token=invite_token,
#         status="pending",
#         invited_by=user_id,
#         expires_at=datetime.now(timezone.utc) + timedelta(days=1),
#     )
#     db.add(invitation)

#     # Send email
#     try:
#         send_invite_email(
#             to_email=email_lower,
#             invite_token=invite_token,
#             org_name=org.name,
#             org_id=org_id,
#         )
#     except Exception as email_err:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Failed to send email to {email_lower}: {str(email_err)}")

#     db.commit()

#     return {
#         "message": "Invitation sent successfully",
#         "sent": email_lower
#     }


# def accept_invitation(email: str, password: str, token: str, db: Session):
#     # 1. Find and validate invitation
#     invitation = db.query(Invitation).filter(
#         Invitation.token == token,
#         Invitation.status == "pending"
#     ).first()

#     if not invitation:
#         raise HTTPException(status_code=400, detail="Invalid or expired invitation")

#     # 2. Check expiry (1-day expiry)
#     if datetime.now(timezone.utc) > invitation.expires_at.replace(tzinfo=timezone.utc):
#         invitation.status = "expired"
#         db.commit()
#         raise HTTPException(status_code=400, detail="This invitation has expired")

#     # 3. Check email matches
#     if email.lower() != invitation.email:
#         raise HTTPException(status_code=400, detail="Email does not match the invitation")

#     # 4. Check if user already exists
#     existing_user = db.query(User).filter(
#         User.email == email.lower()
#     ).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="User already exists")

#     # 5. Get organization details
#     org = db.query(Organization).filter(
#         Organization.org_id == invitation.org_id
#     ).first()
#     if not org:
#         raise HTTPException(status_code=400, detail="Organization not found")

#     # 6. Create user as member
#     user_id = str(uuid.uuid4())
#     hashed_password = hashPassword(password)

#     new_user = User(
#         user_id=user_id,
#         email=email.lower(),
#         password=hashed_password,
#         domain=org.domain,
#         role="member",
#         organization_id=invitation.org_id,
#     )
#     db.add(new_user)

#     # 7. Mark invitation as accepted
#     invitation.status = "accepted"
#     db.commit()
#     db.refresh(new_user)

#     return {
#         "message": "Account created successfully",
#         "user_id": new_user.user_id,
#         "email": new_user.email,
#         "role": new_user.role,
#         "organization_id": new_user.organization_id,
#         "token": generateToken(new_user.user_id)
#     }


# def get_org_members(org_id: str, db: Session):
#     members = db.query(User).filter(
#         User.organization_id == org_id
#     ).all()

#     # Also fetch invitations for this org
#     invitations = db.query(Invitation).filter(
#         Invitation.org_id == org_id
#     ).all()

#     now = datetime.now(timezone.utc)
#     for inv in invitations:
#         if inv.status == "pending" and now > inv.expires_at.replace(tzinfo=timezone.utc):
#             inv.status = "expired"
#     db.commit()

#     # Build a lookup of invitation by email
#     inv_by_email = {inv.email: inv for inv in invitations}

#     result = []

#     # Add members (with their invitation data if it exists)
#     for m in members:
#         inv = inv_by_email.pop(m.email, None)
#         result.append({
#             "user_id": m.user_id,
#             "role": m.role,
#             "email": m.email,
#             "invite_id": inv.invite_id if inv else None,
#             "inv_status": inv.status if inv else None,
#             "inv_expires_at": inv.expires_at.isoformat() if inv and inv.expires_at else None,
#         })

#     # Add remaining invitations (pending/expired, not yet a user)
#     for inv in inv_by_email.values():
#         result.append({
#             "user_id": None,
#             "role": None,
#             "email": inv.email,
#             "invite_id": inv.invite_id,
#             "inv_status": inv.status,
#             "inv_expires_at": inv.expires_at.isoformat() if inv.expires_at else None,
#         })

#     return result


# def redeem_promo_code(code: str, org_id: str, db: Session):
#     # 1. Find the promo code
#     promo = db.query(PromoCode).filter(
#         PromoCode.code == code.upper().strip(),
#         PromoCode.is_used == False
#     ).first()

#     if not promo:
#         raise HTTPException(status_code=400, detail="Invalid or already used promo code")

#     # 2. Find the organization
#     org = db.query(Organization).filter(
#         Organization.org_id == org_id
#     ).first()

#     if not org:
#         raise HTTPException(status_code=404, detail="Organization not found")

#     # 3. Mark promo as used and map to org
#     promo.is_used = True
#     promo.used_by_org = org_id
#     promo.used_at = func.now()

#     # 4. Increment org's max_domains
#     org.max_domains = org.max_domains + 1
#     db.commit()

#     return {
#         "message": "Promo code redeemed successfully",
#         "max_domains": org.max_domains,
#     }