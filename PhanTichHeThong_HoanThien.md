# PHÂN TÍCH HỆ THỐNG

**ĐỒ ÁN NGÀNH — HK3 NĂM HỌC 2025–2026**

---

# AI LEGAL INTELLIGENCE PLATFORM
## Nền tảng hỗ trợ tra cứu, phân tích và khai thác tri thức pháp lý dành cho doanh nghiệp Việt Nam

**Sinh viên thực hiện:** Vũ Lưu Minh Toàn — MSSV: 2354050139  
**Khoa:** Công nghệ Thông tin — **Trường:** Đại học Mở TP. Hồ Chí Minh  
**Giảng viên hướng dẫn:** Hồ Hưởng Thiên  
**Năm học:** 2025–2026 — **Học kỳ:** 3  

---

## MỤC LỤC

1. Bối cảnh và Bài toán Thực tế
2. Khảo sát Hiện trạng Hệ thống
3. Cơ hội và Khoảng trống Thị trường
4. Mục tiêu và Phạm vi Đề tài
5. Đối tượng Người dùng và Giá trị Mang lại
6. Yêu cầu Chức năng và Phi Chức năng
7. Tác nhân và Đặc tả Use Case
8. Luồng Nghiệp vụ và Sơ đồ Hoạt động
9. Kiến trúc Hệ thống Tổng thể
10. Thiết kế Mô hình Dữ liệu
11. Nguồn Dữ liệu và Chiến lược AI
12. Phân tích Khai phá Dữ liệu
13. Tech Stack và Công nghệ
14. Kế hoạch Triển khai và Kiểm thử
15. Đánh giá Rủi ro và Giải pháp
16. Điểm khác biệt và Đóng góp

---

## 1. BỐI CẢNH VÀ BÀI TOÁN THỰC TẾ

### 1.1. Bức tranh Pháp lý Việt Nam

Hệ thống pháp luật Việt Nam hiện có hàng trăm nghìn văn bản quy phạm pháp luật, bao gồm Bộ luật, Luật, Nghị định, Thông tư, Công văn và Quyết định được ban hành và liên tục cập nhật bởi nhiều cơ quan nhà nước. Chỉ riêng năm 2023, các bộ ngành đã ban hành hơn **4.000 văn bản mới**. Tính đến năm 2024, Cơ sở dữ liệu Quốc gia về văn bản pháp luật (vbpl.vn) lưu trữ hơn **nửa triệu văn bản** — một khối lượng mà không một cá nhân hay bộ phận nào có thể theo dõi thủ công.

Điều này tạo ra áp lực cực lớn cho những người cần làm việc với pháp luật hàng ngày, đặc biệt là các **Doanh nghiệp vừa và nhỏ (SME)**.

### 1.2. Khó khăn Cụ thể theo Nhóm Người dùng

| Nhóm Người dùng | Khó khăn Thực tế | Hậu quả nếu không giải quyết |
| :--- | :--- | :--- |
| **Nhân viên Nhân sự (HR)** | Phải đọc nhiều văn bản dài, không biết văn bản nào còn hiệu lực, mất 2–4 giờ/lần kiểm tra | Áp dụng sai quy định, bị phạt hành chính, tranh chấp lao động |
| **Kế toán** | Luật thuế thay đổi liên tục, không có công cụ theo dõi hiệu lực | Khai sai thuế, bị truy thu và phạt; chi phí tư vấn cao |
| **Pháp chế & Chủ SME** | Phải tổng hợp nhiều văn bản liên quan nhưng không có công cụ hiển thị mối quan hệ | Sót điều khoản, vi phạm pháp luật, rủi ro kinh doanh cao |

---

## 2. KHẢO SÁT HIỆN TRẠNG HỆ THỐNG

### 2.1. Phân tích các Hệ thống Đang tồn tại

#### A. Thuvienphapluat.vn — Hệ thống phổ biến nhất

- **Về giao diện:** Quá nhiều banner quảng cáo, thông tin rườm rà, liên kết chéo phức tạp, dễ bị "lạc" trong ma trận điều khoản.
- **Về tìm kiếm:** Chỉ hỗ trợ tìm kiếm theo từ khóa chính xác. Không thể đặt câu hỏi tự nhiên như "Nghỉ phép năm được bao nhiêu ngày?". Không có Semantic Search.
- **Về phân tích:** Không có AI hỗ trợ, không có Dashboard thống kê, không có trực quan hóa quan hệ văn bản.
- **Về chi phí:** Gói thuê bao chi phí khá cao, không phù hợp với SME, sinh viên, freelancer.

