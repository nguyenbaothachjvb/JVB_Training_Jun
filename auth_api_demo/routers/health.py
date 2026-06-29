import logging
from fastapi import APIRouter
from schemas.response_schema import APIResponse, ok

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/ping", response_model=APIResponse, status_code=200)
def ping():
    logger.debug("Health check /ping được gọi")
    return ok(message="pong")

@router.get("/", response_model=APIResponse, status_code=200)
def root_route():
    logger.debug("Hello")
    return ok(message="Hello")

@router.get("/db-test")
def db_test():
    import traceback
    try:
        from database.connection import get_connection
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
        conn.close()
        return {"success": True, "message": "Kết nối Database thành công!", "version": version}
    except Exception as e:
        return {"success": False, "message": f"Kết nối Database thất bại: {str(e)}", "traceback": traceback.format_exc()}