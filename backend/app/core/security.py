import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from starlette.concurrency import run_in_threadpool
from app.core.config import settings


async def hash_password(plain_password: str) -> str:
    """Hash mật khẩu bằng Bcrypt sử dụng ThreadPool để không block event loop."""
    password_bytes = plain_password.encode("utf-8")[:72]
    
    def _hash():
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password_bytes, salt).decode("utf-8")
        
    return await run_in_threadpool(_hash)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu với hash đã lưu sử dụng ThreadPool."""
    password_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    
    def _verify():
        return bcrypt.checkpw(password_bytes, hashed_bytes)
        
    return await run_in_threadpool(_verify)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Tạo JWT access token (ngắn hạn — 30 phút)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict) -> str:
    """Tạo JWT refresh token (dài hạn — 7 ngày)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> Optional[dict]:
    """Decode và validate JWT token. Trả về None nếu invalid/expired."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
