import os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

from report_builder import setup_styles, add_cover
from chapter1 import add_chapter_1
from chapter2 import add_chapter_2
from chapter3 import add_chapter_3
from chapter4 import add_chapter_4
from chapter5 import add_chapter_5

def format_heading(paragraph, level=1):
    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
    for run in paragraph.runs:
        run.font.name = 'Times New Roman'
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
        if level == 1:
            run.font.size = Pt(18)
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        elif level == 2:
            run.font.size = Pt(16)
        elif level == 3:
            run.font.size = Pt(14)

def format_normal(paragraph):
    paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
    for run in paragraph.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)

def main():
    print("Start building the report...")
    
    # Khởi tạo Document
    doc = Document()
    
    # Thiết lập style (Font, Size)
    setup_styles(doc)
    
    # 0. Trang bìa
    add_cover(doc)
    print("Cover added...")
    
    # 1. Phần mở đầu & Chương 1
    add_chapter_1(doc, format_heading, format_normal)
    print("Chapter 1 added...")
    
    # 2. Chương 2
    add_chapter_2(doc, format_heading, format_normal)
    print("Chapter 2 added...")
    
    # 3. Chương 3
    add_chapter_3(doc, format_heading, format_normal)
    print("Chapter 3 added...")
    
    # 4. Chương 4
    add_chapter_4(doc, format_heading, format_normal)
    print("Chapter 4 added...")
    
    # 5. Chương 5
    add_chapter_5(doc, format_heading, format_normal)
    print("Chapter 5 added...")
    
    # Lưu file
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Bao_cao_Do_An_Nganh_Final_v3.docx")
    doc.save(output_path)
    
    print(f"Successfully saved to: {output_path}")

if __name__ == "__main__":
    main()
