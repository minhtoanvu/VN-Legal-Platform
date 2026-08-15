"""fix_query_logs_add_response_duration

Revision ID: f794d49e846e
Revises: ebcecd945d00
Create Date: 2026-08-10

Theo PhanTichHeThong_v2_Fixed.docx mục 10.4:
  query_logs phải có:
    - response    JSONB    -- lưu câu trả lời AI + sources để RAG Evaluation
    - duration_ms INTEGER  -- thời gian xử lý (ms) để đo hiệu năng
  Đổi tên response_time_ms → duration_ms cho đúng tài liệu thiết kế.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f794d49e846e'
down_revision: Union[str, None] = 'ebcecd945d00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Thêm cột response JSONB (câu trả lời AI + citations để RAG Evaluation)
    op.add_column('query_logs',
        sa.Column('response', sa.JSON(), nullable=True)
    )
    # Đổi tên response_time_ms → duration_ms (theo đúng thiết kế)
    op.alter_column('query_logs', 'response_time_ms',
        new_column_name='duration_ms'
    )


def downgrade() -> None:
    op.alter_column('query_logs', 'duration_ms',
        new_column_name='response_time_ms'
    )
    op.drop_column('query_logs', 'response')
