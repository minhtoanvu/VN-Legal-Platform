import json
import os
from pathlib import Path

RAW_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

dummy_data = [
    {
        "id": "luat_doanh_nghiep_2020",
        "title": "Luật Doanh nghiệp 2020",
        "text": "Điều 1. Phạm vi điều chỉnh. Luật này quy định về việc thành lập, tổ chức quản lý, tổ chức lại, giải thể và hoạt động có liên quan của doanh nghiệp, bao gồm công ty trách nhiệm hữu hạn, công ty cổ phần, công ty hợp danh và doanh nghiệp tư nhân.",
        "url": "https://thuvienphapluat.vn"
    },
    {
        "id": "luat_lao_dong_2019",
        "title": "Bộ luật Lao động 2019",
        "text": "Điều 15. Hợp đồng lao động. Hợp đồng lao động là sự thỏa thuận giữa người lao động và người sử dụng lao động về việc làm có trả công, tiền lương, điều kiện lao động, quyền và nghĩa vụ của mỗi bên trong quan hệ lao động.",
        "url": "https://thuvienphapluat.vn"
    },
    {
        "id": "luat_dan_su_2015",
        "title": "Bộ luật Dân sự 2015",
        "text": "Điều 468. Lãi suất. Lãi suất vay do các bên thỏa thuận. Trường hợp các bên có thỏa thuận về lãi suất thì lãi suất thỏa thuận không được vượt quá 20%/năm của khoản tiền vay.",
        "url": "https://thuvienphapluat.vn"
    },
    {
        "id": "luat_hon_nhan_2014",
        "title": "Luật Hôn nhân và Gia đình 2014",
        "text": "Điều 33. Tài sản chung của vợ chồng. Tài sản chung của vợ chồng gồm tài sản do vợ, chồng tạo ra, thu nhập do lao động, hoạt động sản xuất, kinh doanh, hoa lợi, lợi tức phát sinh từ tài sản riêng và thu nhập hợp pháp khác trong thời kỳ hôn nhân.",
        "url": "https://thuvienphapluat.vn"
    },
    {
        "id": "luat_dat_dai_2024",
        "title": "Luật Đất đai 2024",
        "text": "Sổ đỏ, sổ hồng được cấp theo quy định mới nhất. Người sử dụng đất được cấp Giấy chứng nhận quyền sử dụng đất, quyền sở hữu nhà ở và tài sản khác gắn liền với đất khi có đủ điều kiện.",
        "url": "https://thuvienphapluat.vn"
    }
]

def main():
    print("📥 Tạo dữ liệu mẫu (Mock Data) vì máy bị đầy RAM...")
    
    # Save main dataset
    main_path = RAW_DATA_DIR / "main_dataset.json"
    with open(main_path, "w", encoding="utf-8") as f:
        json.dump(dummy_data, f, ensure_ascii=False, indent=2)
    print(f"   ✅ Tạo thành công {len(dummy_data)} văn bản mẫu.")
    print(f"   💾 Lưu tại: {main_path}")
    
    # Eval dataset (not strictly needed for just running it, but we can make an empty one)
    eval_path = RAW_DATA_DIR / "eval_qa.json"
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False)

if __name__ == "__main__":
    main()
