import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from schemas.user_schema import UserRegister, UserLogin
from schemas.token_schema import TokenRefreshRequest
from schemas.response_schema import APIResponse, ok
from database.connection import get_connection
from utils.password_hash import hash_password, verify_password
from utils.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_token,
    blacklist_token,
)

logger = logging.getLogger(__name__)
router = APIRouter()

bearer_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Đọc header Authorization (Bearer token), kiểm tra access token và trả về payload.
    Dùng HTTPBearer để Swagger UI tự hiển thị nút Authorize và gắn token vào header.
    """
    token = credentials.credentials
    payload = verify_token(token, expected_type="access")

    if not payload:
        logger.warning("Token không hợp lệ hoặc đã hết hạn")
        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ hoặc đã hết hạn",
        )

    payload["_raw_token"] = token
    return payload


@router.post("/register", response_model=APIResponse, status_code=201)
def register(user: UserRegister):
    logger.info("Yêu cầu đăng ký: email=%s", user.email)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
            if cursor.fetchone():
                logger.warning("Đăng ký thất bại – email đã tồn tại: %s", user.email)
                raise HTTPException(status_code=400, detail="Email đã được đăng ký")

            hashed = hash_password(user.password)
            cursor.execute(
                "INSERT INTO users (email, name, password_hash, role) VALUES (%s, %s, %s, %s)",
                (user.email, user.name, hashed, user.role),
            )
        conn.commit()
        logger.info("Đăng ký thành công: email=%s", user.email)
    finally:
        conn.close()

    return ok(
        message="Đăng ký thành công",
        data={"email": user.email, "name": user.name, "role": user.role},
    )


@router.post("/login", response_model=APIResponse, status_code=200)
def login(user: UserLogin):
    """Đăng nhập, trả về access_token và refresh_token."""
    logger.info("Yêu cầu đăng nhập: email=%s", user.email)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
            db_user = cursor.fetchone()

        if not db_user or not verify_password(user.password, db_user["password_hash"]):
            logger.warning("Đăng nhập thất bại – sai thông tin: email=%s", user.email)
            raise HTTPException(
                status_code=401,
                detail="Email hoặc mật khẩu không chính xác",
            )

        payload = {"sub": db_user["email"], "role": db_user["role"]}
        access_token = create_access_token(data=payload)
        refresh_token = create_refresh_token(data=payload)

        logger.info("Đăng nhập thành công: email=%s", user.email)
        return ok(
            message="Đăng nhập thành công",
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            },
        )
    finally:
        conn.close()


@router.post("/token/refresh", response_model=APIResponse, status_code=200)
def refresh_token(request: TokenRefreshRequest):
    """Cấp lại access_token mới từ refresh_token hợp lệ."""
    logger.info("Yêu cầu làm mới token")
    payload = verify_token(request.refresh_token, expected_type="refresh")

    if not payload:
        logger.warning("Refresh token không hợp lệ hoặc đã hết hạn")
        raise HTTPException(
            status_code=401,
            detail="Refresh token không hợp lệ hoặc đã hết hạn",
        )

    new_payload = {"sub": payload.get("sub"), "role": payload.get("role")}
    new_access_token = create_access_token(data=new_payload)

    logger.info("Cấp lại access token thành công: sub=%s", payload.get("sub"))
    return ok(
        message="Cấp lại access token thành công",
        data={"access_token": new_access_token, "token_type": "bearer"},
    )


# ── POST /auth/logout ─────────────────────────────────────────────────────────
@router.post("/logout", response_model=APIResponse, status_code=200)
def logout(current_user: dict = Depends(get_current_user)):
    """Đăng xuất và vô hiệu hóa access token hiện tại (blacklist)."""
    token = current_user.get("_raw_token")
    blacklist_token(token)
    logger.info("Đăng xuất thành công: sub=%s", current_user.get("sub"))
    return ok(message="Đăng xuất thành công")
