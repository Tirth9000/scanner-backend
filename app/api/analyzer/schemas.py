from typing import List, Dict, Optional
from pydantic import BaseModel

class UserHistoryRequest(BaseModel):
    user_id: str