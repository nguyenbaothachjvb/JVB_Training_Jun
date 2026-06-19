import os
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError

# Các cấu hình mặc định (nên lưu trong file .env ở thực tế)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-jvb-training-week1")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Mảng bộ nhớ tạm (in-memory) để lưu các token đã logout
token_blacklist = set()

def blacklist_token(token: str):
    """
    Đưa token vào danh sách đen (Blacklist) khi user Logout
    """
    token_blacklist.add(token)

def is_token_blacklisted(token: str) -> bool:
    """
    Kiểm tra xem token đã bị vô hiệu hóa (Logout) chưa
    """
    return token in token_blacklist

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Tạo Access Token có thời hạn ngắn (mặc định 15 phút).
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Tạo Refresh Token có thời hạn dài (mặc định 7 ngày).
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, expected_type: str = "access") -> dict:
    """
    Giải mã và xác minh tính hợp lệ của token.
    - Trả về payload (dict) chứa thông tin của token nếu hợp lệ.
    - Trả về None nếu token bị lỗi (hết hạn, sai chữ ký, sai loại token, hoặc đã bị logout).
    """
    if is_token_blacklisted(token):
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Kiểm tra xem token có đúng loại mong muốn (access hoặc refresh) không
        if payload.get("type") != expected_type:
            return None
        return payload
    except InvalidTokenError:
        return None
