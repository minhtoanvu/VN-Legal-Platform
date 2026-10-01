"""
Admin Router — /admin
UC-20: Quản lý, phân quyền và thống kê người dùng
UC-21: Quản lý Thêm/Sửa/Xóa/Sync dữ liệu văn bản pháp luật

Tất cả endpoint yêu cầu role Admin (require_admin dependency).

Endpoints:
  GET    /admin/users                  — Danh sách users (phân trang, filter role)
  GET    /admin/users/{id}             — Chi tiết user
  PATCH  /admin/users/{id}/role        — Thay đổi role
  PATCH  /admin/users/{id}/status      — Kích hoạt / khóa tài khoản
  GET    /admin/stats                  — Thống kê tổng hợp hệ thống
  POST   /admin/documents              — Thêm văn bản mới
  PUT    /admin/documents/{id}         — Sửa metadata văn bản
  DELETE /admin/documents/{id}         — Xóa văn bản
  POST   /admin/documents/sync         — Trigger đồng bộ dữ liệu (ETL hook)
"""
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.document import Document
from app.models.user import Organization, User
from app.schemas.auth import AdminUserResponse, PatchRoleRequest, PatchStatusRequest

router = APIRouter()


# ── UC-20: Quản lý Người dùng ─────────────────────────────────────────


@router.get(
    "/users",
    response_model=list[AdminUserResponse],
    summary="[Admin] Danh sách tất cả người dùng - UC-20",
)
async def list_users(
    role: str | None = Query(None, description="Lọc theo role: user | enterprise | admin"),
    is_active: bool | None = Query(None, description="Lọc theo trạng thái hoạt động"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    _admin = Depends(require_admin),
):
    """Lấy danh sách toàn bộ users với phân trang và filter theo role/status."""
    stmt = select(User)
    if role:
        stmt = stmt.where(User.role == role)
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
    stmt = stmt.order_by(User.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/users/{user_id}",
    response_model=AdminUserResponse,
    summary="[Admin] Chi tiết user - UC-20",
)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(require_admin),
):
    """Xem thông tin chi tiết của một user bất kỳ."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy người dùng.")
    return user


@router.patch(
    "/users/{user_id}/role",
    response_model=AdminUserResponse,
    summary="[Admin] Thay đổi role người dùng - UC-20",
)
async def patch_user_role(
    user_id: UUID,
    body: PatchRoleRequest,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin),
):
    """
    Admin thay đổi role của user: user → enterprise → admin.
    Admin không thể tự hạ cấp chính mình để tránh mất quyền hệ thống.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy người dùng.")

    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể thay đổi role của chính mình."
        )

    user.role = body.role
    await db.commit()
    await db.refresh(user)
    return user


