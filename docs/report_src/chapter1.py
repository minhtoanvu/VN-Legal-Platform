from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def add_chapter_1(doc, format_heading, format_normal):
    """
    Chương 1: GIỚI THIỆU - Phân tích bối cảnh, thực trạng, mục tiêu và phạm vi đề tài
    """
    doc.add_page_break()
    h = doc.add_paragraph('Chương 1. GIỚI THIỆU & KHẢO SÁT HIỆN TRẠNG')
    format_heading(h, level=1)

    # 1.1 Bối cảnh
    h = doc.add_paragraph('1.1. Bối cảnh và Bài toán Thực tế')
    format_heading(h, level=2)
    
    h = doc.add_paragraph('1.1.1. Bức tranh pháp lý Việt Nam')
    format_heading(h, level=3)
    p = doc.add_paragraph(
        "Hệ thống pháp luật Việt Nam hiện có hàng trăm nghìn văn bản quy phạm pháp luật, bao gồm Bộ luật, "
        "Luật, Nghị định, Thông tư, Công văn và Quyết định được ban hành và liên tục cập nhật bởi nhiều cơ quan nhà nước. "
        "Chỉ riêng năm 2023, các bộ ngành đã ban hành hơn 4.000 văn bản mới. Tính đến năm 2024, Cơ sở dữ liệu Quốc gia "
        "về văn bản pháp luật (vbpl.vn) lưu trữ hơn nửa triệu văn bản - một khối lượng mà không một cá nhân hay bộ phận nào "
        "có thể theo dõi thủ công.\n\n"
        "Sự bùng nổ thông tin pháp lý này tạo ra một hiện tượng được giới nghiên cứu gọi là 'Information Overload' (Quá tải thông tin). "
        "Điều này tạo ra áp lực cực lớn cho những người cần làm việc với pháp luật hàng ngày, đặc biệt là các Doanh nghiệp vừa và nhỏ (SME) - "
        "những đơn vị không có đủ nhân lực pháp chế chuyên sâu và chi phí thuê luật sư tư vấn thường xuyên là quá cao."
    )
    format_normal(p)

    h = doc.add_paragraph('1.1.2. Phân tích Khó khăn Theo Nhóm Người dùng')
    format_heading(h, level=3)
    
    p = doc.add_paragraph(
        "Để làm rõ vấn đề, nhóm nghiên cứu đã tiến hành phân tích 'Nỗi đau' (Pain points) của các nhóm người dùng chính "
        "khi tương tác với văn bản pháp luật truyền thống:"
    )
    format_normal(p)
    
    table1 = doc.add_table(rows=1, cols=3)
    table1.style = 'Table Grid'
    hdr_cells = table1.rows[0].cells
    hdr_cells[0].text = 'Nhóm Người dùng'
    hdr_cells[1].text = 'Khó khăn Thực tế'
    hdr_cells[2].text = 'Hậu quả'
    
    row_cells = table1.add_row().cells
    row_cells[0].text = 'Nhân viên Nhân sự (HR)'
    row_cells[1].text = 'Phải đọc nhiều văn bản dài, không biết văn bản nào còn hiệu lực, mất 2-4 giờ mỗi lần kiểm tra.'
    row_cells[2].text = 'Áp dụng sai quy định, bị phạt hành chính, tranh chấp lao động.'
    
    row_cells = table1.add_row().cells
    row_cells[0].text = 'Kế toán'
    row_cells[1].text = 'Luật thuế thay đổi liên tục, phải lưu thủ công hoặc nhờ tư vấn, không có công cụ theo dõi hiệu lực tự động.'
    row_cells[2].text = 'Khai sai thuế, bị truy thu và phạt; chi phí tư vấn pháp lý cao.'
    
    row_cells = table1.add_row().cells
    row_cells[0].text = 'Pháp chế & Chủ SME'
    row_cells[1].text = 'Phải tổng hợp nhiều văn bản liên quan nhưng không có công cụ hiển thị mối quan hệ.'
    row_cells[2].text = 'Sót điều khoản, vi phạm pháp luật mà không biết, rủi ro kinh doanh cao.'

    # 1.2 Khảo sát
    h = doc.add_paragraph('1.2. Khảo sát Hiện trạng Hệ thống')
    format_heading(h, level=2)
    p = doc.add_paragraph(
        "Nhóm đã khảo sát 3 hệ thống pháp luật phổ biến nhất hiện nay để xác định khoảng trống công nghệ:"
    )
    format_normal(p)

    p = doc.add_paragraph(
        "A. Thuvienphapluat.vn: Đây là cơ sở dữ liệu lớn nhất Việt Nam. Tuy nhiên, giao diện có quá nhiều banner quảng cáo, "
        "thông tin rườm rà. Người dùng dễ bị lạc trong ma trận điều khoản. Hệ thống chỉ hỗ trợ tìm kiếm bằng từ khóa chính xác "
        "(Lexical Search), không hỗ trợ Semantic Search và không có AI phân tích dữ liệu.\n\n"
        "B. Vbpl.vn: Cổng thông tin của Chính phủ. Dữ liệu có tính pháp lý cao nhưng giao diện cũ, không thân thiện. "
        "Không có tài khoản người dùng, không có công cụ phân tích đồ thị hoặc theo dõi lịch sử văn bản.\n\n"
        "C. VN-Law-Advisor (GitHub): Dự án sinh viên xuất sắc có ứng dụng RAG. Tuy nhiên, hệ thống này chỉ dừng ở mức Chatbot, "
        "thiếu công cụ phân tích dữ liệu cho doanh nghiệp, không có Dashboard thống kê xu hướng, và không có Knowledge Graph (Đồ thị Tri thức)."
    )
    format_normal(p)

    h = doc.add_paragraph('1.3. Mục tiêu và Phạm vi Đề tài')
    format_heading(h, level=2)
    p = doc.add_paragraph(
        "Mục tiêu cốt lõi: Xây dựng một nền tảng Web App nội bộ (Modular Monolith) cho phép tìm kiếm và hỏi đáp pháp luật "
        "ứng dụng công nghệ Semantic Search và Retrieval-Augmented Generation (RAG). Nền tảng hướng tới việc cung cấp giá trị "
        "phân tích dữ liệu thực tế cho doanh nghiệp (Enterprise-oriented).\n\n"
        "Phạm vi dữ liệu: Tập trung khai thác 2 lĩnh vực cốt lõi đối với doanh nghiệp SME: Lao động - Bảo hiểm Xã hội "
        "và Thuế - Kế toán. Hạ tầng vector database (pgvector) được thiết kế sẵn để scale-up toàn bộ 500,000 văn bản trong tương lai.\n\n"
        "Phạm vi chức năng: Hoàn thiện Hybrid Search (BM25 + Semantic), RAG Chatbot chống Hallucination, Timeline văn bản, "
        "Knowledge Graph và Dashboard thống kê dữ liệu trực quan."
    )
    format_normal(p)

    h = doc.add_paragraph('1.4. Yêu cầu Chức năng & Tác nhân (Actors)')
    format_heading(h, level=2)
    p = doc.add_paragraph(
        "Hệ thống định nghĩa 3 tác nhân chính: Khách (Guest - chỉ tra cứu cơ bản), Người dùng (User - sử dụng AI và Workspace cá nhân), "
        "và Quản trị viên (Admin - quản lý dữ liệu). Dưới đây là danh sách 15/21 Use Case cốt lõi của nền tảng:"
    )
    format_normal(p)

    use_cases = [
        ("UC-01 & 02", "Xác thực (Đăng ký / Đăng nhập JWT)."),
        ("UC-04", "Tìm kiếm Full-text bằng thuật toán BM25 trên PostgreSQL."),
        ("UC-05", "Tìm kiếm Semantic Search bằng Embedding Model bkai-vietnamese-bi-encoder."),
        ("UC-06", "Lọc đa chiều theo lĩnh vực, cơ quan ban hành, ngày hiệu lực."),
        ("UC-07", "Xem chi tiết metadata và nội dung Toàn văn văn bản."),
        ("UC-08", "Xem Timeline Lịch sử thay đổi (Sửa đổi, bổ sung, bãi bỏ) của văn bản."),
        ("UC-09", "Hỏi đáp Pháp luật bằng ngôn ngữ tự nhiên (AI Assistant RAG Pipeline)."),
        ("UC-10", "Truy xuất Nguồn trích dẫn (Citations) chính xác từ câu trả lời AI."),
        ("UC-12", "Trực quan hóa Đồ thị Tri thức (Knowledge Graph) của mạng lưới văn bản."),
        ("UC-14", "Dashboard Thống kê Xu hướng lập pháp (Line, Pie, Bar charts)."),
        ("UC-16", "Đánh dấu (Bookmark) và lưu trữ văn bản vào Collection cá nhân.")
    ]
    
    for uc, desc in use_cases:
        p = doc.add_paragraph(f"• {uc}: {desc}", style='List Bullet')
        format_normal(p)

    h = doc.add_paragraph('1.5. Cấu trúc Báo cáo')
    format_heading(h, level=2)
    p = doc.add_paragraph(
        "Báo cáo này được cấu trúc thành 5 chương nhằm phản ánh logic kỹ thuật và quy trình phần mềm chuẩn mực:\n"
        "Chương 1: Giới thiệu bối cảnh, bài toán thực tế và khảo sát các hệ thống đang tồn tại.\n"
        "Chương 2: Đào sâu vào cơ sở lý thuyết toán học của thuật toán Vector Search, BM25, RRF và RAG Architecture.\n"
        "Chương 3: Phân tích chi tiết kiến trúc Modular Monolith, Thiết kế CSDL (10 bảng) và Sequence Diagrams.\n"
        "Chương 4: Đặc tả chi tiết về việc hiện thực hệ thống (Code Snippets, APIs) và cấu hình hạ tầng CI/CD.\n"
        "Chương 5: Đánh giá chất lượng bằng RAGAs framework, phân tích rủi ro và kết luận các đóng góp khoa học."
    )
    format_normal(p)
