# Kế hoạch thực hiện NCKH: Ứng dụng CoT Prompting phân tích rủi ro hợp đồng AI

## Tổng quan đề tài

**Tên đề tài:** Ứng dụng kỹ thuật Chain-of-Thought Prompting trong phân tích và đánh giá rủi ro văn bản hợp đồng sử dụng tác tử AI  
**Thời gian:** 6 tháng | **Năm học:** 2026–2027  
**Người thực hiện:** Vũ Lưu Minh Toàn (2354050139) — Khoa CNTT, ĐH Mở TP.HCM  
**GVHD:** Hồ Hưởng Thiên

---

## Mục tiêu cốt lõi

Xây dựng hệ thống **Single-Agent AI** phân tích hợp đồng tiếng Việt, tự động:
1. Trích xuất & phân đoạn điều khoản từ file PDF/text
2. Phân tích từng điều khoản bằng **Structured CoT Prompting**
3. Phân loại mức độ rủi ro: **Thấp / Trung bình / Cao**
4. Tự phản ánh kết quả qua cơ chế **Self-Reflection**
5. Hiển thị kết quả trên **web app** với highlight màu theo mức rủi ro

---

## Lộ trình thực hiện theo 6 tháng

### 📅 Tháng 1 — Thu thập tài liệu & Xây dựng Dataset

#### Mục tiêu:
- Có bộ dữ liệu hợp đồng mô phỏng tiếng Việt đã gán nhãn rủi ro.

#### Cách làm cụ thể:

**Bước 1: Nghiên cứu lý thuyết nền**
- Đọc và tóm tắt 5 tài liệu tham khảo chính:
  - Wei et al. (2022) — Chain-of-Thought Prompting [NeurIPS]
  - Chalkidis et al. (2020) — LEGAL-BERT
  - Koreeda & Manning (2021) — ContractNLI
  - Shinn et al. (2023) — Reflexion framework
  - Brown et al. (2020) — Few-Shot Learners
- Nghiên cứu quy định pháp luật Việt Nam: Bộ luật Lao động 2019, Luật Thương mại 2005

**Bước 2: Thu thập hợp đồng mẫu**
- Thu thập 30–50 hợp đồng mô phỏng (không dùng hợp đồng thật):
  - Hợp đồng lao động (~15 mẫu)
  - Hợp đồng mua bán hàng hóa (~15 mẫu)
  - Hợp đồng cung cấp dịch vụ (~15 mẫu)
- Mỗi hợp đồng có 5–10 điều khoản đa dạng

**Bước 3: Xây dựng bộ tiêu chí gán nhãn rủi ro**

| Tiêu chí | Mô tả | Mức độ rủi ro |
|----------|-------|---------------|
| Điều khoản phạt vi phạm | Phạt không xác định / vô lý cao | Cao |
| Điều khoản bồi thường | Giới hạn bồi thường bất lợi | Trung bình–Cao |
| Điều khoản chấm dứt | Điều kiện đơn phương / không rõ | Trung bình–Cao |
| Điều khoản bất khả kháng | Thiếu hoặc mơ hồ | Trung bình |
| Điều khoản thanh toán | Điều kiện không rõ ràng | Thấp–Trung bình |
| Điều khoản bảo mật | Quá rộng hoặc thiếu giới hạn | Thấp–Trung bình |
| Điều khoản giải quyết tranh chấp | Không có hoặc thiên vị | Cao |

**Bước 4: Gán nhãn dataset**
- Mỗi điều khoản được gán: `risk_level` ∈ {`low`, `medium`, `high`}
- Định dạng JSON:
```json
{
  "contract_id": "LĐ-001",
  "contract_type": "labor",
  "clauses": [
    {
      "clause_id": "LĐ-001-C1",
      "title": "Điều 5: Phạt vi phạm",
      "content": "...",
      "risk_label": "high",
      "risk_reason": "Phạt vi phạm 50% giá trị hợp đồng..."
    }
  ]
}
```
- **Mục tiêu:** ≥ 150 điều khoản đã gán nhãn

