"""Initial migration

Revision ID: 150d29399618
Revises: 
Create Date: 2025-10-18 17:10:14.897200

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '150d29399618'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=200), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create tokens table
    op.create_table('tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.UUID(), nullable=True),
        sa.Column('creation_time', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tokens_id'), 'tokens', ['id'], unique=False)

    # Create halls table
    op.create_table('halls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('rows', sa.Integer(), nullable=False),
        sa.Column('seats_per_row', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_halls_id'), 'halls', ['id'], unique=False)
    op.create_index(op.f('ix_halls_name'), 'halls', ['name'], unique=True)

    # Create films table
    op.create_table('films',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=False),
        sa.Column('poster_url', sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_films_id'), 'films', ['id'], unique=False)

    # Create seances table
    op.create_table('seances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hall_id', sa.Integer(), nullable=False),
        sa.Column('film_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('price_standard', sa.Float(), nullable=False),
        sa.Column('price_vip', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['film_id'], ['films.id'], ),
        sa.ForeignKeyConstraint(['hall_id'], ['halls.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_seances_id'), 'seances', ['id'], unique=False)

    # Create seats table
    op.create_table('seats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hall_id', sa.Integer(), nullable=False),
        sa.Column('row_number', sa.Integer(), nullable=False),
        sa.Column('seat_number', sa.Integer(), nullable=False),
        sa.Column('seat_type', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['hall_id'], ['halls.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_seats_id'), 'seats', ['id'], unique=False)

    # Create tickets table
    op.create_table('tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('seance_id', sa.Integer(), nullable=False),
        sa.Column('seat_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('user_name', sa.String(length=100), nullable=True),
        sa.Column('user_phone', sa.String(length=20), nullable=True),
        sa.Column('user_email', sa.String(length=100), nullable=True),
        sa.Column('booked', sa.Boolean(), nullable=True),
        sa.Column('booking_code', sa.String(length=50), nullable=True),
        sa.Column('qr_code_data', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['seat_id'], ['seats.id'], ),
        sa.ForeignKeyConstraint(['seance_id'], ['seances.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tickets_id'), 'tickets', ['id'], unique=False)
    op.create_index(op.f('ix_tickets_booking_code'), 'tickets', ['booking_code'], unique=True)

    # Create prices table
    op.create_table('prices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('seat_type', sa.String(length=20), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_prices_id'), 'prices', ['id'], unique=False)
    op.create_index(op.f('ix_prices_seat_type'), 'prices', ['seat_type'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('prices')
    op.drop_table('tickets')
    op.drop_table('seats')
    op.drop_table('seances')
    op.drop_table('films')
    op.drop_table('halls')
    op.drop_table('tokens')
    op.drop_table('users')
