"""
Auth Router — /auth/register, /auth/login, /auth/refresh, /auth/me
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.security import decode_token
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    UserResponse,
    RegisterResponse,
)
from app.services import auth_service

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Tạo tài khoản mới với email và mật khẩu (Bcrypt hash).
    Trả về access_token + refresh_token ngay sau khi đăng ký.
    """
    try:
        user = await auth_service.register_user(
            session=db,
            email=body.email,
            password=body.password,
            full_name=body.full_name,
            organization_name=body.organization,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    tokens = auth_service.generate_tokens(user)
    return RegisterResponse(
        message="Đăng ký thành công!",
        user=UserResponse.model_validate(user),
        **tokens,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Đăng nhập và nhận JWT token",
)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Xác thực email + password. Trả về access_token (30 phút) + refresh_token (7 ngày).
    """
    try:
        user = await auth_service.login_user(
            session=db,
            email=body.email,
            password=body.password,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(**auth_service.generate_tokens(user))


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Làm mới access token bằng refresh token",
)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Dùng refresh_token để lấy access_token mới (không cần đăng nhập lại).
    """
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token không hợp lệ hoặc đã hết hạn.",
        )

    user = await auth_service.get_user_by_email(db, payload.get("email", ""))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản không tồn tại hoặc đã bị khóa.",
        )

    return TokenResponse(**auth_service.generate_tokens(user))


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Lấy thông tin tài khoản hiện tại",
)
async def get_me(current_user: User = Depends(get_current_user)):
    """Trả về thông tin user đang đăng nhập (yêu cầu Bearer token)."""
    return UserResponse.model_validate(current_user)


@router.post(
    "/promote-admin",
    summary="Nâng cấp tài khoản hiện tại lên Admin (API Tạm thời)",
    description="⚠️ Chỉ dùng trong lúc chấm Đồ án để tự thăng cấp tài khoản của mình."
)
async def promote_to_admin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cập nhật role của user đang đăng nhập thành 'admin'."""
    current_user.role = "admin"
    db.add(current_user)
    await db.commit()
    return {"message": f"Thành công! Tài khoản {current_user.email} đã được nâng cấp lên Admin."}