#### B. Vbpl.vn — Cổng thông tin Pháp luật Chính phủ

- Giao diện cũ, không thân thiện với người dùng phổ thông.
- Tìm kiếm chỉ theo từ khóa, không hỗ trợ lọc phức tạp.
- Không có bất kỳ tính năng AI, phân tích hay trực quan hóa nào.
- Không có tài khoản người dùng, không lưu lịch sử, không có workspace.

#### C. VN-Law-Advisor (GitHub) — Dự án học thuật tiêu biểu nhất

Hệ thống gần nhất về mặt kỹ thuật — đạt giải Olympic Tin học Sinh viên. Có kiến trúc microservices, tích hợp RAG, semantic search và chatbot hỏi đáp pháp luật. Tuy nhiên vẫn còn thiếu:

- Không có công cụ phân tích dữ liệu pháp lý cho doanh nghiệp.
- Không có Dashboard thống kê xu hướng lập pháp.
- Không có Knowledge Graph trực quan hóa quan hệ giữa các văn bản.
- Không có Timeline lịch sử thay đổi của văn bản.
- Không có Workspace cá nhân/nhóm.
- Chưa hướng đến đối tượng doanh nghiệp và hỗ trợ ra quyết định kinh doanh.

### 2.2. Bảng So sánh Tổng hợp

| Tiêu chí | thuvienphapluat.vn | vbpl.vn | VN-Law-Advisor | **AI Legal Platform (đề xuất)** |
| :--- | :---: | :---: | :---: | :---: |
| Tìm kiếm từ khóa | Có | Có (hạn chế) | Có | **Có** |
| Tìm kiếm ngữ nghĩa AI | Không | Không | Có | **Có** |
| AI hỏi đáp pháp luật | Hạn chế | Không | Có | **Có** |
| Dashboard phân tích xu hướng | Không | Không | Không | **Có** |
| Knowledge Graph trực quan | Không | Không | Không | **Có** |
| Timeline lịch sử văn bản | Không | Không | Không | **Có** |
| Workspace cá nhân/nhóm | Không | Không | Không | **Có** |
| Hướng đến Doanh nghiệp | Có | Không | Không | **Có** |
| Miễn phí / Mã nguồn mở | Một phần | Có | Có | **Có** |

---

## 3. CƠ HỘI VÀ KHOẢNG TRỐNG THỊ TRƯỜNG

| # | Khoảng trống | Cơ hội cụ thể |
| :--- | :--- | :--- |
| **1** | Thiếu công cụ phân tích và trợ lý AI chuyên sâu | RAG Pipeline với LLM cho bài toán pháp lý tiếng Việt |
| **2** | Thiếu trực quan hóa quan hệ văn bản | Knowledge Graph động và tương tác |
| **3** | Thiếu công cụ phân tích dữ liệu pháp lý cho doanh nghiệp | Dashboard Data Analytics hỗ trợ ra quyết định |
| **4** | Thiếu không gian làm việc pháp lý cho nhóm | Workspace cá nhân và chia sẻ nội bộ |
| **5** | Chi phí tiếp cận cao | Mô hình freemium với tính năng AI cơ bản miễn phí |

---

## 4. MỤC TIÊU VÀ PHẠM VI ĐỀ TÀI

### 4.1. Mục tiêu Tổng quát

Xây dựng một nền tảng web tích hợp AI giúp doanh nghiệp tra cứu, phân tích và khai thác tri thức từ hệ thống văn bản pháp luật Việt Nam — hướng đến sản phẩm có thể sử dụng thực tế.

### 4.2. Mục tiêu Cụ thể — theo Nhu cầu Người dùng

| Nhu cầu Người dùng | Mục tiêu Hệ thống | Giải pháp Kỹ thuật |
| :--- | :--- | :--- |
| Tìm đúng văn bản khi không biết từ khóa chính xác | Tìm kiếm theo ngữ nghĩa câu hỏi tự nhiên | Semantic Search: Embedding Model + pgvector |
| Hỏi câu hỏi pháp luật có trích dẫn nguồn | Trợ lý AI trả lời pháp lý có căn cứ văn bản | RAG (Retrieval-Augmented Generation) + LLM |
| Hiểu mối quan hệ giữa các văn bản | Đồ thị trực quan mạng lưới quan hệ văn bản | Knowledge Graph + Vis.js |
| Theo dõi lịch sử thay đổi văn bản | Timeline sửa đổi, bổ sung, hết hiệu lực | Timeline component + dữ liệu quan hệ văn bản |
| Phân tích xu hướng pháp luật | Dashboard thống kê và phân tích dữ liệu | Data Analytics + Recharts |
| Lưu trữ và quản lý tài liệu pháp lý nội bộ | Workspace cá nhân/nhóm: bookmark, ghi chú | Workspace module + PostgreSQL |

