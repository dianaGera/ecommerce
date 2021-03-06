"""empty message

Revision ID: e32e6447feb1
Revises: d85599619b98
Create Date: 2022-04-21 23:28:37.154844

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e32e6447feb1'
down_revision = 'd85599619b98'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('seller', schema=None) as batch_op:
        batch_op.alter_column('phone',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('seller', schema=None) as batch_op:
        batch_op.alter_column('phone',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)

    # ### end Alembic commands ###
