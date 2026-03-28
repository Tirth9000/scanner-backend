from typing import Any, Optional
from pydantic import BaseModel


class FixRequest(BaseModel):
    scan_id: str
    domain: str
    fix_type: str
    data: Any


class FixResponse(BaseModel):
    message: str
    scan_id: str
    domain_score: Optional[int] = None
    severity: Optional[str] = None


class FixResultRequest(BaseModel):
    scan_id: str
    domain: str
    fix_type: str
    result: Any
