"""
Auth Service — Business logic cho đăng ký và đăng nhập.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.config import settings
from app.models.user import User, Organization


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """Tìm user theo email."""
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id) -> Optional[User]:
    """Tìm user theo UUID."""
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def register_user(
    session: AsyncSession,
    email: str,
    password: str,
    full_name: str,
    organization_name: Optional[str] = None,
) -> User:
    """
    Tạo user mới.
    Raises ValueError nếu email đã tồn tại.
    """
    existing = await get_user_by_email(session, email)
    if existing:
        raise ValueError(f"Email '{email}' đã được đăng ký.")

    # Tạo organization nếu có
    org_id = None
    if organization_name:
        org = Organization(name=organization_name)
        session.add(org)
        await session.flush()  # Lấy org.id mà không commit
        org_id = org.id

    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        organization_id=org_id,
        role="user",
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def login_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> User:
    """
    Xác thực email + password.
    Raises ValueError nếu sai credentials.
    """
    user = await get_user_by_email(session, email)
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Email hoặc mật khẩu không đúng.")

    if not user.is_active:
        raise ValueError("Tài khoản đã bị khóa. Liên hệ admin.")

    # Cập nhật last_login
    user.last_login = datetime.now(timezone.utc)
    await session.commit()
    return user


def generate_tokens(user: User) -> dict:
    """Tạo cặp access_token + refresh_token cho user."""
    payload = {"sub": str(user.id), "email": user.email, "role": user.role}
    return {
        "access_token": create_access_token(payload),
        "refresh_token": create_refresh_token(payload),
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }
