"""add publication status

Revision ID: 04379e71fcb1
Revises: f2f1c45ade3b
Create Date: 2024-09-23 13:28:34.828901

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "04379e71fcb1"
down_revision = "f2f1c45ade3b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum(
        "DRAFT", "READY_FOR_PUBLICATION", "PUBLISHED", name="publication_status"
    ).create(op.get_bind())
    with op.batch_alter_table("local_plan", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "publication_status",
                postgresql.ENUM(
                    "DRAFT",
                    "READY_FOR_PUBLICATION",
                    "PUBLISHED",
                    name="publication_status",
                    create_type=False,
                ),
                nullable=False,
            )
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("local_plan", schema=None) as batch_op:
        batch_op.drop_column("publication_status")

    sa.Enum(
        "DRAFT", "READY_FOR_PUBLICATION", "PUBLISHED", name="publication_status"
    ).drop(op.get_bind())
    # ### end Alembic commands ###
