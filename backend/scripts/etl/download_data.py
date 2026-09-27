# Bước 1 ETL: tải dữ liệu từ HuggingFace về máy
# Dataset: tmquan/phapdien-moj-gov-vn (Pháp điển Quốc gia)
# Chỉ lấy văn bản thuộc lĩnh vực Lao động và Thuế

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ═══ CẤU HÌNH ĐƯỜNG DẪN ═══
# Thư mục lưu dữ liệu thô: D:\NCKH\data\raw
RAW_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)  # tạo folder nếu chưa có

# ═══ TỪ KHÓA PHÂN LOẠI LĨNH VỰC ═══
# Dùng để lọc văn bản thuộc lĩnh vực Lao động — so khớp với trường linh_vuc/title
LABOR_TOPIC_KEYWORDS = [
    "lao động", "lao-động", "việc làm", "tiền lương",
    "bảo hiểm xã hội", "bhxh", "bhyt", "bhtn",
    "hợp đồng lao động", "người lao động",
    "bộ luật lao động", "an toàn lao động",
    "quan hệ lao động", "thị trường lao động",
]

# Dùng để lọc văn bản thuộc lĩnh vực Thuế/Tài chính
TAX_TOPIC_KEYWORDS = [
    "thuế", "thuế thu nhập", "thuế giá trị gia tăng",
    "thuế gtgt", "thuế tncn", "thuế tndn",
    "kế toán", "kiểm toán", "tài chính",
    "ngân sách", "hóa đơn", "hoá đơn",
    "tổng cục thuế", "thuế xuất nhập khẩu",
]


# ═══ HÀM NHẬN DIỆN LĨNH VỰC ═══
def detect_field_from_topic(topic_vi: str) -> str | None:
    """Nhận vào chuỗi metadata, trả về 'labor' | 'tax' | None."""
    topic_lower = (topic_vi or "").lower()
    if any(kw in topic_lower for kw in LABOR_TOPIC_KEYWORDS):
        return "labor"  # khớp ít nhất 1 từ khóa Lao động
    if any(kw in topic_lower for kw in TAX_TOPIC_KEYWORDS):
        return "tax"    # khớp ít nhất 1 từ khóa Thuế
    return None          # không thuộc lĩnh vực nào → bỏ qua


# ═══ HÀM TẢI DỮ LIỆU CHÍNH ═══
def download_dataset(target_per_field: int = 1500, max_scan: int = 500_000):
    """Quét dữ liệu từ bộ Pháp điển tmquan/phapdien-moj-gov-vn.
    Dùng streaming để không tốn RAM — không load toàn bộ dataset về trước.
    """
    try:
        from datasets import load_dataset
    except ImportError:
        print("Thiếu thư viện: pip install datasets")
        return False
    import re
    from bs4 import BeautifulSoup

    print(f"Đang stream tmquan/phapdien-moj-gov-vn...")
    print(f"Target: {target_per_field:,} records/lĩnh vực")

    try:
        ds = load_dataset(
            "tmquan/phapdien-moj-gov-vn",
            split="train",
            streaming=True,   # ← KEY: tránh OOM
        )
    except Exception as e:
        print(f"Không load được dataset: {e}")
        return False

    labor_records = []
    tax_records = []
    scanned = 0

    print("Đang scan dataset Pháp điển...")
    for row in ds:
        scanned += 1
        topic_vi = row.get("topic_title_vi") or ""
        subject_vi = row.get("subject_title_vi") or ""
        combined = f"{topic_vi} {subject_vi}"
        field = detect_field_from_topic(combined)

        if not field:
            continue

        # Ánh xạ trường cho khớp với normalize.py
        row["content"] = row.get("content_text", "")
        row["title"] = row.get("article_title", "")
        row["doc_number"] = row.get("article_id", "")
        row["url"] = row.get("source_url", "")

        if field == "labor" and len(labor_records) < target_per_field:
            row["field_detected"] = "labor"
            labor_records.append(row)
        elif field == "tax" and len(tax_records) < target_per_field:
            row["field_detected"] = "tax"
            tax_records.append(row)

        # In tiến độ mỗi 5000 record
        if scanned % 5000 == 0:
            print(
                f"  Scanned: {scanned:,} | "
                f"Lao dong: {len(labor_records):,}/{target_per_field:,} | "
                f"Thue: {len(tax_records):,}/{target_per_field:,}"
            )

        # Dừng sớm khi đã đủ cả 2 lĩnh vực
        if len(labor_records) >= target_per_field and len(tax_records) >= target_per_field:
            print(f"Du target, dung scan tai #{scanned:,}")
            break

        if scanned >= max_scan:
            print(f"Da scan {max_scan:,} records, dung.")
            break

    all_records = labor_records + tax_records
    print(f"\nKet qua: {len(all_records):,} records")

    if len(all_records) == 0:
        print("Khong co records nao duoc luu.")
        return False

    # ── LƯU OUTPUT → normalize.py sẽ đọc file này ở Bước 2 ──
    output_path = RAW_DATA_DIR / "main_dataset.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

    print(f"Da luu: {output_path} ({output_path.stat().st_size / 1024 / 1024:.1f} MB)")
    return True


# ═══ TẢI BỘ CÂU HỎI QA ĐỂ ĐÁNH GIÁ RAG ═══
def download_eval_dataset(max_qa: int = 500):
    """Dataset phụ: 500 cặp câu hỏi-đáp pháp lý để đánh giá recall của RAG.
    Lưu vào data/raw/eval_qa.json — dùng cho đánh giá sau này.
    """
    try:
        from datasets import load_dataset
    except ImportError:
        return

    print(f"\nTai tap QA danh gia (toi da {max_qa} cap)...")
    try:
        ds = load_dataset("thangvip/vietnamese-legal-qa", split="train", streaming=True)
        records = []
        for row in ds:
            records.append(row)
            if len(records) >= max_qa:
                break

        output_path = RAW_DATA_DIR / "eval_qa.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"  {len(records):,} cau hoi QA -> {output_path}")
    except Exception as e:
        print(f"  Khong tai duoc QA dataset: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download legal datasets tu HuggingFace")
    parser.add_argument(
        "--target-per-field", type=int, default=1500,
        help="So records can tai moi linh vuc (default: 1500)"
    )
    parser.add_argument(
        "--max-scan", type=int, default=500_000,
        help="So records toi da de scan (default: 500000)"
    )
    args = parser.parse_args()

    ok = download_dataset(
        target_per_field=args.target_per_field,
        max_scan=args.max_scan,
    )
    if ok:
        download_eval_dataset()
        print("\nHoan thanh! Chay tiep: python scripts/etl/normalize.py")
    else:
        print("\nDownload that bai.")
