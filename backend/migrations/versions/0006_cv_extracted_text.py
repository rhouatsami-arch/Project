"""CV extracted raw text storage

Revision ID: 0006_cv_extracted_text
Revises: 0005_add_candidates_table
Create Date: 2026-07-08
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0006_cv_extracted_text"
down_revision: str | None = "0005_add_candidates_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("students", sa.Column("cv_extracted_text", sa.Text(), nullable=True))
    op.add_column(
        "students", sa.Column("cv_extracted_at", sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("students", "cv_extracted_at")
    op.drop_column("students", "cv_extracted_text")