### 4.3. Phạm vi và Giới hạn (10 tuần)

- **Về dữ liệu:** Tập trung 2 lĩnh vực cốt lõi: **Lao động – BHXH** và **Thuế – Kế toán**. Hạ tầng sẵn sàng để scale-up sau.
- **Về chức năng:** Hoàn thiện RAG, Semantic Search, Timeline, Workspace cá nhân. Tạm hoãn Workspace chia sẻ nhóm Enterprise và Export báo cáo.

---

## 5. ĐỐI TƯỢNG NGƯỜI DÙNG VÀ GIÁ TRỊ MANG LẠI

### 5.1. Stakeholder của Hệ thống

| Vai trò | Mô tả | Chức năng hệ thống sử dụng chính |
| :--- | :--- | :--- |
| **Admin** | Quản trị viên hệ thống, quản lý dữ liệu và người dùng | Quản lý văn bản, cập nhật dữ liệu, phân quyền |
| **Nhân viên HR** | Cần tra cứu Luật Lao động, BHXH, quy định tuyển dụng | Semantic Search, AI Assistant, Timeline, Dashboard |
| **Kế toán** | Cần tra cứu Luật Thuế, VAT, nghị định hướng dẫn | Semantic Search, AI Assistant, Notification thay đổi |
| **Nhân viên Pháp chế** | Cần phân tích quan hệ văn bản, kiểm tra hiệu lực | Knowledge Graph, Timeline, Workspace, Dashboard |
| **Chủ doanh nghiệp SME** | Cần hỏi đáp pháp luật bằng ngôn ngữ thông thường | AI Assistant, Dashboard tổng quan |
| **Sinh viên / Nhà nghiên cứu** | Học tập, nghiên cứu xu hướng lập pháp | Search, Knowledge Graph, Dashboard, Export |

---

## 6. YÊU CẦU CHỨC NĂNG VÀ PHI CHỨC NĂNG

### 6.1. Yêu cầu Chức năng (Functional Requirements)

| Mã | Nhóm | Yêu cầu Chức năng | Actor | Ưu tiên | Phạm vi |
| :--- | :--- | :--- | :--- | :--- | :--- |
| UC-01 | Xác thực | Đăng ký tài khoản bằng email | Guest | Cao | Đồ án |
| UC-02 | Xác thực | Đăng nhập / Đăng xuất an toàn qua JWT | Tất cả | Cao | Đồ án |
| UC-03 | Xác thực | Quản lý hồ sơ cá nhân và đổi mật khẩu | User | Trung bình | Đồ án |
| UC-04 | Tra cứu | Tìm kiếm văn bản theo từ khóa (BM25 Full-text) | Tất cả | Cao | Đồ án |
| UC-05 | Tra cứu | Tìm kiếm văn bản theo ngữ nghĩa (Semantic Search) | User, Enterprise | Cao | Đồ án |
| UC-06 | Tra cứu | Lọc đa chiều: lĩnh vực, cơ quan, thời gian, hiệu lực | Tất cả | Cao | Đồ án |
| UC-07 | Tra cứu | Xem chi tiết toàn văn, metadata và trạng thái hiệu lực | Tất cả | Cao | Đồ án |
| UC-08 | Tra cứu | Xem Timeline lịch sử thay đổi của một văn bản | Tất cả | Cao | Đồ án |
| UC-09 | AI Assistant | Hỏi đáp pháp luật bằng tiếng Việt tự nhiên (RAG) | User, Enterprise | Cao | Đồ án |
| UC-10 | AI Assistant | Xem và truy xuất nguồn trích dẫn từ câu trả lời AI | User, Enterprise | Cao | Đồ án |
| UC-11 | AI Assistant | Yêu cầu AI tóm tắt văn bản pháp lý dài | User, Enterprise | Trung bình | Đồ án |
| UC-12 | Knowledge Graph | Xem đồ thị trực quan quan hệ giữa các văn bản | User, Enterprise | Cao | Đồ án |
| UC-13 | Knowledge Graph | Duyệt và chuyển hướng từ node trên đồ thị | User, Enterprise | Trung bình | Đồ án |
| UC-14 | Dashboard | Xem Dashboard phân tích tổng quan dữ liệu pháp luật | User, Enterprise | Cao | Đồ án |
| UC-15 | Dashboard | Lọc và Drill-down Dashboard theo lĩnh vực/thời gian | User, Enterprise | Trung bình | Đồ án |
| UC-16 | Workspace | Đánh dấu (Bookmark) văn bản vào Collection cá nhân | User, Enterprise | Trung bình | Đồ án |
| UC-17 | Workspace | Đính kèm ghi chú (Note) cá nhân vào văn bản | User, Enterprise | Thấp | Đồ án |
| UC-18 | Workspace | Chia sẻ Collection trong nhóm doanh nghiệp | Enterprise | Thấp | Roadmap |
| UC-19 | Báo cáo | Xuất báo cáo phân tích Dashboard ra PDF/Excel | Enterprise | Thấp | Roadmap |
| UC-20 | Quản trị | Quản lý, phân quyền và thống kê người dùng | Admin | Cao | Đồ án |
| UC-21 | Quản trị | Quản lý Thêm/Sửa/Xóa/Sync dữ liệu văn bản | Admin | Cao | Đồ án |

