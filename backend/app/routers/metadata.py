from fastapi import APIRouter
from app.services.db_service import get_views, get_columns

router = APIRouter(prefix="/meta", tags=["Metadata"])


@router.get("/views")
def meta_views():
    views = get_views()
    return {"views": views}


@router.get("/columns/{view_name}")
def meta_columns(view_name: str):
    columns = get_columns(view_name)
    return {
        "view": view_name,
        "columns": columns
    }