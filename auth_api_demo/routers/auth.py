import logging
import jwt
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer
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

def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.split(" ")[1]
    payload = verify_token(token)

    if not payload:
        logger.warning("Token không hợp lệ hoặc đã hết hạn")
        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ hoặc đã hết hạn",
        )
    return payload


@router.post("/register", response_model=APIResponse, status_code=201)
def register(user: UserRegister):
    logger.info("Yêu cầu đăng ký: username=%s, email=%s", user.username, user.email)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email = %s OR username = %s", (user.email, user.username))
            if cursor.fetchone():
                logger.warning("Đăng ký thất bại – email hoặc username đã tồn tại")
                raise HTTPException(status_code=400, detail="Email hoặc Username đã được sử dụng")

            hashed = hash_password(user.password)
            cursor.execute(
                "INSERT INTO users (username, email, full_name, password_hash) VALUES (%s, %s, %s, %s)",
                (user.username, user.email, user.full_name, hashed),
            )
            user_id = cursor.lastrowid
            
            # Gán quyền mặc định 'customer' (giả sử role_id = 3)
            cursor.execute("INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)", (user_id, 3))
            
        conn.commit()
        logger.info("Đăng ký thành công: username=%s", user.username)
    finally:
        conn.close()

    return ok(
        message="Đăng ký thành công",
        data={"username": user.username, "email": user.email, "full_name": user.full_name},
    )


@router.post("/login", response_model=APIResponse, status_code=200)
def login(user: UserLogin):
    logger.info("Yêu cầu đăng nhập: email=%s", user.email)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.*, r.name as role_name 
                FROM users u 
                LEFT JOIN user_roles ur ON u.id = ur.user_id 
                LEFT JOIN roles r ON ur.role_id = r.id 
                WHERE u.email = %s
            """, (user.email,))
            db_user = cursor.fetchone()

        if not db_user or not verify_password(user.password, db_user["password_hash"]):
            logger.warning("Đăng nhập thất bại – sai thông tin: email=%s", user.email)
            raise HTTPException(
                status_code=401,
                detail="Email hoặc mật khẩu không chính xác",
            )

        if not db_user.get("is_active", 1):
            logger.warning("Tài khoản bị vô hiệu hóa: email=%s", user.email)
            raise HTTPException(
                status_code=403,
                detail="Tài khoản đã bị vô hiệu hóa",
            )

        payload = {"sub": db_user["email"], "role": db_user["role_name"] or "customer"}
        access_token = create_access_token(data=payload)
        refresh_token = create_refresh_token(data=payload)

        # Trích xuất jti và exp từ token
        decoded_refresh = jwt.decode(refresh_token, options={"verify_signature": False})
        jti = decoded_refresh.get("jti")
        exp_datetime = datetime.fromtimestamp(decoded_refresh.get("exp"), tz=timezone.utc)

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO refresh_tokens (user_id, jti, revoked, expired_at) 
                VALUES (%s, %s, 0, %s)
            """, (db_user["id"], jti, exp_datetime.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()

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
    logger.info("Yêu cầu làm mới token")
    payload = verify_token(request.refresh_token, expected_type="refresh")

    if not payload:
        logger.warning("Refresh token không hợp lệ hoặc đã hết hạn")
        raise HTTPException(
            status_code=401,
            detail="Refresh token không hợp lệ hoặc đã hết hạn",
        )

    jti = payload.get("jti")
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id, revoked FROM refresh_tokens WHERE jti = %s", (jti,))
            db_token = cursor.fetchone()
            
            if not db_token or db_token["revoked"] == 1:
                raise HTTPException(status_code=401, detail="Refresh token đã bị thu hồi hoặc không tồn tại")
                
            # Thu hồi token cũ
            cursor.execute("UPDATE refresh_tokens SET revoked = 1 WHERE jti = %s", (jti,))
            
            new_payload = {"sub": payload.get("sub"), "role": payload.get("role")}
            new_access_token = create_access_token(data=new_payload)
            new_refresh_token = create_refresh_token(data=new_payload)
            
            # Lưu token mới vào DB
            new_decoded = jwt.decode(new_refresh_token, options={"verify_signature": False})
            new_jti = new_decoded.get("jti")
            new_exp_datetime = datetime.fromtimestamp(new_decoded.get("exp"), tz=timezone.utc)
            
            cursor.execute("""
                INSERT INTO refresh_tokens (user_id, jti, revoked, expired_at) 
                VALUES (%s, %s, 0, %s)
            """, (db_token["user_id"], new_jti, new_exp_datetime.strftime('%Y-%m-%d %H:%M:%S')))
            
        conn.commit()
    finally:
        conn.close()

    # Vẫn blacklist access token cũ nếu cần bằng redis (để đảm bảo không bị lạm dụng)
    blacklist_token(request.refresh_token, expires_in_seconds=7 * 24 * 3600)

    logger.info("Cấp lại token thành công: sub=%s", payload.get("sub"))
    return ok(
        message="Cấp lại token thành công",
        data={
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        },
    )


@router.post("/logout", response_model=APIResponse, status_code=200, dependencies=[Depends(bearer_scheme)])
def logout(request: Request, body: Optional[TokenRefreshRequest] = None):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = auth_header.split(" ")[1]

    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Token không hợp lệ")

    # Blacklist access token trong Redis
    blacklist_token(token)

    # Revoke refresh token trong DB nếu client gửi kèm
    if body and body.refresh_token:
        try:
            decoded = jwt.decode(body.refresh_token, options={"verify_signature": False})
            jti = decoded.get("jti")
            if jti:
                conn = get_connection()
                try:
                    with conn.cursor() as cursor:
                        cursor.execute("UPDATE refresh_tokens SET revoked = 1 WHERE jti = %s", (jti,))
                    conn.commit()
                finally:
                    conn.close()
                blacklist_token(body.refresh_token, expires_in_seconds=7 * 24 * 3600)
        except Exception:
            logger.warning("Không thể revoke refresh token khi logout")

    logger.info("Đăng xuất thành công")
    return ok(message="Đăng xuất thành công")
