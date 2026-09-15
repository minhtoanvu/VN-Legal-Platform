# Xây dựng Knowledge Graph từ cấu trúc mã Pháp Điển trong DB
# Phân tích doc_number (VD: "Điều 20.2.LQ.1") để suy ra quan hệ giữa các văn bản
# - GUIDES: văn bản cấp thấp hướng dẫn văn bản cấp cao (TT hướng dẫn NĐ, NĐ hướng dẫn LQ)
# - CITES: điều khoản liền kề trong cùng loại văn bản
# Dùng psycopg2 đồng bộ để tránh lỗi asyncpg connection

import re
import sys
import time
import unicodedata
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

DB_URL = "host=localhost port=5432 dbname=legal_db user=postgres password=password"

# ═══ THỨ BẬC VĂN BẢN PHÁP LÝ VIỆT NAM ═══
# Số nhỏ hơn = cấp cao hơn. Dùng để suy luận quan hệ GUIDES giữa các văn bản
TYPE_RANK = {
    "HP":   5,   # Hiến pháp — cao nhất
    "LQ":  10,   # Luật
    "NQ":  10,   # Nghị quyết Quốc hội
    "PL":  10,   # Pháp lệnh
    "ND":  20,   # Nghị định
    "QD":  30,   # Quyết định
    "TT":  30,   # Thông tư
    "CT":  30,   # Chỉ thị
    "TTLT": 30,  # Thông tư liên tịch
    "HD":  30,   # Hướng dẫn
    "CV":  40,   # Công văn — thấp nhất
}


# ═══ XOÁ DẤU TIẼNG VIỆT — dùng để so khớp doc_number ═══
def normalize(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s)
    result = "".join(c for c in nfkd if not unicodedata.combining(c)).upper()
    return result.replace("Đ", "D").replace("đ", "D")  # xử lý riêng chữ Đ


# ═══ PARSE DOC_NUMBER — trích xuất chủ đề + loại văn bản ═══
def parse_doc(dn: str):
    """Ví dụ: 'Điều 17.1.LQ.1' → {'topic': '17.1', 'vtype': 'LQ', 'rest': '1'}
    topic = chủ đề pháp luật | vtype = loại văn bản | rest = số thứ tự
    """
    if not dn:
        return None
    norm = normalize(dn)
    # Pattern: "DIEU XX.X.LOAI.SO" — chỉ parse được format chuẩn Pháp Điển
    m = re.match(r"DIEU\s+(\d+\.\d+)\.([A-Z]+)\.(.+)", norm)
    if not m:
        return None  # doc_number không đúng format → bỏ qua
    topic, vtype, rest = m.groups()
    return {"topic": topic, "vtype": vtype, "rest": rest}


def wait_for_db(conn_str: str, max_retries: int = 10) -> object:
    try:
        import psycopg2
    except ImportError:
        print("psycopg2 chua cai. Thu: pip install psycopg2-binary")
        sys.exit(1)

    for i in range(max_retries):
        try:
            conn = psycopg2.connect(conn_str)
            print(f"Ket noi DB thanh cong (lan thu {i+1})")
            return conn
        except psycopg2.OperationalError as e:
            print(f"Cho DB... ({i+1}/{max_retries}): {e}")
            time.sleep(3)
    print("Khong ket noi duoc DB sau nhieu lan thu.")
    sys.exit(1)


def main():
    conn = wait_for_db(DB_URL)
    cur = conn.cursor()

    # Lấy toàn bộ documents từ DB
    print("Dang tai documents tu DB...")
    cur.execute("SELECT id, doc_number FROM documents WHERE doc_number IS NOT NULL")
    docs = cur.fetchall()
    print(f"Tong documents: {len(docs)}")

    # Parse doc_number để lấy topic, vtype
    parsed = []
    for doc_id, doc_number in docs:
        p = parse_doc(doc_number)
        if p:
            p["id"] = str(doc_id)
            parsed.append(p)
    print(f"Parse thanh cong: {len(parsed)}/{len(docs)}")

    if not parsed:
        print("Khong parse duoc doc nao. Kiem tra format doc_number trong DB.")
        cur.close()
        conn.close()
        return

    # ── GROUP văn bản theo chủ đề, so sánh trong cùng nhóm ──
    by_topic: dict = defaultdict(list)
    for p in parsed:
        by_topic[p["topic"]].append(p)
    print(f"So chu de (topics): {len(by_topic)}")

    # ── SUŸ LUẬN QUAN HỆ TỰ CẤU TRÚC DOC_NUMBER ──
    relations = []
    seen = set()  # tránh insert trùng cặp (source, target)

    for topic, items in by_topic.items():
        by_type: dict = defaultdict(list)
        for item in items:
            by_type[item["vtype"]].append(item)

        # ─ GUIDES: văn bản cấp thấp hướng dẫn văn bản cấp cao ─
        # Ví dụ: Thông tư (rank 30) GUIDES Nghị định (rank 20) GUIDES Luật (rank 10)
        vtypes_sorted = sorted(by_type.keys(), key=lambda v: TYPE_RANK.get(v, 50))
        for i in range(len(vtypes_sorted) - 1):
            lower_type = vtypes_sorted[i]    # cấp cao hơn (rank nhỏ)
            higher_type = vtypes_sorted[i + 1]  # cấp thấp hơn (rank lớn)
            for dh in by_type[higher_type]:
                for dl in by_type[lower_type]:
                    pair = (dh["id"], dl["id"])
                    if pair not in seen:
                        seen.add(pair)
                        relations.append((dh["id"], dl["id"], "GUIDES"))

        # ─ CITES: điều khoản liền kề trong cùng loại văn bản ─
        # Giới hạn 100 cặp/loại — tránh bùng nổ số lượng quan hệ
        for vtype, st in by_type.items():
            st.sort(key=lambda x: x["rest"])
            max_cites = min(len(st) - 1, 100)
            for k in range(max_cites):
                pair = (st[k]["id"], st[k + 1]["id"])
                if pair not in seen:
                    seen.add(pair)
                    relations.append((st[k]["id"], st[k + 1]["id"], "CITES"))

    print(f"Tong quan he suy luan duoc: {len(relations):,}")

    if not relations:
        print("Khong co quan he nao. Kiem tra lai du lieu.")
        cur.close()
        conn.close()
        return

    # Xóa cũ và insert mới
    print("Dang xoa du lieu cu...")
    cur.execute("DELETE FROM document_relations")
    conn.commit()

    print(f"Dang insert {len(relations):,} quan he theo batch...")
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

    cur.execute("SELECT COUNT(*) FROM document_relations")
    total = cur.fetchone()[0]
    print(f"\nXong! {total:,} quan he trong document_relations.")
    print("Mo http://localhost:5173/knowledge-graph de xem ket qua!")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
