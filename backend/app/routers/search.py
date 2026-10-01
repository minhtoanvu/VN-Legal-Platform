"""
Search Router — /search (keyword / semantic / hybrid)

3 modes:
  - keyword  : BM25 (PostgreSQL tsvector) — cho cả Guest và User (UC-04: Actor = "Tất cả")
  - semantic : Vector similarity (pgvector HNSW) — yêu cầu đăng nhập (UC-05: Actor = "User, Enterprise")
  - hybrid   : BM25 + Semantic với Reciprocal Rank Fusion (RRF) — yêu cầu đăng nhập
"""
import time

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_optional_user
from app.schemas.search import DocumentResult, SearchRequest, SearchResponse
from app.services import semantic_service
from app.services.bm25_service import bm25_search
from app.services.rrf_service import merge_by_score, reciprocal_rank_fusion

router = APIRouter()


@router.post(
    "",
    response_model=SearchResponse,
    summary="Tìm kiếm văn bản pháp lý",
    description="""
Tìm kiếm với 3 chế độ:
- **keyword**: Full-text search BM25 (nhanh, không cần AI) — **Chách dùng không cần đăng nhập**
- **semantic**: Semantic search bằng vector embedding — yêu cầu đăng nhập (UC-05)
- **hybrid**: Kết hợp BM25 + Semantic với RRF — yêu cầu đăng nhập
    """,
)
async def search(
    body: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_optional_user),
):
    # Phân quyền theo mode: semantic và hybrid yêu cầu User đăng nhập (UC-05)
    if body.mode in ("semantic", "hybrid") and current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tìm kiếm ngữ nghĩa và hybrid yêu cầu đăng nhập. Vui lòng đăng nhập hoặc dùng chế độ tìm kiếm từ khóa.",
            headers={"WWW-Authenticate": "Bearer"},
        )
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

    # Giới hạn offset tối đa để chống tràn RAM khi tính toán RRF
    MAX_OFFSET = 200
    if body.offset > MAX_OFFSET:
        raise HTTPException(
            status_code=400,
            detail=f"Để đảm bảo hiệu năng, hệ thống chỉ hỗ trợ xem tối đa {MAX_OFFSET} kết quả đầu tiên."
        )

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
    summary="Tìm kiếm nhanh (GET) — keyword không cần đăng nhập",
)
async def search_get(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm"),
    mode: str = Query(default="keyword", description="keyword | semantic | hybrid"),
    field: str | None = Query(default=None, description="Lọc theo lĩnh vực"),
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_optional_user),
):
    """GET endpoint để dễ test trên Swagger / browser. Keyword mode không cần đăng nhập."""
    body = SearchRequest(query=q, mode=mode, field=field, limit=limit)
    return await search(body=body, db=db, current_user=current_user)
