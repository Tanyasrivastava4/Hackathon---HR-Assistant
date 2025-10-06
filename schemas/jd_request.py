# schemas/jd_request.py
from pydantic import BaseModel
from typing import List, Optional

class JDRequest(BaseModel):
    role: str
    level: str
    skills: Optional[List[str]] = None
