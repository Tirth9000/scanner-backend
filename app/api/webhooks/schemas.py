from pydantic import BaseModel
from typing import Any
import time


class ScannerWebhookRequest(BaseModel):
    user_id: str
    target: str
    event: str
    status : str

class ScannerWebhookResultRequest(BaseModel):
    user_id: str
    target: str
    data: Any