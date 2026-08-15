"""
ETL Step 1: Download dataset từ HuggingFace — Lọc đúng lĩnh vực Lao động & Thuế.

Dataset chính: tmquan/phapdien-moj-gov-vn (Pháp điển Bộ Tư pháp)
Chiến lược: Stream toàn bộ dataset, chỉ giữ records thuộc Lao động và Thuế.
Target: ít nhất 1,500 records/lĩnh vực (tổng ~3,000+)

Chạy: python scripts/etl/download_data.py
      python scripts/etl/download_data.py --target-per-field 2000
"""

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

RAW_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── Từ khóa lọc theo topic_title_vi ──────────────────────────────────────────
LABOR_TOPIC_KEYWORDS = [
    "lao động", "lao-động", "việc làm", "tiền lương",
    "bảo hiểm xã hội", "bhxh", "bhyt", "bhtn",
    "hợp đồng lao động", "người lao động",
    "bộ luật lao động", "an toàn lao động",
    "quan hệ lao động", "thị trường lao động",
]

TAX_TOPIC_KEYWORDS = [
    "thuế", "thuế thu nhập", "thuế giá trị gia tăng",
    "thuế gtgt", "thuế tncn", "thuế tndn",
    "kế toán", "kiểm toán", "tài chính",
    "ngân sách", "hóa đơn", "hoá đơn",
    "tổng cục thuế", "thuế xuất nhập khẩu",
]


def detect_field_from_topic(topic_vi: str) -> str | None:
    """Phát hiện lĩnh vực từ topic_title_vi (chuẩn hơn keyword matching trên content)."""
    topic_lower = (topic_vi or "").lower()
    if any(kw in topic_lower for kw in LABOR_TOPIC_KEYWORDS):
        return "labor"
    if any(kw in topic_lower for kw in TAX_TOPIC_KEYWORDS):
        return "tax"
    return None


def download_dataset(target_per_field: int = 1500, max_scan: int = 500_000):
    """
    Stream dataset th1nhng0/vietnamese-legal-documents, chỉ giữ records thuộc Lao động và Thuế.
    Dừng khi đạt target_per_field records cho MỖI lĩnh vực.
    """
    try:
        from datasets import load_dataset
    except ImportError:
        print("❌ Thiếu thư viện: pip install datasets")
        return False
    import re
    from bs4 import BeautifulSoup

    print(f"📥 Streaming th1nhng0/vietnamese-legal-documents...")
    print(f"   Target: {target_per_field:,} records/lĩnh vực (tổng ~{target_per_field*2:,})")

    # 1. Stream metadata để tìm ID của các documents thuộc lĩnh vực
    try:
        ds_meta = load_dataset(
            "th1nhng0/vietnamese-legal-documents",
            name="metadata",
            split="data",
            streaming=True,
        )
    except Exception as e:
        print(f"❌ Không load được dataset metadata: {e}")
        return False

    labor_records = {}
    tax_records = {}
    scanned = 0

    print("   Đang scan metadata...")
    for row in ds_meta:
        scanned += 1
        
        # Lọc theo lĩnh vực
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
            
        if scanned % 5000 == 0:
            print(
                f"   Đã scan metadata: {scanned:,} | "
                f"Lao động: {len(labor_records):,}/{target_per_field:,} | "
                f"Thuế: {len(tax_records):,}/{target_per_field:,}"
            )
            
        if len(labor_records) >= target_per_field and len(tax_records) >= target_per_field:
            print(f"\n   ✅ Đã đủ target metadata! Dừng scan metadata tại #{scanned:,}")
            break
            
        if scanned >= max_scan:
            print(f"\n   ⚠️ Đã scan {max_scan:,} metadata, dừng.")
            break

    target_ids = set(labor_records.keys()) | set(tax_records.keys())
    if not target_ids:
        print("❌ Không tìm thấy record metadata nào phù hợp.")
        return False

    # 2. Stream content để lấy nội dung
    print(f"\n   Đang lấy nội dung cho {len(target_ids):,} documents từ content split...")
    try:
        ds_content = load_dataset(
            "th1nhng0/vietnamese-legal-documents",
            name="content",
            split="data",
            streaming=True,
        )
    except Exception as e:
        print(f"❌ Không load được dataset content: {e}")
        return False

    all_records = []
    found_content_count = 0
    scanned_content = 0

    for row in ds_content:
        scanned_content += 1
        doc_id = row.get("id")
        if doc_id in target_ids:
            # Lấy record metadata tương ứng
            if doc_id in labor_records:
                meta = labor_records[doc_id]
            else:
                meta = tax_records[doc_id]
                
            content_html = row.get("content_html") or ""
            # Strip HTML to plain text
            soup = BeautifulSoup(content_html, "html.parser")
            plain_text = soup.get_text(separator="\n", strip=True)
            
            if plain_text:
                # Merge
                merged = {**meta, "content": plain_text}
                all_records.append(merged)
                found_content_count += 1
                
                if found_content_count % 100 == 0:
                    print(f"   Đã lấy nội dung: {found_content_count:,}/{len(target_ids):,}")
                    
                if found_content_count >= len(target_ids):
                    print("   ✅ Đã lấy đủ nội dung cho tất cả target documents.")
                    break
                    
    print(f"\n📊 Kết quả:")
    print(f"   ✅ Lấy thành công nội dung cho {len(all_records):,} / {len(target_ids):,} records")
    
    if len(all_records) == 0:
        print("❌ Không có records nào được lưu.")
        return False

    # Lưu ra JSON
    output_path = RAW_DATA_DIR / "main_dataset.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Đã lưu tại: {output_path} ({output_path.stat().st_size / 1024 / 1024:.1f} MB)")
    return True


def download_eval_dataset(max_qa: int = 500):
    """Tải dataset đánh giá RAG: thangvip/vietnamese-legal-qa."""
    try:
        from datasets import load_dataset
    except ImportError:
        return

    print(f"\n📥 Tải tập QA đánh giá (tối đa {max_qa} cặp)...")
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
        print(f"   ✅ {len(records):,} câu hỏi QA → {output_path}")
    except Exception as e:
        print(f"   ⚠️  Không tải được QA dataset: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download legal datasets từ HuggingFace")
    parser.add_argument(
        "--target-per-field", type=int, default=1500,
        help="Số records cần tải mỗi lĩnh vực (default: 1500 → tổng ~3000)"
    )
    parser.add_argument(
        "--max-scan", type=int, default=500_000,
        help="Số records tối đa để scan (default: 500000)"
    )
    args = parser.parse_args()

    ok = download_dataset(
        target_per_field=args.target_per_field,
        max_scan=args.max_scan,
    )
    if ok:
        download_eval_dataset()
        print("\n✅ Hoàn thành! Chạy tiếp: python scripts/etl/normalize.py")
    else:
        print("\n❌ Download thất bại.")
