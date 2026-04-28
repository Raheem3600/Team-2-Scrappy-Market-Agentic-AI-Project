from pydantic import BaseModel, Field
from typing import List, Dict, Any


class AnalysisRequest(BaseModel):
    analysis_type: str
    view_name: str
    metrics: List[str]
    group_by: List[str]
    filters: Dict[str, Any] = Field(default_factory=dict)
    limit: int = Field(default=100, ge=1, le=1000)
    sort_by: str | None = None
    sort_direction: str = "desc"