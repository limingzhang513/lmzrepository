"""empty message

Revision ID: 49e81816e446
Revises: d9e8b5768925
Create Date: 2018-12-24 11:00:13.341549

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '49e81816e446'
down_revision = 'd9e8b5768925'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('result_models', sa.Column('plt_path', sa.String(length=512), nullable=True))
    op.drop_column('task_models', 'plt_path')
    op.drop_column('task_models', 'trained_path')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task_models', sa.Column('trained_path', mysql.VARCHAR(length=256), nullable=True))
    op.add_column('task_models', sa.Column('plt_path', mysql.VARCHAR(length=128), nullable=True))
    op.drop_column('result_models', 'plt_path')
    # ### end Alembic commands ###
