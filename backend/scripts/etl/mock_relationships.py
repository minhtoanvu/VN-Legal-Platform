import psycopg2
import uuid
import random

DB_URL = "host=localhost port=5432 dbname=legal_db user=postgres password=password"

def main():
    print("=== TẠO MOCK DỮ LIỆU KNOWLEDGE GRAPH CHO MỤC ĐÍCH DEMO ===")
    try:
        conn = psycopg2.connect(DB_URL)
    except Exception as e:
        print("Lỗi kết nối DB:", e)
        return
        
    cur = conn.cursor()

    # Lấy 50 văn bản đầu tiên
    cur.execute("SELECT id FROM documents LIMIT 50")
    doc_ids = [str(r[0]) for r in cur.fetchall()]

    if len(doc_ids) < 5:
        print("Không đủ document để tạo relations")
        return
        
    cur.execute("TRUNCATE TABLE document_relations CASCADE")

    relations = ["AMENDS", "GUIDES", "REPLACES", "CITES"]
    batch = []
    
    # Tạo 50 relations ngẫu nhiên
    for _ in range(50):
        source = random.choice(doc_ids)
        target = random.choice(doc_ids)
        while source == target:
            target = random.choice(doc_ids)
            
        rel = random.choice(relations)
        batch.append((
            str(uuid.uuid4()),
            source,
            target,
            rel,
            f"Dữ liệu giả lập để test giao diện Knowledge Graph"
        ))

    query = """
    INSERT INTO document_relations (id, source_doc_id, target_doc_id, relation_type, description)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (source_doc_id, target_doc_id, relation_type) DO NOTHING
    """
    cur.executemany(query, batch)
    conn.commit()
    
    print(f"Thành công! Đã bơm {len(batch)} mối quan hệ (Mock) vào hệ thống.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
