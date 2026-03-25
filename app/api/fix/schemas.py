from typing import Any
from pydantic import BaseModel


class FixRequest(BaseModel):
    scan_id: str
    domain: str
    fix_type: str
    data: Any


class FixResponse(BaseModel):
    message: str
    scan_id: str


class FixResultRequest(BaseModel):
    scan_id: str
    domain: str
    fix_type: str
    result: Any
