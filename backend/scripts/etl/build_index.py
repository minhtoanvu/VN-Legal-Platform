# Bước 6 ETL: tạo HNSW index trên cột embedding
# Phải chạy SAU khi embedder.py xong hết
# Tham số: m=16, ef_construction=128, cosine distance

import sys
import asyncio
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
sys.path.append(str(backend_dir))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def main():
    print("=== Tao HNSW Index tren document_chunks ===")

    import asyncpg
    conn = await asyncpg.connect("postgres://postgres:password@localhost:5432/legal_db")

    count = await conn.fetchval("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL")
    print(f"Chunks co embedding: {count}")

    if count == 0:
        print("Chua co embedding nao! Hay chay embedder.py truoc.")
        await conn.close()
        return

    print("Xoa index cu neu co...")
    await conn.execute("DROP INDEX IF EXISTS idx_chunks_embedding_hnsw")

    print("Dang tao HNSW index (co the mat 1-5 phut)...")
    print("  m=16, ef_construction=128, cosine")

    await conn.execute(
        """
        CREATE INDEX idx_chunks_embedding_hnsw
        ON document_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 128)
        """,
        timeout=1000
    )

    idx = await conn.fetchrow("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'document_chunks'
        AND indexname = 'idx_chunks_embedding_hnsw'
    """)

    if idx:
        print(f"Index tao thanh cong: {idx['indexname']}")
    else:
        print("Loi: khong tim thay index sau khi tao!")

    await conn.close()
    print("=== Xong! Semantic Search san sang ===")


if __name__ == "__main__":
    asyncio.run(main())
