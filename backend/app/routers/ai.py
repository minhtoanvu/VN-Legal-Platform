"""
AI Router — /ai
UC-04: Hỏi đáp pháp luật qua RAG (AI Chat)
UC-12: Tóm tắt văn bản

Endpoints:
  POST /ai/chat      — Streaming RAG response (Server-Sent Events)
  POST /ai/summarize — Tóm tắt toàn văn một văn bản
"""
import json
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.document import Document
from app.models.workspace import QueryLog
from app.services.rag_service import rag_generate_stream
from app.core.dependencies import get_current_active_user, limiter
from fastapi import Request
import time

router = APIRouter()

class AIChatRequest:
    def __init__(self, question: str, field: Optional[str] = None):
        self.question = question
        self.field = field


from typing import List
from pydantic import BaseModel, model_validator


class ChatRequest(BaseModel):
    question: Optional[str] = None
    query: Optional[str] = None
    field: Optional[str] = None
    session_id: Optional[str] = None
    context_doc_ids: Optional[List[str]] = None
    history: Optional[List[dict]] = None

    @model_validator(mode="after")
    def resolve_question(self):
        if not self.question and self.query:
            self.question = self.query
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "Thử việc tối đa bao nhiêu ngày theo luật lao động?",
            }
        }
    }


class SummarizeRequest(BaseModel):
    doc_id: UUID


@router.post(
    "/chat",
    summary="Hỏi đáp pháp luật (RAG Streaming) - UC-04",
    description="""
Gửi câu hỏi, nhận câu trả lời streaming kèm Citations. Đã bật tính năng chống Spam (Rate Limiter).
""",
)
@limiter.limit("5/minute")
async def ai_chat(
    request: Request,
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    if not body.question or not body.question.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Câu hỏi không được để trống."
        )

    async def event_stream():
        start_time = time.perf_counter()
        full_response_text = ""
        try:
            async for token in rag_generate_stream(
                session=db,
                question=body.question,
                field=body.field,
                history=body.history,
            ):
                if not token.startswith("__CITATIONS__"):
                    full_response_text += token
                yield f"data: {json.dumps({'text': token}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield "data: [DONE]\n\n"
            # Lưu log truy vấn
            try:
                duration_ms = int((time.perf_counter() - start_time) * 1000)
                query_log = QueryLog(
                    query_text=body.question,
                    query_type="ai_chat",
                    response={"text": full_response_text},
                    duration_ms=duration_ms,
                )
                db.add(query_log)
                await db.commit()
            except Exception as e:
                print("Failed to save query log:", str(e))

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@router.post(
    "/summarize",
    summary="Tóm tắt văn bản pháp luật - UC-12",
)
async def summarize_document(
    body: SummarizeRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Document).where(Document.id == body.doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy văn bản.")

    content_preview = (doc.content or "")[:3000]
    if not content_preview:
        raise HTTPException(status_code=422, detail="Văn bản không có nội dung để tóm tắt.")

    summary_question = f"""
Tóm tắt ngắn gọn văn bản pháp luật sau (tối đa 300 từ):
- Tên văn bản: {doc.title}
- Số hiệu: {doc.doc_number}
- Nội dung:
{content_preview}
"""

    tokens = []
    async for token in rag_generate_stream(session=db, question=summary_question):
        if not token.startswith("__CITATIONS__"):
            tokens.append(token)

    return {
        "doc_id": str(doc.id),
        "doc_number": doc.doc_number,
        "title": doc.title,
        "summary": "".join(tokens).strip(),
    }
