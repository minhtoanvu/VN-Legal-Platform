"""
ETL Step 1: Download dataset từ HuggingFace.

Dataset chính: th1nhng0/vietnamese-legal-documents
Backup:        tmquan/phapdien-moj-gov-vn

Chạy: python scripts/etl/download_data.py
"""

import argparse
import json
import os
from pathlib import Path

from datasets import load_dataset

# Thư mục lưu dữ liệu raw
RAW_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_main_dataset(max_samples: int = 0):
    """
    Tải dataset chính: th1nhng0/vietnamese-legal-documents
    max_samples=0 → tải toàn bộ
    """
    print("📥 Tải th1nhng0/vietnamese-legal-documents từ HuggingFace...")

    try:
        ds = load_dataset(
            "th1nhng0/vietnamese-legal-documents",
            split="train",
            trust_remote_code=True,
        )

        if max_samples > 0:
            ds = ds.select(range(min(max_samples, len(ds))))

        print(f"   ✅ Tải thành công: {len(ds):,} documents")
        print(f"   Cột dữ liệu: {ds.column_names}")

        # Lưu ra JSON để xử lý tiếp
        output_path = RAW_DATA_DIR / "main_dataset.json"
        ds.to_json(str(output_path), force_ascii=False)
        print(f"   💾 Lưu tại: {output_path}")

        return ds

    except Exception as e:
        print(f"   ❌ Lỗi tải dataset chính: {e}")
        print("   → Thử tải dataset backup...")
        return download_backup_dataset(max_samples)


def download_backup_dataset(max_samples: int = 0):
    """Tải dataset backup: tmquan/phapdien-moj-gov-vn"""
    print("📥 Tải tmquan/phapdien-moj-gov-vn...")

    ds = load_dataset("tmquan/phapdien-moj-gov-vn", split="train")

    if max_samples > 0:
        ds = ds.select(range(min(max_samples, len(ds))))

    print(f"   ✅ Tải thành công: {len(ds):,} documents")

    output_path = RAW_DATA_DIR / "backup_dataset.json"
    ds.to_json(str(output_path), force_ascii=False)
    print(f"   💾 Lưu tại: {output_path}")

    return ds


def download_eval_dataset():
    """Tải dataset đánh giá RAG: thangvip/vietnamese-legal-qa"""
    print("📥 Tải thangvip/vietnamese-legal-qa (evaluation dataset)...")

    ds = load_dataset("thangvip/vietnamese-legal-qa", split="train")
    print(f"   ✅ Tải thành công: {len(ds):,} QA pairs")

    output_path = RAW_DATA_DIR / "eval_qa.json"
    ds.to_json(str(output_path), force_ascii=False)
    print(f"   💾 Lưu tại: {output_path}")

    return ds


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download legal datasets từ HuggingFace")
    parser.add_argument(
        "--max-samples",
        type=int,
        default=0,
        help="Số lượng mẫu tối đa (0 = toàn bộ). VD: --max-samples 5000",
    )
    parser.add_argument(
        "--eval-only",
        action="store_true",
        help="Chỉ tải evaluation dataset",
    )
    args = parser.parse_args()

    if args.eval_only:
        download_eval_dataset()
    else:
        download_main_dataset(max_samples=args.max_samples)
        download_eval_dataset()

    print("\n✅ Hoàn thành download!")
    print(f"   Dữ liệu lưu tại: {RAW_DATA_DIR}")