### 6.2. Yêu cầu Phi Chức năng (Non-Functional Requirements)

| Thuộc tính | Yêu cầu Kỹ thuật & Chỉ số Đo lường |
| :--- | :--- |
| **Hiệu năng** | Tìm kiếm từ khóa < 1 giây. Luồng RAG < 5 giây. Knowledge Graph (< 100 nodes) < 2 giây. |
| **Mở rộng** | Kiến trúc Modular, dễ thêm module mới. pgvector tối ưu cho hàng triệu records. |
| **Bảo mật** | Bcrypt cho mật khẩu. JWT Token (Access 30 phút, Refresh 7 ngày). RBAC phân quyền API. |
| **Sẵn sàng** | LLM API timeout > 10 giây → Fallback về Semantic Search, không làm đứng hệ thống. |
| **Bảo trì** | PEP8 (Python), ESLint (TypeScript). Swagger/OpenAPI tự sinh. Cấu hình qua .env. |
| **UX/UI** | Minimalist, không quảng cáo. Responsive mọi thiết bị. Skeleton UI khi gọi AI. |

---

## 7. TÁC NHÂN VÀ ĐẶC TẢ USE CASE

### 7.1. Phân tích Tác nhân (Actors)

1. **Khách (Guest):** Chưa đăng nhập. Chỉ tra cứu cơ bản, xem nội dung công khai và Dashboard tổng quan.
2. **User:** Đã tạo tài khoản miễn phí. Được dùng Semantic Search, AI, Knowledge Graph, Bookmark cá nhân.
3. **Enterprise User:** Nhân sự đã đăng ký gói Doanh nghiệp. Thêm Workspace chia sẻ nhóm và Export.
4. **Admin:** Quản lý toàn bộ nền tảng, tài khoản người dùng và CSDL văn bản.

### 7.2. Đặc tả 5 Use Case Cốt lõi

---

**UC-05: Tìm kiếm Văn bản theo Ngữ nghĩa**

- **Tác nhân:** User, Enterprise User | **Tiền điều kiện:** Đã đăng nhập.
- **Luồng chính:**
  1. Người dùng gõ câu hỏi tự nhiên (VD: "Nghỉ phép năm tối đa bao nhiêu ngày?").
  2. Chọn chế độ "Tìm kiếm thông minh".
  3. Backend embedding câu hỏi thành vector ngữ nghĩa bằng Embedding Model.
  4. Truy vấn Cosine Similarity tìm Top-10 DocumentChunk gần nhất.
  5. Re-rank theo metadata (ưu tiên văn bản còn hiệu lực, ban hành gần nhất).
  6. Trả về kết quả kèm đoạn trích highlight.
- **Ngoại lệ:** Câu hỏi < 5 ký tự → Yêu cầu nhập chi tiết. Score < 0.5 → Gợi ý tìm kiếm từ khóa.

---

**UC-09: Hỏi đáp Pháp luật với AI (RAG Pipeline)**

- **Tác nhân:** User, Enterprise | **Tiền điều kiện:** Đã đăng nhập, có kết nối LLM API.
- **Luồng RAG chi tiết:**
  1. Người dùng nhập câu hỏi pháp lý vào AI Chat Interface.
  2. **[Retrieve]** Embedding câu hỏi → Truy vấn pgvector → Lấy Top-5 chunks có độ tương đồng cao nhất.
  3. **[Augment]** Xây dựng System Prompt: `[Vai trò AI] + [5 đoạn ngữ cảnh] + [Câu hỏi] + [Chỉ dẫn chống Hallucination]`.
  4. **[Generate]** Gửi Prompt cho LLM (Gemini 2.5 Flash / GPT-4o-mini).
  5. AI stream câu trả lời, cuối có danh sách Citations click được.
  6. Click vào Citation → Mở trang chi tiết văn bản nguồn.
