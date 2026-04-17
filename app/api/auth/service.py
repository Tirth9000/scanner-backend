import bcrypt
import uuid
import secrets
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import os
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from app.db.models import User, Organization, Invitation, PromoCode, PasswordResetOTP, Blacklist
from app.utils.email import send_invite_email, send_password_reset_otp_email

JWT_SECRET = os.getenv('JWT_SECRET')
OTP_EXPIRY_MINUTES = 10

def hashPassword(password: str) -> str:
    salt = bcrypt.gensalt(10)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verifyPassword(entered_password: str, stored_hash: str) -> bool:
    return bcrypt.checkpw(entered_password.encode('utf-8'), stored_hash.encode('utf-8'))

def generateToken(user_id: str, org_id: str = None, role: str = "owner"):
    payload = {
        "user_id" : user_id,
        "org_id": org_id,
        "role": role,
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

def register(email: str, password: str, domain: str, db: Session):
    email_lower = email.lower().strip()
    existing_user = db.query(User).filter(User.email == email_lower).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    domain = domain.strip().lower()
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")

    email_domain = email_lower.split("@")[-1]
    existing_domain_owner = db.query(User).filter(
        User.email.like(f"%@{email_domain}"),
        User.role == "owner"
    ).first()

    if existing_domain_owner:
        raise HTTPException(
            status_code=400, 
            detail=f"An account for '@{email_domain}' already exists. Cannot create a new account, you need to be invited by the owner."
        )

    user_id = str(uuid.uuid4())
    hashed_password = hashPassword(password)

    new_user = User(
        user_id=user_id,
        email=email_lower,
        password=hashed_password,
        role="owner",
    )
    db.add(new_user)
    db.flush()

    # Create organization for the owner (first domain is set at registration)
    org_id = str(uuid.uuid4())
    new_org = Organization(
        org_id=org_id,
        user_id=user_id,
        domain=[domain],
    )
    db.add(new_org)
    db.flush()

    # Link the user to the org
    new_user.org_id = org_id
    db.commit()

    return {"message": "Registration successful", "email": email_lower}

def login_user(email: str, password: str, db: Session):
    email_lower = email.lower().strip()
    blocked_user = db.query(Blacklist).filter(Blacklist.email == email_lower).first()
    if blocked_user:
        raise HTTPException(status_code=403, detail="This user has been blocked by an admin")

    user = db.query(User).filter(
        User.email == email_lower
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verifyPassword(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = generateToken(user.user_id, org_id=user.org_id, role=user.role)
    org = (
        db.query(Organization).filter(Organization.org_id == user.org_id).first()
        if user.org_id
        else None
    )
    org_domains = list(org.domain) if org and org.domain else []
    primary_domain = org_domains[0] if org_domains else ""
    return {
        "token": access_token,
        "user": {
            "role": user.role,
            "user_id": user.user_id,
            "org_id": user.org_id,
            "email": user.email,
        },
    }

def send_forgot_password_otp(email: str, db: Session):
    email_lower = email.lower()
    user = db.query(User).filter(User.email == email_lower).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = f"{secrets.randbelow(1000000):06d}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)

    existing_otp = db.query(PasswordResetOTP).filter(
        PasswordResetOTP.user_id == user.user_id
    ).first()

    if existing_otp:
        db.delete(existing_otp)
        db.flush()

    reset_otp = PasswordResetOTP(
        user_id=user.user_id,
        otp_hash=hashPassword(otp),
        expires_at=expires_at
    )
    db.add(reset_otp)

    try:
        send_password_reset_otp_email(to_email=user.email, otp=otp)
    except Exception as email_err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to send email to {email_lower}: {str(email_err)}")

    db.commit()
    return {"message": "OTP sent successfully"}

def verify_otp_and_reset_password(email: str, otp: str, new_password: str, db: Session):
    email_lower = email.lower()
    user = db.query(User).filter(User.email == email_lower).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp_record = db.query(PasswordResetOTP).filter(
        PasswordResetOTP.user_id == user.user_id
    ).first()

    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    now_utc = datetime.now(timezone.utc)
    expires_at = otp_record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now_utc:
        db.delete(otp_record)
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    if not verifyPassword(otp.strip(), otp_record.otp_hash):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user.password = hashPassword(new_password)
    db.delete(otp_record)

    db.commit()
    return {"message": "Password reset successful"}

def reset_password_with_old_password(user_id: str, old_password: str, new_password: str, db: Session):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verifyPassword(old_password, user.password):
        raise HTTPException(status_code=401, detail="Old password is incorrect")

    user.password = hashPassword(new_password)
    db.commit()

    return {"message": "Password updated successfully"}

def invite_member(owner: User, invite_email: str, db: Session):
    org_id = owner.org_id

    existing_members = db.query(User).filter(
        User.org_id == org_id,
        User.role == "member"
    ).count()

    if existing_members >= 5:
        raise HTTPException(
            status_code=400,
            detail="You have already reached the maximum limit of 5 invited members."
        )

#     email_lower = invite_email.lower()
#     if not email_lower:
#         raise HTTPException(status_code=400, detail="Please provide an email")

    existing_user = db.query(User).filter(User.email == email_lower).first()
    if existing_user:
        raise HTTPException(status_code=400, detail=f"{email_lower} is already a registered user")

    plain_password = secrets.token_urlsafe(12)
    hashed_password = hashPassword(plain_password)

    member_id = str(uuid.uuid4())
    new_member = User(
        user_id=member_id,
        org_id=org_id,
        email=email_lower,
        password=hashed_password,
        role="member",
    )
    db.add(new_member)

    try:
        send_invite_email(
            to_email=email_lower,
            plain_password=plain_password,
            sender_email=owner.email,
        )
    except Exception as email_err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to send email to {email_lower}: {str(email_err)}")

#     db.commit()

#     return {
#         "message": "Invitation sent successfully",
#         "sent": email_lower
#     }

def get_members(owner: User, db: Session):
    members = db.query(User).filter(
        User.org_id == owner.org_id,
    ).all()

    return [
        {
            "user_id": m.user_id,
            "role": m.role,
            "email": m.email,
        }
        for m in members
    ]

def redeem_promo_code(user_id: str, code: str, db: Session):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or not user.org_id:
        raise HTTPException(status_code=400, detail="User not associated with an organization")

    promo = db.query(PromoCode).filter(PromoCode.code == code).first()
    
    if not promo:
        raise HTTPException(status_code=404, detail="Promo code not found")
        
    if promo.is_used:
        raise HTTPException(status_code=400, detail="Promo code already used")
        
    org = db.query(Organization).filter(Organization.org_id == user.org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    promo.is_used = True
    promo.used_at = datetime.now(timezone.utc)
    promo.used_by = user_id
    
    org.max_domains += 1
    
    db.commit()
    return {
        "message": "Promo code redeemed successfully",
        "max_domains": org.max_domains
    }

def add_domain(user_id: str, domain: str, db: Session):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or not user.org_id:
        raise HTTPException(status_code=400, detail="User not associated with an organization")

    org = db.query(Organization).filter(Organization.org_id == user.org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    domain = domain.strip().lower()
    if not domain:
        raise HTTPException(status_code=400, detail="Domain is required")

    org_domains = list(org.domain) if org.domain else []

    if domain in org_domains:
        raise HTTPException(status_code=400, detail="Domain already added")

    if len(org_domains) >= org.max_domains:
        raise HTTPException(
            status_code=400,
            detail=f"Domain limit reached. Maximum {org.max_domains} domain(s) allowed. Redeem a promo code to add more."
        )

    org_domains.append(domain)
    org.domain = org_domains
    flag_modified(org, "domain")

    db.commit()
    return {
        "message": "Domain added successfully",
        "domains": org_domains
    }
