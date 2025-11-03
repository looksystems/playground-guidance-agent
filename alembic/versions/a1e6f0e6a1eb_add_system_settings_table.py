"""add_system_settings_table

Revision ID: a1e6f0e6a1eb
Revises: d54d8651560e
Create Date: 2025-11-03 11:49:37.758845

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1e6f0e6a1eb'
down_revision: Union[str, Sequence[str], None] = 'd54d8651560e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create system_settings table
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Integer(), nullable=False, default=1),
        sa.Column('system_name', sa.String(length=255), nullable=False, server_default='Pension Guidance Service'),
        sa.Column('support_email', sa.String(length=255), nullable=False, server_default='support@pensionguidance.com'),
        sa.Column('session_timeout', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('fca_compliance_enabled', sa.String(length=10), nullable=False, server_default='true'),
        sa.Column('risk_assessment_required', sa.String(length=10), nullable=False, server_default='true'),
        sa.Column('auto_archive', sa.String(length=10), nullable=False, server_default='false'),
        sa.Column('email_notifications', sa.String(length=10), nullable=False, server_default='true'),
        sa.Column('compliance_alerts', sa.String(length=10), nullable=False, server_default='true'),
        sa.Column('daily_digest', sa.String(length=10), nullable=False, server_default='false'),
        sa.Column('ai_model', sa.String(length=100), nullable=False, server_default='gpt-4'),
        sa.Column('temperature', sa.Float(), nullable=False, server_default='0.7'),
        sa.Column('max_tokens', sa.Integer(), nullable=False, server_default='2000'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('session_timeout >= 1', name='settings_session_timeout_check'),
        sa.CheckConstraint('temperature >= 0.0 AND temperature <= 2.0', name='settings_temperature_check'),
        sa.CheckConstraint('max_tokens >= 1', name='settings_max_tokens_check'),
        sa.CheckConstraint('id = 1', name='settings_single_row_check'),
    )

    # Insert default settings row
    op.execute("""
        INSERT INTO system_settings (id) VALUES (1)
        ON CONFLICT (id) DO NOTHING
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('system_settings')
