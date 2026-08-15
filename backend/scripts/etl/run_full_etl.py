"""
Pipeline Tổng hợp: Re-ETL với đúng dữ liệu Lao động & Thuế

Script này chạy tuần tự:
  1. download_data.py  — Tải dữ liệu từ HuggingFace (lọc đúng lĩnh vực)
  2. normalize.py      — Chuẩn hóa schema
  3. load_db.py        — Load vào PostgreSQL (xóa và insert lại)
  4. chunker.py        — Cắt chunks (sliding window)

Chạy: python scripts/etl/run_full_etl.py
      python scripts/etl/run_full_etl.py --target-per-field 2000 --skip-download
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

# Thêm backend root vào path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def print_step(step: int, title: str):
    print(f"\n{'='*60}")
    print(f"  BƯỚC {step}: {title}")
    print(f"{'='*60}")


def run_download(target_per_field: int) -> bool:
    print_step(1, "Tải dữ liệu Lao động & Thuế từ HuggingFace")
    from scripts.etl.download_data import download_dataset, download_eval_dataset
    ok = download_dataset(target_per_field=target_per_field)
    if ok:
        download_eval_dataset()
    return ok


def run_normalize() -> int:
    print_step(2, "Chuẩn hóa schema → documents_normalized.jsonl")
    raw_dir = Path(__file__).parent.parent.parent / "data" / "raw"
    processed_dir = Path(__file__).parent.parent.parent / "data" / "processed"
    from scripts.etl.normalize import normalize_dataset
    n = normalize_dataset(
        raw_dir / "main_dataset.json",
        processed_dir / "documents_normalized.jsonl",
    )
    return n


async def run_load_db() -> int:
    print_step(3, "Load documents vào PostgreSQL (xóa cũ + insert mới)")
    from sqlalchemy import text
    from app.core.database import AsyncSessionLocal, engine
    from scripts.etl.load_db import load_documents, verify_load

    processed_dir = Path(__file__).parent.parent.parent / "data" / "processed"
    input_file = processed_dir / "documents_normalized.jsonl"

    # Xóa dữ liệu cũ trước khi insert lại
    print("   Xóa dữ liệu cũ trong DB...")
    async with AsyncSessionLocal() as session:
        await session.execute(text("TRUNCATE TABLE document_chunks CASCADE"))
        await session.execute(text("TRUNCATE TABLE documents CASCADE"))
        await session.commit()
        print("   ✅ Đã xóa documents + document_chunks cũ")

    inserted = await load_documents(input_file, batch_size=100)
    await verify_load()
    return inserted


async def run_chunker() -> int:
    print_step(4, "Cắt chunks (sliding window 500 ký tự, overlap 50)")
    # Import và chạy trực tiếp chunker logic
    from sqlalchemy import select, text
    from app.core.database import AsyncSessionLocal
    from app.models.document import Document, DocumentChunk

    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        from langchain.text_splitter import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    total_chunks = 0
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Document.id, Document.content).where(Document.content.isnot(None))
        )
        docs = result.all()
        total_docs = len(docs)
        print(f"   {total_docs:,} documents cần xử lý")

        batch_size = 100
        chunks_to_insert = []

        for i, (doc_id, content) in enumerate(docs):
            if not content:
                continue

            splits = text_splitter.split_text(content)
            for chunk_idx, chunk_text in enumerate(splits):
                chunks_to_insert.append(DocumentChunk(
                    document_id=doc_id,
                    chunk_index=chunk_idx,
                    content_chunk=chunk_text,
                    token_count=len(chunk_text.split()),
                ))
                total_chunks += 1

            if (i + 1) % batch_size == 0 or i == total_docs - 1:
                session.add_all(chunks_to_insert)
                await session.commit()
                pct = (i + 1) / total_docs * 100
                print(f"   [{pct:5.1f}%] {i+1:,}/{total_docs:,} docs | {total_chunks:,} chunks", end="\r")
                chunks_to_insert = []

    print(f"\n   ✅ Tổng chunks đã tạo: {total_chunks:,}")
    return total_chunks


async def main(target_per_field: int, skip_download: bool):
    t0 = time.time()
    print("\n🚀 BẮT ĐẦU RE-ETL PIPELINE — AI Legal Intelligence Platform")
    print(f"   Target: {target_per_field:,} records/lĩnh vực")

    # Bước 1: Download
    if not skip_download:
        ok = run_download(target_per_field)
        if not ok:
            print("\n❌ Download thất bại. Dừng pipeline.")
            return
    else:
        print("\n⏭️  Bỏ qua download (--skip-download)")

    # Bước 2: Normalize
    n_docs = run_normalize()
    if n_docs == 0:
        print("\n❌ Normalize không ra documents. Kiểm tra dữ liệu raw.")
        return

    # Bước 3: Load DB
    inserted = await run_load_db()

    # Bước 4: Chunker
    n_chunks = await run_chunker()

    # Tổng kết
    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"  ✅ PIPELINE HOÀN THÀNH — {elapsed/60:.1f} phút")
    print(f"{'='*60}")
    print(f"  📄 Documents trong DB : {inserted:,}")
    print(f"  🔖 Chunks trong DB    : {n_chunks:,}")
    print(f"\n  Bước tiếp theo:")
    print(f"  → Chạy embedder.py để tạo vector embedding")
    print(f"  → Chạy build_index.py để tạo HNSW index")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chạy toàn bộ ETL pipeline")
    parser.add_argument(
        "--target-per-field", type=int, default=1500,
        help="Số records cần cho mỗi lĩnh vực (default: 1500)"
    )
    parser.add_argument(
        "--skip-download", action="store_true",
        help="Bỏ qua bước download (dùng file raw có sẵn)"
    )
    args = parser.parse_args()

    asyncio.run(main(
        target_per_field=args.target_per_field,
        skip_download=args.skip_download,
    ))
