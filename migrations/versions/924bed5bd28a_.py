"""empty message

Revision ID: 924bed5bd28a
Revises: 
Create Date: 2019-06-25 22:41:03.746644

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '924bed5bd28a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subject',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('classITA', sa.String(length=20), nullable=False),
    sa.Column('lim_abs', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('absence',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('subject_id', sa.Integer(), nullable=False),
    sa.Column('abs', sa.Float(), nullable=False),
    sa.Column('just', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rating_elective_subject',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subjectId', sa.Integer(), nullable=True),
    sa.Column('raterId', sa.Integer(), nullable=True),
    sa.Column('anonymous', sa.Boolean(), nullable=False),
    sa.Column('courseware', sa.Integer(), nullable=False),
    sa.Column('teacherRate', sa.Integer(), nullable=False),
    sa.Column('evaluationMethod', sa.Integer(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['raterId'], ['user.id'], ),
    sa.ForeignKeyConstraint(['subjectId'], ['subject.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subject-student association',
    sa.Column('subjectId', sa.Integer(), nullable=True),
    sa.Column('studentId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['studentId'], ['user.id'], ),
    sa.ForeignKeyConstraint(['subjectId'], ['subject.id'], )
    )
    op.create_table('subject-teacher association',
    sa.Column('subjectId', sa.Integer(), nullable=True),
    sa.Column('teacherId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['subjectId'], ['subject.id'], ),
    sa.ForeignKeyConstraint(['teacherId'], ['teacher.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subject-teacher association')
    op.drop_table('subject-student association')
    op.drop_table('rating_elective_subject')
    op.drop_table('absence')
    op.drop_table('subject')
    # ### end Alembic commands ###
