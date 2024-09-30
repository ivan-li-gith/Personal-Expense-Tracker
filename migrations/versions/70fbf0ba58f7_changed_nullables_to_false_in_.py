"""changed nullables to false in investment history db

Revision ID: 70fbf0ba58f7
Revises: 4e0da66d6be1
Create Date: 2024-09-30 01:23:21.658540

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70fbf0ba58f7'
down_revision = '4e0da66d6be1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('investment__history', schema=None) as batch_op:
        batch_op.alter_column('date',
               existing_type=sa.DATE(),
               nullable=False)
        batch_op.alter_column('eod_initial_investment',
               existing_type=sa.FLOAT(),
               nullable=False)
        batch_op.alter_column('eod_investment',
               existing_type=sa.FLOAT(),
               nullable=False)
        batch_op.alter_column('percent_diff',
               existing_type=sa.FLOAT(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('investment__history', schema=None) as batch_op:
        batch_op.alter_column('percent_diff',
               existing_type=sa.FLOAT(),
               nullable=True)
        batch_op.alter_column('eod_investment',
               existing_type=sa.FLOAT(),
               nullable=True)
        batch_op.alter_column('eod_initial_investment',
               existing_type=sa.FLOAT(),
               nullable=True)
        batch_op.alter_column('date',
               existing_type=sa.DATE(),
               nullable=True)

    # ### end Alembic commands ###