- **Ngoại lệ:** LLM timeout → Thông báo thân thiện + fallback Semantic Search.

---

**UC-12: Khám phá Knowledge Graph**

- **Tác nhân:** User, Enterprise.
- **Luồng chính:**
  1. Từ trang chi tiết văn bản A, click "Mở Knowledge Graph".
  2. Backend truy vấn DocumentRelation, lấy quan hệ của văn bản A ở depth = 2.
  3. Vis.js render đồ thị: Node = Văn bản, Edge = Loại quan hệ (mã hóa màu: Hướng dẫn = Xanh, Sửa đổi = Cam, Thay thế = Tím, Bãi bỏ = Đỏ).
  4. Hover → Popup tóm tắt. Double-click → Điều hướng đến văn bản đó.

---

**UC-14: Phân tích Dữ liệu Pháp luật (Dashboard)**

- **Luồng chính:**
  1. Truy cập tab Dashboard. Render 5 biểu đồ: Line Chart (tốc độ ban hành theo năm), Pie Chart (phân bổ lĩnh vực), Bar Chart (top cơ quan ban hành), Heatmap Calendar (tần suất theo tháng), KPI Cards (tổng quan).
  2. Người dùng filter theo lĩnh vực "Lao động" và khoảng "2020–2024".
  3. Toàn bộ biểu đồ đồng loạt cập nhật (Reactive Updates).

---

**UC-08: Xem Timeline Lịch sử Văn bản**

- **Tác nhân:** Tất cả (kể cả Guest) | **Mục đích:** Không áp dụng nhầm luật đã hết hiệu lực.
- **Luồng chính:**
  1. Mở chi tiết văn bản, tab "Lịch sử / Timeline".
  2. Hệ thống vẽ trục thời gian dọc với các mốc màu sắc:
     - Ngày ban hành (Xanh lá) → Ngày có hiệu lực (Xanh dương) → Sửa đổi/bổ sung (Cam) → Hết hiệu lực (Đỏ).
  3. Click vào mốc sửa đổi → Mở văn bản sửa đổi tương ứng.

---

## 8. LUỒNG NGHIỆP VỤ VÀ SƠ ĐỒ HOẠT ĐỘNG

**Luồng 1: Tìm kiếm và Tra cứu Văn bản**

Người dùng → Search Bar → [BM25 hoặc Semantic] → Embedding/pgvector → Re-rank → Kết quả → [Toàn văn / Timeline / Graph / Bookmark]

**Luồng 2: Hỏi đáp với AI (RAG)**

Người dùng → Câu hỏi → Backend → [Retrieve: pgvector Top-5] → [Augment: System Prompt] → [Generate: LLM] → [Stream Response + Citations] hoặc [Fallback: Semantic Search nếu timeout]

**Luồng 3: Phân tích Dashboard**

Người dùng → Dashboard → Chọn lĩnh vực + thời gian → Aggregation Query → Render 5 biểu đồ đồng loạt → Filter/Drill-down/Export

---

## 9. KIẾN TRÚC HỆ THỐNG TỔNG THỂ

Hệ thống xây dựng theo kiến trúc **Modular Monolith** kết hợp **Component-based Frontend**.

**Tầng Frontend (React 18 + TypeScript + Vite):**
- Search & Filter UI
- AI Chat Interface (streaming)
- Knowledge Graph Visualization (Vis.js)
- Dashboard (Recharts)
- Auth, Workspace, Timeline Components

**Tầng Backend (FastAPI + Python 3.11+):**
- Auth & RBAC Module
- Search API (BM25 + Semantic Hybrid)
- RAG Engine (LangChain + LLM)
- Knowledge Graph API
- Analytics API (Dashboard)
- Workspace API (Bookmark, Note, Collection)
- Embedding Service (Sentence Transformers)

**Tầng Dữ liệu:**
- PostgreSQL 16 + pgvector (lưu metadata + vector embedding)
- External LLM API: Google Gemini 2.5 Flash / OpenAI GPT-4o-mini

---

## 10. THIẾT KẾ MÔ HÌNH DỮ LIỆU

Kiến trúc Database chuẩn hóa trên **PostgreSQL**, phục vụ Relational query, Full-text search và Vector search qua **pgvector**.

**Bảng documents** — Lưu metadata văn bản pháp luật:
- id (UUID PK), doc_number, title, doc_type, issuing_body, field, issue_date, effective_date, expired_date, status ('active'/'expired'/'amended'), content, source_url, created_at

