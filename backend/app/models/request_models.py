from pydantic import BaseModel, Field
from typing import Dict, Any


class QueryRequest(BaseModel):
    view_name: str
    metric_column: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    order_by: str | None = None
    aggregation: str | None = None
    group_by: str | None = None
    limit: int = Field(default=100, ge=1, le=1000)
