import logging
from fastapi import APIRouter, Depends, HTTPException
from schemas.response_schema import APIResponse, ok
from database.connection import get_connection
from auth_api_demo.routers.auth import get_current_user, bearer_scheme

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/me", response_model=APIResponse, status_code=200, dependencies=[Depends(bearer_scheme)])
def get_me(current_user: dict = Depends(get_current_user)):
    email = current_user.get("sub")
    logger.info("Lấy thông tin user: email=%s", email)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, email, name, role, created_at FROM users WHERE email = %s",
                (email,),
            )
            user = cursor.fetchone()

        if not user:
            logger.error("Không tìm thấy user trong DB: email=%s", email)
            raise HTTPException(status_code=404, detail="Không tìm thấy user")

        # Convert datetime -> string để JSON serializable
        if user.get("created_at"):
            user["created_at"] = user["created_at"].isoformat()

        return ok(message="Lấy thông tin thành công", data=user)
    finally:
        conn.close()


@router.get("/all", response_model=APIResponse, status_code=200, dependencies=[Depends(bearer_scheme)])
def get_all_users(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        logger.warning(
            "Truy cập /users/all bị từ chối – không phải admin: sub=%s",
            current_user.get("sub"),
        )
        raise HTTPException(status_code=403, detail="Chỉ admin mới được truy cập")

    logger.info("Admin lấy danh sách users: sub=%s", current_user.get("sub"))
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, email, name, role, created_at FROM users")
            users = cursor.fetchall()

        # Convert datetime -> string để JSON serializable
        for u in users:
            if u.get("created_at"):
                u["created_at"] = u["created_at"].isoformat()

        return ok(message="Lấy danh sách user thành công", data=users)
    finally:
        conn.close()
