from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import os
from app.db.base import get_db
from app.db.models import User

JWT_SECRET = os.getenv("JWT_SECRET")
security = HTTPBearer()


# Protect middleware - verify JWT and return current user
def protect(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        if not JWT_SECRET:
            raise ValueError("JWT_SECRET not set")

        # 1️⃣ Verify token
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = decoded.get("user_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # 2️⃣ Fetch user using ORM
        user = db.query(User).filter(User.user_id == user_id).first()

        if not user:
            raise HTTPException(status_code=401, detail="Not authorized, user not found")

        return {
            "user_id": user.user_id,
            "email": user.email,
            "domain": user.domain,
        }

    except JWTError as error:
        raise HTTPException(status_code=401, detail="Not authorized, token failed")