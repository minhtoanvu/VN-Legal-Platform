# AI Legal Intelligence Platform - System Analysis & Architecture

Dựa trên tài liệu "Khảo sát hiện trạng" và "Mô tả đề tài", đây là bản thiết kế hệ thống tổng thể (System Architecture) cho nền tảng "AI Legal Intelligence Platform" phục vụ doanh nghiệp Việt Nam.

## User Review Required

> [!IMPORTANT]
> Đây là bản phác thảo kiến trúc hệ thống theo chuẩn quy trình phần mềm. Vui lòng xem xét các quyết định công nghệ và luồng xử lý dưới đây. Hãy bấm **Proceed** (Tiếp tục) nếu bạn đồng ý với hướng đi này để chúng ta chuyển sang bước chia nhỏ công việc (Task Breakdown) và code.

## Open Questions

> [!WARNING]
> Để hệ thống hoàn chỉnh hơn, tôi cần bạn xác nhận 2 điểm sau (bạn có thể trả lời ở khung chat):
> 1. **Mô hình AI sinh thành (LLM):** Bạn dự tính sẽ gọi API của bên thứ 3 (như OpenAI GPT-4, Google Gemini) hay muốn dùng mô hình mã nguồn mở chạy local (do NCKH thường có giới hạn về kinh phí/phần cứng)?
> 2. **Xây dựng Knowledge Graph:** Bạn đã có sẵn script NLP để trích xuất các cụm từ quan hệ ("căn cứ", "thay thế") chưa, hay chúng ta sẽ phải tự code phần này bằng Regex/LLM?

## System Architecture

Dựa trên yêu cầu của đề tài, hệ thống sẽ được xây dựng theo kiến trúc Micro-monolith/Modular với 3 phân hệ chính:

### 1. Data & AI Pipeline (Xử lý dữ liệu & AI)
- **Nguồn dữ liệu:** Tận dụng 3 dataset có sẵn trên HuggingFace để không mất thời gian cào (crawl) lại từ đầu.
- **Vectorization:** Dùng một Embedding Model (tiếng Việt) chuyển văn bản thành vector ngữ nghĩa.
- **Lưu trữ lõi:** Sử dụng **PostgreSQL** có cài thêm extension **pgvector**. Tại đây sẽ chứa: Metadata, quan hệ văn bản, và Vector data.

### 2. Backend API (FastAPI + Python)
- Cung cấp REST API (hiệu năng cao, async) cho Frontend. Các module chính:
  - **Auth & Access Control:** Phân quyền Guest, User, Enterprise, Admin.
  - **Hybrid Search:** Kết hợp tìm kiếm BM25 (từ khóa) và Vector Search (ngữ nghĩa).
  - **RAG Engine (LangChain):** Quản lý luồng `Retrieve` (Tìm kiếm ngữ cảnh) -> `Augment` (Ghép prompt) -> `Generate` (Sinh câu trả lời).
  - **Knowledge Graph API:** Trả về dữ liệu nodes/edges cho Frontend vẽ biểu đồ.
  - **Analytics API:** Tính toán các chỉ số thống kê xu hướng cho Dashboard.
  - **Workspace API:** Quản lý bookmark và collection cá nhân/nhóm.

### 3. Frontend Web App (React + TypeScript)
- SPA (Single Page Application) tương tác cao:
  - **AI Chat Interface:** Giao diện hỏi đáp pháp luật, bắt buộc hiển thị rõ **nguồn trích dẫn (Citations)** để tránh AI nói mớ (Hallucination).
  - **Knowledge Graph Viewer:** Dùng `Vis.js` hoặc `D3.js` để render mạng lưới quan hệ văn bản luật.
  - **Dashboard:** Trực quan hóa dữ liệu xu hướng lập pháp bằng các thư viện Chart (như Recharts/Chart.js).

## Infrastructure & DevOps
- Đóng gói toàn bộ bằng **Docker** (có file `docker-compose.yml` để bạn dễ dàng deploy demo chấm điểm đồ án).
- Sử dụng **GitHub Actions** để thiết lập CI/CD cơ bản (chạy `pytest`).

## Verification Plan

### Automated Tests
- Viết `pytest` cho các endpoint FastAPI.
- Đánh giá chất lượng của luồng RAG bằng bộ dataset QA (`thangvip`).

### Manual Verification
- Chạy hệ thống local bằng Docker.
- Demo thực tế các tình huống nghiệp vụ đã nêu trong PDF (VD: Vai trò nhân viên HR tra cứu luật lao động, Xem sơ đồ liên kết văn bản).