@router.patch(
    "/users/{user_id}/status",
    response_model=AdminUserResponse,
    summary="[Admin] Kích hoạt / khóa tài khoản - UC-20",
)
async def patch_user_status(
    user_id: UUID,
    body: PatchStatusRequest,
    db: AsyncSession = Depends(get_db),
    admin = Depends(require_admin),
):
    """
    Admin kích hoạt hoặc khóa tài khoản người dùng.
    Admin không thể tự khóa chính mình.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy người dùng.")

    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể tự khóa tài khoản của chính mình."
        )

    user.is_active = body.is_active
    await db.commit()
    await db.refresh(user)
    return user


@router.get(
    "/stats",
    summary="[Admin] Thống kê tổng hợp hệ thống - UC-20",
)
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    _admin = Depends(require_admin),
):
    """Thống kê: tổng users, phân bố theo role, tổng văn bản, tổ chức."""
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar()
    users_by_role = {}
    for role in ("user", "enterprise", "admin"):
        count = (await db.execute(
            select(func.count()).select_from(User).where(User.role == role)
        )).scalar()
        users_by_role[role] = count

    active_users = (await db.execute(
        select(func.count()).select_from(User).where(User.is_active.is_(True))
    )).scalar()

    total_docs = (await db.execute(select(func.count()).select_from(Document))).scalar()
    active_docs = (await db.execute(
        select(func.count()).select_from(Document).where(Document.status == "active")
    )).scalar()

    total_orgs = (await db.execute(select(func.count()).select_from(Organization))).scalar()

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "by_role": users_by_role,
        },
        "documents": {
            "total": total_docs,
            "active": active_docs,
        },
        "organizations": {
            "total": total_orgs,
        },
    }


# ── UC-21: Quản lý Văn bản Pháp luật ─────────────────────────────────


class DocumentCreateRequest(BaseModel):
    """UC-21: Tạo văn bản mới."""
    doc_number: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1)
    doc_type: str | None = Field(None, max_length=50)
    issuing_body: str | None = Field(None, max_length=200)
    field: str | None = Field(None, max_length=100)
    issue_date: date | None = None
    effective_date: date | None = None
    expired_date: date | None = None
    status: str = Field(default="active", pattern="^(active|expired|amended)$")
    content: str | None = None
    source_url: str | None = None

    model_config = {"json_schema_extra": {
        "example": {
            "doc_number": "45/2019/QH14",
            "title": "Bộ Luật Lao động",
            "doc_type": "Luật",
            "issuing_body": "Quốc hội",
            "field": "labor",
            "issue_date": "2019-11-20",
            "effective_date": "2021-01-01",
            "status": "active"
        }
    }}


class DocumentUpdateRequest(BaseModel):
    """UC-21: Cập nhật metadata văn bản."""
    title: str | None = Field(None, min_length=1)
    doc_type: str | None = Field(None, max_length=50)
    issuing_body: str | None = Field(None, max_length=200)
    field: str | None = Field(None, max_length=100)
    issue_date: date | None = None
    effective_date: date | None = None
    expired_date: date | None = None
    status: str | None = Field(None, pattern="^(active|expired|amended)$")
    content: str | None = None
    source_url: str | None = None


class DocumentAdminOut(BaseModel):
    id: UUID
    doc_number: str
    title: str
    doc_type: str | None
    issuing_body: str | None
    field: str | None
    issue_date: date | None
    effective_date: date | None
    expired_date: date | None
    status: str
    source_url: str | None

    model_config = {"from_attributes": True}


@router.post(
    "/documents",
    response_model=DocumentAdminOut,
    status_code=status.HTTP_201_CREATED,
    summary="[Admin] Thêm văn bản mới - UC-21",
)
async def create_document(
    body: DocumentCreateRequest,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(require_admin),
):
    """Admin thêm một văn bản pháp luật mới vào hệ thống."""
    # Kiểm tra doc_number trùng
    existing = await db.execute(select(Document).where(Document.doc_number == body.doc_number))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Văn bản số hiệu '{body.doc_number}' đã tồn tại trong hệ thống."
        )

    doc = Document(**body.model_dump())
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.put(
    "/documents/{doc_id}",
    response_model=DocumentAdminOut,
    summary="[Admin] Cập nhật metadata văn bản - UC-21",
)
async def update_document(
    doc_id: UUID,
    body: DocumentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(require_admin),
):
    """Admin cập nhật metadata văn bản (không ảnh hưởng chunks/embeddings)."""
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy văn bản.")

    update_data = body.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(doc, field, value)

    await db.commit()
    await db.refresh(doc)
    return doc


@router.delete(
    "/documents/{doc_id}",
    status_code=status.HTTP_200_OK,
    summary="[Admin] Xóa văn bản - UC-21",
)
async def delete_document(
    doc_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(require_admin),
):
    """
    Admin xóa văn bản pháp luật.
    CASCADE sẽ tự xóa document_chunks và document_relations liên quan.
    """
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy văn bản.")

    doc_number = doc.doc_number
    await db.delete(doc)
    await db.commit()
    return {"message": f"Đã xóa văn bản '{doc_number}' và toàn bộ dữ liệu liên quan."}


@router.post(
    "/documents/sync",
    status_code=status.HTTP_202_ACCEPTED,
    summary="[Admin] Trigger đồng bộ dữ liệu ETL - UC-21",
)
async def sync_documents(
    _admin = Depends(require_admin),
):
    """
    Gửi tín hiệu kích hoạt pipeline ETL để đồng bộ dữ liệu từ nguồn.
    Chạy async — không block response. Kiểm tra tiến độ qua logs.

    Lưu ý: Trong môi trường production, nên dùng task queue (Celery/RQ).
    Hiện tại trả về 202 Accepted với hướng dẫn chạy thủ công.
    """
    return {
        "message": "Đã nhận yêu cầu đồng bộ dữ liệu.",
        "status": "accepted",
        "instructions": (
            "Chạy ETL thủ công: "
            "cd backend && python scripts/etl/run_full_etl.py"
        ),
    }
