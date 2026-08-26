"""add student account_kind for admin management

Revision ID: 0009_student_account_kind
Revises: 0008_intelligent_scheduling
Create Date: 2026-07-21
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0009_student_account_kind"
down_revision: str | None = "0008_intelligent_scheduling"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "students",
        sa.Column(
            "account_kind",
            sa.String(length=30),
            nullable=False,
            server_default="student",
        ),
    )
    op.execute(
        "UPDATE students SET account_kind = 'candidate' "
        "WHERE email LIKE '%candidate%' OR internship_type IS NULL"
    )
    op.execute(
        "UPDATE students SET account_kind = 'student' "
        "WHERE email LIKE '%student%' OR internship_type IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_column("students", "account_kind")
