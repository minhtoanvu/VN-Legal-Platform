"""
Knowledge Graph Router — /graph
UC-09: Xem Knowledge Graph của một văn bản
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.document import Document
from app.services.graph_service import build_graph

router = APIRouter()


@router.get(
    "/{doc_id}",
    summary="Knowledge Graph của văn bản (UC-09)",
    description="""
Trả về đồ thị quan hệ văn bản pháp luật, tương thích Vis.js Network.

**Màu sắc edges:**
- 🔵 Xanh dương `#2196F3` — GUIDES (hướng dẫn thi hành)
- 🟠 Cam `#FF9800` — AMENDS (sửa đổi, bổ sung)
- 🟣 Tím `#9C27B0` — REPLACES (thay thế toàn bộ)
- 🔴 Đỏ `#F44336` — REVOKES (bãi bỏ)
- ⚫ Xám `#9E9E9E` — CITES (căn cứ theo)
- 🟢 Xanh lá `#4CAF50` — IMPLEMENTS (triển khai thi hành)
    """,
)
async def get_knowledge_graph(
    doc_id: UUID,
    depth: int = Query(default=2, ge=1, le=3, description="Độ sâu (1-3, mặc định 2)"),
    db: AsyncSession = Depends(get_db),
):
    """Xây dựng và trả về Knowledge Graph theo format Vis.js."""
    # Kiểm tra doc tồn tại
    result = await db.execute(select(Document.id).where(Document.id == doc_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy văn bản.")

    graph = await build_graph(session=db, root_doc_id=doc_id, depth=depth)
    return graph
