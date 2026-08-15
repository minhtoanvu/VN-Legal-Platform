"""
Models cho Workspace cá nhân.

Bảng:
- collections          : Nhóm văn bản (cá nhân hoặc chia sẻ nhóm)
- collection_documents : Bảng trung gian n-n Collection ↔ Document
- notes                : Ghi chú cá nhân trên văn bản
- query_logs           : Log lịch sử hỏi AI (Analytics nội bộ)
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlalchemy import (
    UUID,
    Boolean,
    DateTime,
    ForeignKey,
    PrimaryKeyConstraint,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # is_shared=True → Enterprise: chia sẻ cho tất cả user cùng organization
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="collections")  # type: ignore[name-defined]
    document_links: Mapped[list["CollectionDocument"]] = relationship(
        "CollectionDocument", back_populates="collection", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Collection '{self.name}' owner={self.owner_id}>"


class CollectionDocument(Base):
    """Bảng trung gian n-n: Collection ↔ Document."""

    __tablename__ = "collection_documents"

    collection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("collections.id", ondelete="CASCADE"),
        nullable=False,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    collection: Mapped["Collection"] = relationship("Collection", back_populates="document_links")

    __table_args__ = (
        PrimaryKeyConstraint("collection_id", "document_id", name="pk_collection_document"),
    )


class Note(Base):
    """Ghi chú cá nhân của người dùng trên một văn bản cụ thể."""

    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notes")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return f"<Note user={self.user_id} doc={self.document_id}>"


class QueryLog(Base):
    """
    Log mỗi truy vấn tìm kiếm / hỏi AI.
    Dùng để: Analytics nội bộ, gợi ý câu hỏi phổ biến, RAG Evaluation.

    Theo PhanTichHeThong_v2_Fixed.docx mục 10.4:
      - response    JSONB    -- lưu câu trả lời AI + sources để RAG Evaluation
      - duration_ms INTEGER  -- thời gian xử lý (ms) để đo hiệu năng
    """

    __tablename__ = "query_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    # keyword / semantic / hybrid / ai_chat / summarize
    query_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # Câu trả lời AI + sources (để RAG Evaluation sau này)
    response: Mapped[Optional[dict]] = mapped_column(sa.JSON, nullable=True)
    # Thời gian xử lý (ms) để đo hiệu năng theo SLA
    duration_ms: Mapped[Optional[int]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="query_logs")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return f"<QueryLog type={self.query_type} user={self.user_id}>"

