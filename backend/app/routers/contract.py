from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.contract import ContractReport
from app.services.contract_service import process_contract

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB giới hạn để tránh sập API Gemini

@router.post("/analyze", response_model=ContractReport)
async def analyze_contract_endpoint(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Phân tích rủi ro hợp đồng PDF/DOCX/TXT bằng AI.
    Yêu cầu đăng nhập.
    """
    if not file.filename.lower().endswith((".pdf", ".docx", ".doc", ".txt")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Định dạng file không được hỗ trợ. Vui lòng tải lên PDF, DOCX hoặc TXT."
        )
        
    # Đọc file thẳng vào RAM
    file_bytes = await file.read()
    
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File quá lớn. Vui lòng tải lên file nhỏ hơn 5MB."
        )
        
    try:
        report = await process_contract(db, file_bytes, file.filename)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi phân tích hợp đồng: {str(e)}"
        )
