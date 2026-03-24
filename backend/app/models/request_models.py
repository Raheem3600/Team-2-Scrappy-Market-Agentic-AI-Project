from pydantic import BaseModel
from typing import Optional, Dict, Any

class QueryRequest(BaseModel):
    view_name: str
    filters: Optional[Dict[str, Any]] = {}
    limit: Optional[int] = 100