from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    domain: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class InviteRequest(BaseModel):
    email: EmailStr

class RedeemPromoRequest(BaseModel):
    code: str

class ForgotPasswordOtpRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResetRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

class ResetPasswordRequest(BaseModel):
    old_password: str
    new_password: str

class AcceptInviteRequest(BaseModel):
    email: EmailStr
    password: str
    token: str

class OrgMembersRequest(BaseModel):
    org_id: str
