"""
Search Router — /search (keyword / semantic / hybrid)

3 modes:
  - keyword  : BM25 (PostgreSQL tsvector)
  - semantic : Vector similarity (pgvector HNSW) — cần embedding model
  - hybrid   : BM25 + Semantic với Reciprocal Rank Fusion (RRF)
"""
import time
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.search import SearchRequest, SearchResponse, DocumentResult
from app.services.bm25_service import bm25_search
from app.services.rrf_service import reciprocal_rank_fusion, merge_by_score
from app.services import semantic_service

router = APIRouter()


@router.post(
    "",
    response_model=SearchResponse,
    summary="Tìm kiếm văn bản pháp lý",
    description="""
Tìm kiếm với 3 chế độ:
- **keyword**: Full-text search BM25 (nhanh, không cần AI)
- **semantic**: Semantic search bằng vector embedding (cần model loaded)
- **hybrid**: Kết hợp BM25 + Semantic với Reciprocal Rank Fusion
    """,
)
async def search(
    body: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    start_total = time.perf_counter()

    bm25_docs = []
    semantic_docs = []

    if body.mode in ("keyword", "hybrid"):
        bm25_docs, _ = await bm25_search(
            session=db,
            query=body.query,
            field=body.field,
            filters=body.filters,
            limit=body.limit + body.offset,
        )

    if body.mode in ("semantic", "hybrid"):
        # Kiểm tra HNSW index đã sẵn sàng chưa
        index_ready = await semantic_service.is_index_ready(db)
        if index_ready:
            semantic_docs = await semantic_service.semantic_search(
                session=db,
                query=body.query,
                field=body.field,
                filters=body.filters,
                top_k=body.limit + body.offset,
            )
        else:
            # Fallback BM25 nếu embedding chưa sẵn sàng
            semantic_docs, _ = await bm25_search(
                session=db, query=body.query, field=body.field, filters=body.filters, limit=body.limit + body.offset
            )
            for i, doc in enumerate(semantic_docs):
                doc["rank"] = i + 1

    # Merge kết quả
    if body.mode == "hybrid":
        merged = reciprocal_rank_fusion(bm25_docs, semantic_docs, top_k=body.limit + body.offset)
    elif body.mode == "keyword":
        merged = merge_by_score([bm25_docs], top_k=body.limit + body.offset)
    else:
        merged = merge_by_score([semantic_docs], top_k=body.limit + body.offset)

    # Phân trang
    paginated = merged[body.offset: body.offset + body.limit]

    elapsed_ms = (time.perf_counter() - start_total) * 1000

    results = [DocumentResult(**doc) for doc in paginated]

    return SearchResponse(
        query=body.query,
        mode=body.mode,
        total=len(merged),
        results=results,
        took_ms=round(elapsed_ms, 2),
    )


@router.get(
    "",
    response_model=SearchResponse,
    summary="Tìm kiếm nhanh (GET)",
)
async def search_get(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    mode: str = Query(default="keyword", description="keyword | semantic | hybrid"),
    field: Optional[str] = Query(default=None, description="Lọc theo lĩnh vực"),
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """GET endpoint để dễ test trên Swagger / browser."""
    body = SearchRequest(query=q, mode=mode, field=field, limit=limit)
    return await search(body, db)
