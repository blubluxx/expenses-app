"""Fix updated_at timestamp arg final

Revision ID: 645abe72bd83
Revises: 2ed25376bb28
Create Date: 2025-01-20 16:03:50.149679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '645abe72bd83'
down_revision: Union[str, None] = '2ed25376bb28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
