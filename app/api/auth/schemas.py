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

class AcceptInviteRequest(BaseModel):
    email: EmailStr
    password: str
    token: str

class OrgMembersRequest(BaseModel):
    org_id: str