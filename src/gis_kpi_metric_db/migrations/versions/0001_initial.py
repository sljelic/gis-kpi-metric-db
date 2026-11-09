"""Initial documented Accelo, ADMS and KPI tables."""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE SCHEMA IF NOT EXISTS accelo")
    op.execute("CREATE SCHEMA IF NOT EXISTS adms")
    op.create_table(
        "issues",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        *[
            sa.Column(k, sa.String())
            for k in (
                "custom_id",
                "description",
                "against",
                "against_type",
                "resolution_detail",
                "standing",
                "referrer_type",
            )
        ],
        *[
            sa.Column(k, sa.BigInteger())
            for k in (
                "against_id",
                "date_submitted",
                "date_opened",
                "date_resolved",
                "date_closed",
                "date_due",
                "date_last_interacted",
                "date_modified",
                "referrer_id",
                "billable_seconds",
            )
        ],
        *[
            sa.Column(k, sa.JSON())
            for k in (
                "type",
                "issue_type",
                "affiliation",
                "class",
                "priority",
                "issue_priority",
                "resolution",
                "status",
                "submitted_by",
                "opened_by",
                "resolved_by",
                "closed_by",
                "company",
                "assignee",
                "contract",
                "issue_object_budget",
                "object_budget",
            )
        ],
        sa.Column("staff_bookmarked", sa.Boolean()),
        schema="accelo",
    )
    op.create_table(
        "issue_progressions",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("to_id", sa.BigInteger(), nullable=False),
        sa.Column("to_title", sa.String(), nullable=False),
        sa.Column("against_type", sa.String()),
        *[
            sa.Column(k, sa.BigInteger())
            for k in ("against_id", "modified_by", "date_modified")
        ],
        schema="accelo",
    )
    op.create_table(
        "extension_values",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        *[
            sa.Column(k, sa.String(), nullable=False)
            for k in ("field_type", "file_name")
        ],
        sa.Column("value", sa.JSON(), nullable=False),
        *[sa.Column(k, sa.JSON()) for k in ("values", "modified_by", "default_value")],
        *[
            sa.Column(k, sa.BigInteger())
            for k in (
                "field_id",
                "link_id",
                "link_type_id",
                "date_modified",
                "value_id",
            )
        ],
        *[
            sa.Column(k, sa.String())
            for k in ("link_type", "value_type", "field_description", "field_name")
        ],
        *[
            sa.Column(k, sa.Boolean())
            for k in ("is_sensitive", "is_important", "is_exported")
        ],
        schema="accelo",
    )
    op.create_table(
        "holidays",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("date", sa.BigInteger(), nullable=False),
        schema="accelo",
    )
    op.create_table(
        "incident",
        sa.Column("incident_id", sa.BigInteger(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        *[
            sa.Column(k, sa.BigInteger(), nullable=False)
            for k in ("type_id", "against_id")
        ],
        sa.Column("against_type", sa.String(), nullable=False),
        *[sa.Column(k, sa.String()) for k in ("standing", "description")],
        *[
            sa.Column(k, sa.BigInteger())
            for k in (
                "status_id",
                "affiliation_id",
                "date_started",
                "date_due",
                "class_id",
                "assignee",
                "priority_id",
                "date_created_in_accelo",
            )
        ],
        sa.UniqueConstraint("title", name="uq_incident_title"),
        schema="adms",
    )
    op.create_table(
        "metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "issue_id",
            sa.BigInteger(),
            sa.ForeignKey("accelo.issues.id"),
            nullable=False,
        ),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("value", sa.Float()),
        sa.Column("datetime_calculated", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "issue_id", "title", "datetime_calculated", name="uq_metrics_issue_id"
        ),
    )


def downgrade():
    op.drop_table("metrics")
    op.drop_table("incident", schema="adms")
    for name in ("holidays", "extension_values", "issue_progressions", "issues"):
        op.drop_table(name, schema="accelo")
