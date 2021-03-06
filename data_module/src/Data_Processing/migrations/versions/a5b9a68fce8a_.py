"""empty message

Revision ID: a5b9a68fce8a
Revises: 
Create Date: 2019-08-20 15:09:01.612000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a5b9a68fce8a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ds_shares',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('my_share', sa.String(length=128), nullable=True),
    sa.Column('share_collection', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('default', sa.Boolean(), nullable=True),
    sa.Column('permissions', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_roles_default'), 'roles', ['default'], unique=False)
    op.create_table('ds_users',
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('shares_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('login_time', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.ForeignKeyConstraint(['shares_id'], ['ds_shares.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_ds_users_email'), 'ds_users', ['email'], unique=True)
    op.create_table('ds_collections',
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('type', sa.Integer(), nullable=True),
    sa.Column('desc', sa.String(length=128), nullable=True),
    sa.Column('parameter_1', sa.String(length=32), nullable=True),
    sa.Column('parameter_2', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['ds_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ds_labels',
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('collection_id', sa.Integer(), nullable=True),
    sa.Column('label_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['collection_id'], ['ds_collections.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ds_versions',
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('collection_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('zip_path', sa.String(length=64), nullable=True),
    sa.Column('average_number', sa.Integer(), nullable=True),
    sa.Column('mean_size', sa.String(length=16), nullable=True),
    sa.Column('label_info', sa.String(length=512), nullable=True),
    sa.ForeignKeyConstraint(['collection_id'], ['ds_collections.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ds_images',
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('update_time', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('version_id', sa.Integer(), nullable=True),
    sa.Column('collection_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('site', sa.String(length=128), nullable=False),
    sa.Column('label_path', sa.String(length=128), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('structured_path', sa.String(length=128), nullable=True),
    sa.Column('md5', sa.String(length=32), nullable=True),
    sa.ForeignKeyConstraint(['collection_id'], ['ds_collections.id'], ),
    sa.ForeignKeyConstraint(['version_id'], ['ds_versions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ds_images_md5'), 'ds_images', ['md5'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_ds_images_md5'), table_name='ds_images')
    op.drop_table('ds_images')
    op.drop_table('ds_versions')
    op.drop_table('ds_labels')
    op.drop_table('ds_collections')
    op.drop_index(op.f('ix_ds_users_email'), table_name='ds_users')
    op.drop_table('ds_users')
    op.drop_index(op.f('ix_roles_default'), table_name='roles')
    op.drop_table('roles')
    op.drop_table('ds_shares')
    # ### end Alembic commands ###
