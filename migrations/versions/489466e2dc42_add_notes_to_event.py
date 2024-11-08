"""add notes to event

Revision ID: 489466e2dc42
Revises: 5b1077cbd163
Create Date: 2024-11-06 16:38:46.438808

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '489466e2dc42'
down_revision = '5b1077cbd163'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('local_plan_event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('notes', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('local_plan_event', schema=None) as batch_op:
        batch_op.drop_column('notes')

    # ### end Alembic commands ###