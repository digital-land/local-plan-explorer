"""initial migration

Revision ID: f2f1c45ade3b
Revises:
Create Date: 2024-09-17 16:42:26.608515

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f2f1c45ade3b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "local_plan_boundary",
        sa.Column("plan_boundary_type", sa.Text(), nullable=True),
        sa.Column("geometry", sa.Text(), nullable=True),
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("reference"),
    )
    op.create_table(
        "organisation",
        sa.Column("organisation", sa.Text(), nullable=False),
        sa.Column("local_authority_type", sa.Text(), nullable=True),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("official_name", sa.Text(), nullable=True),
        sa.Column("geometry", sa.Text(), nullable=True),
        sa.Column("geojson", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("point", sa.Text(), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("organisation"),
    )
    op.create_table(
        "boundary_organisation",
        sa.Column("local_plan_boundary", sa.Text(), nullable=False),
        sa.Column("organisation", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["local_plan_boundary"],
            ["local_plan_boundary.reference"],
        ),
        sa.ForeignKeyConstraint(
            ["organisation"],
            ["organisation.organisation"],
        ),
        sa.PrimaryKeyConstraint("local_plan_boundary", "organisation"),
    )
    op.create_table(
        "local_plan",
        sa.Column("period_start_date", sa.Integer(), nullable=True),
        sa.Column("period_end_date", sa.Integer(), nullable=True),
        sa.Column("documentation_url", sa.Text(), nullable=True),
        sa.Column("adopted_date", sa.Text(), nullable=True),
        sa.Column("local_plan_boundary", sa.Text(), nullable=False),
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["local_plan_boundary"],
            ["local_plan_boundary.reference"],
        ),
        sa.PrimaryKeyConstraint("reference"),
    )
    op.create_table(
        "local_plan_document",
        sa.Column("plan_boundary_type", sa.Text(), nullable=True),
        sa.Column("geometry", sa.Text(), nullable=True),
        sa.Column("documentation_url", sa.Text(), nullable=True),
        sa.Column("document_url", sa.Text(), nullable=True),
        sa.Column("document_types", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("local_plan", sa.Text(), nullable=False),
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["local_plan"],
            ["local_plan.reference"],
        ),
        sa.PrimaryKeyConstraint("reference"),
    )
    op.create_table(
        "plan_organisation",
        sa.Column("local_plan", sa.Text(), nullable=False),
        sa.Column("organisation", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["local_plan"],
            ["local_plan.reference"],
        ),
        sa.ForeignKeyConstraint(
            ["organisation"],
            ["organisation.organisation"],
        ),
        sa.PrimaryKeyConstraint("local_plan", "organisation"),
    )
    op.create_table(
        "document_organisation",
        sa.Column("local_plan_document", sa.Text(), nullable=False),
        sa.Column("organisation", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["local_plan_document"],
            ["local_plan_document.reference"],
        ),
        sa.ForeignKeyConstraint(
            ["organisation"],
            ["organisation.organisation"],
        ),
        sa.PrimaryKeyConstraint("local_plan_document", "organisation"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("document_organisation")
    op.drop_table("plan_organisation")
    op.drop_table("local_plan_document")
    op.drop_table("local_plan")
    op.drop_table("boundary_organisation")
    op.drop_table("organisation")
    op.drop_table("local_plan_boundary")
    # ### end Alembic commands ###