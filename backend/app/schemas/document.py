"""
Pydantic schemas cho Documents endpoints.
Theo PhanTichHeThong_v2_Fixed.docx mục 10.1 và UC-07.
"""
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentBase(BaseModel):
    id: UUID
    doc_number: str
    title: str
    doc_type: str | None
    issuing_body: str | None
    field: str | None
    issue_date: date | None
    effective_date: date | None
    expired_date: date | None
    status: str           # active / expired / amended
    source_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListItem(DocumentBase):
    """Dùng cho danh sách tìm kiếm — không có content đầy đủ."""
    content_snippet: str | None = None   # 200 ký tự đầu


class DocumentDetail(DocumentBase):
    """Dùng cho trang chi tiết — có full content."""
    content: str | None


class DocumentRelationOut(BaseModel):
    """Quan hệ văn bản — dùng cho Knowledge Graph và Timeline."""
    id: UUID
    relation_type: str       # GUIDES / AMENDS / REPLACES / REVOKES / CITES / IMPLEMENTS
    related_doc_id: UUID
    related_doc_title: str
    related_doc_number: str
    direction: str           # outgoing / incoming
    description: str | None

    model_config = {"from_attributes": True}


class TimelineEvent(BaseModel):
    """Một mốc trong Timeline lịch sử văn bản (UC-08)."""
    date: date | None
    event_type: str          # issued / effective / amended / expired
    label: str               # Mô tả ngắn
    related_doc_id: UUID | None = None
    related_doc_title: str | None = None


class DocumentWithTimeline(DocumentDetail):
    """Document + Timeline events cho trang chi tiết (UC-07 + UC-08)."""
    timeline: list[TimelineEvent] = []
    relations: list[DocumentRelationOut] = []
