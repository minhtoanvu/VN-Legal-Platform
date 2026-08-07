"""
Models cho văn bản pháp lý.

Bảng:
- documents         : Metadata văn bản pháp luật
- document_chunks   : Đoạn văn bản + vector embedding (RAG)
- document_relations: Quan hệ giữa các văn bản (Knowledge Graph)
"""

import uuid
from datetime import date, datetime, timezone
from typing import List, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    UUID,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    doc_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    doc_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # Luật / Nghị định / Thông tư / Quyết định / Công văn
    issuing_body: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    field: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True
    )  # labor / tax / enterprise / ...
    issue_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expired_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True
    )  # NULL = còn hiệu lực
    status: Mapped[str] = mapped_column(
        String(20), default="active", index=True
    )  # active / expired / amended
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    chunks: Mapped[List["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )
    source_relations: Mapped[List["DocumentRelation"]] = relationship(
        "DocumentRelation",
        foreign_keys="DocumentRelation.source_doc_id",
        back_populates="source_document",
    )
    target_relations: Mapped[List["DocumentRelation"]] = relationship(
        "DocumentRelation",
        foreign_keys="DocumentRelation.target_doc_id",
        back_populates="target_document",
    )

    def __repr__(self) -> str:
        return f"<Document {self.doc_number}: {self.title[:50]}>"


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content_chunk: Mapped[str] = mapped_column(Text, nullable=False)
    # Vector 768D — output của bkai-foundation-models/vietnamese-bi-encoder
    embedding: Mapped[Optional[list]] = mapped_column(Vector(768), nullable=True)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")

    __table_args__ = (
        # HNSW index cho Cosine Similarity — tốt hơn IVFFlat cho production
        # Tạo bằng Alembic migration sau khi insert dữ liệu xong
        # (Không tạo ở đây vì cần dữ liệu đủ mới hiệu quả)
        Index("idx_chunks_document_id", "document_id"),
    )

    def __repr__(self) -> str:
        return f"<Chunk doc={self.document_id} idx={self.chunk_index}>"


class DocumentRelation(Base):
    """
    Quan hệ giữa các văn bản — dữ liệu nền cho Knowledge Graph.

    Loại quan hệ:
    - GUIDES     : Văn bản A hướng dẫn thi hành văn bản B
    - AMENDS     : Văn bản A sửa đổi, bổ sung văn bản B
    - REPLACES   : Văn bản A thay thế toàn bộ văn bản B
    - REVOKES    : Văn bản A bãi bỏ văn bản B
    - CITES      : Văn bản A căn cứ theo văn bản B
    - IMPLEMENTS : Văn bản A triển khai thi hành văn bản B
    """

    __tablename__ = "document_relations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_doc_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    target_doc_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    source_document: Mapped["Document"] = relationship(
        "Document", foreign_keys=[source_doc_id], back_populates="source_relations"
    )
    target_document: Mapped["Document"] = relationship(
        "Document", foreign_keys=[target_doc_id], back_populates="target_relations"
    )

    __table_args__ = (
        UniqueConstraint("source_doc_id", "target_doc_id", "relation_type", name="uq_doc_relation"),
        Index("idx_relation_source", "source_doc_id"),
        Index("idx_relation_target", "target_doc_id"),
    )

    def __repr__(self) -> str:
        return f"<Relation {self.source_doc_id} --{self.relation_type}--> {self.target_doc_id}>"
