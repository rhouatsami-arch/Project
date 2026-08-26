"""student profile sections

Revision ID: 0002_student_profile_sections
Revises: 0001_initial_recruitment_schema
Create Date: 2026-07-06
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_student_profile_sections"
down_revision: str | None = "0001_initial_recruitment_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("students", sa.Column("technical_skills", sa.Text(), nullable=True))
    op.add_column("students", sa.Column("soft_skills", sa.Text(), nullable=True))
    op.add_column("students", sa.Column("experiences", sa.Text(), nullable=True))
    op.add_column("students", sa.Column("projects", sa.Text(), nullable=True))
    op.add_column("students", sa.Column("certifications", sa.Text(), nullable=True))
    op.add_column("students", sa.Column("languages", sa.Text(), nullable=True))
    op.execute(
        "UPDATE students SET technical_skills = skills "
        "WHERE technical_skills IS NULL AND skills IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_column("students", "languages")
    op.drop_column("students", "certifications")
    op.drop_column("students", "projects")
    op.drop_column("students", "experiences")
    op.drop_column("students", "soft_skills")
    op.drop_column("students", "technical_skills")
