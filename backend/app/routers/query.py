from fastapi import APIRouter, HTTPException
from app.models.request_models import QueryRequest
from app.models.response_models import QueryResponse
from app.services.query_service import execute_safe_query
from app.models.analysis_models import AnalysisRequest
from app.services.analytics_service import execute_analysis

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/execute", response_model=QueryResponse)
def execute_query(request: QueryRequest):
    try:
        results = execute_safe_query(
            view_name=request.view_name,
            metric_column=request.metric_column,
            filters=request.filters,
            order_by=request.order_by,
            aggregation=request.aggregation,
            group_by=request.group_by,
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
    
@router.post("/analyze")
def analyze_query(request: AnalysisRequest):
    try:
        results = execute_analysis(request)

        return {
            "success": True,
            "analysis_type": request.analysis_type,
            "row_count": len(results),
            "results": results
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
