# Phân tích mối liên hệ giữa 2 đề tài

## Tổng quan: Bạn đang làm 2 đề tài song song

| | Đồ án ngành (cá nhân) | NCKH (nhóm) |
|---|---|---|
| **Tên** | AI Legal Intelligence Platform | CoT Prompting phân tích rủi ro hợp đồng |
| **Phạm vi** | Toàn nền tảng pháp lý doanh nghiệp | Chỉ module phân tích hợp đồng |
| **Thời gian** | HK3 năm 2025–2026 (10 tuần) | 6 tháng, 2026–2027 |
| **Quy mô** | Lớn — platform đầy đủ | Nhỏ — nghiên cứu 1 kỹ thuật |
| **Vai trò** | Bạn là chủ đề tài | Nhóm nghiên cứu |

---

## Mối quan hệ: NCKH là "module nổi bật" trong Đồ án

```
Đồ án ngành — AI Legal Intelligence Platform
│
├── Semantic Search (Vector DB + Embedding)         ← Core feature
├── AI Assistant / RAG Q&A                          ← Core feature
├── Knowledge Graph (quan hệ văn bản)               ← Độc đáo
├── Timeline lịch sử văn bản                        ← Độc đáo
├── Dashboard phân tích xu hướng lập pháp           ← Độc đáo
├── Workspace cá nhân/nhóm                          ← Độc đáo
│
└── ★ MODULE PHÂN TÍCH HỢP ĐỒNG (CoT + RAG)        ← ĐÂY LÀ NCKH
      → Phân tích rủi ro điều khoản
      → Có căn cứ pháp lý trích dẫn
      → Đây là điểm "Có thể tích thêm module
         phân tích hợp đồng sau này" đã đề cập
         trong khảo sát hiện trạng của đồ án!
```

> **Đây là thiết kế rất thông minh**: NCKH là công trình nghiên cứu kỹ thuật mới (CoT Prompting), sau khi hoàn thành sẽ được tích hợp vào đồ án như một tính năng cao cấp.

---

## Điều đồ án đang xây dựng (từ file Mô tả đề tài)

### Platform AI Legal Intelligence — 6 tính năng cốt lõi:

| # | Tính năng | Kỹ thuật | Người dùng chính |
|---|---|---|---|
| 1 | **Semantic Search** | Embedding + Vector DB | HR, Kế toán, Pháp chế |
| 2 | **AI Assistant (RAG Q&A)** | RAG + LLM | Chủ SME, HR |
| 3 | **Knowledge Graph** | Graph DB + Visualization | Pháp chế |
| 4 | **Timeline văn bản** | Data tracking | HR, Kế toán |
| 5 | **Dashboard phân tích** | Data Analytics | Giám đốc, Quản lý |
| 6 | **Workspace cá nhân/nhóm** | PostgreSQL | Tất cả |

### Phạm vi dữ liệu đồ án (10 tuần):
- **2 lĩnh vực cốt lõi** cho SME: Lao động-BHXH + Thuế-Kế toán
- Nguồn dữ liệu: `vbpl.vn`, HuggingFace datasets (th1nhng0, thangvip, tmquan)

---

## NCKH bổ sung gì cho đồ án?

### Đồ án có RAG Q&A rồi — NCKH nâng cấp lên tầm mới:

```
Đồ án — AI Assistant (RAG thông thường):
  Câu hỏi → Tìm văn bản → LLM trả lời → Hiển thị

NCKH — CoT + RAG + Self-Reflection:
  Upload HĐ → Trích xuất điều khoản →
  Đối chiếu kho luật (RAG) →
  Phân tích từng bước (CoT) →
  Tự kiểm tra lại (Self-Reflection) →
  Kết quả: risk_level + trích dẫn điều luật cụ thể
```

**Giá trị thêm vào đồ án:**
- Từ "hỏi đáp pháp luật" → "phân tích hợp đồng có chuyên sâu"
- Từ trả lời chung chung → trích dẫn đúng điều khoản pháp luật
- Tính năng mà **không hệ thống nào trong nước có đồng thời**

---

## Điểm tương đồng kỹ thuật — Dùng chung được

| Component | Đồ án dùng | NCKH dùng | Dùng chung? |
|---|---|---|---|
| Vector DB | ✅ (Semantic Search) | ✅ (Kho luật) | ✅ Dùng chung 1 ChromaDB |
| LLM API | ✅ (RAG Q&A) | ✅ (CoT Analysis) | ✅ Cùng Gemini API |
| Embedding Model | ✅ | ✅ | ✅ vietnamese-sbert |
| PDF Extraction | ❓ (văn bản luật) | ✅ (hợp đồng) | ✅ Cùng pdfplumber |
| Backend | ✅ FastAPI/Python | ✅ FastAPI/Python | ✅ Cùng 1 backend |
| PostgreSQL | ✅ (Workspace) | ❌ | Đồ án có sẵn |

