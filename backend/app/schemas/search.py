"""
Pydantic schemas cho Search endpoints.
"""
from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    mode: Literal["keyword", "semantic", "hybrid"] = "hybrid"
    field: str | None = None          # Filter theo lĩnh vực
    doc_type: str | None = None       # Filter theo loại văn bản
    filters: dict | None = None       # Lọc chi tiết (cơ quan, năm, tình trạng...)
    limit: int = Field(default=10, ge=1, le=50)
    offset: int = Field(default=0, ge=0)

    model_config = {"json_schema_extra": {
        "example": {
            "query": "nghỉ phép năm bao nhiêu ngày",
            "mode": "hybrid",
            "field": "labor",
            "limit": 10
        }
    }}


class DocumentResult(BaseModel):
    id: UUID
    doc_number: str
    title: str
    doc_type: str | None
    issuing_body: str | None
    field: str | None
    issue_date: date | None
    status: str
    source_url: str | None
    # Snippet của nội dung liên quan (150 ký tự)
    content_snippet: str
    score: float                          # RRF score hoặc similarity score

    model_config = {"from_attributes": True}


class SearchResponse(BaseModel):
    query: str
    mode: str
    total: int
    results: list[DocumentResult]
    took_ms: float                        # Thời gian xử lý (milliseconds)
