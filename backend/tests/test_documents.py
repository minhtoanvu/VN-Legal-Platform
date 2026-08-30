import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import datetime
from app.models.document import Document, DocumentRelation
from app.core.database import AsyncSessionLocal

@pytest.fixture
async def mock_docs_and_relations():
    """Tạo mock documents và relations để test get/list."""
    doc_1_id = uuid.uuid4()
    doc_2_id = uuid.uuid4()
    
    doc1 = Document(
        id=doc_1_id,
        title="Luật Test 1",
        doc_number="01/TEST",
        field="Dân sự",
        status="active",
        doc_type="Luật",
        issue_date=datetime.date(2020, 1, 1),
        effective_date=datetime.date(2020, 2, 1),
        content="Nội dung luật 1"
    )
    
    doc2 = Document(
        id=doc_2_id,
        title="Nghị định Test 2",
        doc_number="02/TEST",
        field="Hình sự",
        status="expired",
        doc_type="Nghị định",
        issue_date=datetime.date(2021, 1, 1),
        expired_date=datetime.date(2023, 1, 1),
        content="Nội dung luật 2"
    )
    
    relation = DocumentRelation(
        id=uuid.uuid4(),
        source_doc_id=doc_2_id,
        target_doc_id=doc_1_id,
        relation_type="AMENDS",
        description="Nghị định 02 sửa đổi Luật 01"
    )
    
    async with AsyncSessionLocal() as session:
        session.add_all([doc1, doc2, relation])
        await session.commit()
    
    yield {"doc1": str(doc_1_id), "doc2": str(doc_2_id)}
    
    # Dọn dẹp
    async with AsyncSessionLocal() as session:
        await session.delete(await session.get(DocumentRelation, relation.id))
        await session.delete(await session.get(Document, doc_1_id))
        await session.delete(await session.get(Document, doc_2_id))
        await session.commit()

# ---------- Documents API ----------

@pytest.mark.anyio
async def test_list_documents(client: AsyncClient, mock_docs_and_relations):
    """Test lấy danh sách văn bản và filter."""
    resp = await client.get("/documents")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2
    
    # Test filter status
    resp_active = await client.get("/documents?status=active")
    assert resp_active.status_code == 200
    assert all(d["status"] == "active" for d in resp_active.json())
    
    # Test filter field
    resp_field = await client.get("/documents?field=Hình sự")
    assert resp_field.status_code == 200
    assert all(d["field"] == "Hình sự" for d in resp_field.json())

@pytest.mark.anyio
async def test_get_document_detail_and_timeline(client: AsyncClient, mock_docs_and_relations):
    """Test lấy chi tiết, timeline và relations của văn bản."""
    doc1_id = mock_docs_and_relations["doc1"]
    
    resp = await client.get(f"/documents/{doc1_id}")
    assert resp.status_code == 200
    data = resp.json()
    
    assert data["id"] == doc1_id
    assert data["title"] == "Luật Test 1"
    
    # Kiểm tra timeline
    timeline = data.get("timeline", [])
    assert len(timeline) >= 2
    # Có event 'issued' và 'effective', cộng thêm 'amended' do có relation
    event_types = [t["event_type"] for t in timeline]
    assert "issued" in event_types
    assert "effective" in event_types
    assert "amended" in event_types
    
    # Kiểm tra relations
    relations = data.get("relations", [])
    assert len(relations) == 1
    assert relations[0]["relation_type"] == "AMENDS"
    assert relations[0]["direction"] == "incoming"

@pytest.mark.anyio
async def test_get_document_not_found(client: AsyncClient):
    """Test lấy văn bản không tồn tại."""
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/documents/{fake_id}")
    assert resp.status_code == 404
