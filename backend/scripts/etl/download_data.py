# Bước 1 ETL: tải dữ liệu từ HuggingFace về máy
# Dataset: th1nhng0/vietnamese-legal-documents
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


# ═══ HÀM TẢI DỮ LIỆU CHÍNH — 2 PASS ═══
def download_dataset(target_per_field: int = 1500, max_scan: int = 500_000):
    """Pass 1: quét metadata → chọn ID. Pass 2: lấy content cho các ID đó.
    Dùng streaming để không tốn RAM — không load toàn bộ dataset về trước.
    """
    try:
        from datasets import load_dataset
    except ImportError:
        print("Thiếu thư viện: pip install datasets")
        return False
    import re
    from bs4 import BeautifulSoup

    print(f"Đang stream th1nhng0/vietnamese-legal-documents...")
    print(f"Target: {target_per_field:,} records/lĩnh vực")

    # ── PASS 1: Quét metadata, chọn ID theo lĩnh vực ──
    # streaming=True → không download toàn bộ, đọc từng record một
    try:
        ds_meta = load_dataset(
            "th1nhng0/vietnamese-legal-documents",
            name="metadata",
            split="data",
            streaming=True,   # ← KEY: tránh OOM khi dataset hàng trăm nghìn record
        )
    except Exception as e:
        print(f"Không load được dataset metadata: {e}")
        return False

    labor_records = {}
    tax_records = {}
    scanned = 0

    print("Đang scan metadata...")
    for row in ds_meta:
        scanned += 1
        topic_vi = row.get("linh_vuc") or row.get("nganh") or ""
        subject_vi = row.get("title") or ""
        combined = f"{topic_vi} {subject_vi}"
        field = detect_field_from_topic(combined)

        doc_id = row.get("id")
        if not doc_id:
            continue

        if field == "labor" and len(labor_records) < target_per_field:
            labor_records[doc_id] = row
            labor_records[doc_id]["field_detected"] = "labor"
        elif field == "tax" and len(tax_records) < target_per_field:
            tax_records[doc_id] = row
            tax_records[doc_id]["field_detected"] = "tax"

        # In tiến độ mỗi 5000 record để theo dõi
        if scanned % 5000 == 0:
            print(
                f"  Scanned: {scanned:,} | "
                f"Lao dong: {len(labor_records):,}/{target_per_field:,} | "
                f"Thue: {len(tax_records):,}/{target_per_field:,}"
            )

        # Dừng sớm khi đã đủ cả 2 lĩnh vực — không cần scan thêm
        if len(labor_records) >= target_per_field and len(tax_records) >= target_per_field:
            print(f"Du target, dung scan tai #{scanned:,}")
            break

        # Dừng nếu quét quá max_scan (safety guard)
        if scanned >= max_scan:
            print(f"Da scan {max_scan:,} records, dung.")
            break

    target_ids = set(labor_records.keys()) | set(tax_records.keys())
    if not target_ids:
        print("Khong tim thay record nao phu hop.")
        return False

    # ── PASS 2: Lấy content HTML cho các ID đã chọn ở Pass 1 ──
    # Chỉ merge metadata + content khi ID khớp → tránh lấy thừa
    print(f"\nDang lay noi dung cho {len(target_ids):,} documents...")
    try:
        ds_content = load_dataset(
            "th1nhng0/vietnamese-legal-documents",
            name="content",
            split="data",
            streaming=True,
        )
    except Exception as e:
        print(f"Khong load duoc dataset content: {e}")
        return False

    all_records = []
    found_content_count = 0
    scanned_content = 0

    for row in ds_content:
        scanned_content += 1
        doc_id = row.get("id")
        if doc_id in target_ids:
            if doc_id in labor_records:
                meta = labor_records[doc_id]
            else:
                meta = tax_records[doc_id]

            content_html = row.get("content_html") or ""
            # Bóc HTML → text thuần (bỏ tags, giữ xuống dòng)
            soup = BeautifulSoup(content_html, "html.parser")
            plain_text = soup.get_text(separator="\n", strip=True)

            if plain_text:
                # Gộp metadata (từ Pass 1) + content (từ Pass 2) thành 1 record
                merged = {**meta, "content": plain_text}
                all_records.append(merged)
                found_content_count += 1

                if found_content_count % 100 == 0:
                    print(f"  Da lay: {found_content_count:,}/{len(target_ids):,}")

                if found_content_count >= len(target_ids):
                    print("Da lay du tat ca target documents.")
                    break

    print(f"\nKet qua: {len(all_records):,} / {len(target_ids):,} records")

    if len(all_records) == 0:
        print("Khong co records nao duoc luu.")
        return False

    # ── LƯU OUTPUT → normalize.py sẽ đọc file này ở Bước 2 ──
    output_path = RAW_DATA_DIR / "main_dataset.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)  # ensure_ascii=False để giữ tiếng Việt

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
