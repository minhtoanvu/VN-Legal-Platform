"""Add search_vector to documents

Revision ID: c59dc66e73da
Revises: f794d49e846e
Create Date: 2026-08-13 10:27:47.711768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c59dc66e73da'
down_revision: Union[str, None] = 'f794d49e846e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add search_vector column
    op.add_column('documents', sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True))
    
    # Enable unaccent extension
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")
    
    # Create GIN index
    op.execute("CREATE INDEX idx_documents_search_vector ON documents USING GIN (search_vector);")
    
    # Create trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION documents_tsvector_trigger() RETURNS trigger AS $$
        begin
          new.search_vector :=
             to_tsvector('simple', unaccent(coalesce(new.title, '') || ' ' || coalesce(new.content, '')));
          return new;
        end
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger
    op.execute("""
        CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
        ON documents FOR EACH ROW EXECUTE FUNCTION documents_tsvector_trigger();
    """)
    
    # Populate existing rows
    op.execute("""
        UPDATE documents SET search_vector = to_tsvector('simple', unaccent(coalesce(title, '') || ' ' || coalesce(content, '')));
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS tsvectorupdate ON documents;")
    op.execute("DROP FUNCTION IF EXISTS documents_tsvector_trigger();")
    op.execute("DROP INDEX IF EXISTS idx_documents_search_vector;")
    op.drop_column('documents', 'search_vector')
