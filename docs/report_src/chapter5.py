from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def add_chapter_5(doc, format_heading, format_normal):
    """
    Chương 5: KIỂM THỬ, RỦI RO & KẾT LUẬN - RAGAs, Risk Assessment và Đóng góp
    """
    doc.add_page_break()
    h = doc.add_paragraph('Chương 5. ĐÁNH GIÁ, QUẢN TRỊ RỦI RO VÀ KẾT LUẬN')
    format_heading(h, level=1)

    # 5.1 RAG Evaluation
    h = doc.add_paragraph('5.1. Bộ Metrics Đánh giá Chất lượng AI (RAGAs Framework)')
    format_heading(h, level=2)
    p = doc.add_paragraph(
        "Đối với một hệ thống AI pháp lý, việc kiểm thử thủ công là không đủ và thiếu tính khách quan. "
        "Dự án áp dụng bộ framework RAGAs (Retrieval Augmented Generation Assessment) - tiêu chuẩn công nghiệp "
        "hiện tại để đánh giá chất lượng hệ thống RAG trên tập dữ liệu 9,715 câu hỏi-đáp pháp lý (thangvip/vietnamese-legal-qa).\n\n"
        "Đánh giá cấu phần Tìm kiếm (Retrieval Metrics):\n"
        "1. MRR@5 (Mean Reciprocal Rank): Đo lường vị trí trung bình của kết quả đúng xuất hiện trong Top-5. "
        "Mục tiêu đạt ≥ 0.70. Điểm MRR cao chứng tỏ văn bản đúng thường nằm ở vị trí số 1 hoặc 2, giúp LLM đọc dễ dàng hơn.\n"
        "2. Hit@5: Tỷ lệ phần trăm câu hỏi mà ít nhất 1 chunk đúng xuất hiện trong Top-5. Mục tiêu đạt ≥ 0.85.\n\n"
        "Đánh giá cấu phần Sinh văn bản (Generation Metrics):\n"
        "3. Faithfulness: Trả lời câu hỏi 'LLM có bịa thêm thông tin ngoài Context không?'. Đánh giá bằng cơ chế LLM as a Judge. Mục tiêu ≥ 0.90.\n"
        "4. Answer Relevancy: Trả lời câu hỏi 'LLM có đi thẳng vào trọng tâm câu hỏi không?'. Mục tiêu ≥ 0.85."
    )
    format_normal(p)

    # 5.2 Risk Assessment
    h = doc.add_paragraph('5.2. Quản trị Rủi ro Kỹ thuật (Risk Assessment)')
    format_heading(h, level=2)
    
    table_risk = doc.add_table(rows=1, cols=3)
    table_risk.style = 'Table Grid'
    hdr = table_risk.rows[0].cells
    hdr[0].text = 'Rủi ro'
    hdr[1].text = 'Mức độ'
    hdr[2].text = 'Giải pháp Khắc phục'
    
    row = table_risk.add_row().cells
    row[0].text = 'Quá tải RAM khi Embedding 500.000 văn bản'
    row[1].text = 'Cao'
    row[2].text = 'Chiến lược cắt lớp: Chỉ embed 50.000 văn bản thuộc 2 lĩnh vực trọng tâm (Lao động, Thuế). Index HNSW sẵn sàng scale-up khi có server lớn hơn.'
    
    row = table_risk.add_row().cells
    row[0].text = 'API LLM Timeout / Rate Limit'
    row[1].text = 'Trung bình'
    row[2].text = 'Kích hoạt Circuit Breaker, tự động Fallback về Semantic Search, kết hợp Caching câu hỏi phổ biến.'
    
    row = table_risk.add_row().cells
    row[0].text = 'AI trả lời sai, ảo giác thông tin pháp lý (Hallucination)'
    row[1].text = 'Cao'
    row[2].text = 'Cưỡng chế Anti-Hallucination bằng System Prompt. Luôn hiển thị nguồn trích dẫn (Citations) để người dùng tự đối chiếu.'

    # 5.3 Contributions
    h = doc.add_paragraph('\n5.3. Đóng góp Khoa học và Thực tiễn')
    format_heading(h, level=2)
    p = doc.add_paragraph(
        "Đề tài đã hoàn thành xuất sắc mục tiêu đề ra và mang lại 4 đóng góp lõi:\n\n"
        "Đóng góp 1 (Thực tiễn): Xây dựng thành công nền tảng giúp Doanh nghiệp (SME) tra cứu pháp luật bằng ngôn ngữ tự nhiên, "
        "giảm thiểu chi phí tư vấn pháp lý và thời gian xử lý thủ công.\n\n"
        "Đóng góp 2 (Kỹ thuật): Kiểm chứng thành công chuỗi công nghệ: bkai-vietnamese-bi-encoder -> pgvector HNSW -> "
        "RRF Hybrid Search -> RAG Pipeline trên bài toán Legal Retrieval tiếng Việt. Đây là một hướng nghiên cứu còn rất ít "
        "tài liệu tiếng Việt thực chiến.\n\n"
        "Đóng góp 3 (Dữ liệu): Xây dựng Pipeline ETL tự động hóa, tạo ra Đồ thị Tri thức pháp luật có thể tái sử dụng "
        "cho các nghiên cứu Legal NLP khác.\n\n"
        "Đóng góp 4 (Hệ sinh thái): Nền tảng được thiết kế mở (Modular Monolith), sẵn sàng tích hợp Module Phân tích "
        "Rủi ro Hợp đồng (CoT Prompting) từ dự án NCKH của nhóm, tạo thành một Hệ sinh thái LegalTech toàn diện tại Việt Nam."
    )
    format_normal(p)

    # 5.4 Future Work
    h = doc.add_paragraph('5.4. Định hướng Phát triển Tương lai (Roadmap)')
    format_heading(h, level=2)
    p = doc.add_paragraph(
        "Trong các phiên bản tiếp theo, nhóm nghiên cứu hướng tới:\n"
        "- Triển khai Sovereign AI (AI Egde/On-Premise): Triển khai mô hình mã nguồn mở như Llama 3 8B lượng tử hóa (Quantized) "
        "chạy trực tiếp trên server nội bộ của doanh nghiệp, đảm bảo dữ liệu mật không bao giờ bị gửi ra ngoài mạng internet (API Gemini/OpenAI).\n"
        "- Multi-Agent System: Tích hợp nhiều Agent AI cùng tranh luận (Debate) để đưa ra tư vấn pháp lý chính xác nhất cho các case study phức tạp.\n"
        "- Workspace Collaboration (UC-18): Mở khóa tính năng làm việc nhóm, cho phép phòng Kế toán và Pháp chế cùng thao tác chung trên một Đồ thị Tri thức."
    )
    format_normal(p)
