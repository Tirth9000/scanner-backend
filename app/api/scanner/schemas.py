from pydantic import BaseModel


class RegisterScannerRequest(BaseModel):
    scan_id: str
    # user_id : str
    domain: str
    status: str
    progress: int

class RequestScanTask(BaseModel):
    # user_id: str
    target: str

class WebHookResponse(BaseModel):
    scan_id: str
    data: dict
    message: str
    
