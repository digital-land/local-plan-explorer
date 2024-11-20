"""add lds published date to local plan

Revision ID: df8fe8c2526a
Revises: 07b7215fc0c9
Create Date: 2024-11-19 12:09:26.014961

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df8fe8c2526a'
down_revision = '07b7215fc0c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('local_plan', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lds_published_date', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('local_plan', schema=None) as batch_op:
        batch_op.drop_column('lds_published_date')

    # ### end Alembic commands ###