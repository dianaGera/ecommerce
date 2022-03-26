"""empty message

Revision ID: c80fb7f4cb48
Revises: 5de40023a77b
Create Date: 2022-03-26 21:43:50.780186

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c80fb7f4cb48'
down_revision = '5de40023a77b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('card', schema=None) as batch_op:
        batch_op.drop_column('price')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('card', schema=None) as batch_op:
        batch_op.add_column(sa.Column('price', sa.INTEGER(), nullable=True))

    # ### end Alembic commands ###
