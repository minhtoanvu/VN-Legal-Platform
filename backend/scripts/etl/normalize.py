"""
ETL Step 2: Normalize raw data → chuẩn schema DB.

Map các trường từ HuggingFace dataset sang schema bảng documents.
Lọc 2 lĩnh vực trọng tâm: Lao động (labor) và Thuế (tax).

Chạy: python scripts/etl/normalize.py
"""

import json
import re
from datetime import date
from pathlib import Path
from typing import Optional

# ── Từ khóa phát hiện lĩnh vực ──────────────────────────────────────
# Dùng cho cả topic_title_vi và fallback trên content
FIELD_KEYWORDS = {
    "labor": [
        "lao động", "lao-động", "bộ luật lao động",
        "hợp đồng lao động", "tiền lương", "bảo hiểm xã hội",
        "bhxh", "bhyt", "bhtn", "việc làm", "tuyển dụng",
        "sa thải", "thử việc", "nghỉ phép", "làm thêm giờ",
        "người lao động", "người sử dụng lao động",
        "an toàn lao động", "quan hệ lao động",
        "thị trường lao động", "lao động nước ngoài",
    ],
    "tax": [
        "thuế", "thuế thu nhập", "thuế giá trị gia tăng",
        "thuế gtgt", "thuế tncn", "thuế tndn", "thuế xuất nhập khẩu",
        "hoá đơn", "hóa đơn", "khai thuế", "nộp thuế",
        "tổng cục thuế", "cục thuế", "kế toán", "kiểm toán",
        "tài chính", "ngân sách nhà nước", "tài chính nhà nước",
    ],
}

RAW_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def detect_field_from_topic(topic_vi: str, subject_vi: str = "") -> Optional[str]:
    """
    Phát hiện lĩnh vực từ topic_title_vi / subject_title_vi.
    Ưu tiên dùng hàm này vì chính xác hơn keyword search trên content.
    """
    combined = (topic_vi + " " + subject_vi).lower()
    for field, keywords in FIELD_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            return field
    return None


def detect_field(title: str, content: str = "") -> Optional[str]:
    """Fallback: Phát hiện lĩnh vực từ title và đầu content."""
    text = (title + " " + content[:500]).lower()
    for field, keywords in FIELD_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return field
    return None


def parse_date(date_str: Optional[str]) -> Optional[str]:
    """Parse ngày tháng từ nhiều định dạng khác nhau → YYYY-MM-DD."""
    if not date_str:
        return None
    # Thử các định dạng phổ biến
    patterns = [
        r"(\d{4})-(\d{2})-(\d{2})",           # 2024-01-15
        r"(\d{2})/(\d{2})/(\d{4})",           # 15/01/2024
        r"(\d{2})-(\d{2})-(\d{4})",           # 15-01-2024
        r"ngày (\d{1,2}) tháng (\d{1,2}) năm (\d{4})",  # ngày 15 tháng 1 năm 2024
    ]
    for pattern in patterns:
        m = re.search(pattern, str(date_str), re.IGNORECASE)
        if m:
            groups = m.groups()
            try:
                if len(groups[0]) == 4:  # YYYY-MM-DD
                    return f"{groups[0]}-{groups[1].zfill(2)}-{groups[2].zfill(2)}"
                elif "tháng" in pattern:  # ngày X tháng Y năm Z
                    return f"{groups[2]}-{groups[1].zfill(2)}-{groups[0].zfill(2)}"
                else:  # DD/MM/YYYY hoặc DD-MM-YYYY
                    return f"{groups[2]}-{groups[1].zfill(2)}-{groups[0].zfill(2)}"
            except Exception:
                continue
    return None


