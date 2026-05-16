import json


def build_resume_analysis_prompt(resume_text: str) -> str:
    return f"""
You are an interview coach for Chinese postgraduate recommendation interviews.
Return strict JSON only, with no markdown.

Extract:
- candidate summary
- education background
- projects / research / internship experience
- strengths
- risks
- possible follow-up questions
- recommended interview focus

JSON schema:
{{
  "summary": "candidate summary",
  "education": "education summary",
  "projects": [
    {{
      "name": "project name",
      "description": "project description",
      "possible_questions": ["question 1", "question 2"],
      "risks": ["risk 1", "risk 2"]
    }}
  ],
  "strengths": ["strength 1"],
  "risks": ["risk 1"],
  "recommended_focus": ["focus 1"]
}}

Resume text:
{resume_text}
""".strip()


def build_experience_extract_prompt(raw_content: str, metadata: dict) -> str:
    return f"""
You are extracting actionable training knowledge for a Chinese postgraduate recommendation mock interview system.
Return strict JSON only, with no markdown, comments, or extra text.

Goal:
- Do not write a generic article summary.
- Extract structured interview knowledge that can directly improve mock interviews.
- Focus on the real interview process, high-frequency questions, real questions, technical basics, research questions, English questions, pressure questions, mentor focus points, risks, preparation advice, and questioning strategy.
- If the source text does not contain enough evidence, return empty arrays instead of inventing facts.
- Do not fabricate specific school, lab, teacher, or major facts.

JSON schema:
{{
  "summary": "core summary for training",
  "interview_process": ["waiting", "self introduction"],
  "question_categories": [
    {{
      "category": "research experience",
      "frequency": "high | medium | low",
      "questions": ["question 1", "question 2"]
    }}
  ],
  "real_questions": [
    {{
      "question": "real question text",
      "category": "research experience",
      "difficulty": "easy | medium | hard",
      "source_context": "supporting context from the article"
    }}
  ],
  "focus_points": ["focus 1", "focus 2"],
  "risk_points": [
    {{
      "level": "high | medium | low",
      "point": "risk point",
      "suggestion": "how to prepare"
    }}
  ],
  "suggested_strategy": ["strategy 1", "strategy 2"],
  "timeline": [
    {{
      "step": "self introduction",
      "estimated_minutes": 1,
      "notes": "notes"
    }}
  ]
}}

Metadata:
{json.dumps(metadata, ensure_ascii=False)}

Source text:
{raw_content}
""".strip()


def build_next_question_prompt(
    interview: dict,
    resume_analysis: dict,
    messages: list[dict],
    latest_answer: str,
    controlled_stage: str,
    experience_context: list[dict] | None = None,
) -> str:
    return f"""
You are a realistic Chinese interview professor for a postgraduate recommendation interview.
Return strict JSON only, with no markdown.

Rules:
- Ask only one question at a time.
- Sound like a real interviewer, not a study guide.
- Prefer the high-frequency and real questions shown in the selected interview experiences, but do not mechanically repeat them.
- Personalize follow-up questions using the candidate's resume and previous answers.
- If the experience context suggests stronger emphasis on fundamentals, increase the probability of professional/basic theory questions.
- If the experience context suggests English questioning, add suitable English questions at appropriate moments.
- If the experience context contains high-risk points, probe them at natural stages.
- If the latest answer is vague, continue follow-up; if it is strong enough, move to the next topic.
- Do not generate a final report before the interview ends.
- The current stage must remain exactly: {controlled_stage}

JSON schema:
{{
  "answer_quality": "poor | medium | good",
  "detected_issues": ["issue 1", "issue 2"],
  "action": "follow_up | next_question | end_interview",
  "stage": "{controlled_stage}",
  "interviewer_reply": "the next interviewer reply",
  "brief_feedback": "one short internal feedback note"
}}

Interview config:
{json.dumps(interview, ensure_ascii=False)}

Resume analysis:
{json.dumps(resume_analysis, ensure_ascii=False)}

Selected experience insights:
{json.dumps(experience_context or [], ensure_ascii=False)}

Conversation history:
{json.dumps(messages, ensure_ascii=False)}

Latest candidate answer:
{latest_answer}
""".strip()


def build_report_prompt(interview: dict, resume_analysis: dict, messages: list[dict]) -> str:
    return f"""
You are a rigorous Chinese interview evaluator.
Return strict JSON only, with no markdown.

JSON schema:
{{
  "total_score": 78,
  "dimension_scores": {{
    "表达逻辑": {{
      "score": 16,
      "max": 20,
      "comment": "comment"
    }}
  }},
  "overall_comment": "overall comment",
  "strengths": ["strength 1"],
  "weaknesses": ["weakness 1"],
  "resume_risks": ["risk 1"],
  "question_reviews": [
    {{
      "question": "question",
      "answer_summary": "answer summary",
      "score": 7,
      "comment": "comment",
      "improved_answer_suggestion": "suggestion"
    }}
  ],
  "next_training_plan": ["plan 1", "plan 2"]
}}

Interview config:
{json.dumps(interview, ensure_ascii=False)}

Resume analysis:
{json.dumps(resume_analysis, ensure_ascii=False)}

Conversation:
{json.dumps(messages, ensure_ascii=False)}
""".strip()


def build_resume_diagnostic_prompt(resume_text: str) -> str:
    return f"""
You are a Chinese resume reviewer focused on postgraduate recommendation interviews.
Return strict JSON only, with no markdown or extra explanation.

JSON schema:
{{
  "overall_score": 82,
  "summary": "summary",
  "strengths": ["strength 1"],
  "weaknesses": ["weakness 1"],
  "suggestions": [
    {{
      "priority": "high | medium | low",
      "problem": "specific problem",
      "advice": "specific advice",
      "example": "optional example"
    }}
  ],
  "section_reviews": [
    {{
      "section": "education/research/project/competition/skills",
      "score": 78,
      "comment": "comment"
    }}
  ],
  "follow_up_questions": ["possible follow-up question"]
}}

Resume text:
{resume_text}
""".strip()
