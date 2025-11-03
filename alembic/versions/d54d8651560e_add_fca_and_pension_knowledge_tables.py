"""add_fca_and_pension_knowledge_tables

Revision ID: d54d8651560e
Revises: a7b3073fdead
Create Date: 2025-11-01 23:21:46.436784

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector.sqlalchemy


# revision identifiers, used by Alembic.
revision: str = 'd54d8651560e'
down_revision: Union[str, Sequence[str], None] = 'a7b3073fdead'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create FCA knowledge table
    op.create_table('fca_knowledge',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=1536), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create HNSW index for FCA knowledge embeddings
    op.execute('CREATE INDEX fca_knowledge_embedding_idx ON fca_knowledge USING hnsw (embedding vector_cosine_ops)')

    # Create index for category filtering
    op.create_index('fca_knowledge_category_idx', 'fca_knowledge', ['category'])

    # Create pension knowledge table
    op.create_table('pension_knowledge',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('subcategory', sa.String(100), nullable=True),
        sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=1536), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create HNSW index for pension knowledge embeddings
    op.execute('CREATE INDEX pension_knowledge_embedding_idx ON pension_knowledge USING hnsw (embedding vector_cosine_ops)')

    # Create index for category filtering
    op.create_index('pension_knowledge_category_idx', 'pension_knowledge', ['category'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop pension knowledge table and indexes
    op.drop_index('pension_knowledge_category_idx')
    op.execute('DROP INDEX IF EXISTS pension_knowledge_embedding_idx')
    op.drop_table('pension_knowledge')

    # Drop FCA knowledge table and indexes
    op.drop_index('fca_knowledge_category_idx')
    op.execute('DROP INDEX IF EXISTS fca_knowledge_embedding_idx')
    op.drop_table('fca_knowledge')
