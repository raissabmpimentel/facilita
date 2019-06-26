"""empty message

Revision ID: c0c3a6497c31
Revises: 93021f8469f6
Create Date: 2019-06-26 12:33:24.645127

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0c3a6497c31'
down_revision = '93021f8469f6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('calendar_months',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('dateToStart', sa.Date(), nullable=False),
    sa.Column('month', sa.Integer(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('calendar_months')
    # ### end Alembic commands ###