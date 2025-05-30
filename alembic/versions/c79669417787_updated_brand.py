"""updated brand

Revision ID: c79669417787
Revises: 2e00324af513
Create Date: 2025-05-07 11:55:14.562777

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c79669417787'
down_revision: Union[str, None] = '2e00324af513'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('brand', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'brand')
    # ### end Alembic commands ###
