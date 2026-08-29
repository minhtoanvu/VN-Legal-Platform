from locust import HttpUser, task, between
import json

class AILIPUser(HttpUser):
    # Thời gian chờ giữa các lần gửi request của một user ảo (1 - 3 giây)
    wait_time = between(1, 3)

    @task(3) # Trọng số 3: Tỉ lệ gọi keyword search nhiều gấp 3 lần semantic search
    def test_keyword_search(self):
        headers = {'Content-Type': 'application/json'}
        payload = {
            "query": "nghỉ việc",
            "mode": "keyword",
            "limit": 10
        }
        # Đánh giá xem hệ thống có sập khi gọi tìm kiếm đồng loạt không
        with self.client.post("/search", data=json.dumps(payload), headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed with status code: {response.status_code}")

    @task(1)
    def test_semantic_search(self):
        headers = {'Content-Type': 'application/json'}
        payload = {
            "query": "quy định về phụ cấp độc hại",
            "mode": "semantic",
            "limit": 5
        }
        # Vector search thường nặng CPU hơn, ta test xem Database (pgvector) chịu tải tốt không
        with self.client.post("/search", data=json.dumps(payload), headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Semantic search failed: {response.status_code}")
