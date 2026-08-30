"""
RAG Service Module
"""

import asyncio
import time
from typing import AsyncGenerator, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.bm25_service import bm25_search
from app.services import semantic_service
from app.services.rrf_service import reciprocal_rank_fusion

TOP_K_RETRIEVE = 20
TOP_K_RERANK = 10
LLM_TIMEOUT_SEC = 10

SYSTEM_PROMPT_TEMPLATE = """Bạn là trợ lý pháp lý AI chuyên về luật Việt Nam.
Nhiệm vụ: Trả lời câu hỏi pháp lý dựa HOÀN TOÀN vào TÀI LIỆU THAM KHẢO được cung cấp bên dưới.

QUY TẮC BẮT BUỘC:
1. Nếu câu hỏi liên quan đến pháp lý, CHỈ sử dụng thông tin từ [TÀI LIỆU THAM KHẢO]. KHÔNG bịa đặt hoặc suy diễn thông tin bên ngoài.
2. PHẢI trích dẫn điều luật hoặc số hiệu văn bản (ví dụ: "Theo Điều 3...", "Căn cứ khoản 1...").
3. Nếu tài liệu không có thông tin, hãy trả lời chính xác: "Dựa trên dữ liệu hiện tại, tôi không tìm thấy quy định pháp luật nào đề cập đến vấn đề này."
4. Nếu người dùng chỉ chào hỏi, hãy phản hồi lịch sự như một trợ lý.
5. Trả lời bằng tiếng Việt, phân chia đoạn văn mạch lạc, rõ ràng.

[TÀI LIỆU THAM KHẢO]
{context}"""


async def rag_retrieve(
    session: AsyncSession,
    question: str,
    field: Optional[str] = None,
) -> list[dict]:
    import logging
    log = logging.getLogger(__name__)


    t0 = time.perf_counter()
    bm25_docs = []
    try:
        bm25_res = await bm25_search(session=session, query=question, field=field, limit=TOP_K_RETRIEVE)
        bm25_docs = bm25_res[0] if isinstance(bm25_res, tuple) else bm25_res
    except Exception as e:
        log.warning(f"BM25 failed: {e}")
    log.info(f"BM25 done in {(time.perf_counter()-t0)*1000:.0f}ms, got {len(bm25_docs)} docs")


    t1 = time.perf_counter()
    sem_raw = []
    try:
        index_ready = await semantic_service.is_index_ready(session)
        if index_ready:
            sem_raw = await semantic_service.semantic_search(
                session=session, query=question, top_k=TOP_K_RETRIEVE
            )
    except Exception as e:
        log.warning(f"Semantic search failed: {e}")
    log.info(f"Semantic done in {(time.perf_counter()-t1)*1000:.0f}ms, got {len(sem_raw)} docs")

    sem_docs = [
        {
            "doc_id": str(r.get("id", r.get("doc_id", ""))),
            "title": r.get("title", ""),
            "doc_number": r.get("doc_number", ""),
            "snippet": r.get("content_snippet", r.get("snippet", "")),
            "score": float(r.get("score", 0.0)),
            "rank": i + 1,
        }
        for i, r in enumerate(sem_raw)
    ]

    if sem_docs:
        merged = reciprocal_rank_fusion(bm25_docs, sem_docs, top_k=TOP_K_RERANK)
    else:
        from app.services.rrf_service import merge_by_score
        merged = merge_by_score([bm25_docs], top_k=TOP_K_RERANK)

    return merged[:TOP_K_RERANK]


def _build_context(chunks: list[dict]) -> tuple[str, list[dict]]:
    context_parts = []
    citations = []

    for i, chunk in enumerate(chunks, 1):
        doc_number = chunk.get("doc_number", f"Doc {i}")
        title = chunk.get("title", "")
        snippet = chunk.get("snippet", chunk.get("content_snippet", ""))

        context_parts.append(
            f"[{i}] {doc_number} — {title}\n{snippet}"
        )
        citations.append({
            "index": i,
            "doc_id": str(chunk.get("doc_id") or chunk.get("id", "")),
            "doc_number": doc_number,
            "title": title,
        })

    return "\n\n---\n\n".join(context_parts), citations


async def rag_generate_stream(
    session: AsyncSession,
    question: str,
    field: Optional[str] = None,
    history: Optional[list[dict]] = None
) -> AsyncGenerator[str, None]:
    import logging, json
    log = logging.getLogger(__name__)

    yield "*(⏳ Đang tra cứu cơ sở dữ liệu pháp luật...)*\n\n"

    t0 = time.perf_counter()
    chunks = await rag_retrieve(session, question, field)
    log.info(f"Retrieve total: {(time.perf_counter()-t0)*1000:.0f}ms, {len(chunks)} chunks")

    yield "*(⏳ Đang tổng hợp câu trả lời từ AI...)*\n\n"

    context, citations = _build_context(chunks)

    system_instruction = SYSTEM_PROMPT_TEMPLATE.format(
        context=context or "(Không có tài liệu liên quan)"
    )

    contents = []
    if history:
        for msg in history:
            role = "user" if msg.get("role") == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})
    
    contents.append({"role": "user", "parts": [{"text": question}]})

    try:
        from app.core.config import settings
        from google import genai as google_genai
        from app.core.circuit_breaker import llm_circuit_breaker, CircuitState

        if not settings.gemini_api_key:
            yield "⚠️ Chưa cấu hình GEMINI_API_KEY. Vui lòng thêm key vào file .env."
            return

        # Cập nhật trạng thái cầu dao
        llm_circuit_breaker._update_state()
        if llm_circuit_breaker.state == CircuitState.OPEN:
            yield "⚠️ Hệ thống AI đang tạm gián đoạn (Circuit Breaker OPEN). Đây là kết quả tìm kiếm:\n\n"
            for i, chunk in enumerate(chunks, 1):
                yield f"**[{i}] {chunk.get('doc_number', '')}** — {chunk.get('title', '')}\n\n"
            return

        client = google_genai.Client(api_key=settings.gemini_api_key)

        t1 = time.perf_counter()
        stream = await client.aio.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=contents,
            config=google_genai.types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1024,
                system_instruction=system_instruction,
            )
        )

        iterator = stream.__aiter__()
        try:
            first_chunk = await asyncio.wait_for(iterator.__anext__(), timeout=LLM_TIMEOUT_SEC)
            log.info(f"First token in {(time.perf_counter()-t1)*1000:.0f}ms")
            if first_chunk.text:
                yield first_chunk.text
        except StopAsyncIteration:
            pass

        async for chunk in iterator:
            if chunk.text:
                yield chunk.text

        llm_circuit_breaker.record_success()
        yield f"\n\n__CITATIONS__:{json.dumps(citations, ensure_ascii=False)}"

    except asyncio.TimeoutError:
        llm_circuit_breaker.record_failure()
        yield "⚠️ AI phản hồi quá 10 giây (Timeout), đây là kết quả tìm kiếm thay thế:\n\n"
        for i, chunk in enumerate(chunks, 1):
            yield f"**[{i}] {chunk.get('doc_number', '')}** — {chunk.get('title', '')}\n\n"

    except Exception as e:
        llm_circuit_breaker.record_failure()
        log.error(f"Generate error: {e}")
        yield f"Lỗi kết nối AI: {type(e).__name__}. Vui lòng thử lại sau."
