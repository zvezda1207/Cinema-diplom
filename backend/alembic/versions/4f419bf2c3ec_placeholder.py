"""placeholder to restore missing revision

Revision ID: 4f419bf2c3ec
Revises: 150d29399618
Create Date: 2025-11-13 13:10:00

"""
from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401


# revision identifiers, used by Alembic.
revision = "4f419bf2c3ec"
down_revision = "150d29399618"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op upgrade to keep history consistent."""
    pass


def downgrade() -> None:
    """No-op downgrade matching upgrade."""
    pass


