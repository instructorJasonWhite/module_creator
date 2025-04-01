"""create user preferences table

Revision ID: 2024_03_30_user_preferences
Revises:
Create Date: 2024-03-30 23:15:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "2024_03_30_user_preferences"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "number_of_modules", sa.Integer(), nullable=False, server_default="5"
        ),
        sa.Column("theme_prompt", sa.String(), nullable=True),
        sa.Column("module_preferences", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_preferences_id"), "user_preferences", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_user_preferences_user_id"),
        "user_preferences",
        ["user_id"],
        unique=True,
    )


def downgrade():
    op.drop_index(op.f("ix_user_preferences_user_id"), table_name="user_preferences")
    op.drop_index(op.f("ix_user_preferences_id"), table_name="user_preferences")
    op.drop_table("user_preferences")
