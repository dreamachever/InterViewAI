STAGE_LIMITS: dict[str, int] = {
    "SELF_INTRODUCTION": 1,
    "BACKGROUND": 2,
    "RESUME_DEEP_DIVE": 4,
    "PROFESSIONAL_QUESTIONS": 3,
    "MOTIVATION": 2,
    "PRESSURE_TEST": 2,
    "CLOSING": 1,
}

STAGE_ORDER = list(STAGE_LIMITS.keys())
MAX_CANDIDATE_TURNS = 20


def count_candidate_turns_by_stage(messages: list, stage: str) -> int:
    return len([m for m in messages if m.role == "candidate" and m.stage == stage])


def total_candidate_turns(messages: list) -> int:
    return len([m for m in messages if m.role == "candidate"])


def next_stage(current_stage: str) -> str:
    try:
        index = STAGE_ORDER.index(current_stage)
    except ValueError:
        return STAGE_ORDER[0]
    return STAGE_ORDER[min(index + 1, len(STAGE_ORDER) - 1)]


def resolve_stage(current_stage: str, messages: list, ai_action: str) -> tuple[str, str]:
    if total_candidate_turns(messages) >= MAX_CANDIDATE_TURNS:
        return current_stage, "end_interview"

    stage_count = count_candidate_turns_by_stage(messages, current_stage)
    stage_limit = STAGE_LIMITS.get(current_stage, 2)
    if current_stage == "CLOSING" and stage_count >= stage_limit:
        return current_stage, "end_interview"
    if stage_count >= stage_limit or ai_action == "next_question":
        return next_stage(current_stage), "next_question"
    return current_stage, "follow_up"


def should_force_finish(messages: list) -> bool:
    return total_candidate_turns(messages) >= MAX_CANDIDATE_TURNS
