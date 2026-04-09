# import os
# import sys
# import uuid

# # Ensure we can import from the app directory
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from app.db.base import SessionLocal
# from app.db.models import User
# from app.api.auth.service import hashPassword

# def create_admin_user(email=None, password=None):
#     email = email or os.getenv("ADMIN_EMAIL")
#     password = password or os.getenv("ADMIN_PASSWORD")
    
#     email = email.lower().strip()

#     db = SessionLocal()
#     try:
#         # Check if user already exists
#         existing_user = db.query(User).filter(User.email == email).first()
#         if existing_user:
#             return

#         user_id = str(uuid.uuid4())
#         hashed_password = hashPassword(password)

#         new_admin = User(
#             user_id=user_id,
#             email=email,
#             password=hashed_password,
#             domain="system-admin",
#             role="admin",
#             organization_id=None # Admin belongs to no organization
#         )

#         db.add(new_admin)
#         db.commit()
#         print(f"Admin user '{email}' auto-created successfully.")

#     except Exception as e:
#         db.rollback()
#         print(f"An error occurred while creating admin: {e}")
#     finally:
#         db.close()

# if __name__ == "__main__":
#     create_admin_user()
