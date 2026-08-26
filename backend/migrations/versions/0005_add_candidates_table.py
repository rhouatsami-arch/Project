"""add candidates table

Revision ID: 0005_add_candidates_table
Revises: 0004_application_internship_type
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005_add_candidates_table"
down_revision: str | None = "0004_application_internship_type"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create candidates table as a view of students who have applied
    op.create_table(
        "candidates",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("university", sa.String(255), nullable=True),
        sa.Column("field_of_study", sa.String(255), nullable=True),
        sa.Column("graduation_year", sa.Integer, nullable=True),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("skills", sa.Text, nullable=True),
        sa.Column("technical_skills", sa.Text, nullable=True),
        sa.Column("soft_skills", sa.Text, nullable=True),
        sa.Column("experiences", sa.Text, nullable=True),
        sa.Column("projects", sa.Text, nullable=True),
        sa.Column("certifications", sa.Text, nullable=True),
        sa.Column("languages", sa.Text, nullable=True),
        sa.Column("cv_filename", sa.String(255), nullable=True),
        sa.Column("cv_path", sa.String(500), nullable=True),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        schema="public",
    )


def downgrade() -> None:
    op.drop_table("candidates", schema="public")
