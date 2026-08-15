"""
Semantic Search Service — pgvector HNSW Cosine Similarity
Truy vấn theo ngữ nghĩa bằng cách:
  1. Embed câu query bằng bkai bi-encoder (768D)
  2. Tìm top-K chunks gần nhất qua HNSW index
  3. Trả về danh sách (doc_id, score) để RRF merge

Theo PhanTichHeThong_v2_Fixed.docx mục 10.2 và UC-05.
"""

import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import asyncio
from typing import Optional
from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"
_model = None   # lazy-load


def _get_model():
    """Lazy-load model để không làm chậm startup của FastAPI."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(MODEL_NAME, device="cpu")
        except Exception as e:
            raise RuntimeError(f"Không thể tải model '{MODEL_NAME}': {e}")
    return _model


def embed_query(query: str) -> list[float]:
    """Chuyển câu query thành vector 768D."""
    model = _get_model()
    vec = model.encode(query, normalize_embeddings=True, show_progress_bar=False)
    return vec.tolist()


async def semantic_search(
    session: AsyncSession,
    query: str,
    field: Optional[str] = None,
    filters: Optional[dict] = None,
    top_k: int = 20,
) -> list[dict]:
    """
    Tìm top-K document chunks gần nhất theo Cosine Similarity (HNSW).
    Nếu model chưa load được (thiếu RAM...), trả về [] để caller fallback.
    """
    try:
        query_vec = await asyncio.get_event_loop().run_in_executor(
            None, embed_query, query
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Semantic model unavailable, skipping: {e}")
        return []

    filters = filters or {}
    field_filter = "AND d.field ILIKE :field" if field else ""
    status_filter = "AND d.status = :status" if filters.get("status") else ""
    type_filter = "AND d.doc_type = :doc_type" if filters.get("doc_type") else ""
    year_filter = "AND EXTRACT(YEAR FROM d.issue_date) >= :year_from" if filters.get("year_from") else ""
    issuing_body_filter = "AND d.issuing_body ILIKE :issuing_body" if filters.get("issuing_body") else ""

    sql = text(f"""
        SELECT
            d.id,
            d.doc_number,
            d.title,
            d.doc_type,
            d.issuing_body,
            d.field,
            d.issue_date,
            d.status,
            d.source_url,
            LEFT(dc.content_chunk, 250) AS content_snippet,
            1 - (dc.embedding <=> CAST(:vec AS vector)) AS score
        FROM document_chunks dc
        JOIN documents d ON dc.document_id = d.id
        WHERE dc.embedding IS NOT NULL
        {field_filter}
        {status_filter}
        {type_filter}
        {year_filter}
        {issuing_body_filter}
        ORDER BY dc.embedding <=> CAST(:vec AS vector) ASC
        LIMIT :top_k
    """)

    params = {"vec": str(query_vec), "top_k": top_k * 3}
    if field:
        params["field"] = f"%{field}%"
    if filters.get("status"): params["status"] = filters["status"]
    if filters.get("doc_type"): params["doc_type"] = filters["doc_type"]
    if filters.get("year_from"): params["year_from"] = filters["year_from"]
    if filters.get("issuing_body"): params["issuing_body"] = f"%{filters['issuing_body']}%"

    result = await session.execute(sql, params)

    rows = result.mappings().all()
    docs = []
    seen = set()
    for row in rows:
        if row["id"] not in seen:
            seen.add(row["id"])
            doc = dict(row)
            doc["score"] = float(doc["score"])
            docs.append(doc)
            if len(docs) == top_k:
                break
                
    for i, doc in enumerate(docs):
        doc["rank"] = i + 1
        
    return docs


async def is_index_ready(session: AsyncSession) -> bool:
    """Kiểm tra HNSW index đã tồn tại chưa."""
    result = await session.execute(text("""
        SELECT 1 FROM pg_indexes
        WHERE tablename = 'document_chunks'
        AND indexname = 'idx_chunks_embedding_hnsw'
    """))
    return result.scalar() is not None
