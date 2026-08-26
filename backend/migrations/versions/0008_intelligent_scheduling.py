"""Intelligent interview scheduling: slots, availability, extended statuses

Revision ID: 0008_intelligent_scheduling
Revises: 0007_platform_features
Create Date: 2026-07-15
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0008_intelligent_scheduling"
down_revision: str | None = "0007_platform_features"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Use VARCHAR statuses to avoid PostgreSQL enum alter transaction limits
    op.execute(
        "ALTER TABLE meetings ALTER COLUMN status TYPE VARCHAR(30) USING status::text"
    )
    op.execute("DROP TYPE IF EXISTS meetingstatus")
    op.execute("UPDATE meetings SET status = 'accepted' WHERE status = 'scheduled'")

    op.add_column("meetings", sa.Column("slot_id", sa.Integer(), nullable=True))
    op.add_column("meetings", sa.Column("updated_at", sa.DateTime(), nullable=True))

    op.create_table(
        "interview_slots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recruiter_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("ends_at", sa.DateTime(), nullable=False),
        sa.Column("is_booked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recruiter_id"], ["recruiters.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_interview_slots_recruiter_id", "interview_slots", ["recruiter_id"]
    )

    op.create_table(
        "candidate_availabilities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("ends_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_candidate_availabilities_student_id",
        "candidate_availabilities",
        ["student_id"],
    )

    op.create_foreign_key(
        "fk_meetings_slot_id",
        "meetings",
        "interview_slots",
        ["slot_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_meetings_slot_id", "meetings", type_="foreignkey")
    op.drop_index(
        "ix_candidate_availabilities_student_id", table_name="candidate_availabilities"
    )
    op.drop_table("candidate_availabilities")
    op.drop_index("ix_interview_slots_recruiter_id", table_name="interview_slots")
    op.drop_table("interview_slots")
    op.drop_column("meetings", "updated_at")
    op.drop_column("meetings", "slot_id")

    meetingstatus = sa.Enum("scheduled", "completed", "cancelled", name="meetingstatus")
    meetingstatus.create(op.get_bind(), checkfirst=True)
    op.execute(
        "UPDATE meetings SET status = 'scheduled' "
        "WHERE status IN ('proposed', 'accepted')"
    )
    op.execute(
        "ALTER TABLE meetings ALTER COLUMN status TYPE meetingstatus "
        "USING status::meetingstatus"
    )