**Bảng document_chunks** — Dữ liệu nền cho RAG:
- id (UUID PK), document_id (FK → documents), chunk_index, content_chunk (256–512 tokens), embedding (VECTOR(768) pgvector), token_count
- Index: `CREATE INDEX USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)`

**Bảng document_relations** — Dữ liệu nền cho Knowledge Graph:
- id, source_doc_id (FK), target_doc_id (FK), relation_type (GUIDES/AMENDS/REPLACES/REVOKES/CITES), description
- UNIQUE(source_doc_id, target_doc_id, relation_type)

**Bảng users** — Xác thực và phân quyền:
- id, email (UNIQUE), password_hash (Bcrypt), full_name, role ('user'/'enterprise'/'admin'), organization_id, created_at

**Workspace Entities:**
- `collections`: id, name, owner_id (FK users), is_shared (BOOL), created_at
- `collection_documents`: (collection_id, document_id) — bảng trung gian n-n
- `notes`: id, user_id, document_id, content, created_at
- `query_logs`: id, user_id, query_text, query_type ('keyword'/'semantic'/'ai_chat'), created_at

---

## 11. NGUỒN DỮ LIỆU VÀ CHIẾN LƯỢC AI

### 11.1. Nguồn Dữ liệu Mở (Tận dụng sẵn có trên HuggingFace)

| Dataset | Nội dung | Mục đích sử dụng |
| :--- | :--- | :--- |
| th1nhng0/vietnamese-legal-documents | Hơn nửa triệu văn bản, có cấu trúc phân cấp và đồ thị quan hệ | Dữ liệu văn bản chính, xây dựng DB và Knowledge Graph |
| tmquan/phapdien-moj-gov-vn | Pháp điển điện tử từ Bộ Tư pháp, hệ thống hóa theo chủ đề | Bổ sung dữ liệu có cấu trúc chủ đề tốt |
| tmquan/thuvienphapluat-vn-tnpl | Văn bản bổ sung từ thuvienphapluat.vn | Mở rộng độ phủ dữ liệu |
| thangvip/vietnamese-legal-qa | 9.715 cặp hỏi-đáp pháp luật tiếng Việt | Đánh giá chất lượng AI Assistant (Evaluation) |

### 11.2. Quy trình ETL và Embedding

1. **Extract:** Tải từ HuggingFace → Chuẩn hóa schema về bảng `documents`.
2. **Transform:** Lọc 2 lĩnh vực → Cắt chunks 256–512 tokens với sliding window có overlap.
3. **Embed:** Embedding bằng `paraphrase-multilingual-mpnet-base-v2` (hỗ trợ tiếng Việt, 768 chiều).
4. **Load:** Metadata vào `documents`, vector vào `document_chunks.embedding`.

### 11.3. Chiến lược Hybrid Search

- **BM25 Full-text Search:** Tìm kiếm chính xác theo từ khóa — dùng PostgreSQL Full-Text Search.
- **Semantic Search:** Embedding câu hỏi → Cosine Similarity với document_chunks → Top-K chunks.
- **Hybrid Re-ranking:** Kết hợp BM25 score + Cosine Similarity score để trả về kết quả tốt nhất.

### 11.4. Anti-Hallucination trong RAG

System Prompt bắt buộc AI chỉ trả lời dựa trên Context được cấp. Nếu không đủ thông tin, AI phải nói rõ thay vì bịa đặt. Mỗi luận điểm phải có trích dẫn nguồn cụ thể (tên văn bản, điều khoản).

---

## 12. PHÂN TÍCH KHAI PHÁ DỮ LIỆU

Hệ thống không chỉ là công cụ tra cứu tĩnh — đóng vai trò **Data Analyst** khai phá tri thức lập pháp:

| Câu hỏi Tri thức Kinh doanh | Kỹ thuật | Ý nghĩa Thực tiễn |
| :--- | :--- | :--- |
| Lĩnh vực nào có xáo trộn pháp lý mạnh nhất? | Aggregation theo field × year. Heatmap. | Biết cần dồn nguồn lực theo dõi rủi ro lĩnh vực nào. |
| "Văn bản rễ" chi phối toàn hệ thống là gì? | Directed Graph + thuật toán PageRank trên nodes. | Top 10 văn bản nền tảng không thể bỏ qua. |
| Pháp luật VN có tính "Mùa vụ" ban hành không? | Phân phối tần suất theo tháng. Heatmap Calendar. | Dự báo tháng "nóng" để chuẩn bị cập nhật chính sách. |
| Lĩnh vực nào ràng buộc, chồng chéo nhau? | Community Detection (Louvain) trên Knowledge Graph. | Gom cụm lĩnh vực — VD Lao động kéo theo Bảo hiểm, Thuế TNCN. |

