from fastapi import APIRouter, HTTPException
from schemas.user_schema import UserRegister
from database.connection import get_connection
from utils.password_hash import hash_password

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
                "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
                (user.email, user.name, hashed)
            )
        conn.commit()  # Lưu thay đổi vào DB
    finally:
        conn.close()   # Luôn đóng kết nối
    return {"message": "Đăng ký thành công"}
