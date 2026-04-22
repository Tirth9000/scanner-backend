from pydantic import BaseModel, EmailStr


class BlacklistEmailRequest(BaseModel):
    email: EmailStr
