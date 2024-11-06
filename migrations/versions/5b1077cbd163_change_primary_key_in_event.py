"""change primary key in event

Revision ID: 5b1077cbd163
Revises: 28a934c3d949
Create Date: 2024-11-06 09:38:56.444051

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b1077cbd163'
down_revision = '28a934c3d949'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('local_plan_event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reference', sa.Text(), nullable=False))
        batch_op.add_column(sa.Column('name', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('entry_date', sa.Date(), nullable=False))
        batch_op.add_column(sa.Column('start_date', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('end_date', sa.Date(), nullable=True))
        batch_op.create_index(batch_op.f('ix_local_plan_event_end_date'), ['end_date'], unique=False)
        batch_op.drop_column('id')
        batch_op.create_primary_key('pk_local_plan_event_reference', ['reference'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('local_plan_event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.UUID(), autoincrement=False, nullable=False))
        batch_op.drop_constraint('pk_local_plan_event_reference')
        batch_op.create_primary_key('pk_local_plan_event_id', ['id'])
        batch_op.drop_index(batch_op.f('ix_local_plan_event_end_date'))
        batch_op.drop_column('end_date')
        batch_op.drop_column('start_date')
        batch_op.drop_column('entry_date')
        batch_op.drop_column('description')
        batch_op.drop_column('name')
        batch_op.drop_column('reference')

    # ### end Alembic commands ###