**Output tháng 1:**
- [ ] Tóm tắt lý thuyết (file .md)
- [ ] Dataset JSON: ≥ 150 điều khoản có nhãn
- [ ] Bộ tiêu chí gán nhãn rủi ro (rubric)

---

### 📅 Tháng 2 — Thiết kế Prompt Template CoT & Xây dựng Pipeline

#### Mục tiêu:
- Có pipeline Single-Agent hoàn chỉnh: nhận PDF → trả JSON phân tích

#### Cách làm cụ thể:

**Bước 1: Thiết kế Structured CoT Prompt Template**

Mỗi điều khoản được xử lý qua 4 bước suy luận tuần tự trong prompt:

```
SYSTEM PROMPT (Role-based):
Bạn là chuyên gia pháp lý AI chuyên phân tích hợp đồng tiếng Việt.
Nhiệm vụ: phân tích từng điều khoản hợp đồng theo chuỗi lập luận có cấu trúc.

USER PROMPT (Chain-of-Thought có cấu trúc):
Điều khoản: {clause_text}
Loại hợp đồng: {contract_type}

Hãy phân tích theo các bước sau:

Bước 1 - NHẬN DIỆN NỘI DUNG:
- Điều khoản này quy định về điều gì?
- Quyền và nghĩa vụ của mỗi bên là gì?

Bước 2 - PHÂN TÍCH RỦI RO:
- Yếu tố nào có thể gây bất lợi?
- Ngôn ngữ có mơ hồ không? Có điều kiện ẩn không?
- So sánh với quy định pháp luật Việt Nam hiện hành.

Bước 3 - ĐÁNH GIÁ MỨC ĐỘ RỦI RO:
- Dựa trên phân tích, mức độ rủi ro là: Thấp / Trung bình / Cao
- Lý do cụ thể: ...

Bước 4 - ĐỀ XUẤT CHỈNH SỬA:
- Nếu có rủi ro, đề xuất chỉnh sửa cụ thể:
- [Nội dung cần thay thế/bổ sung]

Trả về JSON:
{
  "step1_content": "...",
  "step2_analysis": "...",
  "step3_risk_level": "low|medium|high",
  "step3_risk_score": 1-10,
  "step3_explanation": "...",
  "step4_suggestion": "..."
}
```

**Bước 2: Thiết kế Self-Reflection Prompt**

```
REFLECTION PROMPT (chạy sau CoT chính):
Xem lại kết quả phân tích vừa thực hiện:
{previous_analysis}

Kiểm tra:
1. Có điều khoản nào bị bỏ qua không?
2. Các mức rủi ro có nhất quán với nhau không?
3. Đề xuất chỉnh sửa có khả thi và cụ thể không?
4. Có mâu thuẫn nào trong lập luận không?

Nếu cần điều chỉnh, hãy cập nhật kết quả. Nếu đã chính xác, xác nhận.
Trả về: {"needs_revision": true/false, "revised_analysis": {...}}
```

**Bước 3: Xây dựng pipeline Python**

```
architecture:
  input: PDF file / text
  modules:
    1. PDFExtractor    → pdfplumber → raw text
    2. ClauseSegmenter → heuristic rules → list of clauses
    3. CоTAnalyzer    → LLM API call → JSON analysis per clause
    4. RiskClassifier  → parse JSON → risk_level + score
    5. SelfReflector   → second LLM call (khi score gần ngưỡng) → revised
    6. OutputFormatter → structured JSON report
  output: JSON report + highlight data
```

**Bước 4: Lựa chọn LLM API**
- **Ưu tiên:** Google Gemini 2.5 Flash (miễn phí, đa ngôn ngữ tốt)
- **Dự phòng:** OpenAI GPT-4o-mini

**Output tháng 2:**
- [ ] Prompt template CoT hoàn chỉnh (file .txt/.py)
- [ ] Pipeline Python chạy được trên dữ liệu mẫu
- [ ] Kết quả thử nghiệm sơ bộ (≥ 10 điều khoản)

---

### 📅 Tháng 3 — Xây dựng Module & Phân tích hoàn chỉnh

#### Mục tiêu:
- Pipeline xử lý được toàn bộ dataset, có kết quả để đánh giá.

