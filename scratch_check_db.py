import asyncio
import asyncpg
import sys

async def check_db():
    with open('d:\\NCKH\\db_check_result.txt', 'w', encoding='utf-8') as f:
        f.write("Ket noi den CSDL...\n")
        conn = await asyncpg.connect('postgresql://postgres:password@localhost:5432/legal_db')
        
        f.write("\n1. Kiem tra so luong documents theo field:\n")
        records = await conn.fetch("SELECT field, COUNT(*) FROM documents GROUP BY field")
        for r in records:
            f.write(f"  - {r['field']}: {r['count']}\n")

        f.write("\n2. Kiem tra nam ban hanh cua field 'labor':\n")
        res = await conn.fetchrow("SELECT MIN(issue_date), MAX(issue_date) FROM documents WHERE field ILIKE '%lab%' OR field ILIKE '%lao%'")
        if res and res['min']:
            f.write(f"  - Tu {res['min']} den {res['max']}\n")
        else:
            f.write("  - Khong co data issue_date\n")

        f.write("\n3. Kiem tra Bo luat Lao dong 2019:\n")
        # So hieu cua Bo luat Lao dong 2019 la 45/2019/QH14 hoac luat lao dong 2019
        labor_2019 = await conn.fetch("""
            SELECT doc_number, title, issue_date 
            FROM documents 
            WHERE title ILIKE '%Lao động%' AND issue_date >= '2019-01-01'
            ORDER BY issue_date DESC
            LIMIT 10
        """)
        if labor_2019:
            for r in labor_2019:
                f.write(f"  - {r['doc_number']}: {r['title']} ({r['issue_date']})\n")
        else:
            f.write("  - Khong tim thay\n")
            
        f.write("\n4. Bo luat 45/2019 cu the:\n")
        specific = await conn.fetch("""
            SELECT doc_number, title, issue_date FROM documents WHERE doc_number ILIKE '%45/2019%'
        """)
        if specific:
            for r in specific:
                f.write(f"  - {r['doc_number']}: {r['title']} ({r['issue_date']})\n")
        else:
            f.write("  - Khong thay so 45/2019\n")

        await conn.close()
        f.write("\nXong.\n")

if __name__ == '__main__':
    asyncio.run(check_db())
