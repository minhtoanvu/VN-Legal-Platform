"""
Auth Service — Business logic cho đăng ký và đăng nhập.
"""
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import Organization, User


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Tìm user theo email."""
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id) -> User | None:
    """Tìm user theo UUID."""
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def register_user(
    session: AsyncSession,
    email: str,
    password: str,
    full_name: str,
    organization_name: str | None = None,
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
        password_hash=await hash_password(password),
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
    if not user or not await verify_password(password, user.password_hash):
        raise ValueError("Email hoặc mật khẩu không đúng.")

    if not user.is_active:
        raise ValueError("Tài khoản đã bị khóa. Liên hệ admin.")

    # Cập nhật last_login
    user.last_login = datetime.now(UTC)
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


async def update_profile(
    session: AsyncSession,
    user: User,
    full_name: str,
) -> User:
    """
    UC-03: Cập nhật hồ sơ cá nhân.
    Hiện tại chỉ cho phép đổi full_name — email không đổi vì là định danh login.
    """
    user.full_name = full_name
    await session.commit()
    await session.refresh(user)
    return user


async def change_password(
    session: AsyncSession,
    user: User,
    current_password: str,
    new_password: str,
) -> None:
    """
    UC-03: Đổi mật khẩu.
    Raises ValueError nếu mật khẩu cũ sai.
    """
    if not await verify_password(current_password, user.password_hash):
        raise ValueError("Ư4 mật khẩu hiện tại không đúng.")
    user.password_hash = await hash_password(new_password)
    await session.commit()
