# Script chạy toàn bộ pipeline ETL từ đầu đến cuối
# Thứ tự: download -> normalize -> load DB -> chunking
# Chạy: python scripts/etl/run_full_etl.py
#        python scripts/etl/run_full_etl.py --target-per-field 2000 --skip-download

import argparse
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def print_step(step: int, title: str):
    print(f"\n{'='*60}")
    print(f"  BUOC {step}: {title}")
    print(f"{'='*60}")


def run_download(target_per_field: int) -> bool:
    print_step(1, "Tai du lieu Lao dong & Thue tu HuggingFace")
    from scripts.etl.download_data import download_dataset, download_eval_dataset
    ok = download_dataset(target_per_field=target_per_field)
    if ok:
        download_eval_dataset()
    return ok


def run_normalize() -> int:
    print_step(2, "Chuan hoa schema -> documents_normalized.jsonl")
    raw_dir = Path(__file__).parent.parent.parent / "data" / "raw"
    processed_dir = Path(__file__).parent.parent.parent / "data" / "processed"
    from scripts.etl.normalize import normalize_dataset
    n = normalize_dataset(
        raw_dir / "main_dataset.json",
        processed_dir / "documents_normalized.jsonl",
    )
    return n


async def run_load_db() -> int:
    print_step(3, "Load documents vao PostgreSQL (xoa cu + insert moi)")
    from sqlalchemy import text
    from app.core.database import AsyncSessionLocal, engine
    from scripts.etl.load_db import load_documents, verify_load

    processed_dir = Path(__file__).parent.parent.parent / "data" / "processed"
    input_file = processed_dir / "documents_normalized.jsonl"

    print("  Xoa du lieu cu trong DB...")
    async with AsyncSessionLocal() as session:
        await session.execute(text("TRUNCATE TABLE document_chunks CASCADE"))
        await session.execute(text("TRUNCATE TABLE documents CASCADE"))
        await session.commit()
        print("  Da xoa documents + document_chunks cu")

    inserted = await load_documents(input_file, batch_size=100)
    await verify_load()
    return inserted


async def run_chunker() -> int:
    print_step(4, "Cat chunks (sliding window 500 ky tu, overlap 50)")
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
        print(f"  {total_docs:,} documents can xu ly")

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
                print(f"  [{pct:5.1f}%] {i+1:,}/{total_docs:,} docs | {total_chunks:,} chunks", end="\r")
                chunks_to_insert = []

    print(f"\n  Tong chunks da tao: {total_chunks:,}")
    return total_chunks


async def main(target_per_field: int, skip_download: bool):
    t0 = time.time()
    print("\n=== BAT DAU ETL PIPELINE — AI Legal Intelligence Platform ===")
    print(f"  Target: {target_per_field:,} records/linh vuc")

    if not skip_download:
        ok = run_download(target_per_field)
        if not ok:
            print("\nDownload that bai. Dung pipeline.")
            return
    else:
        print("\nBo qua download (--skip-download)")

    n_docs = run_normalize()
    if n_docs == 0:
        print("\nNormalize khong ra documents. Kiem tra du lieu raw.")
        return

    inserted = await run_load_db()
    n_chunks = await run_chunker()

    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"  PIPELINE HOAN THANH — {elapsed/60:.1f} phut")
    print(f"{'='*60}")
    print(f"  Documents trong DB : {inserted:,}")
    print(f"  Chunks trong DB    : {n_chunks:,}")
    print(f"\n  Buoc tiep theo:")
    print(f"  -> Chay embedder.py de tao vector embedding")
    print(f"  -> Chay build_index.py de tao HNSW index")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chay toan bo ETL pipeline")
    parser.add_argument(
        "--target-per-field", type=int, default=1500,
        help="So records can cho moi linh vuc (default: 1500)"
    )
    parser.add_argument(
        "--skip-download", action="store_true",
        help="Bo qua buoc download (dung file raw co san)"
    )
    args = parser.parse_args()

    asyncio.run(main(
        target_per_field=args.target_per_field,
        skip_download=args.skip_download,
    ))
