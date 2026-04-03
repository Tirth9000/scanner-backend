from pydantic import BaseModel

class ScanTaskRequest(BaseModel):
    domain: str
    user_id: str

class ScanHistoryRequest(BaseModel):
    org_id: str