def normalize_record(raw: dict) -> Optional[dict]:
    """
    Normalize một record raw → dict chuẩn schema documents.
    Hỗ trợ 2 schema:
      - tmquan/phapdien-moj-gov-vn (Pháp điển — từng điều luật)
      - Schema cũ (toàn văn)
    """
    # ── Schema tmquan/phapdien-moj-gov-vn ───────────────────────────
    if "article_title" in raw and "content_text" in raw:
        article_title = (raw.get("article_title") or "").strip()
        chapter_title = (raw.get("chapter_title") or "").strip()
        title = f"{article_title} — {chapter_title}" if chapter_title else article_title
        content = (raw.get("content_text") or "").strip()

        if not title or not content:
            return None

        # Phát hiện lĩnh vực: ưu tiên topic_title_vi (chính xác nhất)
        topic_vi = raw.get("topic_title_vi") or ""
        subject_vi = raw.get("subject_title_vi") or ""
        field = detect_field_from_topic(topic_vi, subject_vi)
        # Fallback sang content nếu không detect được từ topic
        if not field:
            field = detect_field(title, content)
        # Gán "Khác" nếu vẫn không xác định được
        if not field:
            field = "Khác"

        # Doc number: dùng article_id hoặc record_id
        doc_number = raw.get("article_id") or raw.get("record_id") or ""

        # Ngày ban hành từ source_note_text
        source_note = raw.get("source_note_text") or ""
        issue_date = parse_date(source_note)

        source_url = raw.get("source_url") or ""

        return {
            "doc_number": doc_number,
            "title": title[:500],
            "doc_type": "Điều luật",
            "issuing_body": subject_vi,
            "field": field,
            "issue_date": issue_date,
            "effective_date": None,
            "expired_date": None,
            "status": "active",
            "content": content[:100_000],
            "source_url": source_url,
        }

    # ── Schema cũ (toàn văn) ────────────────────────────────────────
    title = (
        raw.get("title") or raw.get("ten_van_ban") or raw.get("de muc") or raw.get("name") or ""
    ).strip()
    content = (
        raw.get("content") or raw.get("noi_dung") or raw.get("text") or ""
    ).strip()

    if not title and content:
        title = content.split('\n')[0][:100]

    if not title or not content:
        return None

    chu_de = raw.get("chu de", "")
    field = raw.get("field_detected") or chu_de or detect_field(title, content) or "Khác"

    doc_number = (raw.get("doc_number") or raw.get("so_ky_hieu") or raw.get("so_hieu") or raw.get("number") or "").strip()
    doc_type = raw.get("doc_type") or raw.get("loai_van_ban") or raw.get("type") or ""
    issuing_body = (raw.get("issuing_body") or raw.get("co_quan_ban_hanh") or raw.get("agency") or "").strip()
    issue_date = parse_date(raw.get("issue_date") or raw.get("ngay_ban_hanh") or raw.get("date"))
    effective_date = parse_date(raw.get("effective_date") or raw.get("ngay_co_hieu_luc") or raw.get("ngay_hieu_luc"))
    expired_date = parse_date(raw.get("expired_date") or raw.get("ngay_het_hieu_luc"))

    status_raw = (raw.get("status") or raw.get("tinh_trang_hieu_luc") or raw.get("tinh_trang") or "").lower()
    if "hết hiệu lực" in status_raw or "het hieu luc" in status_raw:
        status = "expired"
    elif "sửa đổi" in status_raw or "sua doi" in status_raw:
        status = "amended"
    elif expired_date:
        status = "expired"
    else:
        status = "active"

    source_url = raw.get("url") or raw.get("source_url") or raw.get("link") or ""

    return {
        "doc_number": doc_number,
        "title": title,
        "doc_type": doc_type,
        "issuing_body": issuing_body,
        "field": field,
        "issue_date": issue_date,
        "effective_date": effective_date,
        "expired_date": expired_date,
        "status": status,
        "content": content[:100_000],
        "source_url": source_url,
    }


def normalize_dataset(input_file: Path, output_file: Path) -> int:
    """Normalize file JSON Array của Mock Dataset, trả về số record hợp lệ."""
    print(f"📂 Đọc: {input_file}")

    normalized = []
    skipped = 0

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = [data]
            
            for raw in data:
                result = normalize_record(raw)
                if result:
                    normalized.append(result)
                else:
                    skipped += 1
    except Exception as e:
        print(f"❌ Lỗi đọc JSON: {e}")
        return 0

    print(f"   Tổng raw: {len(data):,} | Hợp lệ: {len(normalized):,} | Bỏ qua: {skipped:,}")

    # Thống kê theo lĩnh vực
    field_counts: dict[str, int] = {}
    for doc in normalized:
        f = doc["field"]
        field_counts[f] = field_counts.get(f, 0) + 1

    print("   📊 Phân bố lĩnh vực sau normalize:")
    for fname, cnt in sorted(field_counts.items(), key=lambda x: -x[1]):
        bar = "█" * min(cnt // 10, 40)
        print(f"      {fname:<30s}: {cnt:>5,}  {bar}")

    # Lưu ra file processed format JSONL
    with open(output_file, "w", encoding="utf-8") as f:
        for doc in normalized:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    print(f"   💾 Lưu {len(normalized):,} records tại: {output_file}")
    return len(normalized)


if __name__ == "__main__":
    total = 0

    # Normalize dataset chính
    main_raw = RAW_DATA_DIR / "main_dataset.json"
    if main_raw.exists():
        total += normalize_dataset(
            main_raw,
            PROCESSED_DIR / "documents_normalized.jsonl"
        )
    else:
        print(f"⚠️  Không tìm thấy {main_raw}")
        print("   Chạy download_data.py trước!")

    print(f"\n✅ Hoàn thành normalize: {total:,} documents hợp lệ")
