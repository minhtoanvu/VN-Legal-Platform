import uuid

import pytest
from httpx import AsyncClient

from app.core.database import AsyncSessionLocal
from app.models.document import Document


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

# ---------- Enterprise Shared Collections ----------

@pytest.mark.anyio
async def test_shared_collection(client: AsyncClient, mock_doc):
    """Test tính năng Enterprise Sharing: User A tạo thư mục shared, User B cùng công ty có thể xem."""
    from app.core.database import AsyncSessionLocal
    from app.models.user import Organization, User
    from app.core.security import hash_password, create_access_token
    import uuid
    from app.core.security import hash_password, create_access_token

    org_id = uuid.uuid4()
    u1_id = uuid.uuid4()
    u2_id = uuid.uuid4()
    
    # Tạo email ngẫu nhiên để không bị duplicate key error khi chạy test nhiều lần
    u1_email = f"ent1_{u1_id.hex[:6]}@test.com"
    u2_email = f"ent2_{u2_id.hex[:6]}@test.com"

    async with AsyncSessionLocal() as session:
        # 1. Tạo tổ chức
        org = Organization(id=org_id, name="Test Corp")
        # 2. Tạo 2 user chung tổ chức, role=enterprise
        u1_pwd = await hash_password("pass")
        u2_pwd = await hash_password("pass")
        u1 = User(id=u1_id, email=u1_email, password_hash=u1_pwd, role="enterprise", organization_id=org_id)
        u2 = User(id=u2_id, email=u2_email, password_hash=u2_pwd, role="enterprise", organization_id=org_id)
        
        session.add(org)
        session.add_all([u1, u2])
        await session.commit()

    # 3. Đăng nhập User 1
    t1 = create_access_token(data={"sub": str(u1_id), "email": u1_email, "role": "enterprise"})
    c1 = AsyncClient(transport=client._transport, base_url="http://test", headers={"Authorization": f"Bearer {t1}"})

    # User 1 tạo collection shared
    c1_resp = await c1.post("/workspace/collections", json={
        "name": "Shared by Ent1",
        "description": "",
        "is_shared": True
    })
    assert c1_resp.status_code == 201
    col_id = c1_resp.json()["id"]

    # User 1 thêm văn bản vào collection
    await c1.post(f"/workspace/collections/{col_id}/docs", json={"doc_id": mock_doc})

    # 4. Đăng nhập User 2
    t2 = create_access_token(data={"sub": str(u2_id), "email": u2_email, "role": "enterprise"})
    c2 = AsyncClient(transport=client._transport, base_url="http://test", headers={"Authorization": f"Bearer {t2}"})

    # User 2 lấy danh sách thư mục được share (UC-18)
    shared_resp = await c2.get("/workspace/shared-collections")
    assert shared_resp.status_code == 200
    shared_data = shared_resp.json()
    assert len(shared_data) >= 1
    assert any(c["id"] == col_id for c in shared_data)

    # User 2 xem nội dung văn bản bên trong thư mục shared
    docs_resp = await c2.get(f"/workspace/collections/{col_id}/docs")
    assert docs_resp.status_code == 200
    docs_data = docs_resp.json()
    assert len(docs_data) == 1
    assert docs_data[0]["id"] == mock_doc
