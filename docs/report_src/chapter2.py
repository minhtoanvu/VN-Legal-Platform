from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def add_chapter_2(doc, format_heading, format_normal):
    """
    Chương 2: CƠ SỞ LÝ THUYẾT & THUẬT TOÁN - Toán học và các thuật toán nền tảng
    """
    doc.add_page_break()
    h = doc.add_paragraph('Chương 2. CƠ SỞ LÝ THUYẾT & THUẬT TOÁN LÕI')
    format_heading(h, level=1)

    # 2.1 Full-text Search
    h = doc.add_paragraph('2.1. Tìm kiếm Từ khóa Chính xác (Full-Text Search & BM25)')
    format_heading(h, level=2)
    p = doc.add_paragraph(
        "Tìm kiếm theo từ khóa (Lexical Search) là phương pháp truyền thống dựa trên sự khớp chính xác của các ký tự. "
        "Trong dự án này, hệ thống sử dụng thuật toán BM25 (Best Matching 25) thông qua kiểu dữ liệu TSVECTOR của PostgreSQL.\n\n"
        "Thuật toán BM25 là một phiên bản mở rộng của TF-IDF (Term Frequency-Inverse Document Frequency), khắc phục hiện tượng "
        "điểm số tăng vô hạn khi một từ xuất hiện quá nhiều lần trong văn bản. Công thức tính điểm BM25 cho tài liệu D và truy vấn Q như sau:\n\n"
        "    Score(D, Q) = Σ [ IDF(q_i) * (TF(q_i, D) * (k_1 + 1)) / (TF(q_i, D) + k_1 * (1 - b + b * (|D| / avgdl))) ]\n\n"
        "Trong đó:\n"
        "- IDF(q_i): Trọng số nghịch đảo tần suất của từ q_i (từ hiếm có trọng số cao hơn).\n"
        "- TF(q_i, D): Tần suất xuất hiện của từ q_i trong tài liệu D.\n"
        "- |D|: Chiều dài tài liệu D.\n"
        "- avgdl: Chiều dài trung bình của toàn bộ tài liệu trong tập dữ liệu.\n"
        "- k_1 và b: Các hằng số điều chỉnh (thường k_1 = 1.2 đến 2.0, b = 0.75).\n\n"
        "Ưu điểm của phương pháp này là tính chính xác tuyệt đối với mã số văn bản (Ví dụ: '45/2019/QH14'). "
        "Tuy nhiên, nhược điểm chí mạng là không giải quyết được vấn đề từ đồng nghĩa (synonyms) hoặc đa nghĩa (polysemy)."
    )
    format_normal(p)

    # 2.2 Semantic Search
    h = doc.add_paragraph('2.2. Tìm kiếm Ngữ nghĩa (Semantic Search) và Embedding')
    format_heading(h, level=2)
    
    h = doc.add_paragraph('2.2.1. Vector Embedding')
    format_heading(h, level=3)
    p = doc.add_paragraph(
        "Để vượt qua hạn chế của BM25, hệ thống áp dụng kỹ thuật Vector Embedding. Một câu hỏi ngôn ngữ tự nhiên "
        "như 'Làm thêm giờ vào chủ nhật được trả lương thế nào?' sẽ được chuyển đổi (map) thành một điểm trong không gian toán học "
        "nhiều chiều (Cụ thể là 768 chiều). Các đoạn văn bản luật có ý nghĩa tương tự cũng sẽ nằm gần điểm đó trong không gian.\n\n"
        "Dự án sử dụng mô hình 'bkai-foundation-models/vietnamese-bi-encoder' thay vì các mô hình đa ngôn ngữ (như mBERT). "
        "Lý do kỹ thuật: Mô hình bkai đã được fine-tune trực tiếp trên tập dữ liệu Zalo Legal Text Retrieval, đạt độ chính xác "
        "(Accuracy@10) lên tới 93.59% đối với bài toán pháp luật tiếng Việt, vượt trội hoàn toàn so với mô hình tổng quát (chỉ đạt ~75-80%)."
    )
    format_normal(p)

    h = doc.add_paragraph('2.2.2. HNSW vs IVFFlat trong Vector Database')
    format_heading(h, level=3)
    p = doc.add_paragraph(
        "Để tìm kiếm điểm gần nhất trong không gian 768 chiều, PostgreSQL với pgvector cung cấp 2 thuật toán chỉ mục (Index): "
        "IVFFlat (Inverted File Flat) và HNSW (Hierarchical Navigable Small World).\n\n"
        "Hệ thống quyết định sử dụng thuật toán HNSW vì các lý do toán học sau:\n"
        "1. HNSW là thuật toán đồ thị, không yêu cầu phải biết trước số lượng vector để tạo centroids như IVFFlat.\n"
        "2. HNSW đạt tỷ lệ Recall (độ phủ kết quả đúng) cao hơn rất nhiều khi truy vấn k-Nearest Neighbors (k-NN).\n"
        "3. HNSW không cần chạy lệnh 'VACUUM ANALYZE' sau mỗi lần chèn dữ liệu (Insert) để cập nhật index, giúp tối ưu "
        "chi phí vận hành khi hệ thống cập nhật văn bản pháp luật hàng ngày.\n\n"
        "Cấu hình toán học cho HNSW trong dự án: m = 16 (số kết nối tối đa mỗi node), ef_construction = 128 (độ rẽ nhánh khi xây dựng đồ thị)."
    )
    format_normal(p)

    # 2.3 Hybrid Search
    h = doc.add_paragraph('2.3. Hybrid Search và Thuật toán Reciprocal Rank Fusion (RRF)')
    format_heading(h, level=2)
    p = doc.add_paragraph(
        "Hệ thống kết hợp cả BM25 và Semantic Search. Tuy nhiên, điểm số (Score) của BM25 (từ 0 đến hàng chục) "
        "và Cosine Similarity của Semantic Search (từ 0.0 đến 1.0) nằm ở hai thang đo hoàn toàn khác nhau. Việc cộng trực tiếp "
        "hay tính trung bình là sai lầm về mặt toán học.\n\n"
        "Giải pháp chuẩn công nghiệp là sử dụng thuật toán Reciprocal Rank Fusion (RRF) (Cormack et al., 2009). RRF hợp nhất "
        "hai danh sách kết quả không dựa trên điểm số nguyên thủy, mà dựa trên Hạng (Rank) của tài liệu:\n\n"
        "    RRF_Score(D) = Σ [ 1 / (k + Rank_i(D)) ]\n\n"
        "Trong đó, 'k' là hằng số (trong dự án chọn k=60 theo nghiên cứu nguyên bản), và Rank_i là thứ hạng của tài liệu D "
        "trong danh sách kết quả của phương pháp thứ i. Tài liệu xuất hiện ở vị trí cao trong cả hai danh sách sẽ có điểm RRF cao nhất."
    )
    format_normal(p)

    # 2.4 RAG Architecture
    h = doc.add_paragraph('2.4. Retrieval-Augmented Generation (RAG) và Anti-Hallucination')
    format_heading(h, level=2)
    p = doc.add_paragraph(
        "Mô hình Ngôn ngữ Lớn (LLM) như Gemini 2.5 Flash rất giỏi xử lý ngôn ngữ, nhưng lại hay bị ảo giác (Hallucination) "
        "- tức là tự bịa ra thông tin pháp luật không có thật. Để giải quyết vấn đề này, kiến trúc RAG được áp dụng gồm 4 pha:\n\n"
        "1. Retrieve: Nhận câu hỏi, chuyển thành vector, truy vấn top-20 chunks bằng pgvector.\n"
        "2. Rerank: Áp dụng thuật toán RRF kết hợp BM25 và Vector Search để chọn lọc Top-5 chunks tốt nhất.\n"
        "3. Augment: Nén Top-5 chunks này vào System Prompt cùng với câu hỏi của người dùng.\n"
        "4. Generate: Yêu cầu LLM chỉ được phép trả lời dựa trên những chunks đã cung cấp. Nếu không tìm thấy, "
        "LLM buộc phải nói 'Không tìm thấy cơ sở pháp lý' thay vì cố gắng đoán mò.\n\n"
        "Toàn bộ luồng RAG được xây dựng theo kiểu Streaming (Server-Sent Events) để đảm bảo độ trễ trả về token đầu tiên "
        "(First-token latency) dưới 3 giây."
    )
    format_normal(p)

    # 2.5 Knowledge Graph
    h = doc.add_paragraph('2.5. Đồ thị Tri thức (Knowledge Graph) và Khai phá Dữ liệu')
    format_heading(h, level=2)
    p = doc.add_paragraph(
        "Cấu trúc pháp luật là một mạng lưới chằng chịt các văn bản hướng dẫn, sửa đổi, bãi bỏ lẫn nhau. "
        "Hệ thống mô hình hóa mạng lưới này thành Đồ thị Tri thức (Knowledge Graph) có hướng (Directed Graph) với:\n"
        "- Đỉnh (Nodes): Các văn bản pháp luật.\n"
        "- Cạnh (Edges): Quan hệ pháp lý (Guides, Amends, Replaces, Revokes, Cites).\n\n"
        "Dựa trên cấu trúc đồ thị này, hệ thống áp dụng các thuật toán Khai phá Dữ liệu (Data Mining):\n"
        "1. Thuật toán PageRank: Để xác định các 'văn bản rễ' có tầm ảnh hưởng lớn nhất trong hệ thống pháp luật.\n"
        "2. Thuật toán Louvain (Community Detection): Để phân cụm các văn bản liên quan mật thiết với nhau (Ví dụ: "
        "cụm văn bản Thuế GTGT, cụm Bảo hiểm Xã hội)."
    )
    format_normal(p)
