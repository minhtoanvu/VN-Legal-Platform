# Import quan hệ dẫn chiếu giữa các điều luật từ Pháp điển vào bảng document_relations
# Đọc trường related_note_text trong main_dataset.json, dùng regex bắt mã điều luật
# Sau đó ánh xạ sang UUID trong DB và insert edge vào bảng

import asyncio
import uuid
import re
import sys

sys.path.insert(0, ".")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from datasets import load_dataset
from app.core.database import AsyncSessionLocal
from sqlalchemy import text


async def main():
    print("=== Trich xuat quan he dan chieu tu Phap Dien ===")
    try:
        db = AsyncSessionLocal()
    except Exception as e:
        print("Loi ket noi DB:", e)
        return

    # Lấy mapping doc_number -> UUID từ DB để tra cứu nhanh
    print("1. Lay danh sach cac Dieu luat trong DB...")
    result = await db.execute(text("SELECT id, doc_number FROM documents"))
    db_docs = {row[1]: str(row[0]) for row in result.fetchall()}
    print(f"  -> Da tai {len(db_docs)} Dieu luat tu DB.")

    await db.execute(text("TRUNCATE TABLE document_relations CASCADE"))
    await db.commit()

    print("2. Quet main_dataset.json de trich xuat related_note_text...")
    import json
    with open("data/raw/main_dataset.json", "r", encoding="utf-8") as f:
        ds = json.load(f)

    # Regex bắt mã điều luật dạng: Điều 6.3.LQ.33
    pattern = r'(Điều \d+\.\d+\.[A-Z]+\.\d+)'

    batch = []
    inserted_count = 0
    unique_edges = set()

    for row in ds:
        source_article_id = row.get("article_id")
        related_text = row.get("related_note_text")

        if not related_text or source_article_id not in db_docs:
            continue

        source_uuid = db_docs[source_article_id]

        # Tìm tất cả mã điều luật được nhắc đến trong related_note_text
        matches = re.findall(pattern, related_text)
        for target_article_id in matches:
            if target_article_id in db_docs and target_article_id != source_article_id:
                target_uuid = db_docs[target_article_id]

                edge_key = (source_uuid, target_uuid, "CITES")
                if edge_key not in unique_edges:
                    unique_edges.add(edge_key)
                    batch.append((
                        str(uuid.uuid4()),
                        source_uuid,
                        target_uuid,
                        "CITES",
                        related_text[:255]  # lưu đoạn text làm mô tả quan hệ
                    ))

        # Insert theo batch 500 records cho nhanh
        if len(batch) >= 500:
            params = []
            for b in batch:
                params.append({"p_id": b[0], "p_src": b[1], "p_tgt": b[2], "p_rel": b[3], "p_desc": b[4]})

            await db.execute(text("""
            INSERT INTO document_relations (id, source_doc_id, target_doc_id, relation_type, description)
            VALUES (:p_id, :p_src, :p_tgt, :p_rel, :p_desc)
            ON CONFLICT (source_doc_id, target_doc_id, relation_type) DO NOTHING
            """), params)
            await db.commit()
            inserted_count += len(batch)
            batch = []
            print(f"  ...da trich xuat {inserted_count} quan he")

    # Flush batch cuối còn dư
    if batch:
        params = []
        for b in batch:
            params.append({"p_id": b[0], "p_src": b[1], "p_tgt": b[2], "p_rel": b[3], "p_desc": b[4]})

        await db.execute(text("""
        INSERT INTO document_relations (id, source_doc_id, target_doc_id, relation_type, description)
        VALUES (:p_id, :p_src, :p_tgt, :p_rel, :p_desc)
        ON CONFLICT (source_doc_id, target_doc_id, relation_type) DO NOTHING
        """), params)
        await db.commit()
        inserted_count += len(batch)

    print(f"\nHoan tat! Da trich xuat {inserted_count} quan he dan chieu tu Phap dien.")
    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
