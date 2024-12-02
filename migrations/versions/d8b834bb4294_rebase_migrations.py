"""rebase_migrations

Revision ID: d8b834bb4294
Revises:
Create Date: 2024-11-29 11:57:57.264563

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d8b834bb4294"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum(
        "TIMETABLE_PUBLISHED",
        "ESTIMATED_REGULATION_18",
        "ESTIMATED_REGULATION_19",
        "ESTIMATED_EXAMINATION_AND_ADOPTION",
        "REGULATION_18",
        "REGULATION_19",
        "PLANNING_INSPECTORATE_EXAMINATION",
        "PLANNING_INSPECTORATE_FINDINGS",
        name="eventcategory",
    ).create(op.get_bind())
    sa.Enum(
        "FOR_REVIEW", "FOR_PLATFORM", "NOT_FOR_PLATFORM", "EXPORTED", name="status"
    ).create(op.get_bind())
    op.create_table(
        "local_plan_boundary",
        sa.Column("geometry", sa.Text(), nullable=True),
        sa.Column("geojson", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("reference"),
    )
    with op.batch_alter_table("local_plan_boundary", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_local_plan_boundary_end_date"), ["end_date"], unique=False
        )

    op.create_table(
        "local_plan_document_type",
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("reference"),
    )
    with op.batch_alter_table("local_plan_document_type", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_local_plan_document_type_end_date"),
            ["end_date"],
            unique=False,
        )

    op.create_table(
        "local_plan_event_type",
        sa.Column(
            "event_category",
            postgresql.ENUM(
                "TIMETABLE_PUBLISHED",
                "ESTIMATED_REGULATION_18",
                "ESTIMATED_REGULATION_19",
                "ESTIMATED_EXAMINATION_AND_ADOPTION",
                "REGULATION_18",
                "REGULATION_19",
                "PLANNING_INSPECTORATE_EXAMINATION",
                "PLANNING_INSPECTORATE_FINDINGS",
                name="eventcategory",
                create_type=False,
            ),
            nullable=True,
        ),
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("reference"),
    )
    with op.batch_alter_table("local_plan_event_type", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_local_plan_event_type_end_date"), ["end_date"], unique=False
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
        sa.Column("statistical_geography", sa.Text(), nullable=True),
        sa.Column("website", sa.Text(), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("organisation"),
    )
    with op.batch_alter_table("organisation", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_organisation_end_date"), ["end_date"], unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_organisation_name"), ["name"], unique=False
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
        sa.Column("lds_published_date", sa.Text(), nullable=True),
        sa.Column("local_plan_boundary", sa.Text(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "FOR_REVIEW",
                "FOR_PLATFORM",
                "NOT_FOR_PLATFORM",
                "EXPORTED",
                name="status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "boundary_status",
            postgresql.ENUM(
                "FOR_REVIEW",
                "FOR_PLATFORM",
                "NOT_FOR_PLATFORM",
                "EXPORTED",
                name="status",
                create_type=False,
            ),
            nullable=True,
        ),
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
    with op.batch_alter_table("local_plan", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_local_plan_end_date"), ["end_date"], unique=False
        )

    op.create_table(
        "local_plan_document",
        sa.Column("local_plan", sa.Text(), nullable=False),
        sa.Column("documentation_url", sa.Text(), nullable=True),
        sa.Column("document_url", sa.Text(), nullable=True),
        sa.Column("document_types", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "FOR_REVIEW",
                "FOR_PLATFORM",
                "NOT_FOR_PLATFORM",
                "EXPORTED",
                name="status",
                create_type=False,
            ),
            nullable=False,
        ),
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
    with op.batch_alter_table("local_plan_document", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_local_plan_document_end_date"), ["end_date"], unique=False
        )

    op.create_table(
        "local_plan_organisation",
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
    with op.batch_alter_table("local_plan_organisation", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_local_plan_organisation_local_plan"),
            ["local_plan"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_local_plan_organisation_organisation"),
            ["organisation"],
            unique=False,
        )

    op.create_table(
        "local_plan_timetable",
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("local_plan", sa.Text(), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["local_plan"],
            ["local_plan.reference"],
        ),
        sa.PrimaryKeyConstraint("reference"),
    )
    with op.batch_alter_table("local_plan_timetable", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_local_plan_timetable_end_date"), ["end_date"], unique=False
        )

    op.create_table(
        "document_organisation",
        sa.Column("local_plan_document_reference", sa.Text(), nullable=False),
        sa.Column("organisation", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["local_plan_document_reference"],
            ["local_plan_document.reference"],
        ),
        sa.ForeignKeyConstraint(
            ["organisation"],
            ["organisation.organisation"],
        ),
        sa.PrimaryKeyConstraint("local_plan_document_reference", "organisation"),
    )
    op.create_table(
        "local_plan_event",
        sa.Column(
            "event_category",
            postgresql.ENUM(
                "TIMETABLE_PUBLISHED",
                "ESTIMATED_REGULATION_18",
                "ESTIMATED_REGULATION_19",
                "ESTIMATED_EXAMINATION_AND_ADOPTION",
                "REGULATION_18",
                "REGULATION_19",
                "PLANNING_INSPECTORATE_EXAMINATION",
                "PLANNING_INSPECTORATE_FINDINGS",
                name="eventcategory",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("event_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_date", sa.DateTime(), nullable=False),
        sa.Column("local_plan_timetable", sa.Text(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("reference", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["local_plan_timetable"],
            ["local_plan_timetable.reference"],
        ),
        sa.PrimaryKeyConstraint("reference"),
    )
    with op.batch_alter_table("local_plan_event", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_local_plan_event_end_date"), ["end_date"], unique=False
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("local_plan_event", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_local_plan_event_end_date"))

    op.drop_table("local_plan_event")
    op.drop_table("document_organisation")
    with op.batch_alter_table("local_plan_timetable", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_local_plan_timetable_end_date"))

    op.drop_table("local_plan_timetable")
    with op.batch_alter_table("local_plan_organisation", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_local_plan_organisation_organisation"))
        batch_op.drop_index(batch_op.f("ix_local_plan_organisation_local_plan"))

    op.drop_table("local_plan_organisation")
    with op.batch_alter_table("local_plan_document", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_local_plan_document_end_date"))

    op.drop_table("local_plan_document")
    with op.batch_alter_table("local_plan", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_local_plan_end_date"))

    op.drop_table("local_plan")
    op.drop_table("boundary_organisation")
    with op.batch_alter_table("organisation", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_organisation_name"))
        batch_op.drop_index(batch_op.f("ix_organisation_end_date"))

    op.drop_table("organisation")
    with op.batch_alter_table("local_plan_event_type", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_local_plan_event_type_end_date"))

    op.drop_table("local_plan_event_type")
    with op.batch_alter_table("local_plan_document_type", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_local_plan_document_type_end_date"))

    op.drop_table("local_plan_document_type")
    with op.batch_alter_table("local_plan_boundary", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_local_plan_boundary_end_date"))

    op.drop_table("local_plan_boundary")
    sa.Enum(
        "FOR_REVIEW", "FOR_PLATFORM", "NOT_FOR_PLATFORM", "EXPORTED", name="status"
    ).drop(op.get_bind())
    sa.Enum(
        "TIMETABLE_PUBLISHED",
        "ESTIMATED_REGULATION_18",
        "ESTIMATED_REGULATION_19",
        "ESTIMATED_EXAMINATION_AND_ADOPTION",
        "REGULATION_18",
        "REGULATION_19",
        "PLANNING_INSPECTORATE_EXAMINATION",
        "PLANNING_INSPECTORATE_FINDINGS",
        name="eventcategory",
    ).drop(op.get_bind())
    # ### end Alembic commands ###
