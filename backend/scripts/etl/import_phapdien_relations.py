import psycopg2
import uuid
import re
from datasets import load_dataset

DB_URL = "host=localhost port=5432 dbname=legal_db user=postgres password=password"

def main():
    print("=== TRÍCH XUẤT QUAN HỆ TỪ PHÁP ĐIỂN (REAL DATA) ===")
    try:
        conn = psycopg2.connect(DB_URL)
    except Exception as e:
        print("Lỗi kết nối DB:", e)
        return
        
    cur = conn.cursor()

    print("1. Lấy danh sách ID các Điều luật trong DB...")
    cur.execute("SELECT id, doc_number FROM documents")
    db_docs = {row[1]: str(row[0]) for row in cur.fetchall()}  # doc_number (e.g. Điều 20.2.LQ.1) -> UUID
    print(f"   -> Đã tải {len(db_docs)} Điều luật từ DB.")

    cur.execute("TRUNCATE TABLE document_relations CASCADE")

    print("2. Quét file main_dataset.json để trích xuất related_note_text...")
    import json
    with open("data/raw/main_dataset.json", "r", encoding="utf-8") as f:
        ds = json.load(f)
    
    # Regex để bắt các mã Điều luật được trích dẫn (VD: Điều 6.3.LQ.33)
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
        
        # Tìm tất cả các Điều luật được nhắc đến trong text
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
                        "CITES",  # Pháp điển chủ yếu là dẫn chiếu (CITES)
                        related_text[:255]  # Lưu đoạn text giải thích làm description
                    ))
                
        if len(batch) >= 500:
            cur.executemany("""
            INSERT INTO document_relations (id, source_doc_id, target_doc_id, relation_type, description)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (source_doc_id, target_doc_id, relation_type) DO NOTHING
            """, batch)
            conn.commit()
            inserted_count += len(batch)
            batch = []
            print(f"   ...đã trích xuất {inserted_count} quan hệ thật")
            
    if batch:
        cur.executemany("""
        INSERT INTO document_relations (id, source_doc_id, target_doc_id, relation_type, description)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (source_doc_id, target_doc_id, relation_type) DO NOTHING
        """, batch)
        conn.commit()
        inserted_count += len(batch)

    print(f"\nHoàn tất! Đã trích xuất thành công {inserted_count} quan hệ DẪN CHIẾU THẬT từ Pháp điển.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
