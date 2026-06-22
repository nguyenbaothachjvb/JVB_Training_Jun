import os
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
import redis

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-jvb-training-week1")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=True, 
)

BLACKLIST_PREFIX = "blacklist:" 

def blacklist_token(token: str, expires_in_seconds: int = None):
    """
    Đưa token vào danh sách đen (Blacklist) khi user Logout.
    - expires_in_seconds: Thời gian (giây) token còn hiệu lực.
      Nếu truyền vào, Redis sẽ tự động xóa key sau khoảng thời gian này (TTL).
      Nếu không truyền, mặc định TTL = thời hạn của access token.
    """
    key = BLACKLIST_PREFIX + token
    ttl = expires_in_seconds or (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    redis_client.setex(key, ttl, "1")

def is_token_blacklisted(token: str) -> bool:
    """
    Kiểm tra xem token đã bị vô hiệu hóa (Logout) chưa.
    - Trả về True nếu key tồn tại trong Redis (token đã bị blacklist).
    """
    key = BLACKLIST_PREFIX + token
    return redis_client.exists(key) == 1

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
