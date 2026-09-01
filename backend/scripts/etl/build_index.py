"""
ETL Pipeline - Bước 5: HNSW Index Builder
Tạo chỉ mục HNSW trên cột embedding trong document_chunks.

Theo PhanTichHeThong_v2_Fixed.docx:
  - m=16, ef_construction=128
  - distance_function=cosine (phù hợp với bi-encoder normalize=True)

Chú ý: Phải chạy sau khi embedder.py hoàn thành.
"""

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
    print("=== Tạo HNSW Index trên document_chunks ===")

    import asyncpg
    conn = await asyncpg.connect("postgres://postgres:password@localhost:5432/legal_db")
    
    count = await conn.fetchval("SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL")
    print(f"Chunks có embedding: {count}")
    
    if count == 0:
        print("Chưa có embedding nào! Hãy chạy embedder.py trước.")
        await conn.close()
        return

    print("Xóa index cũ nếu có...")
    await conn.execute("DROP INDEX IF EXISTS idx_chunks_embedding_hnsw")

    print("Đang tạo HNSW index (có thể mất 1-5 phút)...")
    print("  m=16, ef_construction=128, operator=vector_cosine_ops")
    
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
        print(f"✓ Index tạo thành công: {idx['indexname']}")
    else:
        print("✗ Lỗi: Không tìm thấy index sau khi tạo!")
        
    await conn.close()
    
    print("=== Xong! Semantic Search đã sẵn sàng ===")

if __name__ == "__main__":
    asyncio.run(main())
