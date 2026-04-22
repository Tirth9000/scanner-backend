from pydantic import BaseModel
from typing import Any, Optional
import time


class ScannerWebhookRequest(BaseModel):
    user_id: str
    target: str
    event: str
    status : str

class ScannerWebhookResultRequest(BaseModel):
    target: str
    data: Any
    scan_id: Optional[str] = None
    status: Optional[str] = None