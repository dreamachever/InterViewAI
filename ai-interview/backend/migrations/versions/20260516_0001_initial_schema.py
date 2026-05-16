"""initial schema

Revision ID: 20260516_0001
Revises:
Create Date: 2026-05-16
"""
from alembic import op
import sqlalchemy as sa


revision = "20260516_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("nickname", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "resumes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=True),
        sa.Column("parsed_text", sa.Text(), nullable=False),
        sa.Column("parse_status", sa.String(length=50), nullable=False),
        sa.Column("parse_error", sa.Text(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_resumes_user_id"), "resumes", ["user_id"], unique=False)

    op.create_table(
        "user_llm_configs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("base_url", sa.String(length=1024), nullable=True),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("encrypted_api_key", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("last_test_status", sa.String(length=50), nullable=True),
        sa.Column("last_test_message", sa.Text(), nullable=True),
        sa.Column("last_tested_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_llm_configs_user_id"), "user_llm_configs", ["user_id"], unique=False)

    op.create_table(
        "interviews",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("resume_id", sa.String(), nullable=True),
        sa.Column("llm_config_id", sa.String(), nullable=True),
        sa.Column("llm_provider_used", sa.String(length=100), nullable=True),
        sa.Column("llm_model_used", sa.String(length=255), nullable=True),
        sa.Column("voice_enabled", sa.Boolean(), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("interviewer_style", sa.String(length=50), nullable=False),
        sa.Column("target_school", sa.String(length=255), nullable=True),
        sa.Column("target_company", sa.String(length=255), nullable=True),
        sa.Column("target_major", sa.String(length=255), nullable=True),
        sa.Column("target_position", sa.String(length=255), nullable=True),
        sa.Column("resume_text", sa.Text(), nullable=False),
        sa.Column("resume_analysis", sa.JSON(), nullable=True),
        sa.Column("interview_plan", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("current_stage", sa.String(length=50), nullable=False),
        sa.Column("total_score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["llm_config_id"], ["user_llm_configs.id"]),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_interviews_llm_config_id"), "interviews", ["llm_config_id"], unique=False)
    op.create_index(op.f("ix_interviews_resume_id"), "interviews", ["resume_id"], unique=False)
    op.create_index(op.f("ix_interviews_user_id"), "interviews", ["user_id"], unique=False)

    op.create_table(
        "messages",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("interview_id", sa.String(), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("stage", sa.String(length=50), nullable=True),
        sa.Column("answer_quality", sa.String(length=30), nullable=True),
        sa.Column("detected_issues", sa.JSON(), nullable=True),
        sa.Column("brief_feedback", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["interview_id"], ["interviews.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_messages_interview_id"), "messages", ["interview_id"], unique=False)

    op.create_table(
        "reports",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("interview_id", sa.String(), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=True),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("total_score", sa.Integer(), nullable=False),
        sa.Column("dimension_scores", sa.JSON(), nullable=True),
        sa.Column("overall_comment", sa.Text(), nullable=False),
        sa.Column("strengths", sa.JSON(), nullable=True),
        sa.Column("weaknesses", sa.JSON(), nullable=True),
        sa.Column("resume_risks", sa.JSON(), nullable=True),
        sa.Column("question_reviews", sa.JSON(), nullable=True),
        sa.Column("next_training_plan", sa.JSON(), nullable=True),
        sa.Column("full_report", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["interview_id"], ["interviews.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reports_interview_id"), "reports", ["interview_id"], unique=True)

    op.create_table(
        "resume_diagnostics",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("resume_id", sa.String(), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("fallback_used", sa.Boolean(), nullable=False),
        sa.Column("fallback_reason", sa.Text(), nullable=True),
        sa.Column("overall_score", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("strengths_json", sa.JSON(), nullable=True),
        sa.Column("weaknesses_json", sa.JSON(), nullable=True),
        sa.Column("suggestions_json", sa.JSON(), nullable=True),
        sa.Column("section_reviews_json", sa.JSON(), nullable=True),
        sa.Column("follow_up_questions_json", sa.JSON(), nullable=True),
        sa.Column("raw_result_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_resume_diagnostics_resume_id"), "resume_diagnostics", ["resume_id"], unique=False)
    op.create_index(op.f("ix_resume_diagnostics_user_id"), "resume_diagnostics", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_resume_diagnostics_user_id"), table_name="resume_diagnostics")
    op.drop_index(op.f("ix_resume_diagnostics_resume_id"), table_name="resume_diagnostics")
    op.drop_table("resume_diagnostics")
    op.drop_index(op.f("ix_reports_interview_id"), table_name="reports")
    op.drop_table("reports")
    op.drop_index(op.f("ix_messages_interview_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_index(op.f("ix_interviews_user_id"), table_name="interviews")
    op.drop_index(op.f("ix_interviews_resume_id"), table_name="interviews")
    op.drop_index(op.f("ix_interviews_llm_config_id"), table_name="interviews")
    op.drop_table("interviews")
    op.drop_index(op.f("ix_user_llm_configs_user_id"), table_name="user_llm_configs")
    op.drop_table("user_llm_configs")
    op.drop_index(op.f("ix_resumes_user_id"), table_name="resumes")
    op.drop_table("resumes")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
