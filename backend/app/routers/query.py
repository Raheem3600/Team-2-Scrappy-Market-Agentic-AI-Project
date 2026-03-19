from fastapi import APIRouter, HTTPException
from app.models.request_models import QueryRequest
from app.models.response_models import QueryResponse
from app.services.query_service import execute_safe_query

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/execute", response_model=QueryResponse)
def execute_query(request: QueryRequest):
    try:
        results = execute_safe_query(
            view_name=request.view_name,
            filters=request.filters,
            limit=request.limit
        )

        return {
            "success": True,
            "row_count": len(results),
            "results": results
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))