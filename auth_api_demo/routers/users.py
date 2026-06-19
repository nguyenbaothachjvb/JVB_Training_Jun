from fastapi import APIRouter, HTTPException
from schemas.user_schema import UserRegister, UserLogin
from schemas.token_schema import TokenRefreshRequest
from database.connection import get_connection
from utils.password_hash import hash_password, verify_password
from utils.jwt_handler import create_access_token, create_refresh_token, verify_token

router = APIRouter()

@router.post("/register")
def register(user: UserRegister):
    conn = get_connection()
    try:
        with conn.cursor() as cursor: 
            cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email đã được đăng ký")

            hashed = hash_password(user.password)

            cursor.execute(
                "INSERT INTO users (email, name, password_hash, role) VALUES (%s, %s, %s, %s)",
                (user.email, user.name, hashed, user.role)
            )
        conn.commit()  # Lưu thay đổi vào DB
    finally:
        conn.close()   # Luôn đóng kết nối
    return {"message": "Đăng ký thành công"}

@router.post("/login")
def login(user: UserLogin):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
            db_user = cursor.fetchone()
            
            if not db_user or not verify_password(user.password, db_user["password_hash"]):
                raise HTTPException(status_code=401, detail="Email hoặc mật khẩu không chính xác")
            
            # 3. Sinh token (truyền thông tin cần thiết vào payload)
            payload = {"sub": db_user["email"], "role": db_user["role"]}
            access_token = create_access_token(data=payload)
            refresh_token = create_refresh_token(data=payload)
            
            # 4. Trả về token
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
    finally:
        conn.close()

@router.post("/token/refresh")
def refresh_token(request: TokenRefreshRequest):
    payload = verify_token(request.refresh_token, expected_type="refresh")
    
    if not payload:
        raise HTTPException(status_code=401, detail="Refresh token không hợp lệ hoặc đã hết hạn")
    
    user_email = payload.get("sub")
    role = payload.get("role")
    
    new_payload = {"sub": user_email, "role": role}
    new_access_token = create_access_token(data=new_payload)
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
