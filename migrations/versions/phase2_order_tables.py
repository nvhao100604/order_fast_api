"""phase2 order_tables junction table

Revision ID: phase2_order_tables
Revises: 9999_area_layout_upgrade
Create Date: 2026-10-08
"""
from alembic import op
import sqlalchemy as sa

revision = 'phase2_order_tables'
down_revision = '9999_area_layout_upgrade'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'order_tables',
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('table_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['table_id'], ['tables.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('order_id', 'table_id'),
    )
    # Backfill: copy existing orders.table_id into order_tables
    op.execute("""
        INSERT INTO order_tables (order_id, table_id)
        SELECT id, table_id FROM orders
        WHERE table_id IS NOT NULL
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    op.drop_table('order_tables')
