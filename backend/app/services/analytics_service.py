"""
Analytics Service — Aggregation queries cho Dashboard
UC-11: Dashboard thống kê hệ thống

5 metrics theo PhanTichHeThong_v2_Fixed.docx:
  1. documents_by_field    — Phân bổ theo lĩnh vực (Pie Chart)
  2. documents_by_type     — Phân bổ theo loại VB (Bar Chart)
  3. documents_by_status   — active/expired/amended (Donut Chart)
  4. documents_by_year     — Văn bản ban hành theo năm (Line Chart)
  5. top_queried_fields    — Lĩnh vực được tìm kiếm nhiều nhất (Bar Chart)
"""

from sqlalchemy import text, func, extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.workspace import QueryLog


async def get_dashboard_metrics(session: AsyncSession) -> dict:
    """Tổng hợp 5 metrics cho Dashboard."""

    # 1. Phân bổ theo lĩnh vực
    r1 = await session.execute(
        select(Document.field, func.count().label("count"))
        .where(Document.field != None)
        .group_by(Document.field)
        .order_by(func.count().desc())
        .limit(10)
    )
    documents_by_field = [{"field": row.field, "count": row.count} for row in r1]

    # 2. Phân bổ theo loại văn bản
    r2 = await session.execute(
        select(Document.doc_type, func.count().label("count"))
        .where(Document.doc_type != None)
        .group_by(Document.doc_type)
        .order_by(func.count().desc())
        .limit(10)
    )
    documents_by_type = [{"doc_type": row.doc_type, "count": row.count} for row in r2]

    # 3. Phân bổ theo trạng thái
    r3 = await session.execute(
        select(Document.status, func.count().label("count"))
        .group_by(Document.status)
    )
    documents_by_status = [{"status": row.status, "count": row.count} for row in r3]

    # 4. Văn bản theo năm ban hành (10 năm gần nhất)
    r4 = await session.execute(
        select(
            extract("year", Document.issue_date).label("year"),
            func.count().label("count")
        )
        .where(Document.issue_date != None)
        .group_by("year")
        .order_by("year")
        .limit(20)
    )
    documents_by_year = [
        {"year": int(row.year), "count": row.count}
        for row in r4 if row.year
    ]

    # 5. Top lĩnh vực được truy vấn nhiều nhất (từ query_logs)
    r5 = await session.execute(
        select(QueryLog.query_type, func.count().label("count"))
        .where(QueryLog.query_type != None)
        .group_by(QueryLog.query_type)
        .order_by(func.count().desc())
        .limit(5)
    )
    top_query_types = [{"query_type": row.query_type, "count": row.count} for row in r5]

    # KPI tổng quan
    total_docs = await session.execute(select(func.count()).select_from(Document))
    total_queries = await session.execute(select(func.count()).select_from(QueryLog))
    
    # KPI mới trong 30 ngày
    docs_30d_query = await session.execute(
        select(func.count()).select_from(Document).where(Document.created_at >= text("NOW() - INTERVAL '30 days'"))
    )
    docs_30d = docs_30d_query.scalar() or 0
    
    # 6. Top cơ quan ban hành
    r6 = await session.execute(
        select(Document.issuing_body, func.count().label("count"))
        .where(Document.issuing_body != None)
        .group_by(Document.issuing_body)
        .order_by(func.count().desc())
        .limit(10)
    )
    top_issuing_bodies = [{"issuing_body": row.issuing_body, "count": row.count} for row in r6]

    return {
        "kpi": {
            "total_documents": total_docs.scalar() or 0,
            "total_queries": total_queries.scalar() or 0,
            "new_docs_30d": docs_30d,
        },
        "documents_by_field": documents_by_field,
        "documents_by_type": documents_by_type,
        "documents_by_status": documents_by_status,
        "documents_by_year": documents_by_year,
        "top_query_types": top_query_types,
        "top_issuing_bodies": top_issuing_bodies,
    }
