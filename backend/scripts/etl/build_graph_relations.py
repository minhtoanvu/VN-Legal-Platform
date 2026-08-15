"""
Build Knowledge Graph relations từ cấu trúc mã Pháp Điển có trong DB.
Dùng psycopg2 đồng bộ để tránh lỗi asyncpg connection.

Chạy: python scripts/etl/build_graph_relations.py
"""
import re
import sys
import time
import unicodedata
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"): sys.stderr.reconfigure(encoding="utf-8")

DB_URL = "host=localhost port=5432 dbname=legal_db user=postgres password=password"

# Thứ bậc loại văn bản (số nhỏ hơn = cấp cao hơn trong hệ thống pháp luật)
TYPE_RANK = {
    "LQ":  10,   # Luật
    "NQ":  10,   # Nghị quyết Quốc hội
    "PL":  10,   # Pháp lệnh
    "HP":  5,    # Hiến pháp
    "ND":  20,   # Nghị định
    "QD":  30,   # Quyết định
    "TT":  30,   # Thông tư
    "CT":  30,   # Chỉ thị
    "TTLT": 30,  # Thông tư liên tịch
    "HD":  30,   # Hướng dẫn
    "CV":  40,   # Công văn
}

def normalize(s: str) -> str:
    """Bỏ dấu tiếng Việt, in hoa."""
    nfkd = unicodedata.normalize("NFKD", s)
    result = "".join(c for c in nfkd if not unicodedata.combining(c)).upper()
    # Xử lý Đ/đ đặc biệt (không decompose theo NFKD)
    return result.replace("Đ", "D").replace("đ", "D")

def parse_doc(dn: str):
    """
    Parse mã Pháp Điển: 'Điều 17.1.LQ.1' → {'topic': '17.1', 'vtype': 'LQ', 'rest': '1'}
    """
    if not dn:
        return None
    norm = normalize(dn)
    m = re.match(r"DIEU\s+(\d+\.\d+)\.([A-Z]+)\.(.+)", norm)
    if not m:
        return None
    topic, vtype, rest = m.groups()
    return {"topic": topic, "vtype": vtype, "rest": rest}


def wait_for_db(conn_str: str, max_retries: int = 10) -> object:
    """Thử kết nối DB với retry logic."""
    try:
        import psycopg2
    except ImportError:
        print("psycopg2 chưa cài. Thử pip install psycopg2-binary")
        sys.exit(1)

    for i in range(max_retries):
        try:
            conn = psycopg2.connect(conn_str)
            print(f"✅ Kết nối DB thành công (lần thử {i+1})")
            return conn
        except psycopg2.OperationalError as e:
            print(f"⏳ Chờ DB... ({i+1}/{max_retries}): {e}")
            time.sleep(3)
    print("❌ Không kết nối được DB sau nhiều lần thử.")
    sys.exit(1)


def main():
    conn = wait_for_db(DB_URL)
    cur = conn.cursor()

    # 1. Lấy toàn bộ documents
    print("Đang tải documents từ DB...")
    cur.execute("SELECT id, doc_number FROM documents WHERE doc_number IS NOT NULL")
    docs = cur.fetchall()
    print(f"Tổng documents: {len(docs)}")

    # 2. Parse doc_number
    parsed = []
    for doc_id, doc_number in docs:
        p = parse_doc(doc_number)
        if p:
            p["id"] = str(doc_id)
            parsed.append(p)
    print(f"Parsed thành công: {len(parsed)}/{len(docs)}")

    if not parsed:
        print("⚠️  Không parse được doc nào. Kiểm tra format doc_number trong DB.")
        cur.close()
        conn.close()
        return

    # 3. Group by chủ đề
    by_topic: dict = defaultdict(list)
    for p in parsed:
        by_topic[p["topic"]].append(p)
    print(f"Số chủ đề (topics): {len(by_topic)}")

    # 4. Suy luận quan hệ
    relations = []
    seen = set()

    for topic, items in by_topic.items():
        # Group by loại văn bản
        by_type: dict = defaultdict(list)
        for item in items:
            by_type[item["vtype"]].append(item)

        # Quan hệ GUIDES: loại thấp hơn trong phân cấp hướng dẫn loại cao hơn
        vtypes_sorted = sorted(by_type.keys(), key=lambda v: TYPE_RANK.get(v, 50))
        for i in range(len(vtypes_sorted) - 1):
            lower_type = vtypes_sorted[i]   # cấp cao hơn (rank nhỏ hơn)
            higher_type = vtypes_sorted[i + 1]  # cấp thấp hơn (rank lớn hơn)
            # docs cấp thấp hơn GUIDES docs cấp cao hơn (TT hướng dẫn NĐ, NĐ hướng dẫn LQ)
            for dh in by_type[higher_type]:
                for dl in by_type[lower_type]:
                    pair = (dh["id"], dl["id"])
                    if pair not in seen:
                        seen.add(pair)
                        relations.append((dh["id"], dl["id"], "GUIDES"))

        # Quan hệ CITES: điều khoản liền kề cùng loại trong cùng chủ đề
        for vtype, st in by_type.items():
            st.sort(key=lambda x: x["rest"])
            max_cites = min(len(st) - 1, 100)  # Giới hạn để tránh quá nhiều
            for k in range(max_cites):
                pair = (st[k]["id"], st[k + 1]["id"])
                if pair not in seen:
                    seen.add(pair)
                    relations.append((st[k]["id"], st[k + 1]["id"], "CITES"))

    print(f"Tổng quan hệ suy luận được: {len(relations):,}")

    if not relations:
        print("Không có quan hệ nào. Kiểm tra lại dữ liệu.")
        cur.close()
        conn.close()
        return

    # 5. Xóa và insert mới
    print("Đang xóa dữ liệu cũ...")
    cur.execute("DELETE FROM document_relations")
    conn.commit()

    print(f"Đang insert {len(relations):,} quan hệ theo batch...")
    BATCH = 200
    inserted = 0
    for i in range(0, len(relations), BATCH):
        batch = relations[i:i + BATCH]
        values = ",".join(
            cur.mogrify("(gen_random_uuid(), %s::uuid, %s::uuid, %s)", (s, t, r)).decode("utf-8")
            for s, t, r in batch
        )
        cur.execute(
            "INSERT INTO document_relations (id, source_doc_id, target_doc_id, relation_type) "
            "VALUES " + values + " ON CONFLICT DO NOTHING"
        )
        inserted += len(batch)
        if i % 2000 == 0:
            print(f"  ...{inserted:,} inserted")
    conn.commit()

    # 6. Verify
    cur.execute("SELECT COUNT(*) FROM document_relations")
    total = cur.fetchone()[0]
    print(f"\n✅ XONG! {total:,} quan hệ trong document_relations.")
    print("   Mở http://localhost:5173/knowledge-graph để xem kết quả!")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
