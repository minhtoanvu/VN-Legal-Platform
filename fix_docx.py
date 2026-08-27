"""
Script để map toàn bộ cấu trúc file ThietKeHeThong_AILIP.docx
"""
import sys
import io
import docx

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

doc = docx.Document(r'd:\NCKH\ThietKeHeThong_AILIP.docx')

for i, p in enumerate(doc.paragraphs):
    try:
        style = p.style.name if p.style else "None"
    except:
        style = "Unknown"
    text = p.text.strip()
    if text:
        print(f"[{i:03d}] [{style}] {text[:100]}")
