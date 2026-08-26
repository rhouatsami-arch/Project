"""student internship details

Revision ID: 0003_student_internship_details
Revises: 0002_student_profile_sections
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_student_internship_details"
down_revision: str | None = "0002_student_profile_sections"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "students", sa.Column("internship_type", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "students",
        sa.Column("internship_duration", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("students", "internship_duration")
    op.drop_column("students", "internship_type")
