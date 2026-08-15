import time
import psycopg2
import uuid
from datasets import load_dataset
from datetime import datetime

DB_URL = "host=localhost port=5432 dbname=legal_db user=postgres password=password"
#Chuỗi kết nối tới csl PostgresQL qua cổng m,ặc ịnh 5432

#Thử kết nối cơ sở ữ liệu tối a 10 lần cách nhau 2 giây nếu thất bại thì báo lỗi
def wait_for_db():
    for _ in range(10):
        try:
            return psycopg2.connect(DB_URL)
        except Exception:
            time.sleep(2)
    raise Exception("DB not ready")


def parse_date(date_str):
    if not date_str: return None
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").date()
    except Exception:
        return None

def main():
    conn = wait_for_db()
    cur = conn.cursor()

    print("1. Xoá dữ liệu cũ...")
    cur.execute("TRUNCATE TABLE documents CASCADE")
    conn.commit()

    print("2. Đang tải METADATA...")
    # Tải qua stream để không tốn RAM
    ds_meta = load_dataset("th1nhng0/vietnamese-legal-documents", "metadata", split="data")
    
    target_fields = ["lao động", "thuế"]
    
    doc_id_map = {} # HF_id -> UUID
    batch = []
    
    def insert_batch(batch_data):
        if not batch_data: return
        query = """
        INSERT INTO documents (id, doc_number, title, doc_type, issuing_body, field, 
                               issue_date, effective_date, expired_date, status, source_url, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        cur.executemany(query, batch_data)
        conn.commit()

    print("Đang lọc và chèn METADATA...")
    count = 0
    for row in ds_meta:
        field = row.get("linh_vuc")
        if not field: continue
        
        field_lower = field.lower()
        if any(t in field_lower for t in target_fields):
            new_id = str(uuid.uuid4())
            hf_id = row.get("id")
            doc_id_map[hf_id] = new_id
            
            # Map status
            raw_status = row.get("tinh_trang_hieu_luc", "")
            if "Hết hiệu lực" in raw_status: status = "expired"
            elif "Còn hiệu lực" in raw_status: status = "active"
            else: status = "active" # Mặc định
            
            batch.append((
                new_id,
                str(row.get("so_ky_hieu") or "UNKNOWN")[:100],
                row.get("title") or "Untitled",
                str(row.get("loai_van_ban") or "")[:50] if row.get("loai_van_ban") else None,
                str(row.get("co_quan_ban_hanh") or "")[:200] if row.get("co_quan_ban_hanh") else None,
                str(field)[:100],
                parse_date(row.get("ngay_ban_hanh")),
                parse_date(row.get("ngay_co_hieu_luc")),
                parse_date(row.get("ngay_het_hieu_luc")),
                status,
                row.get("nguon_thu_thap")
            ))
            count += 1
            
            if len(batch) >= 500:
                insert_batch(batch)
                batch = []
                print(f"  ...đã chèn {count} văn bản")
    
    if batch:
        insert_batch(batch)
        print(f"  ...đã chèn {count} văn bản (hoàn tất metadata)")

    print(f"Tổng số văn bản cần lấy content: {len(doc_id_map)}")

    print("3. Đang tải CONTENT (Text HTML)...")
    ds_content = load_dataset("th1nhng0/vietnamese-legal-documents", "content", split="data")
    
    updates = []
    updated_count = 0
    
    def update_batch(batch_data):
        if not batch_data: return
        query = "UPDATE documents SET content = %s WHERE id = %s"
        cur.executemany(query, batch_data)
        conn.commit()

    for row in ds_content:
        hf_id = row.get("id")
        if hf_id in doc_id_map:
            db_id = doc_id_map[hf_id]
            html = row.get("content_html", "")
            # Lọc bỏ một phần HTML tag đơn giản (nếu cần, nhưng MVP lưu html vẫn OK)
            updates.append((html, db_id))
            updated_count += 1
            
            if len(updates) >= 100:
                update_batch(updates)
                updates = []
                print(f"  ...đã cập nhật nội dung cho {updated_count} văn bản")
                
            # Tối ưu: Nếu đã tìm thấy đủ thì dừng sớm
            if updated_count >= len(doc_id_map):
                break

    if updates:
        update_batch(updates)
    
    print(f"Hoàn tất! Đã lưu toàn vẹn {updated_count} văn bản vào DB.")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
