import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('d:\\NCKH\\backend\\data\\raw\\main_dataset.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
print("Dang tim kiem BLLD 2019 trong file JSON phapdien...")
for r in data:
    source_note = str(r.get('source_note_text', ''))
    if '45/2019' in source_note:
        if count == 0:
            print(f"-> TIM THAY! Vi du:")
            print(f"   Tieu de: {r.get('article_title')}")
            print(f"   Ghi chu nguon: {source_note[:100]}...")
            print(f"   Noi dung: {r.get('content_text', '')[:100]}...\n")
        count += 1

print(f"Tong cong co {count} dieu luat thuoc Bo luat Lao dong 2019 (45/2019/QH14) trong file JSON.")
