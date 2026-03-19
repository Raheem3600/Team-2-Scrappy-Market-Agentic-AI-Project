from fastapi import APIRouter
from app.db import get_connection

router = APIRouter(tags=["Health"])


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/db/ping")
def db_ping():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 as result")
    row = cur.fetchone()
    conn.close()
    return {"db_response": row.result}