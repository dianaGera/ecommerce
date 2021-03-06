"""empty message

Revision ID: 2c91248bffc1
Revises: 0df3553733ad
Create Date: 2022-04-17 14:17:47.702407

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c91248bffc1'
down_revision = '0df3553733ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('_alembic_tmp_seller')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('_alembic_tmp_seller',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('display_currency_id', sa.INTEGER(), nullable=True),
    sa.Column('email', sa.VARCHAR(length=125), nullable=False),
    sa.Column('password', sa.VARCHAR(length=125), nullable=False),
    sa.Column('role', sa.INTEGER(), nullable=False),
    sa.Column('card_id', sa.INTEGER(), nullable=True),
    sa.Column('first_name', sa.VARCHAR(length=50), nullable=True),
    sa.Column('last_name', sa.VARCHAR(length=50), nullable=True),
    sa.Column('company_name', sa.VARCHAR(length=125), nullable=False),
    sa.Column('country', sa.VARCHAR(length=125), nullable=False),
    sa.Column('phone', sa.VARCHAR(length=20), nullable=False),
    sa.Column('logo', sa.INTEGER(), nullable=True),
    sa.Column('active_discount', sa.BOOLEAN(), nullable=True),
    sa.Column('busines_type_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['busines_type_id'], ['type.id'], name='fk_seller_busines_type_id_type'),
    sa.ForeignKeyConstraint(['display_currency_id'], ['currency.id'], name='fk_seller_display_currency_id_currency'),
    sa.ForeignKeyConstraint(['logo'], ['company_logo.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email', name='uq_seller_email')
    )
    # ### end Alembic commands ###