---

## 13. TECH STACK VÀ CÔNG NGHỆ

| Tầng | Công nghệ | Mục đích | Lý do Lựa chọn |
| :--- | :--- | :--- | :--- |
| Backend | FastAPI (Python 3.11+) | API server | Async ASGI, tự sinh Swagger, type hints |
| Frontend | React 18 + TypeScript + Vite | SPA | Component-based, type-safe, ecosystem phong phú |
| Database | PostgreSQL 16 + pgvector | Metadata + Vector | All-in-one: relational + full-text + vector |
| ORM | SQLAlchemy 2.0 | DB Access Layer | Async support, dễ migrate |
| AI Embedding | paraphrase-multilingual-mpnet-base-v2 | Text → vector 768 chiều | Hỗ trợ tiếng Việt, mã nguồn mở, miễn phí |
| AI Generation | Google Gemini 2.5 Flash / GPT-4o-mini | Sinh câu trả lời RAG | Free tier, tốc độ nhanh, đa ngôn ngữ tốt |
| AI Orchestration | LangChain | Quản lý RAG Pipeline | Framework chuẩn, tài liệu phong phú |
| Graph | Vis.js Network | Knowledge Graph tương tác | Tối ưu network graph, hỗ trợ zoom/pan/drag |
| Charts | Recharts | Dashboard biểu đồ | Tích hợp tốt React, responsive |
| Auth | JWT + Bcrypt | Xác thực bảo mật | Stateless, phù hợp REST API |
| DevOps | Docker + Docker Compose | Container hóa hệ thống | Dễ deploy demo, môi trường nhất quán |
| CI/CD | GitHub Actions | Tự động test khi push | Miễn phí cho repo công khai |
| Testing | pytest + httpx | Unit + Integration test | Chuẩn Python, hỗ trợ async FastAPI |

---

## 14. KẾ HOẠCH TRIỂN KHAI VÀ KIỂM THỬ

### 14.1. Lộ trình 10 Tuần

| Tuần | Giai đoạn | Nội dung chính | Output |
| :---: | :--- | :--- | :--- |
| 1 | Setup & Dữ liệu | Cấu hình Docker, DB schema, ETL Pipeline tải 2 lĩnh vực | DB có dữ liệu, pgvector ready |
| 2 | ETL & Embedding | Cắt chunk, Embedding và nạp vào pgvector | Toàn bộ chunks được embed |
| 3 | Backend Core | Auth, Search API (BM25 + Semantic), Document detail | API /auth /search /documents |
| 4 | Backend AI + Graph | RAG Engine (LangChain), Knowledge Graph API, Analytics API | API /ai/chat /graph /analytics |
| 5 | Frontend Foundation | React setup, UI Search, Document detail, Timeline | Giao diện tìm kiếm và xem văn bản |
| 6 | Frontend AI + Graph | UI AI Chat (streaming), Knowledge Graph (Vis.js) | AI Chat và Graph trên giao diện |
| 7 | Frontend Dashboard + Workspace | Dashboard Charts, Workspace (Bookmark, Note, Collection) | Dashboard và Workspace hoàn chỉnh |
| 8 | Tích hợp & Testing | Kiểm thử E2E, sửa lỗi, Evaluation RAG | Test pass, RAG quality đạt ngưỡng |
| 9 | Tối ưu & UX Polish | Cải thiện hiệu năng, UI/UX, Responsive | Hệ thống mượt trên mọi thiết bị |
| 10 | Báo cáo & Demo | Hoàn thiện báo cáo, slide, demo video | Báo cáo hoàn chỉnh + Demo live |

### 14.2. Chiến lược Kiểm thử

**Kiểm thử Tự động:**
- pytest tests/ -v --cov=app --cov-report=html
- pytest tests/test_rag_pipeline.py (đánh giá chất lượng RAG)
- pytest tests/test_performance.py (đo thời gian phản hồi)

**Đánh giá Chất lượng AI:** Dùng `thangvip/vietnamese-legal-qa` (9.715 cặp QA).
- Đo: MRR@5, Hit@5 cho Retrieval. Faithfulness và Answer Relevancy cho Generation.

**Kiểm thử Thủ công — 3 kịch bản nghiệp vụ:**
1. HR scenario: Tra cứu quy định thử việc, xem timeline Bộ Luật Lao động.
2. CEO scenario: Hỏi AI về quy định làm thêm giờ cuối tuần, nhận trích dẫn điều khoản.
3. Legal scenario: Mở Knowledge Graph lĩnh vực Lao động nước ngoài, duyệt mạng lưới văn bản.

