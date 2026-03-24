from pydantic import BaseModel
from typing import List, Dict, Any


class QueryResponse(BaseModel):
    success: bool
    row_count: int
    results: List[Dict[str, Any]]