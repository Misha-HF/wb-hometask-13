"""Init

Revision ID: 92a45f303138
Revises: e2874c9c1ba9
Create Date: 2024-04-28 09:08:38.119392

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92a45f303138'
down_revision: Union[str, None] = 'e2874c9c1ba9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('avatar', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'avatar')
    # ### end Alembic commands ###
