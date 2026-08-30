"""
Analytics Router — /analytics
UC-11: Dashboard thống kê hệ thống
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.analytics_service import get_dashboard_metrics
from app.core.dependencies import get_current_user

router = APIRouter()


@router.get(
    "/dashboard",
    summary="Dashboard thống kê (UC-11)",
    description="""
Trả về 5 aggregation metrics cho Dashboard:
1. **documents_by_field** — Phân bổ theo lĩnh vực (Pie Chart)
2. **documents_by_type** — Phân bổ theo loại văn bản (Bar Chart)
3. **documents_by_status** — active/expired/amended (Donut Chart)
4. **documents_by_year** — Văn bản ban hành theo năm (Line Chart)
5. **top_query_types** — Loại truy vấn phổ biến nhất (Bar Chart)

🚨 **Yêu cầu Quyền:** Mọi User đã đăng nhập
    """,
)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Tổng hợp metrics cho Dashboard UI."""
    return await get_dashboard_metrics(db)


@router.get(
    "/advanced",
    summary="Data Mining Nâng cao (UC-11 mở rộng)",
    description="""
Trả về các phân tích chuyên sâu:
1. **PageRank**: Top 10 văn bản rễ
2. **Louvain**: Top 5 cụm cộng đồng (Community Detection)
3. **Heatmap Calendar**: Lịch sử ban hành theo tháng/năm
    """,
)
async def get_advanced_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Tổng hợp các chỉ số Data Mining nâng cao."""
    from app.services.analytics_service import get_advanced_analytics
    return await get_advanced_analytics(db)
