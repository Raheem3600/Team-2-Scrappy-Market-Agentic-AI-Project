from pydantic import BaseModel, Field
from typing import Dict, Any


class QueryRequest(BaseModel):
    view_name: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=100, ge=1, le=1000)