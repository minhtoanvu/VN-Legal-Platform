from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def add_chapter_3(doc, format_heading, format_normal):
    """
    Chương 3: PHÂN TÍCH & THIẾT KẾ HỆ THỐNG - Kiến trúc, CSDL và Sequence Diagrams
    """
    doc.add_page_break()
    h = doc.add_paragraph('Chương 3. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG')
    format_heading(h, level=1)

    # 3.1 Architecture
    h = doc.add_paragraph('3.1. Thiết kế Kiến trúc Tổng thể (System Architecture)')
    format_heading(h, level=2)
    p = doc.add_paragraph(
        "Hệ thống được thiết kế theo kiến trúc Modular Monolith 3 tầng (3-Tier Architecture) "
        "kết hợp Component-based Frontend. Kiến trúc này được lựa chọn để tối ưu thời gian phát triển 10 tuần, "
        "đồng thời vẫn đảm bảo tính cô lập của các module để dễ dàng nâng cấp lên Microservices trong tương lai.\n\n"
        "1. Tầng Client (Frontend): Xây dựng bằng React 18, TypeScript, Vite. Quản lý trạng thái bằng Zustand. "
        "Giao tiếp với API qua REST/JSON và nhận luồng dữ liệu AI qua Server-Sent Events (SSE).\n"
        "2. Tầng API Server (Backend): Sử dụng FastAPI (Python 3.11+) xử lý bất đồng bộ (async/await). Các logic "
        "được chia thành: Auth Router, Document Router, Search Service, RAG Service, Graph Service.\n"
        "3. Tầng Dữ liệu (Database): Sử dụng duy nhất PostgreSQL 16 tích hợp extension pgvector. Quyết định "
        "sử dụng PostgreSQL làm 'All-in-one' database (lưu trữ quan hệ, Full-text TSVECTOR, và Vector Search) "
        "giúp giảm thiểu tối đa độ phức tạp vận hành so với việc phải duy trì thêm một Vector DB độc lập (như Milvus hay Pinecone)."
    )
    format_normal(p)

    # 3.2 Database Schema
    h = doc.add_paragraph('3.2. Thiết kế Cơ sở Dữ liệu Vật lý (Physical Data Model)')
    format_heading(h, level=2)
    p = doc.add_paragraph(
        "Hệ thống bao gồm 10 bảng dữ liệu được chuẩn hóa, trong đó 9 bảng nghiệp vụ cốt lõi và 1 bảng quản lý version (alembic). "
        "Dưới đây là đặc tả chi tiết các bảng quan trọng nhất:"
    )
    format_normal(p)

    h = doc.add_paragraph('3.2.1. Bảng documents (Văn bản pháp luật)')
    format_heading(h, level=3)
    p = doc.add_paragraph(
        "Lưu trữ metadata và toàn văn văn bản.\n"
        "- id (UUID): Khóa chính.\n"
        "- doc_number (VARCHAR): Số hiệu văn bản (Ví dụ: '45/2019/QH14').\n"
        "- title (TEXT): Tên văn bản.\n"
        "- doc_type, issuing_body, field: Loại văn bản, cơ quan ban hành, lĩnh vực.\n"
        "- issue_date, effective_date, expired_date: Các mốc thời gian quan trọng.\n"
        "- status (VARCHAR): Trạng thái hiệu lực ('active', 'expired', 'amended'). Có đánh Index.\n"
        "- search_vector (TSVECTOR): Trường lưu trữ kết quả phân tích chỉ mục Full-text để chạy thuật toán BM25."
    )
    format_normal(p)

    h = doc.add_paragraph('3.2.2. Bảng document_chunks (Dữ liệu nền cho AI RAG)')
    format_heading(h, level=3)
    p = doc.add_paragraph(
        "Lưu trữ các đoạn văn bản nhỏ (chunks) đã được băm ra từ văn bản gốc.\n"
        "- id (UUID): Khóa chính.\n"
        "- document_id (UUID): Khóa ngoại tham chiếu bảng documents (ON DELETE CASCADE).\n"
        "- content_chunk (TEXT): Nội dung đoạn cắt (khoảng 256-512 tokens).\n"
        "- embedding (VECTOR(768)): Vector đặc trưng 768 chiều. Trường này được áp dụng chỉ mục HNSW "
        "(Hierarchical Navigable Small World) với tham số m=16, ef_construction=128 để tối ưu tốc độ Semantic Search."
    )
    format_normal(p)

    h = doc.add_paragraph('3.2.3. Các bảng Workspace & Analytics')
    format_heading(h, level=3)
    p = doc.add_paragraph(
        "- Bảng users, organizations: Quản lý người dùng, phân quyền RBAC và mã hóa mật khẩu bằng Bcrypt.\n"
        "- Bảng document_relations: Lưu trữ đồ thị quan hệ (GUIDES, AMENDS, REPLACES, REVOKES). Khóa chính kết hợp "
        "giữa source_doc_id và target_doc_id đảm bảo tính duy nhất của mạng lưới.\n"
        "- Bảng query_logs: Ghi nhận mọi câu hỏi gửi tới AI, loại truy vấn (keyword/semantic), thời gian xử lý (duration_ms) "
        "và phản hồi JSON. Dữ liệu này đóng vai trò sống còn để chấm điểm chất lượng RAG (RAGAs Evaluation) và vẽ Dashboard."
    )
    format_normal(p)

    # 3.3 Sequence Diagrams & Logic
    h = doc.add_paragraph('3.3. Thiết kế Luồng xử lý (Sequence & Logic Flow)')
    format_heading(h, level=2)
    p = doc.add_paragraph(
        "Dưới đây là mô tả luồng hoạt động của 2 tiến trình cốt lõi nhất trong hệ thống:"
    )
    format_normal(p)

    h = doc.add_paragraph('3.3.1. Luồng truy vấn RAG (Hỏi đáp AI)')
    format_heading(h, level=3)
    p = doc.add_paragraph(
        "1. Người dùng gõ câu hỏi pháp lý vào AI Chat Interface.\n"
        "2. Backend gọi mô hình bkai-bi-encoder để chuyển câu hỏi thành vector 768 chiều.\n"
        "3. pgvector thực hiện truy vấn k-NN qua HNSW index, lấy Top-20 chunks gần nhất.\n"
        "4. Cùng lúc, Full-text search (BM25) lấy Top-20 chunks khớp từ khóa.\n"
        "5. Module RRF Reranker hợp nhất hai kết quả, chọn lọc ra Top-5 chunks xuất sắc nhất.\n"
        "6. Backend nhúng Top-5 chunks này vào System Prompt (kèm lệnh Anti-Hallucination) và gọi Gemini 2.5 Flash.\n"
        "7. LLM stream từng token câu trả lời về giao diện người dùng qua SSE, kèm theo siêu liên kết (Citations) để người dùng "
        "có thể click thẳng vào văn bản gốc kiểm chứng."
    )
    format_normal(p)

    h = doc.add_paragraph('3.3.2. Luồng ETL Pipeline (Xử lý dữ liệu đầu vào)')
    format_heading(h, level=3)
    p = doc.add_paragraph(
        "Quá trình chuyển đổi nửa triệu văn bản thành dữ liệu AI (Extract-Transform-Load) diễn ra như sau:\n"
        "- Extract: Tải dataset từ HuggingFace (th1nhng0/vietnamese-legal-documents), ánh xạ schema.\n"
        "- Transform: Áp dụng chiến lược Sliding Window: Cắt văn bản thành các khối 256-512 tokens. "
        "Đặc biệt, thiết lập phần giao nhau (Overlap) là 50 tokens giữa các khối liên tiếp. Kỹ thuật Overlap "
        "giúp bảo toàn ngữ cảnh, tránh việc một câu luật quan trọng bị cắt làm đôi làm mất đi nghĩa gốc.\n"
        "- Embed & Load: Batch processing qua bkai-bi-encoder và lưu vào pgvector. Xây dựng HNSW index."
    )
    format_normal(p)

    # 3.4 Resilience Design
    h = doc.add_paragraph('3.4. Thiết kế Khả năng Chịu lỗi (Resilience Design)')
    format_heading(h, level=2)
    p = doc.add_paragraph(
        "LLM API (Gemini/OpenAI) là thành phần nằm ngoài tầm kiểm soát của hệ thống. Để ngăn chặn việc LLM sập "
        "kéo theo toàn bộ hệ thống bị treo, mẫu thiết kế Circuit Breaker được áp dụng khắt khe:\n\n"
        "1. Timeout Policy: Thời gian chờ tối đa cho token đầu tiên của LLM là 10 giây (LLM_TIMEOUT_SEC = 10). "
        "Nếu vượt quá, hệ thống sẽ chém luồng (Abort).\n"
        "2. Circuit Breaker Fallback: Khi API LLM lỗi hoặc timeout, cầu dao (Circuit Breaker) chuyển sang trạng thái Open. "
        "Thay vì bắt người dùng chờ đợi, hệ thống lập tức Fallback về chế độ Semantic Search thông thường, trả về 5 đoạn văn bản "
        "nguyên thủy kèm thông báo: 'Trợ lý AI đang gián đoạn, dưới đây là các văn bản liên quan nhất'.\n"
        "3. Rate Limiting: Chống Spam bằng cách giới hạn 15 requests / phút / người dùng (HTTP 429 Too Many Requests)."
    )
    format_normal(p)
