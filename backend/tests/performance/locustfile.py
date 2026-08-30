from locust import HttpUser, task, between
import random
import uuid

class LegalPlatformUser(HttpUser):
    # Thời gian chờ ngẫu nhiên giữa các tác vụ (từ 1 đến 3 giây) để mô phỏng người dùng thật
    wait_time = between(1, 3)
    
    def on_start(self):
        """Khởi chạy trước khi bắt đầu bài test: Mô phỏng quá trình Đăng nhập"""
        # Tạo thông tin user ảo cho bài test
        self.email = f"locust_{uuid.uuid4().hex[:8]}@example.com"
        self.password = "LoadTest123!"
        
        # 1. Đăng ký tài khoản ảo
        self.client.post("/auth/register", json={
            "email": self.email,
            "password": self.password,
            "full_name": "Locust Tester"
        })
        
        # 2. Đăng nhập lấy Token
        response = self.client.post("/auth/login", json={
            "email": self.email,
            "password": self.password
        })
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            # Thiết lập Token vào Header mặc định cho mọi Request tiếp theo
            self.client.headers.update({"Authorization": f"Bearer {token}"})
        else:
            print(f"Login Failed! Status: {response.status_code}, Body: {response.text}")

    @task(3)
    def view_documents(self):
        """Tác vụ thường xuyên: Xem danh sách văn bản và click vào 1 văn bản"""
        # Lấy danh sách văn bản (Mô phỏng lướt trang chủ)
        resp = self.client.get("/documents?limit=20")
        
        if resp.status_code == 200:
            docs = resp.json()
            if docs:
                # Ngẫu nhiên chọn 1 văn bản để xem chi tiết
                doc_id = random.choice(docs)["id"]
                self.client.get(f"/documents/{doc_id}")

    @task(2)
    def search_documents(self):
        """Tác vụ phổ biến thứ 2: Tìm kiếm văn bản"""
        keywords = ["Luật", "Đất đai", "Doanh nghiệp", "Thuế", "Nghị định"]
        query = random.choice(keywords)
        self.client.get(f"/search?query={query}")

    @task(1)
    def create_and_view_workspace(self):
        """Tác vụ ít hơn: Vào Workspace xem bộ sưu tập"""
        self.client.get("/workspace/collections")
