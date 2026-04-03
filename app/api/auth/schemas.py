from pydantic import BaseModel, EmailStr
from typing import List

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    domain: str
    org_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class InviteRequest(BaseModel):
    email: EmailStr
    sender_email: EmailStr

class AcceptInviteRequest(BaseModel):
    token: str
    password: str
    email: EmailStr

class OrgMembersRequest(BaseModel):
    org_id: str

class RedeemPromoRequest(BaseModel):
    code: str
    org_id: str