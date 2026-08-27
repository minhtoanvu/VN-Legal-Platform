"""
Documents Router — /documents
UC-07: Xem chi tiết toàn văn, metadata và trạng thái hiệu lực
UC-08: Xem Timeline lịch sử thay đổi của một văn bản
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.document import Document, DocumentRelation
from app.schemas.document import (
    DocumentDetail,
    DocumentListItem,
    DocumentWithTimeline,
    DocumentRelationOut,
    TimelineEvent,
)

router = APIRouter()


@router.get(
    "",
    response_model=list[DocumentListItem],
    summary="Danh sách văn bản (phân trang)",
)
async def list_documents(
    field: Optional[str] = Query(None, description="Lọc theo lĩnh vực"),
    status: Optional[str] = Query(None, description="Lọc theo trạng thái: active/expired/amended"),
    doc_type: Optional[str] = Query(None, description="Lọc theo loại văn bản"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Document)
    if field:
        stmt = stmt.where(Document.field == field)
    if status:
        stmt = stmt.where(Document.status == status)
    if doc_type:
        stmt = stmt.where(Document.doc_type == doc_type)
    stmt = stmt.order_by(Document.issue_date.desc().nullslast()).limit(limit).offset(offset)

    result = await db.execute(stmt)
    docs = result.scalars().all()

    return [
        DocumentListItem(
            **{c: getattr(d, c) for c in DocumentListItem.model_fields if hasattr(d, c)},
            content_snippet=(d.content or "")[:200] if d.content else None,
        )
        for d in docs
    ]


@router.get(
    "/{doc_id}",
    response_model=DocumentWithTimeline,
    summary="Chi tiết văn bản + Timeline (UC-07 + UC-08)",
)
async def get_document(
    doc_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Trả về toàn văn + metadata + Timeline lịch sử + quan hệ văn bản.
    Timeline màu sắc:
      - issued    → Xanh lá (ngày ban hành)
      - effective → Xanh dương (ngày hiệu lực)
      - amended   → Cam (sửa đổi)
      - expired   → Đỏ (hết hiệu lực)
    """
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy văn bản.")

    from sqlalchemy.orm import selectinload

    rel_result = await db.execute(
        select(DocumentRelation)
        .options(
            selectinload(DocumentRelation.source_document),
            selectinload(DocumentRelation.target_document)
        )
        .where(
            (DocumentRelation.source_doc_id == doc_id) |
            (DocumentRelation.target_doc_id == doc_id)
        )
    )
    relations = rel_result.scalars().all()

    timeline = _build_timeline(doc, relations)

    mapped_relations = []
    for r in relations:
        if r.source_doc_id == doc_id:
            direction = "outgoing"
            related_doc = r.target_document
        else:
            direction = "incoming"
            related_doc = r.source_document
            
        mapped_relations.append(DocumentRelationOut(
            id=r.id,
            relation_type=r.relation_type,
            related_doc_id=related_doc.id,
            related_doc_title=related_doc.title,
            related_doc_number=related_doc.doc_number,
            direction=direction,
            description=r.description
        ))

    return DocumentWithTimeline(
        **{c: getattr(doc, c) for c in DocumentDetail.model_fields if hasattr(doc, c)},
        timeline=timeline,
        relations=mapped_relations,
    )


def _build_timeline(doc: Document, relations: list) -> list[TimelineEvent]:
    events = []

    if doc.issue_date:
        events.append(TimelineEvent(
            date=doc.issue_date,
            event_type="issued",
            label=f"Ban hành: {doc.doc_type or 'Văn bản'} số {doc.doc_number}",
        ))

    if doc.effective_date and doc.effective_date != doc.issue_date:
        events.append(TimelineEvent(
            date=doc.effective_date,
            event_type="effective",
            label="Có hiệu lực thi hành",
        ))

    for rel in relations:
        if rel.relation_type in ("AMENDS", "REPLACES") and rel.target_doc_id == doc.id:
            events.append(TimelineEvent(
                date=None,
                event_type="amended",
                label=f"Sửa đổi / bổ sung bởi văn bản khác",
                related_doc_id=rel.source_doc_id,
            ))

    if doc.expired_date:
        events.append(TimelineEvent(
            date=doc.expired_date,
            event_type="expired",
            label="Hết hiệu lực",
        ))

    events.sort(key=lambda e: e.date or __import__('datetime').date.max)
    return events
