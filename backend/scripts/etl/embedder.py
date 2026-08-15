"""
ETL Pipeline - Bước 4: Batch Embedder
Tải mô hình bkai-foundation-models/vietnamese-bi-encoder,
embed từng chunk và lưu vector vào cột embedding trong document_chunks.

Memory-safe: Fetch 1000 chunks each batch, encode them in mini-batches.
Thời gian dự kiến: ~15-30 phút trên CPU với 10,000+ chunks.
"""

import sys
import asyncio
import time
from pathlib import Path

# Fix Windows console encoding for print emojis & Vietnamese
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
sys.path.append(str(backend_dir))

import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from sqlalchemy import select, update, text
from app.core.database import AsyncSessionLocal
from app.models.document import DocumentChunk

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Cài đặt: pip install sentence-transformers")
    sys.exit(1)


MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"
BATCH_SIZE = 16

async def main():
    print("=== Bắt đầu tạo Embeddings cho Chunks (HNSW Vector) ===")
    print(f"Model: {MODEL_NAME}")
    print(f"Batch size: {BATCH_SIZE}")
    print()

    # Load model (chỉ CPU, tránh OOM)
    print("Đang tải model (có thể mất vài phút lần đầu)...")
    t0 = time.time()
    model = SentenceTransformer(MODEL_NAME, device="cpu")
    print(f"Model tải xong ({time.time() - t0:.1f}s). Chiều vector: {model.get_sentence_embedding_dimension()}")

    async with AsyncSessionLocal() as session:
        count_res = await session.execute(text("SELECT count(*) FROM document_chunks WHERE embedding IS NULL"))
        total = count_res.scalar() or 0
        print(f"Chunks chưa có embedding: {total}")

        if total == 0:
            print("Tất cả chunks đã được embed rồi. Thoát.")
            return

        FETCH_SIZE = 1000
        done = 0

        while done < total:
            # Lấy batch 1000 chunks từ db
            result = await session.execute(
                select(DocumentChunk.id, DocumentChunk.content_chunk)
                .where(DocumentChunk.embedding == None)
                .order_by(DocumentChunk.id)
                .limit(FETCH_SIZE)
            )
            rows = result.all()
            if not rows:
                break
                
            ids_batch = []
            texts_batch = []
            
            for chunk_id, text_chunk in rows:
                ids_batch.append(chunk_id)
                texts_batch.append(text_chunk)
                
                # Cứ BATCH_SIZE (32) thì encode và update để đỡ tốn RAM
                if len(texts_batch) >= BATCH_SIZE:
                    await _embed_and_save(session, model, ids_batch, texts_batch)
                    done += len(texts_batch)
                    print(f"  → {done}/{total} chunks đã embed ({done/total*100:.1f}%)")
                    ids_batch, texts_batch = [], []
                    
            # Dư cuối batch 1000
            if texts_batch:
                await _embed_and_save(session, model, ids_batch, texts_batch)
                done += len(texts_batch)
                print(f"  → {done}/{total} chunks đã embed ({done/total*100:.1f}%)")

    elapsed = time.time() - t0
    print(f"\n=== Hoàn thành! {done} chunks embedded trong {elapsed/60:.1f} phút ===")


async def _embed_and_save(session, model, ids, texts):
    """Embed một batch và lưu vào DB bằng bulk update."""
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    # ORM Bulk UPDATE by Primary Key tự động map theo khóa chính 'id' trong dictionary
    await session.execute(
        update(DocumentChunk),
        [{"id": cid, "embedding": vec.tolist()} for cid, vec in zip(ids, vectors)],
        execution_options={"synchronize_session": None}
    )
    await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