#### Cách làm cụ thể:

**Module 1: PDFExtractor & ClauseSegmenter**
```python
# Cài đặt: pdfplumber
import pdfplumber

def extract_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages)
    return text

def segment_clauses(text):
    # Heuristic: tách theo pattern "Điều X:", "Article X:", số thứ tự
    import re
    pattern = r'(Điều\s+\d+[:\.]|ĐIỀU\s+\d+[:\.]|Article\s+\d+[:\.])'
    clauses = re.split(pattern, text)
    # Ghép header với nội dung
    return parsed_clauses
```

**Module 2: CoT Analyzer**
```python
import google.generativeai as genai

def analyze_clause_with_cot(clause, contract_type, model):
    prompt = build_cot_prompt(clause, contract_type)
    response = model.generate_content(prompt)
    return parse_json_response(response.text)
```

**Module 3: Risk Classifier & Self-Reflector**
```python
def classify_risk(analysis_json):
    score = analysis_json["step3_risk_score"]
    if score <= 3: return "low"
    elif score <= 6: return "medium"
    else: return "high"

def self_reflect(analysis_json, model):
    # Chạy khi score nằm gần ngưỡng (3-4 hoặc 6-7)
    if 3 <= analysis_json["step3_risk_score"] <= 4 or \
       6 <= analysis_json["step3_risk_score"] <= 7:
        reflection = model.generate_content(
            build_reflection_prompt(analysis_json)
        )
        return parse_revised_analysis(reflection.text)
    return analysis_json
```

**Cấu trúc thư mục project:**
```
contract-risk-analyzer/
├── data/
│   ├── raw/          # PDF hợp đồng gốc
│   ├── processed/    # JSON đã gán nhãn
│   └── test/         # Tập test độc lập
├── src/
│   ├── extractor.py      # PDF extraction
│   ├── segmenter.py      # Clause segmentation
│   ├── analyzer.py       # CoT analysis
│   ├── classifier.py     # Risk classification
│   ├── reflector.py      # Self-reflection
│   └── pipeline.py       # Main orchestrator
├── prompts/
│   ├── cot_template.txt
│   └── reflection_template.txt
├── webapp/
│   ├── app.py            # Flask/FastAPI backend
│   └── frontend/         # HTML/JS/CSS
├── evaluation/
│   └── metrics.py
└── requirements.txt
```

**Output tháng 3:**
- [ ] Toàn bộ modules Python hoàn chỉnh
- [ ] Pipeline chạy xuyên suốt từ PDF → JSON output
- [ ] Unit test cho từng module

---

### 📅 Tháng 4 — Phát triển Giao diện Web

#### Mục tiêu:
- Có web app cho phép upload hợp đồng, hiển thị phân tích với highlight màu.

#### Cách làm cụ thể:

**Backend (Flask/FastAPI):**
```python
# Endpoint chính
POST /api/analyze
  Input: multipart/form-data (PDF file)
  Output: JSON {
    "contract_id": "...",
    "clauses": [
      {
        "id": "C1",
        "title": "Điều 1",
        "content": "...",
        "risk_level": "high",
        "risk_score": 8,
        "explanation": "...",
        "suggestion": "..."
      }
    ],
    "summary": {"high": 2, "medium": 3, "low": 5}
  }
```

**Frontend UI:**
- Upload PDF → hiển thị preview hợp đồng
- Sidebar danh sách điều khoản với badge màu:
  - 🔴 Cao (high) — đỏ
  - 🟡 Trung bình (medium) — vàng  
  - 🟢 Thấp (low) — xanh lá
- Click vào điều khoản → hiển thị phân tích CoT chi tiết + đề xuất chỉnh sửa
- Dashboard tổng quan: biểu đồ phân bổ rủi ro

**Output tháng 4:**
- [ ] Backend API hoàn chỉnh
- [ ] Frontend web app hoạt động
- [ ] Kiểm thử tích hợp end-to-end

---

### 📅 Tháng 5 — Thực nghiệm so sánh & Đánh giá định lượng

#### Mục tiêu:
- Có số liệu chứng minh pipeline CoT vượt trội hơn zero-shot prompting.

