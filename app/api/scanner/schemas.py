from pydantic import BaseModel


class RegisterScannerRequest(BaseModel):
    scan_id: str
    domain: str
    status: str
    progress: int

class RequestScanTask(BaseModel):
    target: str

class WebHookResponse(BaseModel):
    scan_id: str
    data: dict
    message: str