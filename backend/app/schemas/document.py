"""
Pydantic schemas cho Documents endpoints.
Theo PhanTichHeThong_v2_Fixed.docx mục 10.1 và UC-07.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime


class DocumentBase(BaseModel):
    id: UUID
    doc_number: str
    title: str
    doc_type: Optional[str]
    issuing_body: Optional[str]
    field: Optional[str]
    issue_date: Optional[date]
    effective_date: Optional[date]
    expired_date: Optional[date]
    status: str           # active / expired / amended
    source_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentListItem(DocumentBase):
    """Dùng cho danh sách tìm kiếm — không có content đầy đủ."""
    content_snippet: Optional[str] = None   # 200 ký tự đầu


class DocumentDetail(DocumentBase):
    """Dùng cho trang chi tiết — có full content."""
    content: Optional[str]


class DocumentRelationOut(BaseModel):
    """Quan hệ văn bản — dùng cho Knowledge Graph và Timeline."""
    id: UUID
    relation_type: str       # GUIDES / AMENDS / REPLACES / REVOKES / CITES / IMPLEMENTS
    related_doc_id: UUID
    related_doc_title: str
    related_doc_number: str
    direction: str           # outgoing / incoming
    description: Optional[str]

    model_config = {"from_attributes": True}


class TimelineEvent(BaseModel):
    """Một mốc trong Timeline lịch sử văn bản (UC-08)."""
    date: Optional[date]
    event_type: str          # issued / effective / amended / expired
    label: str               # Mô tả ngắn
    related_doc_id: Optional[UUID] = None
    related_doc_title: Optional[str] = None


class DocumentWithTimeline(DocumentDetail):
    """Document + Timeline events cho trang chi tiết (UC-07 + UC-08)."""
    timeline: List[TimelineEvent] = []
    relations: List[DocumentRelationOut] = []