---

## 15. ĐÁNH GIÁ RỦI RO VÀ GIẢI PHÁP

| Rủi ro | Mức độ | Giải pháp Xử lý |
| :--- | :---: | :--- |
| Embedding hơn 500.000 văn bản quá tải máy cá nhân | Cao | Chỉ embed 2 lĩnh vực trọng tâm (khoảng 50.000 văn bản). Hạ tầng sẵn sàng scale-up sau. |
| Trích xuất tự động Quan hệ văn bản bị sót | Trung bình | Tận dụng dữ liệu quan hệ từ dataset th1nhng0 (đã có sẵn) + Rule-based Regex. |
| API LLM Timeout hoặc Rate Limit | Trung bình | Caching câu hỏi phổ biến; Circuit Breaker > 10 giây; Fallback về Semantic Search. |
| AI trả lời sai (Hallucination) | Cao | System Prompt Anti-Hallucination; AI chỉ dựa trên Context; Luôn hiển thị Citations. |
| Thiếu thời gian hoàn thiện trong 10 tuần | Trung bình | Ưu tiên UC Cao trước. Workspace chia sẻ nhóm, Export báo cáo đưa vào Roadmap. |

---

## 16. ĐIỂM KHÁC BIỆT VÀ ĐÓNG GÓP

### 16.1. Ba Tính năng Độc quyền (Chưa có hệ thống nào trong nước đồng thời)

1. **Dashboard phân tích xu hướng lập pháp** theo thời gian.
2. **Knowledge Graph trực quan hóa mạng lưới quan hệ** giữa văn bản.
3. **Workspace nhóm** cho phép lưu trữ và chia sẻ tài liệu pháp lý trong tổ chức.

### 16.2. Đóng góp Khoa học và Thực tiễn

1. **Thực tiễn:** Nền tảng giúp SME tra cứu pháp luật nhanh, giảm chi phí pháp lý.
2. **Kỹ thuật:** Kiểm chứng Hybrid Search (BM25 + Semantic) + RAG cho bài toán pháp luật tiếng Việt trên pgvector.
3. **Dữ liệu:** Pipeline ETL chuẩn hóa từ dataset mở, tạo Knowledge Graph tái sử dụng cho nghiên cứu Legal NLP.
4. **Mở rộng:** Nền tảng sẵn sàng tích hợp Module Phân tích Hợp đồng (CoT Prompting) từ đề tài NCKH riêng, tạo thành hệ sinh thái LegalTech Việt Nam toàn diện.

---

## TÀI LIỆU THAM KHẢO

**Nguồn Kỹ thuật:**
1. Lewis, P. et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," NeurIPS, 2020.
2. Reimers, N. & Gurevych, I., "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks," EMNLP, 2019.
3. Johnson, J. et al., "Billion-scale similarity search with GPUs," IEEE Transactions on Big Data, 2021.

**Nguồn Pháp lý & Dữ liệu:**
4. th1nhng0, "vietnamese-legal-documents," HuggingFace, 2024. https://huggingface.co/datasets/th1nhng0/vietnamese-legal-documents
5. thangvip, "vietnamese-legal-qa," HuggingFace, 2024. https://huggingface.co/datasets/thangvip/vietnamese-legal-qa
6. tmquan, "phapdien-moj-gov-vn," HuggingFace, 2024. https://huggingface.co/datasets/tmquan/phapdien-moj-gov-vn
7. Cổng thông tin điện tử Chính phủ, "Cơ sở dữ liệu quốc gia về văn bản pháp luật," 2024. https://vbpl.vn
8. CTU-LinguTechies, "VN-Law-Advisor," GitHub, 2024. https://github.com/CTU-LinguTechies/VN-Law-Advisor
9. Thuvienphapluat.vn, "Hướng dẫn sử dụng," 2024. https://thuvienphapluat.vn/hdsd.aspx
10. hronline.vn, "Luật Lao Động 2026 – Những thay đổi HR cần biết ngay," 2025. https://hronline.vn/luat-lao-dong-2026-nhung-thay-doi-hr-can-biet-ngay

---
*Tài liệu này đóng vai trò là "Bản lề" (Blueprint) — căn cứ để bắt tay vào thiết kế Database Schema chi tiết, cấu trúc API và layout giao diện. Mọi quyết định kỹ thuật phải tuân thủ các ràng buộc và ưu tiên được xác định trong tài liệu này.*
