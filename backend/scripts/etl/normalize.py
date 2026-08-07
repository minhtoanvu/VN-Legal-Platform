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

# ── Cấu hình lĩnh vực ─────────────────────────────────────────────
FIELD_KEYWORDS = {
    "labor": [
        "lao động", "lao-động", "bộ luật lao động",
        "hợp đồng lao động", "tiền lương", "bảo hiểm xã hội",
        "bhxh", "bhyt", "bhtn", "việc làm", "tuyển dụng",
        "sa thải", "thử việc", "nghỉ phép", "làm thêm giờ",
        "người lao động", "người sử dụng lao động",
    ],
    "tax": [
        "thuế", "thuế thu nhập", "thuế giá trị gia tăng",
        "thuế gtgt", "thuế tncn", "thuế tndn", "thuế xuất nhập khẩu",
        "hoá đơn", "hóa đơn", "khai thuế", "nộp thuế",
        "tổng cục thuế", "cục thuế", "kế toán", "kiểm toán",
        "tài chính", "ngân sách nhà nước",
    ],
}

RAW_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def detect_field(title: str, content: str = "") -> Optional[str]:
    """Phát hiện lĩnh vực pháp luật dựa trên từ khóa."""
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
    Trả về None nếu không thuộc lĩnh vực cần thiết.
    """
    # Mapping linh hoạt cho nhiều schema dataset khác nhau
    title = (
        raw.get("title") or raw.get("ten_van_ban") or raw.get("name") or ""
    ).strip()
    content = (
        raw.get("content") or raw.get("noi_dung") or raw.get("text") or ""
    ).strip()

    if not title or not content:
        return None

    # Phát hiện lĩnh vực
    field = detect_field(title, content)
    if not field:
        return None

    doc_number = (
        raw.get("doc_number") or raw.get("so_hieu") or raw.get("number") or ""
    ).strip()

    doc_type = raw.get("doc_type") or raw.get("loai_van_ban") or raw.get("type") or ""

    issuing_body = (
        raw.get("issuing_body") or raw.get("co_quan_ban_hanh") or raw.get("agency") or ""
    ).strip()

    issue_date = parse_date(
        raw.get("issue_date") or raw.get("ngay_ban_hanh") or raw.get("date")
    )
    effective_date = parse_date(
        raw.get("effective_date") or raw.get("ngay_hieu_luc")
    )
    expired_date = parse_date(
        raw.get("expired_date") or raw.get("ngay_het_hieu_luc")
    )

    # Xác định trạng thái hiệu lực
    status_raw = (raw.get("status") or raw.get("tinh_trang") or "").lower()
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
        "content": content[:100_000],  # Giới hạn 100K chars để tránh quá lớn
        "source_url": source_url,
    }


def normalize_dataset(input_file: Path, output_file: Path) -> int:
    """Normalize toàn bộ file JSON, trả về số record hợp lệ."""
    print(f"📂 Đọc: {input_file}")

    normalized = []
    total = 0
    skipped = 0

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                total += 1
                result = normalize_record(raw)
                if result:
                    normalized.append(result)
                else:
                    skipped += 1
            except json.JSONDecodeError:
                skipped += 1

    print(f"   Tổng: {total:,} | Hợp lệ: {len(normalized):,} | Bỏ qua: {skipped:,}")

    # Thống kê theo lĩnh vực
    field_counts = {}
    for doc in normalized:
        f = doc["field"]
        field_counts[f] = field_counts.get(f, 0) + 1
    print(f"   Phân bố lĩnh vực: {field_counts}")

    # Lưu ra file processed
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
