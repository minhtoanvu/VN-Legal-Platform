import json
from collections import Counter

with open('backend/data/raw/main_dataset.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

out = []
out.append(f"TONG SO RECORDS: {len(data)}")

# Check fields in first record
out.append(f"\nCAC TRUONG DU LIEU (keys):")
out.append(str(list(data[0].keys())))

# Topic distribution
out.append(f"\nPHAN BO THEO TOPIC (top 20):")
topics = Counter(r.get('topic_title_vi', r.get('field', 'N/A')) for r in data)
for t, c in topics.most_common(20):
    out.append(f"  {c:5d}  {t}")

# Source URL sample
out.append(f"\nMOT SO SOURCE_URL:")
urls = set(r.get('source_url','')[:50] for r in data[:20] if r.get('source_url'))
for u in list(urls)[:5]:
    out.append(f"  {u}")

# Check for BLLD 2019
out.append(f"\nKIEM TRA BO LUAT LAO DONG 2019 (45/2019/QH14):")
blld = [r for r in data if '45/2019' in str(r.get('source_note_text','')) or 'Lao động' in str(r.get('topic_title_vi',''))]
out.append(f"  Records lien quan lao dong: {len(blld)}")

# Sample record
out.append(f"\nMOT RECORD MAU (record[0]):")
r0 = data[0]
for k, v in r0.items():
    val = str(v)[:120] if v else 'NULL'
    out.append(f"  {k}: {val}")

# Date range
dates = [r.get('issue_date','') or r.get('created_at','') for r in data if r.get('issue_date') or r.get('created_at')]
dates = sorted([d for d in dates if d])
if dates:
    out.append(f"\nDAI THOI GIAN: {dates[0]} -> {dates[-1]}")

# Content quality check
has_content = sum(1 for r in data if r.get('content_text') and len(r.get('content_text','')) > 50)
out.append(f"\nRECORDS CO CONTENT (>50 ky tu): {has_content}/{len(data)}")
avg_len = sum(len(r.get('content_text','')) for r in data) / len(data)
out.append(f"DO DAI CONTENT TRUNG BINH: {avg_len:.0f} ky tu")

with open('phapdien_check.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print("Xong! Xem file phapdien_check.txt")
