import pytest
from httpx import AsyncClient
import uuid

# Mock the rag_generate_stream to avoid hitting real Gemini API
async def mock_rag_generate_stream(*args, **kwargs):
    yield "Đây là "
    yield "câu trả lời "
    yield "mock từ AI."
    yield "__CITATIONS__[{\"doc_id\": \"123\", \"title\": \"Luật Mock\"}]"

@pytest.fixture(autouse=True)
def mock_rag_service(monkeypatch):
    from app.routers import ai
    monkeypatch.setattr(ai, "rag_generate_stream", mock_rag_generate_stream)

# ---------- Chat (RAG) ----------

@pytest.mark.anyio
async def test_ai_chat_success(auth_client: AsyncClient):
    """Test gửi câu hỏi thành công và nhận Stream RAG."""
    resp = await auth_client.post("/ai/chat", json={
        "question": "Thử việc tối đa bao nhiêu ngày?"
    })
    
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    # Đọc stream data
    content = resp.text
    assert "Đây là" in content
    assert "câu trả lời" in content
    assert "[DONE]" in content

@pytest.mark.anyio
async def test_ai_chat_empty_question(auth_client: AsyncClient):
    """Test gửi câu hỏi rỗng -> 422."""
    resp = await auth_client.post("/ai/chat", json={
        "question": "   "
    })
    
    assert resp.status_code == 422
    assert "không được để trống" in resp.json()["detail"]

@pytest.mark.anyio
async def test_ai_chat_unauthorized(client: AsyncClient):
    """Guest không được dùng AI Chat -> 401/403."""
    resp = await client.post("/ai/chat", json={
        "question": "Luật lao động"
    })
    
    assert resp.status_code in (401, 403)


# ---------- Summarize ----------

@pytest.mark.anyio
async def test_ai_summarize_not_found(client: AsyncClient):
    """Test tóm tắt văn bản không tồn tại -> 404."""
    fake_uuid = str(uuid.uuid4())
    resp = await client.post("/ai/summarize", json={
        "doc_id": fake_uuid
    })
    
    assert resp.status_code == 404
