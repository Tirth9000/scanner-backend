from pydantic import BaseModel

<<<<<<< HEAD
class ScanTaskRequest(BaseModel):
=======
class ScanRequest(BaseModel):
    domain: str
<<<<<<< HEAD

class RegisterScannerRequest(BaseModel):
    scan_id: str
>>>>>>> f4a690b (Refactor scanner API routes and schemas; remove user_id dependency from scan tasks)
    domain: str
    user_id: str

class ScanHistoryRequest(BaseModel):
    org_id: str
=======
>>>>>>> f08a798 (Refactor authentication and assessment logic; add user role management and email invitation system)
