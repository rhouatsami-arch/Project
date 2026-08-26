"""application internship duration type

Revision ID: 0004_application_internship_type
Revises: 0003_student_internship_details
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004_application_internship_type"
down_revision: str | None = "0003_student_internship_details"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

internship_duration_type = sa.Enum(
    "observation",
    "operational",
    "functional",
    name="internshipdurationtype",
)


def upgrade() -> None:
    internship_duration_type.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "applications",
        sa.Column("internship_type", internship_duration_type, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("applications", "internship_type")
    internship_duration_type.drop(op.get_bind(), checkfirst=True)
