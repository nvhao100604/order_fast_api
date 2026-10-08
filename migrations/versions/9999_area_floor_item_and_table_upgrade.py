"""area floor item and table upgrade

Revision ID: 9999_area_layout_upgrade
Revises: 974f9e0415b3
Create Date: 2026-10-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '9999_area_layout_upgrade'
down_revision = '974f9e0415b3'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Update Enum values outside transaction if needed, or using execute
    op.execute("ALTER TYPE tablestatus ADD VALUE IF NOT EXISTS 'PAYING'")
    op.execute("ALTER TYPE tablestatus ADD VALUE IF NOT EXISTS 'CLEANING'")

    # Create Enum types for FloorItemKind and TableShape
    flooritemkind = postgresql.ENUM('TABLE', 'PILLAR', 'BAR', 'DOOR', 'STAIRS', name='flooritemkind')
    flooritemkind.create(op.get_bind(), checkfirst=True)

    tableshape = postgresql.ENUM('SQUARE', 'ROUND', 'LONG', name='tableshape')
    tableshape.create(op.get_bind(), checkfirst=True)

    # 2. Create areas table
    op.create_table(
        'areas',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('grid_w', sa.Integer(), server_default='30', nullable=False),
        sa.Column('grid_h', sa.Integer(), server_default='20', nullable=False),
        sa.Column('layout_version', sa.Integer(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Add columns to tables
    op.add_column('tables', sa.Column('name', sa.String(length=32), nullable=True))
    op.add_column('tables', sa.Column('seats', sa.Integer(), nullable=True))
    op.add_column('tables', sa.Column('area_id', sa.Integer(), nullable=True))
    op.add_column('tables', sa.Column('cluster_key', sa.String(length=8), nullable=True))
    op.add_column('tables', sa.Column('is_fixed', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('tables', sa.Column('walk_in_only', sa.Boolean(), server_default='false', nullable=False))

    op.create_foreign_key('fk_tables_area_id', 'tables', 'areas', ['area_id'], ['id'], ondelete='SET NULL')

    # Drop old unique constraint tables_number_key if exists
    op.execute("ALTER TABLE tables DROP CONSTRAINT IF EXISTS tables_number_key")
    op.execute("DROP INDEX IF EXISTS tables_number_key")

    # Create partial unique index on tables (number) WHERE status <> 'DELETED'
    op.execute("CREATE UNIQUE INDEX idx_tables_number_active ON tables (number) WHERE status <> 'DELETED'")

    # 4. Create floor_items table
    op.create_table(
        'floor_items',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('area_id', sa.Integer(), nullable=False),
        sa.Column('table_id', sa.Integer(), nullable=True),
        sa.Column('kind', postgresql.ENUM('TABLE', 'PILLAR', 'BAR', 'DOOR', 'STAIRS', name='flooritemkind', create_type=False), nullable=False),
        sa.Column('shape', postgresql.ENUM('SQUARE', 'ROUND', 'LONG', name='tableshape', create_type=False), nullable=True),
        sa.Column('x', sa.Integer(), nullable=False),
        sa.Column('y', sa.Integer(), nullable=False),
        sa.Column('w', sa.Integer(), nullable=False),
        sa.Column('h', sa.Integer(), nullable=False),
        sa.Column('rotation', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['area_id'], ['areas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['table_id'], ['tables.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('w > 0 AND h > 0', name='check_floor_item_dimensions')
    )


    # Partial unique index on floor_items (table_id) WHERE table_id IS NOT NULL
    op.execute("CREATE UNIQUE INDEX idx_floor_items_table_unique ON floor_items (table_id) WHERE table_id IS NOT NULL")

    # 5. Data Backfill
    op.execute("UPDATE tables SET seats = LEAST(max_capacity, 10), max_capacity = LEAST(max_capacity, 10) WHERE seats IS NULL")
    op.alter_column('tables', 'seats', nullable=False)

    # Create default Area "Tầng 1"
    op.execute("INSERT INTO areas (name, grid_w, grid_h, layout_version) VALUES ('Tầng 1', 30, 20, 1) ON CONFLICT DO NOTHING")

    # Assign area_id of Tầng 1 to all tables
    op.execute("UPDATE tables SET area_id = (SELECT id FROM areas WHERE name = 'Tầng 1' LIMIT 1) WHERE area_id IS NULL AND status <> 'DELETED'")

    # Auto grid layout placement for unplaced tables
    op.execute("""
        INSERT INTO floor_items (area_id, table_id, kind, shape, x, y, w, h, rotation)
        SELECT 
            t.area_id,
            t.id,
            'TABLE'::flooritemkind,
            'SQUARE'::tableshape,
            ((row_number() OVER (ORDER BY t.number) - 1) % 5) * 3 + 1 AS x,
            ((row_number() OVER (ORDER BY t.number) - 1) / 5) * 3 + 1 AS y,
            2 AS w,
            2 AS h,
            0 AS rotation
        FROM tables t
        WHERE t.area_id IS NOT NULL AND t.status <> 'DELETED'
        ON CONFLICT DO NOTHING
    """)

    # 6. Add capacity check constraint on tables
    op.execute("""
        ALTER TABLE tables ADD CONSTRAINT check_capacity_bounds 
        CHECK (min_capacity >= 1 AND min_capacity <= seats AND seats <= max_capacity) NOT VALID
    """)
    op.execute("ALTER TABLE tables VALIDATE CONSTRAINT check_capacity_bounds")


def downgrade() -> None:
    op.execute("ALTER TABLE tables DROP CONSTRAINT IF EXISTS check_capacity_bounds")
    op.execute("DROP INDEX IF EXISTS idx_floor_items_table_unique")
    op.drop_table('floor_items')
    op.execute("DROP INDEX IF EXISTS idx_tables_number_active")
    op.drop_constraint('fk_tables_area_id', 'tables', type_='foreignkey')
    op.drop_column('tables', 'walk_in_only')
    op.drop_column('tables', 'is_fixed')
    op.drop_column('tables', 'cluster_key')
    op.drop_column('tables', 'area_id')
    op.drop_column('tables', 'seats')
    op.drop_column('tables', 'name')
    op.drop_table('areas')
    op.execute("DROP TYPE IF EXISTS tableshape")
    op.execute("DROP TYPE IF EXISTS flooritemkind")