#### Cách làm cụ thể:

**Thiết kế thực nghiệm:**

| Phương pháp | Mô tả |
|-------------|-------|
| **Baseline** | Zero-shot: "Phân tích điều khoản này, cho biết mức độ rủi ro" |
| **Đề xuất** | Structured CoT + Self-Reflection pipeline |

**Tập test:**
- 30–50 điều khoản chưa dùng trong training
- Ground truth từ nhãn đã gán ở tháng 1
- **Chia đều:** 10 low / 10 medium / 10 high (mỗi loại)

**Công thức đánh giá:**
```
Accuracy  = (TP + TN) / Total
Precision = TP / (TP + FP)   [cho mỗi class]
Recall    = TP / (TP + FN)   [cho mỗi class]
F1-score  = 2 * (P * R) / (P + R)
```

**Phân tích định tính:**
- Khảo sát 5–10 người dùng thực tế (sinh viên, người có hiểu biết pháp lý cơ bản)
- Đánh giá: Độ rõ ràng của giải thích, tính hữu ích của đề xuất chỉnh sửa

**Output tháng 5:**
- [ ] Bảng số liệu Accuracy/Precision/Recall/F1 của 2 phương pháp
- [ ] Biểu đồ so sánh
- [ ] Kết quả khảo sát người dùng
- [ ] Phân tích ưu điểm, hạn chế

---

### 📅 Tháng 6 — Tổng hợp kết quả & Viết báo cáo NCKH

#### Mục tiêu:
- Hoàn thành báo cáo NCKH + chuẩn bị thuyết trình.

#### Cách làm cụ thể:

**Cấu trúc báo cáo NCKH:**
1. **Giới thiệu** — Tính cấp thiết, mục tiêu, phạm vi
2. **Cơ sở lý thuyết** — LLMs, CoT, Self-Reflection, Risk Assessment
3. **Phương pháp** — Kiến trúc pipeline, thiết kế prompt, dataset
4. **Kết quả thực nghiệm** — Số liệu, bảng so sánh, phân tích
5. **Thảo luận** — Ưu điểm, hạn chế, hướng mở rộng
6. **Kết luận**
7. **Tài liệu tham khảo**

**Chuẩn bị thuyết trình:**
- Slide demo web app trực tiếp
- Bảng kết quả số liệu nổi bật
- Ví dụ minh họa cụ thể: hợp đồng trước và sau phân tích

**Output tháng 6:**
- [ ] Báo cáo NCKH hoàn chỉnh (PDF)
- [ ] Slide thuyết trình (PowerPoint/Canva)
- [ ] Source code + README hướng dẫn chạy
- [ ] Demo video (tùy chọn)

---

## Tóm tắt lộ trình

```
Tháng 1: [Dataset & Lý thuyết]
Tháng 2: [Prompt Design & Pipeline core]
Tháng 3: [Modules Python hoàn chỉnh]
Tháng 4: [Web App]
Tháng 5: [Thực nghiệm & Đánh giá]
Tháng 6: [Báo cáo & Thuyết trình]
```

## Tech Stack đề xuất

| Thành phần | Công nghệ |
|-----------|-----------|
| LLM API | Google Gemini 2.5 Flash (miễn phí) / GPT-4o-mini |
| PDF Extraction | pdfplumber |
| Backend | FastAPI (Python) |
| Frontend | HTML + Vanilla JS + CSS |
| Data format | JSON |
| Evaluation | scikit-learn metrics |
| Version control | Git + GitHub |

## Lưu ý quan trọng

> [!IMPORTANT]
> Pipeline **Single-Agent** — một agent duy nhất xử lý tuần tự tất cả các bước, không dùng multi-agent. Đây là điểm phân biệt với kiến trúc phức tạp hơn.

> [!NOTE]
> **Self-Reflection** chỉ kích hoạt khi điểm rủi ro gần ngưỡng phân loại (ví dụ: score 3–4 hoặc 6–7) để tiết kiệm API calls.

> [!TIP]
> Bắt đầu với **Gemini API** vì có free tier đủ dùng cho nghiên cứu. Dùng `google-generativeai` Python SDK.
