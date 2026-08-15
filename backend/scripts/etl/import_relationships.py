import time
import psycopg2
import uuid
from datasets import load_dataset
from datetime import datetime

DB_URL = "host=localhost port=5432 dbname=legal_db user=postgres password=password"

# Map tiếng Việt sang EN chuẩn theo Backend Graph (UC-09)
RELATION_MAP = {
    "Căn cứ": "CITES",
    "Căn cứ một phần": "CITES",
    "Hướng dẫn": "GUIDES",
    "Sửa đổi, bổ sung": "AMENDS",
    "Sửa đổi": "AMENDS",
    "Bổ sung": "AMENDS",
    "Thay thế": "REPLACES",
    "Thay thế một phần": "REPLACES",
    "Bãi bỏ": "REVOKES",
    "Bãi bỏ một phần": "REVOKES",
    "Được dẫn chiếu": "CITES",
    "Đính chính": "AMENDS"
}

def wait_for_db():
    for _ in range(10):
        try:
            return psycopg2.connect(DB_URL)
        except Exception:
            time.sleep(2)
    raise Exception("DB not ready")

def main():
    print("=== Bắt đầu kéo Dữ liệu Quan hệ (Knowledge Graph) ===")
    conn = wait_for_db()
    cur = conn.cursor()

    # 1. Lấy danh sách doc_number trong DB hiện tại
    print("1. Đọc danh sách văn bản hiện có trong DB...")
    cur.execute("SELECT id, doc_number FROM documents WHERE doc_number IS NOT NULL AND doc_number != 'UNKNOWN'")
    db_docs = {}
    for row in cur.fetchall():
        db_id, doc_number = row
        db_docs[doc_number] = str(db_id)
        
    print(f"   -> Đã tải {len(db_docs)} doc_number từ DB.")

    if not db_docs:
        print("DB trống hoặc không có doc_number. Vui lòng chạy import_th1nh_dataset.py trước.")
        return

    # 2. Quét Metadata để map HF_ID -> doc_number
    print("2. Quét Metadata từ HuggingFace để tạo map (HF_ID -> doc_number)...")
    ds_meta = load_dataset("th1nhng0/vietnamese-legal-documents", "metadata", split="data")
    
    hf_id_to_uuid = {}
    mapped_count = 0
    for row in ds_meta:
        hf_id = row.get("id")
        doc_number = row.get("so_ky_hieu")
        if hf_id and doc_number and doc_number in db_docs:
            hf_id_to_uuid[str(hf_id)] = db_docs[doc_number]
            mapped_count += 1
            if mapped_count >= len(db_docs):
                break  # Tìm đủ rồi thì ngưng
                
    print(f"   -> Đã map thành công {len(hf_id_to_uuid)} HF_ID sang UUID của DB.")

    # 3. Quét Relationships và lọc
    print("3. Tải và lọc dữ liệu Relationships...")
    cur.execute("TRUNCATE TABLE document_relations CASCADE")
    conn.commit()
    
    ds_rel = load_dataset("th1nhng0/vietnamese-legal-documents", "relationships", split="data")
    
    batch = []
    inserted_count = 0
    
    def insert_batch(batch_data):
        if not batch_data: return
        query = """
        INSERT INTO document_relations (id, source_doc_id, target_doc_id, relation_type, description)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (source_doc_id, target_doc_id, relation_type) DO NOTHING
        """
        cur.executemany(query, batch_data)
        conn.commit()

    for row in ds_rel:
        source_hf = str(row.get("doc_id"))
        target_hf = str(row.get("other_doc_id"))
        raw_rel = row.get("relationship")
        
        # Chỉ giữ lại nếu cả 2 văn bản đều nằm trong DB của ta
        if source_hf in hf_id_to_uuid and target_hf in hf_id_to_uuid:
            source_uuid = hf_id_to_uuid[source_hf]
            target_uuid = hf_id_to_uuid[target_hf]
            
            rel_type = "CITES"
            for k, v in RELATION_MAP.items():
                if raw_rel and k.lower() in raw_rel.lower():
                    rel_type = v
                    break
                    
            batch.append((
                str(uuid.uuid4()),
                source_uuid,
                target_uuid,
                rel_type,
                raw_rel
            ))
            
            if len(batch) >= 500:
                insert_batch(batch)
                inserted_count += len(batch)
                batch = []
                print(f"  ...đã chèn {inserted_count} quan hệ")
                
    if batch:
        insert_batch(batch)
        inserted_count += len(batch)
        
    print(f"Hoàn tất! Đã thêm {inserted_count} quan hệ (edges) vào Knowledge Graph.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
