"""boundary status to local plan

Revision ID: 59d28e7fd16f
Revises: c80dbfa47e46
Create Date: 2024-10-07 10:13:28.453225

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "59d28e7fd16f"
down_revision = "c80dbfa47e46"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("local_plan", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "boundary_status",
                postgresql.ENUM(
                    "FOR_REVIEW",
                    "FOR_PUBLICATION",
                    "NOT_FOR_PUBLICATION",
                    "PUBLISHED",
                    name="status",
                    create_type=False,
                ),
                nullable=True,
            )
        )

    op.execute(
        """
        UPDATE local_plan
        SET boundary_status = 'FOR_REVIEW'
        WHERE boundary_status IS NULL;
        """
    )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("local_plan", schema=None) as batch_op:
        batch_op.drop_column("boundary_status")

    # ### end Alembic commands ###
