import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.models.document import Document

from app.core.database import AsyncSessionLocal

@pytest.fixture
async def mock_doc():
    """Tạo một văn bản giả để test add to collection và add note."""
    doc_id = uuid.uuid4()
    doc = Document(
        id=doc_id,
        title="Văn bản test",
        doc_number="123/TEST",
        content="Nội dung test"
    )
    async with AsyncSessionLocal() as session:
        session.add(doc)
        await session.commit()
    
    yield str(doc_id)
    
    # Dọn dẹp sau khi test
    async with AsyncSessionLocal() as session:
        await session.delete(await session.get(Document, doc_id))
        await session.commit()

# ---------- Collections ----------

@pytest.mark.anyio
async def test_create_collection(auth_client: AsyncClient):
    """Test tạo collection thành công."""
    resp = await auth_client.post("/workspace/collections", json={
        "name": "Bộ sưu tập 1",
        "description": "Mô tả test",
        "is_shared": False
    })
    
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Bộ sưu tập 1"
    assert "id" in data
    return data["id"]

@pytest.mark.anyio
async def test_list_collections(auth_client: AsyncClient):
    """Test lấy danh sách collections."""
    # Tạo trước 1 collection
    await auth_client.post("/workspace/collections", json={"name": "Test Col"})
    
    resp = await auth_client.get("/workspace/collections")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

@pytest.mark.anyio
async def test_delete_collection(auth_client: AsyncClient):
    """Test xóa collection."""
    # Tạo
    create_resp = await auth_client.post("/workspace/collections", json={"name": "To delete"})
    col_id = create_resp.json()["id"]
    
    # Xóa
    del_resp = await auth_client.delete(f"/workspace/collections/{col_id}")
    assert del_resp.status_code == 200
    
    # Xóa lại -> 404
    del_resp2 = await auth_client.delete(f"/workspace/collections/{col_id}")
    assert del_resp2.status_code == 404

# ---------- Notes ----------

@pytest.mark.anyio
async def test_create_and_get_note(auth_client: AsyncClient, mock_doc):
    """Test tạo và lấy ghi chú."""
    fake_doc_id = mock_doc
    
    # Tạo note
    create_resp = await auth_client.post("/workspace/notes", json={
        "doc_id": fake_doc_id,
        "content": "Đây là ghi chú quan trọng."
    })
    assert create_resp.status_code == 201
    
    # Lấy danh sách note của doc đó
    get_resp = await auth_client.get(f"/workspace/notes/{fake_doc_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert len(data) == 1
    assert data[0]["content"] == "Đây là ghi chú quan trọng."
