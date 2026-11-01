"""phase5 idempotency records table

Revision ID: phase5_idempotency_records
Revises: phase3_reservation_tables
Create Date: 2026-10-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'phase5_idempotency_records'
down_revision = 'phase3_reservation_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    enum_type = sa.Enum('PENDING', 'SUCCESS', 'FAILED', name='idempotency_status_enum')
    enum_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'idempotency_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('key', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('request_path', sa.String(length=128), nullable=False),
        sa.Column('request_hash', sa.String(length=64), nullable=False),
        sa.Column('status', enum_type, server_default='PENDING', nullable=False),
        sa.Column('response_code', sa.Integer(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_idempotency_records_key'), 'idempotency_records', ['key'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_idempotency_records_key'), table_name='idempotency_records')
    op.drop_table('idempotency_records')
    sa.Enum(name='idempotency_status_enum').drop(op.get_bind(), checkfirst=True)
