from pydantic import BaseModel

class ScanRequest(BaseModel):
    domain: str

class RegisterScannerRequest(BaseModel):
    scan_id: str
class ScanTaskRequest(BaseModel):
    domain: str
    user_id: str

class ScanHistoryRequest(BaseModel):
    org_id: str