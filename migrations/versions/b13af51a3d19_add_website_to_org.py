"""add website to org

Revision ID: b13af51a3d19
Revises: 59d28e7fd16f
Create Date: 2024-10-09 10:17:43.344864

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b13af51a3d19"
down_revision = "59d28e7fd16f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("organisation", schema=None) as batch_op:
        batch_op.add_column(sa.Column("website", sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("organisation", schema=None) as batch_op:
        batch_op.drop_column("website")

    # ### end Alembic commands ###
