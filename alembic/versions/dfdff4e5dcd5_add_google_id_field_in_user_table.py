"""Add google_id field in user table

Revision ID: dfdff4e5dcd5
Revises: 6a83b7380417
Create Date: 2025-03-29 00:00:30.384716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dfdff4e5dcd5'
down_revision: Union[str, None] = '6a83b7380417'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('google_id', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'user', ['google_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_column('user', 'google_id')
    # ### end Alembic commands ###
