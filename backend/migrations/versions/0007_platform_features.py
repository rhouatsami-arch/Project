"""Platform features: admin, meetings, notifications, history, audit

Revision ID: 0007_platform_features
Revises: 0006_cv_extracted_text
Create Date: 2026-07-10
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007_platform_features"
down_revision: str | None = "0006_cv_extracted_text"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "admins",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_admins_email", "admins", ["email"])

    op.create_table(
        "meetings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("application_id", sa.Integer(), nullable=False),
        sa.Column("recruiter_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("student_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("scheduled", "completed", "cancelled", name="meetingstatus"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["application_id"], ["applications.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["recruiter_id"], ["recruiters.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_email", sa.String(255), nullable=False),
        sa.Column("user_role", sa.String(30), nullable=False),
        sa.Column(
            "type",
            sa.Enum("recommendation", "interview", "system", name="notificationtype"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_user_email", "notifications", ["user_email"])

    op.create_table(
        "recommendation_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("compatibility_score", sa.Integer(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("actor_email", sa.String(255), nullable=False),
        sa.Column("actor_role", sa.String(30), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource", sa.String(255), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("recommendation_history")
    op.drop_index("ix_notifications_user_email", "notifications")
    op.drop_table("notifications")
    op.drop_table("meetings")
    op.drop_index("ix_admins_email", "admins")
    op.drop_table("admins")
    op.execute("DROP TYPE IF EXISTS meetingstatus")
    op.execute("DROP TYPE IF EXISTS notificationtype")
