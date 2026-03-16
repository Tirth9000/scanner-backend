# import bcrypt
# from datetime import datetime, timedelta, timezone
# from jose import jwt
# import os

# JWT_SECRET = os.getenv('JWT_SECRET')

# def hashPassword(password: str) -> str:
#     # hash password using bycrypt
#     salt = bcrypt.gensalt(10)
#     return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


# def verifyPassword(entered_password: str, stored_hash: str) -> bool:
#     # Verify entered password against the stored hash
#     return bcrypt.checkpw(entered_password.encode('utf-8'), stored_hash.encode('utf-8'))


# # generate token for user
# def generateToken(id: str):
#     payload = {
#         "id" : id,
#         "exp": datetime.now(timezone.utc) + timedelta(hours=12)
#     }

#     if not JWT_SECRET:
#         raise ValueError("JWT_SECRET not set")
#     return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
