"""
Pydantic schemas cho Search endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from uuid import UUID
from datetime import date


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    mode: Literal["keyword", "semantic", "hybrid"] = "hybrid"
    field: Optional[str] = None          # Filter theo lĩnh vực
    doc_type: Optional[str] = None       # Filter theo loại văn bản
    filters: Optional[dict] = None       # Lọc chi tiết (cơ quan, năm, tình trạng...)
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
    doc_type: Optional[str]
    issuing_body: Optional[str]
    field: Optional[str]
    issue_date: Optional[date]
    status: str
    source_url: Optional[str]
    # Snippet của nội dung liên quan (150 ký tự)
    content_snippet: str
    score: float                          # RRF score hoặc similarity score

    model_config = {"from_attributes": True}


class SearchResponse(BaseModel):
    query: str
    mode: str
    total: int
    results: List[DocumentResult]
    took_ms: float                        # Thời gian xử lý (milliseconds)
