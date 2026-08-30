import asyncio
from app.core.database import AsyncSessionLocal
from app.services.analytics_service import get_advanced_analytics
import json

async def run_test():
    async with AsyncSessionLocal() as session:
        result = await get_advanced_analytics(session)
        with open("advanced_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("Đã lưu kết quả thành công vào advanced_result.json!")

if __name__ == "__main__":
    asyncio.run(run_test())
