"""
ETL Step 3: Load dữ liệu đã normalize vào PostgreSQL.

Chạy: python scripts/etl/load_db.py
Hoặc: python scripts/etl/load_db.py --batch-size 100 --limit 1000
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional
from uuid import uuid4

# Thêm backend root vào path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine
from app.core.config import settings
from app.models.document import Document

PROCESSED_DIR = Path(__file__).parent.parent.parent / "data" / "processed"


async def ensure_extension(session: AsyncSession):
    """Bật pgvector extension nếu chưa có."""
    await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    await session.commit()
    print("✅ pgvector extension đã được bật")


async def load_documents(
    input_file: Path,
    batch_size: int = 100,
    limit: Optional[int] = None,
):
    """Load documents từ JSONL file vào DB theo batch."""
    print(f"📂 Đọc file: {input_file}")

    records = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
            if limit and len(records) >= limit:
                break

    print(f"   Tổng: {len(records):,} records cần insert")

    inserted = 0
    skipped = 0

    async with AsyncSessionLocal() as session:
        await ensure_extension(session)

        # Insert theo batch
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            doc_objects = []

            for rec in batch:
                try:
                    doc = Document(
                        id=uuid4(),
                        doc_number=rec.get("doc_number", ""),
                        title=rec["title"],
                        doc_type=rec.get("doc_type"),
                        issuing_body=rec.get("issuing_body"),
                        field=rec.get("field"),
                        issue_date=_parse_date_str(rec.get("issue_date")),
                        effective_date=_parse_date_str(rec.get("effective_date")),
                        expired_date=_parse_date_str(rec.get("expired_date")),
                        status=rec.get("status", "active"),
                        content=rec.get("content"),
                        source_url=rec.get("source_url"),
                    )
                    doc_objects.append(doc)
                except Exception as e:
                    skipped += 1

            if doc_objects:
                session.add_all(doc_objects)
                await session.commit()
                inserted += len(doc_objects)

            # Progress
            pct = min((i + batch_size) / len(records) * 100, 100)
            print(f"   [{pct:5.1f}%] Đã insert {inserted:,} / {len(records):,}", end="\r")

    print(f"\n✅ Hoàn thành: {inserted:,} inserted | {skipped:,} skipped")
    return inserted


def _parse_date_str(date_str: Optional[str]):
    """Parse 'YYYY-MM-DD' string → date object, None nếu invalid."""
    if not date_str:
        return None
    try:
        from datetime import date
        parts = date_str.split("-")
        return date(int(parts[0]), int(parts[1]), int(parts[2]))
    except Exception:
        return None


async def verify_load():
    """Kiểm tra kết quả sau khi load."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT field, COUNT(*) as cnt FROM documents GROUP BY field ORDER BY cnt DESC")
        )
        rows = result.fetchall()
        print("\n📊 Thống kê sau khi load:")
        total = 0
        for row in rows:
            print(f"   {row[0]:20s}: {row[1]:,} documents")
            total += row[1]
        print(f"   {'TOTAL':20s}: {total:,} documents")


async def main(batch_size: int, limit: Optional[int]):
    input_file = PROCESSED_DIR / "documents_normalized.jsonl"

    if not input_file.exists():
        print(f"❌ Không tìm thấy {input_file}")
        print("   Chạy normalize.py trước!")
        return

    await load_documents(input_file, batch_size=batch_size, limit=limit)
    await verify_load()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load documents vào PostgreSQL")
    parser.add_argument("--batch-size", type=int, default=100, help="Số records mỗi batch")
    parser.add_argument("--limit", type=int, default=None, help="Giới hạn số records (test nhanh)")
    args = parser.parse_args()

    asyncio.run(main(batch_size=args.batch_size, limit=args.limit))
