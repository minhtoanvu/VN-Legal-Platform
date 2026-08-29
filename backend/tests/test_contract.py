import pytest
from httpx import AsyncClient
from io import BytesIO

@pytest.fixture(autouse=True)
def mock_contract_service(monkeypatch):
    """Giả lập process_contract để không gọi LLM thật khi test API."""
    from app.routers import contract
    from app.schemas.contract import ContractReport, ClauseAnalysis, RiskLevel
    
    async def mock_process_contract(session, file_bytes, filename):
        return ContractReport(
            filename=filename,
            total_clauses=1,
            analyses=[
                ClauseAnalysis(
                    clause_title="Điều 1",
                    clause_text="Test clause",
                    step1_identification="Test",
                    step2_legal_comparison="Test",
                    step3_risk_evaluation="Test",
                    step4_suggestion="Test",
                    risk_score=5,
                    risk_level=RiskLevel.MEDIUM,
                    citations=[],
                    is_reflected=True
                )
            ]
        )
        
    monkeypatch.setattr(contract, "process_contract", mock_process_contract)

# ---------- File Validation ----------

@pytest.mark.anyio
async def test_contract_upload_success(auth_client: AsyncClient):
    """Test upload file hợp lệ (txt) và nhận kết quả."""
    file_content = b"Hợp đồng lao động thử việc."
    files = {"file": ("hopdong.txt", BytesIO(file_content), "text/plain")}
    
    resp = await auth_client.post("/contract/analyze", files=files)
    
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "hopdong.txt"
    assert data["total_clauses"] == 1
    assert data["analyses"][0]["risk_score"] == 5

@pytest.mark.anyio
async def test_contract_upload_invalid_format(auth_client: AsyncClient):
    """Test upload file không được hỗ trợ (jpg) -> 400."""
    file_content = b"fake image content"
    files = {"file": ("image.jpg", BytesIO(file_content), "image/jpeg")}
    
    resp = await auth_client.post("/contract/analyze", files=files)
    
    assert resp.status_code == 400
    assert "Định dạng file không được hỗ trợ" in resp.json()["detail"]

@pytest.mark.anyio
async def test_contract_upload_too_large(auth_client: AsyncClient):
    """Test upload file lớn hơn 5MB -> 413."""
    # Tạo một file giả > 5MB
    large_content = b"a" * (5 * 1024 * 1024 + 10)
    files = {"file": ("big_contract.pdf", BytesIO(large_content), "application/pdf")}
    
    resp = await auth_client.post("/contract/analyze", files=files)
    
    assert resp.status_code == 413
    assert "File quá lớn" in resp.json()["detail"]

@pytest.mark.anyio
async def test_contract_upload_unauthorized(client: AsyncClient):
    """Guest không được phân tích hợp đồng -> 401."""
    file_content = b"Hợp đồng"
    files = {"file": ("hopdong.txt", BytesIO(file_content), "text/plain")}
    
    resp = await client.post("/contract/analyze", files=files)
    assert resp.status_code == 401
