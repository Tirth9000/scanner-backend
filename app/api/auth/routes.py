# from fastapi import APIRouter, HTTPException, Depends
# from fastapi.responses import JSONResponse
# import uuid
# from app.api.auth.schemas import RegisterRequest, LoginRequest
# from sqlalchemy.orm import Session
# from app.db.base import get_db
# from app.db.models import User
# from app.api.auth.helper_functions import hashPassword, verifyPassword, generateToken
# from app.core.middleware import protect

# router = APIRouter(prefix='/api/auth', tags=['auth'])

# # new user registration
# @router.post('/register')
# def register(
#     req: RegisterRequest,
#     db: Session = Depends(get_db)
# ):
#     username = req.username
#     email = req.email
#     password = req.password

#     if not username or not email or not password:
#         raise HTTPException(status_code=400, detail="Please fill all the fields")

#     try:
#         # 1️⃣ Check if user exists
#         existing_user = db.query(User).filter(
#             User.email == email.lower()
#         ).first()

#         if existing_user:
#             raise HTTPException(status_code=400, detail="User already exists")

#         # 2️⃣ Create new user
#         hashed_password = hashPassword(password)
#         user_id = str(uuid.uuid4())

#         new_user = User(
#             id=user_id,
#             username=username,
#             email=email.lower(),
#             password=hashed_password
#         )

#         db.add(new_user)
#         db.commit()
#         db.refresh(new_user)

#         return {
#             "id": new_user.id,
#             "username": new_user.username,
#             "email": new_user.email,
#             "token": generateToken(new_user.id)
#         }

#     except HTTPException:
#         raise
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail="Internal Server Error")


# # user login
# @router.post('/login')
# def login(
#     req: LoginRequest,
#     db: Session = Depends(get_db)
# ):
#     email = req.email
#     password = req.password

#     if not email or not password:
#         raise HTTPException(status_code=400, detail="Please fill all the fields")

#     try:
#         user = db.query(User).filter(
#             User.email == email.lower()
#         ).first()

#         if not user:
#             raise HTTPException(status_code=401, detail="Invalid email or password")

#         if not verifyPassword(password, user.password):
#             raise HTTPException(status_code=401, detail="Invalid email or password")

#         return {
#             "id": user.id,
#             "username": user.username,
#             "email": user.email,
#             "token": generateToken(user.id)
#         }

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal Server Error")

# # user profile data
# @router.get('/profile/{id}')
# def getProfile(
#     id: str,
#     db: Session = Depends(get_db)
# ):
#     try:
#         user = db.query(User).filter(User.id == id).first()

#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")

#         return {
#             "_id": user.id,
#             "username": user.username,
#             "email": user.email
#         }

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal Server Error")