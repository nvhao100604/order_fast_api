"""phase3 reservation_tables junction table

Revision ID: phase3_reservation_tables
Revises: phase2_order_tables
Create Date: 2026-10-08
"""
from alembic import op
import sqlalchemy as sa

revision = 'phase3_reservation_tables'
down_revision = 'phase2_order_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'reservation_tables',
        sa.Column('reservation_id', sa.Integer(), nullable=False),
        sa.Column('table_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['reservation_id'], ['reservations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['table_id'], ['tables.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('reservation_id', 'table_id'),
    )
    # Backfill: copy existing reservations.table_id into reservation_tables
    op.execute("""
        INSERT INTO reservation_tables (reservation_id, table_id)
        SELECT id, table_id FROM reservations
        WHERE table_id IS NOT NULL
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    op.drop_table('reservation_tables')
