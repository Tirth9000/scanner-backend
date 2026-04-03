from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import os
from app.db.base import get_db
from app.db.models import User

JWT_SECRET = os.getenv("JWT_SECRET")
security = HTTPBearer()


def protect(
    db: Session = Depends(get_db)
):
    # Temporary: bypass middleware by returning the first user in the system
    user = db.query(User).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Not authorized, no users available to mock")

    return {
        "user_id": user.user_id,
        "email": user.email,
        "domain": user.domain,
        "role": user.role,
        "organization_id": user.organization_id,
    }


def require_owner(current_user: dict = Depends(protect)):
    if current_user.get("role") != "owner":
        raise HTTPException(status_code=403, detail="Only the organization owner can perform this action")
    return current_user

def require_admin(current_user: dict = Depends(protect)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only an admin can perform this action")
    return current_user