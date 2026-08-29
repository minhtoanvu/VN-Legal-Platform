from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class CitationInfo(BaseModel):
    doc_number: str
    title: str
    snippet: str

class ClauseAnalysis(BaseModel):
    clause_title: str = Field(..., description="Tên điều khoản, VD: Điều 1. Tiền lương")
    clause_text: str = Field(..., description="Nội dung gốc của điều khoản")
    
    # CoT 4 Steps
    step1_identification: str = Field(..., description="Bản chất của điều khoản")
    step2_legal_comparison: str = Field(..., description="Đối chiếu với các điều luật (RAG)")
    step3_risk_evaluation: str = Field(..., description="Đánh giá lý do rủi ro")
    step4_suggestion: str = Field(..., description="Đề xuất chỉnh sửa")
    
    # Final Result
    risk_score: int = Field(..., ge=1, le=10, description="Điểm rủi ro (1-10)")
    risk_level: RiskLevel = Field(..., description="low, medium, or high")
    citations: List[CitationInfo] = Field(default_factory=list)
    
    is_reflected: bool = Field(default=False, description="True nếu đã qua vòng Reflection")

class ContractReport(BaseModel):
    filename: str
    total_clauses: int
    analyses: List[ClauseAnalysis]