→ **NCKH xây dựng song song, sau đó tích hợp vào đồ án như 1 module.**

---

## Dữ liệu cần cho từng đề tài

### Đồ án ngành cần:

| Loại dữ liệu | Nguồn | Lĩnh vực |
|---|---|---|
| Văn bản luật, nghị định, thông tư | vbpl.vn, thuvienphapluat.vn | Lao động, Thuế |
| Dataset pháp lý tiếng Việt | HuggingFace: th1nhng0/vietnamese-legal-documents | Toàn diện |
| Dataset Q&A pháp luật | HuggingFace: thangvip/vietnamese-legal-qa | Q&A |
| Pháp điển Bộ Tư Pháp | HuggingFace: tmquan/phapdien-moj-gov-vn | Pháp điển |

### NCKH cần (thêm vào so với đồ án):

| Loại dữ liệu | Nguồn | Ghi chú |
|---|---|---|
| Hợp đồng mô phỏng tiếng Việt có nhãn | Tự tạo bằng AI | 180 điều khoản |
| Văn bản luật PDF (3-5 bộ) | vbpl.vn | Đã có từ đồ án |
| Bộ tiêu chí gán nhãn rủi ro | Tự xây dựng từ luật | Tháng 1 |

---

## Kế hoạch đồng bộ 2 đề tài

### Thứ tự ưu tiên hợp lý:

```
Hiện tại (Tháng 8/2026):
  └── Đồ án ngành đang trong giai đoạn phát triển (10 tuần)
      → Ưu tiên hoàn thành đồ án trước

Tháng 9-10/2026:
  └── NCKH bắt đầu (Tháng 1 của lộ trình 6 tháng)
      → Thu thập dataset hợp đồng + Xây kho luật
      → Dùng lại kho luật đã có từ đồ án!

Tháng 11-12/2026:
  └── NCKH Tháng 2-3: Xây pipeline CoT

Tháng 1-2/2027:
  └── NCKH Tháng 4-5: Web app + Thực nghiệm
      → Tích hợp module vào đồ án nếu cần

Tháng 3/2027:
  └── NCKH Tháng 6: Báo cáo hoàn thành
```

---

## Câu trả lời cho câu hỏi ban đầu

### Dữ liệu pháp lý — cần lấy ở đâu?

Đồ án đã xác định rõ 4 nguồn dataset sẵn có trên HuggingFace:

```bash
# Dataset 1: Văn bản pháp luật tiếng Việt (full text)
https://huggingface.co/datasets/th1nhng0/vietnamese-legal-documents

# Dataset 2: Q&A pháp luật tiếng Việt
https://huggingface.co/datasets/thangvip/vietnamese-legal-qa

# Dataset 3: Pháp điển Bộ Tư Pháp
https://huggingface.co/datasets/tmquan/phapdien-moj-gov-vn

# Nguồn chính thức:
https://vbpl.vn  (Cơ sở dữ liệu văn bản pháp luật Chính phủ)
```

> [!IMPORTANT]
> **Bạn KHÔNG cần thu thập dữ liệu pháp lý từ đầu!** Đã có sẵn các dataset tiếng Việt trên HuggingFace. Chỉ cần tải về và xử lý.

### NCKH cần làm thêm gì so với đồ án?

Chỉ cần bổ sung **1 loại dữ liệu duy nhất mà đồ án chưa có**:

> **Bộ dataset hợp đồng mô phỏng tiếng Việt** — 180 điều khoản có nhãn rủi ro low/medium/high

Đây là phần NCKH tự tạo, không có sẵn trên internet vì là bộ tiếng Việt đặc thù.

---

## Tóm tắt

```
Đồ án = Nền tảng đầy đủ (tra cứu + Q&A + visualize + workspace)
NCKH  = Nghiên cứu sâu 1 kỹ thuật (CoT + RAG phân tích hợp đồng)

→ NCKH là "viên ngọc" được thêm vào đồ án sau này
→ Dữ liệu pháp lý: dùng chung từ HuggingFace + vbpl.vn
→ Dữ liệu hợp đồng: NCKH tự tạo (dataset gán nhãn)
→ Kỹ thuật: RAG, Embedding, LLM — dùng chung giữa 2 đề tài
```
