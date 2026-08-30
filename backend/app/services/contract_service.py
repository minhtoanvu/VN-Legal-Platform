import asyncio
import io
import json
import logging
import re
from typing import List

import pdfplumber
from docx import Document as DocxDocument
from sqlalchemy.ext.asyncio import AsyncSession
from google import genai as google_genai

from app.core.config import settings
from app.schemas.contract import ClauseAnalysis, ContractReport, RiskLevel
from app.services.rag_service import rag_retrieve, _build_context

log = logging.getLogger(__name__)

SYSTEM_COT_PROMPT = """Bạn là một Chuyên gia Pháp lý AI (Legal AI Expert) chuyên phân tích rủi ro hợp đồng dựa trên pháp luật Việt Nam.
Nhiệm vụ của bạn là nhận một điều khoản hợp đồng và thực hiện phân tích theo chuẩn Chain-of-Thought (CoT) 4 bước.

[QUY TẮC BẮT BUỘC]
- TRẢ VỀ DUY NHẤT ĐỊNH DẠNG JSON. KHÔNG BỔ SUNG TEXT BÊN NGOÀI.
- Sử dụng [TÀI LIỆU THAM KHẢO] (nếu có) để đối chiếu luật. Nếu không có tài liệu, sử dụng kiến thức luật chung nhưng phải ghi chú.
- Json output phải có cấu trúc sau:
{
  "step1_identification": "Bản chất điều khoản này quy định về vấn đề gì?",
  "step2_legal_comparison": "Đối chiếu điều khoản này với quy định pháp luật (trích dẫn luật nếu có).",
  "step3_risk_evaluation": "Rủi ro pháp lý tiềm ẩn cho người dùng là gì? Tại sao?",
  "step4_suggestion": "Đề xuất sửa đổi điều khoản này như thế nào để an toàn hơn?",
  "risk_score": Điểm rủi ro từ 1 đến 10 (số nguyên).
  "risk_level": "low" (1-3) hoặc "medium" (4-6) hoặc "high" (7-10)
}

[TÀI LIỆU THAM KHẢO (Luật liên quan)]
{context}

[ĐIỀU KHOẢN CẦN PHÂN TÍCH]
"{clause_text}"
"""

def parse_document(file_bytes: bytes, filename: str) -> str:
    """Extract text from PDF or DOCX file bytes (In-Memory)."""
    text = ""
    if filename.lower().endswith(".pdf"):
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    elif filename.lower().endswith((".docx", ".doc")):
        doc = DocxDocument(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        text = file_bytes.decode("utf-8", errors="ignore")
    return text

def segment_contract(text: str) -> List[dict]:
    """Chia văn bản thành các điều khoản dựa trên regex."""
    # Pattern tìm "Điều X." hoặc "Điều X:"
    pattern = r"(?i)(Điều\s+\d+[\.:])"
    parts = re.split(pattern, text)
    
    clauses = []
    # Nếu file không có "Điều", coi như là 1 đoạn lớn
    if len(parts) <= 1:
        return [{"title": "Nội dung hợp đồng", "text": text[:2000]}] # Giới hạn 2000 ký tự để tránh lỗi
        
    # parts[0] thường là phần mở đầu (Cộng hòa xã hội..., Căn cứ...)
    if parts[0].strip():
        clauses.append({
            "title": "Phần mở đầu",
            "text": parts[0].strip()
        })
        
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        content = parts[i+1].strip() if i+1 < len(parts) else ""
        clauses.append({
            "title": title,
            "text": f"{title} {content}"
        })
        
    return clauses

async def analyze_clause_cot(session: AsyncSession, clause_title: str, clause_text: str) -> ClauseAnalysis:
    """Thực hiện CoT 4 bước để phân tích 1 điều khoản."""
    if not settings.gemini_api_key:
        raise ValueError("Chưa cấu hình GEMINI_API_KEY")

    # BƯỚC 1: Retrieval (Lấy luật liên quan từ pgvector)
    # Rút trích keyword từ điều khoản để search
    search_query = clause_text[:200]  # Lấy phần đầu để search
    try:
        chunks = await rag_retrieve(session, search_query)
        context, citations = _build_context(chunks)
    except Exception as e:
        log.error(f"Lỗi khi search pgvector: {e}")
        context = "(Không tìm thấy tài liệu liên quan)"
        citations = []

    # BƯỚC 2: Gọi Gemini với CoT Prompt
    system_prompt = SYSTEM_COT_PROMPT.replace("{context}", context).replace("{clause_text}", clause_text)
    client = google_genai.Client(api_key=settings.gemini_api_key)
    
    try:
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents="Hãy phân tích điều khoản này và trả về JSON.",
            config=google_genai.types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
                system_instruction=system_prompt,
            )
        )
        
        result = json.loads(response.text)
        
        # Self-Reflection (Bản 1 implementation plan)
        risk_score = result.get("risk_score", 1)
        is_reflected = False
        if 4 <= risk_score <= 7:
            # Ngưỡng trung bình/nhạy cảm, bắt AI suy nghĩ lại 1 lần nữa cho chắc
            reflection_prompt = f"Bạn vừa chấm điểm rủi ro {risk_score}/10 cho điều khoản này. Hãy xem xét lại thật kỹ xem điểm này đã chính xác chưa, có bỏ sót rủi ro ẩn nào không? Hãy trả về JSON tương tự với kết quả sau khi đã suy nghĩ lại."
            response2 = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=reflection_prompt,
                config=google_genai.types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                    system_instruction=system_prompt,
                )
            )
            result = json.loads(response2.text)
            is_reflected = True
            
        return ClauseAnalysis(
            clause_title=clause_title,
            clause_text=clause_text,
            step1_identification=result.get("step1_identification", ""),
            step2_legal_comparison=result.get("step2_legal_comparison", ""),
            step3_risk_evaluation=result.get("step3_risk_evaluation", ""),
            step4_suggestion=result.get("step4_suggestion", ""),
            risk_score=result.get("risk_score", 1),
            risk_level=result.get("risk_level", RiskLevel.LOW),
            citations=citations,
            is_reflected=is_reflected
        )

    except Exception as e:
        log.error(f"Lỗi khi gọi Gemini: {e}")
        # Trả về kết quả default nếu LLM lỗi
        return ClauseAnalysis(
            clause_title=clause_title,
            clause_text=clause_text,
            step1_identification="Lỗi phân tích",
            step2_legal_comparison="N/A",
            step3_risk_evaluation=str(e),
            step4_suggestion="N/A",
            risk_score=1,
            risk_level=RiskLevel.LOW
        )

async def process_contract(session: AsyncSession, file_bytes: bytes, filename: str) -> ContractReport:
    """Luồng chính: Nhận file, parse, chia đoạn và phân tích toàn bộ."""
    text = parse_document(file_bytes, filename)
    clauses = segment_contract(text)
    
    # Phân tích song song nhiều điều khoản cùng lúc để tiết kiệm thời gian
    # Tuy nhiên, để tránh limit API, có thể dùng semaphore. Ở đây giả định limit cho 5 request đồng thời.
    sem = asyncio.Semaphore(5)
    
    async def analyze_with_sem(clause):
        async with sem:
            return await analyze_clause_cot(session, clause["title"], clause["text"])
            
    tasks = [analyze_with_sem(clause) for clause in clauses if len(clause["text"]) > 50] # Bỏ qua đoạn quá ngắn
    analyses = await asyncio.gather(*tasks)
    
    return ContractReport(
        filename=filename,
        total_clauses=len(analyses),
        analyses=list(analyses)
    )
