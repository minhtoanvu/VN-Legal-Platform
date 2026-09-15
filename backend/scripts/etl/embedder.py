# Bước 5 ETL: tạo vector embedding cho từng chunk
# Dùng mô hình bkai-foundation-models/vietnamese-bi-encoder
# Chạy trên CPU, batch nhỏ để tránh tràn RAM
# Thời gian ước tính: 15-45 phút tùy số lượng chunks

import sys
import asyncio
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
sys.path.append(str(backend_dir))

# ═══ TẮT SOẠN SONG SONG — BẮT BUỘC khi chạy model AI trên CPU ═══
import os
os.environ["OMP_NUM_THREADS"] = "1"           # giới hạn thread CPU, tránh tranh chấp
os.environ["TOKENIZERS_PARALLELISM"] = "false" # tắt Rust tokenizer parallel trong async

from sqlalchemy import select, update, text
from app.core.database import AsyncSessionLocal
from app.models.document import DocumentChunk

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Cai dat: pip install sentence-transformers")
    sys.exit(1)


# ═══ CẤU HÌNH MODEL ═══
MODEL_NAME = "bkai-foundation-models/vietnamese-bi-encoder"  # Bi-encoder tiếng Việt từ ĐH Bách Khoa HN
BATCH_SIZE = 16  # sweet-spot: nhỏ hơn → chậm, lớn hơn → RAM tràn trên máy 8GB


async def main():
    print(f"=== Tao Embeddings cho Chunks ===")
    print(f"Model: {MODEL_NAME}, batch_size={BATCH_SIZE}")
    print()

    # ── TảI MODEL (lần đầu mất 1-3 phút để download từ HuggingFace) ──
    print("Dang tai model (co the mat vai phut lan dau)...")
    t0 = time.time()
    model = SentenceTransformer(MODEL_NAME, device="cpu")  # chạy trên CPU (không cần GPU)
    print(f"Model da tai xong ({time.time() - t0:.1f}s). Chieu vector: {model.get_sentence_embedding_dimension()}")

    async with AsyncSessionLocal() as session:
        # ── ĐẾỌ THÔNG MINH: chỉ embed chunk chưa có embedding ──
        # Nếu bị ngắt giữa chừng, chạy lại sẽ tiếp tục từ chỗ dừng (resume)
        count_res = await session.execute(text("SELECT count(*) FROM document_chunks WHERE embedding IS NULL"))
        total = count_res.scalar() or 0
        print(f"Chunks chua co embedding: {total}")

        if total == 0:
            print("Tat ca chunks da duoc embed roi. Thoat.")
            return

        FETCH_SIZE = 1000  # lấy 1000 chunks mỗi lần query DB — giảm số lần round-trip
        done = 0

        # ── VÒNG LẶP CHÍNH: Fetch → Encode → Save → lặp lại cho đến hết ──
        while done < total:
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

                # Khi batch đầy BATCH_SIZE (16) thì encode và lưu người dùng
                if len(texts_batch) >= BATCH_SIZE:
                    await _embed_and_save(session, model, ids_batch, texts_batch)
                    done += len(texts_batch)
                    print(f"  {done}/{total} chunks ({done/total*100:.1f}%)")
                    ids_batch, texts_batch = [], []

            # Xử lý phần dư cuối (< BATCH_SIZE chunks còn lại)
            if texts_batch:
                await _embed_and_save(session, model, ids_batch, texts_batch)
                done += len(texts_batch)
                print(f"  {done}/{total} chunks ({done/total*100:.1f}%)")

    elapsed = time.time() - t0
    print(f"\nHoan thanh! {done} chunks embedded trong {elapsed/60:.1f} phut")


# ═══ HÀM LƬu VECTOR VÀO DB ═══
async def _embed_and_save(session, model, ids, texts):
    # normalize_embeddings=True: chuẩn hoá về unit sphere
    # → cosine similarity = dot product → pgvector tính nhanh hơn
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

    # Bulk update: cập nhật nhiều dòng cùng lúc (hiệu quả hơn từng dòng một)
    await session.execute(
        update(DocumentChunk),
        [{"id": cid, "embedding": vec.tolist()} for cid, vec in zip(ids, vectors)],
        execution_options={"synchronize_session": None}  # bỏ qua sync ORM để nhanh hơn
    )
    await session.commit()  # flush vào DB, giải phóng bộ nhớ


if __name__ == "__main__":
    asyncio.run(main())
