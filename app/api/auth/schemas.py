from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
<<<<<<< HEAD
    domain: str
    org_name: str
=======
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class InviteRequest(BaseModel):
    email: EmailStr

class RedeemPromoRequest(BaseModel):
    code: str