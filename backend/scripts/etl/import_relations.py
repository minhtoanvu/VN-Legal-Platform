import asyncio, sys, unicodedata
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'): sys.stderr.reconfigure(encoding='utf-8')

RELATION_MAP = {
    'can cu': 'CITES', 'huong dan thi hanh': 'GUIDES', 'huong dan': 'GUIDES',
    'thay the': 'REPLACES', 'sua doi, bo sung': 'AMENDS', 'sua doi': 'AMENDS',
    'bo sung': 'AMENDS', 'bai bo': 'REVOKES', 'dinh chi': 'REVOKES',
    'trien khai': 'IMPLEMENTS',
}

def remove_accents(s):
    nfkd = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in nfkd if not unicodedata.combining(c)).lower()

def normalize_relation(rel_str):
    if not rel_str: return 'CITES'
    low = remove_accents(rel_str.strip())
    for key, val in RELATION_MAP.items():
        if key in low: return val
    return 'CITES'

async def import_relations():
    from datasets import load_dataset
    from sqlalchemy import text
    sys.path.insert(0, '.')
    from app.core.database import AsyncSessionLocal

    print('Loading metadata...')
    ds_meta = load_dataset('th1nhng0/vietnamese-legal-documents', 'metadata', split='data', streaming=True)
    id_to_sokyhieu = {}
    for row in ds_meta:
        raw_id = row.get('id')
        ky_hieu = row.get('so_ky_hieu')
        if raw_id is not None and ky_hieu:
            id_to_sokyhieu[str(raw_id)] = ky_hieu.strip()
    print(f'Metadata: {len(id_to_sokyhieu)} records. Sample: {list(id_to_sokyhieu.items())[:3]}')

    print('Loading relationships...')
    ds_rel = load_dataset('th1nhng0/vietnamese-legal-documents', 'relationships', split='data', streaming=True)
    raw_relations, seen = [], set()
    for row in ds_rel:
        src_id = str(row.get('doc_id', '')) if row.get('doc_id') is not None else ''
        tgt_id = str(row.get('other_doc_id', '')) if row.get('other_doc_id') is not None else ''
        src_ky = id_to_sokyhieu.get(src_id)
        tgt_ky = id_to_sokyhieu.get(tgt_id)
        if not src_ky or not tgt_ky: continue
        rel_type = normalize_relation(row.get('relationship', ''))
        pair = (src_ky, tgt_ky)
        if pair not in seen:
            seen.add(pair)
            raw_relations.append((src_ky, tgt_ky, rel_type))
    print(f'Relationships: {len(raw_relations)} unique')

    async with AsyncSessionLocal() as db:
        result = await db.execute(text('SELECT id, doc_number FROM documents WHERE doc_number IS NOT NULL'))
        rows = result.fetchall()
        doc_map = {r.doc_number.strip(): r.id for r in rows}
        print(f'DB documents: {len(doc_map)}. Sample keys: {list(doc_map.keys())[:3]}')

        matched = []
        for src_ky, tgt_ky, rel_type in raw_relations:
            src_uuid = doc_map.get(src_ky)
            tgt_uuid = doc_map.get(tgt_ky)
            if src_uuid and tgt_uuid and src_uuid != tgt_uuid:
                matched.append((src_uuid, tgt_uuid, rel_type))
        print(f'Matched: {len(matched)} pairs')

        if not matched:
            print('NO MATCHES. Checking sample keys...')
            print('th1nhng0 so_ky_hieu samples:', list(id_to_sokyhieu.values())[:10])
            print('DB doc_number samples:', list(doc_map.keys())[:10])
            return

        await db.execute(text('DELETE FROM document_relations'))
        await db.commit()

        inserted = 0
        BATCH = 500
        for i in range(0, len(matched), BATCH):
            batch = matched[i:i+BATCH]
            values = ','.join(f"(gen_random_uuid(), '{src}', '{tgt}', '{rel}', NOW())" for src, tgt, rel in batch)
            await db.execute(text(f'INSERT INTO document_relations (id, source_doc_id, target_doc_id, relation_type, created_at) VALUES {values} ON CONFLICT DO NOTHING'))
            inserted += len(batch)
        await db.commit()
        print(f'DONE! Inserted {inserted} relations.')

asyncio.run(import_relations())
