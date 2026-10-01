"""
Pydantic schemas cho Authentication endpoints.
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=200)
    organization: str | None = None

    model_config = {"json_schema_extra": {
        "example": {
            "email": "user@example.com",
            "password": "secret123",
            "full_name": "Nguyễn Văn A",
            "organization": "Công ty ABC"
        }
    }}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = {"json_schema_extra": {
        "example": {"email": "user@example.com", "password": "secret123"}
    }}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UpdateProfileRequest(BaseModel):
    """UC-03: Cập nhật thông tin hồ sơ cá nhân."""
    full_name: str = Field(..., min_length=1, max_length=200)

    model_config = {"json_schema_extra": {
        "example": {"full_name": "Nguyễn Văn B"}
    }}


class ChangePasswordRequest(BaseModel):
    """UC-03: Đổi mật khẩu — phải cung cấp mật khẩu cũ để xác minh."""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=100)

    model_config = {"json_schema_extra": {
        "example": {
            "current_password": "old_secret",
            "new_password": "new_secure_pass"
        }
    }}


class AdminUserResponse(BaseModel):
    """UC-20: Thông tin user dành cho Admin view."""
    id: UUID
    email: str
    full_name: str | None
    role: str
    is_active: bool
    organization_id: UUID | None
    created_at: datetime
    last_login: datetime | None

    model_config = {"from_attributes": True}


class PatchRoleRequest(BaseModel):
    """UC-20: Admin thay đổi role của user."""
    role: str = Field(..., pattern="^(user|enterprise|admin)$")


class PatchStatusRequest(BaseModel):
    """UC-20: Admin kích hoạt / khóa tài khoản."""
    is_active: bool
