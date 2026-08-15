"""
BM25 Search Service — Full-Text Search bằng PostgreSQL tsvector.
"""
import time
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.search import DocumentResult


async def bm25_search(
    session: AsyncSession,
    query: str,
    field: Optional[str] = None,
    filters: Optional[dict] = None,
    limit: int = 20,
) -> List[dict]:
    """
    Tìm kiếm từ khóa bằng PostgreSQL Full-Text Search (tsvector + ts_rank).
    Trả về list dict với id, score, rank.
    """
    start = time.perf_counter()

    # Build query với filter lĩnh vực và filter phụ
    filters = filters or {}
    field_filter = "AND field ILIKE :field" if field else ""
    status_filter = "AND status = :status" if filters.get("status") else ""
    type_filter = "AND doc_type = :doc_type" if filters.get("doc_type") else ""
    year_filter = "AND EXTRACT(YEAR FROM issue_date) >= :year_from" if filters.get("year_from") else ""
    issuing_body_filter = "AND issuing_body ILIKE :issuing_body" if filters.get("issuing_body") else ""

    sql = text(f"""
        SELECT
            id,
            doc_number,
            title,
            doc_type,
            issuing_body,
            field,
            issue_date,
            status,
            source_url,
            content,
            ts_rank(
                search_vector,
                plainto_tsquery('simple', unaccent(:query))
            ) AS score
        FROM documents
        WHERE
            search_vector @@ plainto_tsquery('simple', unaccent(:query))
            {field_filter}
            {status_filter}
            {type_filter}
            {year_filter}
            {issuing_body_filter}
        ORDER BY score DESC
        LIMIT :limit
    """)

    params = {"query": query, "limit": limit}
    if field:
        params["field"] = f"%{field}%"
    if filters.get("status"): params["status"] = filters["status"]
    if filters.get("doc_type"): params["doc_type"] = filters["doc_type"]
    if filters.get("year_from"): params["year_from"] = filters["year_from"]
    if filters.get("issuing_body"): params["issuing_body"] = f"%{filters['issuing_body']}%"

    result = await session.execute(sql, params)
    rows = result.mappings().all()

    elapsed_ms = (time.perf_counter() - start) * 1000

    docs = []
    for i, row in enumerate(rows):
        content = row["content"] or ""
        # Tìm snippet liên quan đến query
        snippet = _extract_snippet(content, query)
        docs.append({
            "id": row["id"],
            "doc_number": row["doc_number"] or "",
            "title": row["title"],
            "doc_type": row["doc_type"],
            "issuing_body": row["issuing_body"],
            "field": row["field"],
            "issue_date": row["issue_date"],
            "status": row["status"],
            "source_url": row["source_url"],
            "content_snippet": snippet,
            "score": float(row["score"]),
            "rank": i + 1,
        })

    return docs, elapsed_ms


def _extract_snippet(content: str, query: str, max_len: int = 200) -> str:
    """Trích đoạn nội dung liên quan nhất đến query."""
    if not content:
        return ""
    query_words = query.lower().split()
    content_lower = content.lower()

    # Tìm vị trí keyword đầu tiên
    best_pos = 0
    for word in query_words:
        pos = content_lower.find(word)
        if pos >= 0:
            best_pos = max(0, pos - 50)
            break

    snippet = content[best_pos: best_pos + max_len]
    if best_pos > 0:
        snippet = "..." + snippet
    if best_pos + max_len < len(content):
        snippet = snippet + "..."
    return snippet
