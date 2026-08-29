"""
Analytics Router — /analytics
UC-11: Dashboard thống kê hệ thống
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.analytics_service import get_dashboard_metrics
from app.core.dependencies import require_admin

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

🚨 **Yêu cầu Quyền:** Admin
    """,
)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    """Tổng hợp metrics cho Dashboard UI."""
    return await get_dashboard_metrics(db)
