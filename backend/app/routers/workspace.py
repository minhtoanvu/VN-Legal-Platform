"""
Workspace Router — /workspace
UC-10: Lưu văn bản vào Collection (Bookmark)
UC-13: Ghi chú cá nhân trên văn bản

Endpoints:
  GET    /workspace/collections                     — Danh sách collections của user
  POST   /workspace/collections                     — Tạo collection mới
  DELETE /workspace/collections/{id}               — Xóa collection
  GET    /workspace/collections/{id}/docs          — Lấy docs trong collection
  POST   /workspace/collections/{id}/docs          — Thêm văn bản vào collection
  DELETE /workspace/collections/{id}/docs/{doc_id} — Xóa khỏi collection
  GET    /workspace/notes/{doc_id}                 — Ghi chú của user trên văn bản
  POST   /workspace/notes                          — Tạo ghi chú
  DELETE /workspace/notes/{note_id}                — Xóa ghi chú
"""
import uuid
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.document import Document
from app.models.user import User
from app.models.workspace import Collection, CollectionDocument, Note

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────

class CollectionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_shared: bool = False


class CollectionOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    is_shared: bool
    doc_count: Optional[int] = 0
    model_config = {"from_attributes": True}


class AddDocRequest(BaseModel):
    doc_id: UUID


class NoteUpsert(BaseModel):
    doc_id: UUID
    content: str = Field(..., min_length=1)


class NoteOut(BaseModel):
    id: UUID
    document_id: UUID
    content: str
    model_config = {"from_attributes": True}


class DocInCollectionOut(BaseModel):
    id: UUID
    title: str
    doc_number: str
    doc_type: Optional[str] = None
    issuing_body: Optional[str] = None
    status: Optional[str] = None
    model_config = {"from_attributes": True}


# ── Collections ───────────────────────────────────────────────────────

@router.get("/collections", response_model=list[CollectionOut])
async def list_collections(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Danh sách collections của user hiện tại kèm số lượng văn bản."""
    result = await db.execute(
        select(Collection).where(Collection.owner_id == current_user.id)
    )
    collections = result.scalars().all()

    # Đếm số doc trong mỗi collection
    out = []
    for col in collections:
        count_result = await db.execute(
            select(func.count()).select_from(CollectionDocument).where(
                CollectionDocument.collection_id == col.id
            )
        )
        doc_count = count_result.scalar() or 0
        out.append(CollectionOut(
            id=col.id,
            name=col.name,
            description=col.description,
            is_shared=col.is_shared,
            doc_count=doc_count,
        ))
    return out


@router.post("/collections", response_model=CollectionOut, status_code=201)
async def create_collection(
    body: CollectionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Tạo collection mới."""
    col = Collection(
        name=body.name,
        description=body.description,
        owner_id=current_user.id,
        is_shared=body.is_shared,
    )
    db.add(col)
    await db.commit()
    await db.refresh(col)
    return CollectionOut(
        id=col.id,
        name=col.name,
        description=col.description,
        is_shared=col.is_shared,
        doc_count=0,
    )


@router.delete("/collections/{collection_id}", status_code=200)
async def delete_collection(
    collection_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Xóa collection và toàn bộ văn bản trong đó."""
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.owner_id == current_user.id,
        )
    )
    col = result.scalar_one_or_none()
    if not col:
        raise HTTPException(status_code=404, detail="Collection không tồn tại.")
    await db.delete(col)
    await db.commit()
    return {"message": "Đã xóa collection."}


@router.get("/collections/{collection_id}/docs", response_model=list[DocInCollectionOut])
async def get_docs_in_collection(
    collection_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Lấy danh sách văn bản đầy đủ trong một collection."""
    # Kiểm tra quyền truy cập
    col_result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.owner_id == current_user.id,
        )
    )
    if not col_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Collection không tồn tại.")

    result = await db.execute(
        select(Document)
        .join(CollectionDocument, CollectionDocument.document_id == Document.id)
        .where(CollectionDocument.collection_id == collection_id)
        .order_by(CollectionDocument.added_at.desc())
    )
    return result.scalars().all()


@router.post("/collections/{collection_id}/docs", status_code=201)
async def add_document_to_collection(
    collection_id: UUID,
    body: AddDocRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Thêm văn bản vào collection (Bookmark)."""
    # Kiểm tra collection thuộc về user
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.owner_id == current_user.id,
        )
    )
    col = result.scalar_one_or_none()
    if not col:
        raise HTTPException(status_code=404, detail="Collection không tồn tại.")

    # Kiểm tra đã thêm chưa
    existing = await db.execute(
        select(CollectionDocument).where(
            CollectionDocument.collection_id == collection_id,
            CollectionDocument.document_id == body.doc_id,
        )
    )
    if existing.scalar_one_or_none():
        return {"message": "Văn bản đã có trong collection."}

    cd = CollectionDocument(collection_id=collection_id, document_id=body.doc_id)
    db.add(cd)
    await db.commit()
    return {"message": "Đã thêm văn bản vào collection."}


@router.delete("/collections/{collection_id}/docs/{doc_id}", status_code=200)
async def remove_document_from_collection(
    collection_id: UUID,
    doc_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Xóa văn bản khỏi collection."""
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.owner_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Collection không tồn tại.")

    await db.execute(
        delete(CollectionDocument).where(
            CollectionDocument.collection_id == collection_id,
            CollectionDocument.document_id == doc_id,
        )
    )
    await db.commit()
    return {"message": "Đã xóa văn bản khỏi collection."}


# ── Notes ─────────────────────────────────────────────────────────────

@router.get("/notes/{doc_id}", response_model=list[NoteOut])
async def get_notes(
    doc_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Lấy tất cả ghi chú của user trên một văn bản."""
    result = await db.execute(
        select(Note).where(
            Note.user_id == current_user.id,
            Note.document_id == doc_id,
        ).order_by(Note.created_at.desc())
    )
    return result.scalars().all()


@router.post("/notes", response_model=NoteOut, status_code=201)
async def create_note(
    body: NoteUpsert,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Tạo ghi chú mới trên văn bản."""
    note = Note(
        user_id=current_user.id,
        document_id=body.doc_id,
        content=body.content,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@router.delete("/notes/{note_id}", status_code=200)
async def delete_note(
    note_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Xóa ghi chú."""
    result = await db.execute(
        select(Note).where(
            Note.id == note_id,
            Note.user_id == current_user.id,
        )
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Ghi chú không tồn tại.")
    await db.delete(note)
    await db.commit()
    return {"message": "Đã xóa ghi chú."}



