"""Initial migration

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=200), nullable=False),
        sa.Column('role', sa.Enum('admin', 'operator', 'viewer', name='userrole'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)

    # Create cameras table
    op.create_table(
        'cameras',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('rtsp_url', sa.String(length=500), nullable=False),
        sa.Column('status', sa.Enum('online', 'offline', 'maintenance', name='camerastatus'), nullable=True),
        sa.Column('is_360', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cameras_id'), 'cameras', ['id'], unique=False)

    # Create vehicles table
    op.create_table(
        'vehicles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plate_number', sa.String(length=20), nullable=False),
        sa.Column('vehicle_type', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=30), nullable=True),
        sa.Column('owner_name', sa.String(length=100), nullable=True),
        sa.Column('owner_phone', sa.String(length=20), nullable=True),
        sa.Column('is_stolen', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('plate_number')
    )
    op.create_index(op.f('ix_vehicles_id'), 'vehicles', ['id'], unique=False)
    op.create_index(op.f('ix_vehicles_plate_number'), 'vehicles', ['plate_number'], unique=False)

    # Create plate_readings table
    op.create_table(
        'plate_readings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vehicle_id', sa.Integer(), nullable=True),
        sa.Column('camera_id', sa.Integer(), nullable=False),
        sa.Column('plate_number', sa.String(length=20), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('direction', sa.String(length=50), nullable=True),
        sa.Column('speed', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['camera_id'], ['cameras.id'], ),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_plate_readings_id'), 'plate_readings', ['id'], unique=False)

    # Create traffic_zones table
    op.create_table(
        'traffic_zones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('polygon', sa.String(length=1000), nullable=True),
        sa.Column('congestion_level', sa.Float(), nullable=True),
        sa.Column('vehicle_count', sa.Integer(), nullable=True),
        sa.Column('average_speed', sa.Float(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_traffic_zones_id'), 'traffic_zones', ['id'], unique=False)

    # Create incidents table
    op.create_table(
        'incidents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('severity', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('reported', 'confirmed', 'resolved', name='incidentstatus'), nullable=True),
        sa.Column('reported_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['reported_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incidents_id'), 'incidents', ['id'], unique=False)

    # Create traffic_metrics table
    op.create_table(
        'traffic_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('zone_id', sa.Integer(), nullable=False),
        sa.Column('vehicle_count', sa.Integer(), nullable=True),
        sa.Column('average_speed', sa.Float(), nullable=True),
        sa.Column('congestion_level', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['zone_id'], ['traffic_zones.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_traffic_metrics_id'), 'traffic_metrics', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_traffic_metrics_id'), table_name='traffic_metrics')
    op.drop_table('traffic_metrics')
    op.drop_index(op.f('ix_incidents_id'), table_name='incidents')
    op.drop_table('incidents')
    op.drop_index(op.f('ix_traffic_zones_id'), table_name='traffic_zones')
    op.drop_table('traffic_zones')
    op.drop_index(op.f('ix_plate_readings_id'), table_name='plate_readings')
    op.drop_table('plate_readings')
    op.drop_index(op.f('ix_vehicles_plate_number'), table_name='vehicles')
    op.drop_index(op.f('ix_vehicles_id'), table_name='vehicles')
    op.drop_table('vehicles')
    op.drop_index(op.f('ix_cameras_id'), table_name='cameras')
    op.drop_table('cameras')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

    op.execute("DROP TYPE IF EXISTS incidentstatus")
    op.execute("DROP TYPE IF EXISTS camerastatus")
    op.execute("DROP TYPE IF EXISTS userrole")
