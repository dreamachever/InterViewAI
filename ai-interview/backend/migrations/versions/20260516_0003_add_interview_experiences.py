"""add interview experiences

Revision ID: 20260516_0003
Revises: 20260516_0002
Create Date: 2026-05-16
"""
from alembic import op
import sqlalchemy as sa


revision = "20260516_0003"
down_revision = "20260516_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "interview_experiences",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_url", sa.String(length=1024), nullable=True),
        sa.Column("source_site", sa.String(length=255), nullable=True),
        sa.Column("target_school", sa.String(length=255), nullable=True),
        sa.Column("target_major", sa.String(length=255), nullable=True),
        sa.Column("target_lab", sa.String(length=255), nullable=True),
        sa.Column("target_teacher", sa.String(length=255), nullable=True),
        sa.Column("interview_type", sa.String(length=100), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("raw_content", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("extract_status", sa.String(length=50), nullable=False),
        sa.Column("extract_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_interview_experiences_user_id"), "interview_experiences", ["user_id"], unique=False)
    op.create_index(op.f("ix_interview_experiences_target_school"), "interview_experiences", ["target_school"], unique=False)
    op.create_index(op.f("ix_interview_experiences_target_major"), "interview_experiences", ["target_major"], unique=False)
    op.create_index(op.f("ix_interview_experiences_interview_type"), "interview_experiences", ["interview_type"], unique=False)
    op.create_index(op.f("ix_interview_experiences_year"), "interview_experiences", ["year"], unique=False)

    op.create_table(
        "experience_insights",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("experience_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("fallback_used", sa.Boolean(), nullable=False),
        sa.Column("fallback_reason", sa.Text(), nullable=True),
        sa.Column("interview_process_json", sa.JSON(), nullable=True),
        sa.Column("question_categories_json", sa.JSON(), nullable=True),
        sa.Column("real_questions_json", sa.JSON(), nullable=True),
        sa.Column("focus_points_json", sa.JSON(), nullable=True),
        sa.Column("risk_points_json", sa.JSON(), nullable=True),
        sa.Column("suggested_strategy_json", sa.JSON(), nullable=True),
        sa.Column("timeline_json", sa.JSON(), nullable=True),
        sa.Column("raw_result_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["experience_id"], ["interview_experiences.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_experience_insights_experience_id"), "experience_insights", ["experience_id"], unique=False)
    op.create_index(op.f("ix_experience_insights_user_id"), "experience_insights", ["user_id"], unique=False)

    op.create_table(
        "interview_experience_links",
        sa.Column("interview_id", sa.String(), nullable=False),
        sa.Column("experience_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["experience_id"], ["interview_experiences.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["interview_id"], ["interviews.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("interview_id", "experience_id"),
    )


def downgrade() -> None:
    op.drop_table("interview_experience_links")
    op.drop_index(op.f("ix_experience_insights_user_id"), table_name="experience_insights")
    op.drop_index(op.f("ix_experience_insights_experience_id"), table_name="experience_insights")
    op.drop_table("experience_insights")
    op.drop_index(op.f("ix_interview_experiences_year"), table_name="interview_experiences")
    op.drop_index(op.f("ix_interview_experiences_interview_type"), table_name="interview_experiences")
    op.drop_index(op.f("ix_interview_experiences_target_major"), table_name="interview_experiences")
    op.drop_index(op.f("ix_interview_experiences_target_school"), table_name="interview_experiences")
    op.drop_index(op.f("ix_interview_experiences_user_id"), table_name="interview_experiences")
    op.drop_table("interview_experiences")
