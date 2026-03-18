from typing import List, Dict
from pydantic import BaseModel

class ScanScoreResponse(BaseModel):
    scan_id: str
    domain_score: int
    categorized_vulnerabilities: Dict[str, Dict[str, List[str]]]

    class Config:
        from_attributes = True 