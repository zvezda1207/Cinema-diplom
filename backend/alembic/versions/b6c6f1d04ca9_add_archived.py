"""add archived

Revision ID: b6c6f1d04ca9
Revises: 150d29399618
Create Date: 2025-11-13 12:42:38.039693

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "b6c6f1d04ca9"
down_revision = "4f419bf2c3ec"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # добавляем столбец с временным default=False, чтобы существующие записи получили False
    op.add_column(
        "tickets",
        sa.Column(
            "archived",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    # сразу убираем server_default — он больше не нужен
    op.alter_column("tickets", "archived", server_default=None)


def downgrade() -> None:
    # обратная операция: удаляем столбец
    op.drop_column("tickets", "archived")






