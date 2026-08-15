"""
Knowledge Graph Service — Build nodes/edges từ DocumentRelation
UC-09: Xem Knowledge Graph của một văn bản (depth=1 hoặc depth=2)

Output format tương thích Vis.js Network:
  {
    "nodes": [{"id": "...", "label": "...", "color": "..."}],
    "edges": [{"from": "...", "to": "...", "label": "...", "color": "..."}]
  }
"""

from uuid import UUID
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentRelation

# Màu sắc theo loại quan hệ (theo thiết kế UC-09)
RELATION_COLORS = {
    "GUIDES":     "#2196F3",   # Xanh dương — hướng dẫn thi hành
    "AMENDS":     "#FF9800",   # Cam        — sửa đổi, bổ sung
    "REPLACES":   "#9C27B0",   # Tím        — thay thế toàn bộ
    "REVOKES":    "#F44336",   # Đỏ         — bãi bỏ
    "CITES":      "#9E9E9E",   # Xám        — căn cứ theo
    "IMPLEMENTS": "#4CAF50",   # Xanh lá    — triển khai thi hành
}

# Màu node theo trạng thái
NODE_COLORS = {
    "active":  "#1976D2",   # Xanh đậm
    "expired": "#757575",   # Xám
    "amended": "#E65100",   # Cam đậm
}


async def build_graph(
    session: AsyncSession,
    root_doc_id: UUID,
    depth: int = 2,
    max_nodes: int = 150,
) -> dict:
    """
    Xây dựng Knowledge Graph từ một văn bản gốc.

    Args:
        root_doc_id: UUID văn bản trung tâm
        depth: Độ sâu (1 = các văn bản liên trực tiếp, 2 = thêm 1 bước nữa)
        max_nodes: Giới hạn tối đa nodes để tránh Vis.js chậm

    Returns:
        dict với "nodes" và "edges" theo format Vis.js
    """
    visited_ids = set()
    nodes_map = {}   # doc_id → node dict
    edges = []

    queue = [root_doc_id]
    current_depth = 0

    while queue and current_depth < depth and len(nodes_map) < max_nodes:
        next_queue = []

        # Lấy thông tin tất cả docs trong queue hiện tại
        if queue:
            result = await session.execute(
                select(Document).where(Document.id.in_(queue))
            )
            docs = {d.id: d for d in result.scalars().all()}

        for doc_id in queue:
            if doc_id in visited_ids:
                continue
            visited_ids.add(doc_id)

            doc = docs.get(doc_id)
            if not doc:
                continue

            # Thêm node
            is_root = (doc_id == root_doc_id)
            nodes_map[str(doc_id)] = {
                "id": str(doc_id),
                "label": _short_label(doc.title, doc.doc_number),
                "title": f"{doc.doc_number}\n{doc.title}",   # Tooltip
                "color": {
                    "background": "#FFD700" if is_root else NODE_COLORS.get(doc.status, "#1976D2"),
                    "border": "#F57F17" if is_root else "#0D47A1",
                },
                "size": 25 if is_root else 15,
                "font": {"size": 12 if is_root else 10},
                "doc_number": doc.doc_number,
                "status": doc.status,
                "field": doc.field,
            }

            # Lấy relations liên quan đến doc này
            rel_result = await session.execute(
                select(DocumentRelation).where(
                    or_(
                        DocumentRelation.source_doc_id == doc_id,
                        DocumentRelation.target_doc_id == doc_id,
                    )
                )
            )
            relations = rel_result.scalars().all()

            for rel in relations:
                edge_key = (str(rel.source_doc_id), str(rel.target_doc_id), rel.relation_type)
                edge = {
                    "id": str(rel.id),
                    "from": str(rel.source_doc_id),
                    "to": str(rel.target_doc_id),
                    "label": rel.relation_type,
                    "color": {"color": RELATION_COLORS.get(rel.relation_type, "#9E9E9E")},
                    "arrows": "to",
                    "title": rel.description or rel.relation_type,
                }
                if edge not in edges:
                    edges.append(edge)

                # Thêm doc liên quan vào queue tiếp theo
                other_id = rel.target_doc_id if rel.source_doc_id == doc_id else rel.source_doc_id
                if other_id not in visited_ids and len(nodes_map) < max_nodes:
                    next_queue.append(other_id)

        queue = list(set(next_queue))
        current_depth += 1

    return {
        "root_doc_id": str(root_doc_id),
        "nodes": list(nodes_map.values()),
        "edges": edges,
        "stats": {
            "node_count": len(nodes_map),
            "edge_count": len(edges),
            "depth": current_depth,
        }
    }


def _short_label(title: str, doc_number: str) -> str:
    """Rút gọn nhãn node cho Vis.js (tối đa 40 ký tự)."""
    label = doc_number or title
    return label[:40] + "..." if len(label) > 40 else label
