"""empty message

Revision ID: 172f0ae5a54b
Revises: 4685c35ff1d3
Create Date: 2022-04-16 20:15:22.870313

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '172f0ae5a54b'
down_revision = '4685c35ff1d3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('display_currency', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'currency', ['display_currency'], ['id'])

    with op.batch_alter_table('seller', schema=None) as batch_op:
        batch_op.add_column(sa.Column('display_currency', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'currency', ['display_currency'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('seller', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('display_currency')

    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('display_currency')

    # ### end Alembic commands ###
