"""add_location_radius_to_resumes

Revision ID: c12529f517cb
Revises: 6b635902536e
Create Date: 2025-06-22 16:19:23.197954

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c12529f517cb'
down_revision: Union[str, None] = '6b635902536e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add location and radius columns to resumes table."""
    op.add_column('resumes', sa.Column('location', sa.String(), nullable=True))
    op.add_column('resumes', sa.Column('radius', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema - remove location and radius columns from resumes table."""
    op.drop_column('resumes', 'radius')
    op.drop_column('resumes', 'location')
