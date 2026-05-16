import json


def build_resume_analysis_prompt(resume_text: str) -> str:
    return f"""
你是一位专业的中文面试教练。请分析候选人简历，输出严格 JSON，不要包含 markdown。

需要提取：
- 候选人画像
- 教育背景
- 项目/科研/实习经历
- 优势
- 风险点
- 可追问问题
- 推荐面试重点

JSON schema:
{{
  "summary": "候选人简要画像",
  "education": "教育背景总结",
  "projects": [
    {{
      "name": "项目名称",
      "description": "项目简介",
      "possible_questions": ["可追问问题1", "可追问问题2"],
      "risks": ["风险点1", "风险点2"]
    }}
  ],
  "strengths": ["优势1", "优势2"],
  "risks": ["简历风险点1", "简历风险点2"],
  "recommended_focus": ["面试重点1", "面试重点2"]
}}

简历文本：
{resume_text}
""".strip()


def build_next_question_prompt(
    interview: dict,
    resume_analysis: dict,
    messages: list[dict],
    latest_answer: str,
    controlled_stage: str,
) -> str:
    return f"""
你正在扮演一位真实的中文面试官，请根据配置、简历分析和对话历史，生成下一句面试官回复。

要求：
- 不要一次问多个问题
- 不要长篇辅导
- 保持真实面试感
- 回答空泛时继续追问
- 回答充分时进入下一问题
- 压力型风格可以适当质疑
- 面试未结束前不要生成总报告
- 当前阶段必须使用后端给定阶段：{controlled_stage}

输出严格 JSON，不要包含 markdown。
JSON schema:
{{
  "answer_quality": "poor | medium | good",
  "detected_issues": ["问题1", "问题2"],
  "action": "follow_up | next_question | end_interview",
  "stage": "当前阶段",
  "interviewer_reply": "面试官下一句话",
  "brief_feedback": "一句内部反馈，用于后续报告"
}}

面试配置：
{json.dumps(interview, ensure_ascii=False)}

简历分析：
{json.dumps(resume_analysis, ensure_ascii=False)}

当前对话历史：
{json.dumps(messages, ensure_ascii=False)}

用户刚才的回答：
{latest_answer}
""".strip()


def build_report_prompt(interview: dict, resume_analysis: dict, messages: list[dict]) -> str:
    return f"""
你是一位严谨的中文面试评估专家。请根据完整面试记录生成结构化评分报告。

输出严格 JSON，不要包含 markdown。
JSON schema:
{{
  "total_score": 78,
  "dimension_scores": {{
    "表达逻辑": {{
      "score": 16,
      "max": 20,
      "comment": "表达较清楚，但部分回答缺少结构"
    }}
  }},
  "overall_comment": "整体评价",
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["问题1", "问题2"],
  "resume_risks": ["风险点1", "风险点2"],
  "question_reviews": [
    {{
      "question": "问题",
      "answer_summary": "用户回答摘要",
      "score": 7,
      "comment": "点评",
      "improved_answer_suggestion": "建议回答方式"
    }}
  ],
  "next_training_plan": ["训练建议1", "训练建议2"]
}}

面试配置：
{json.dumps(interview, ensure_ascii=False)}

简历分析：
{json.dumps(resume_analysis, ensure_ascii=False)}

完整对话：
{json.dumps(messages, ensure_ascii=False)}
""".strip()


def build_resume_diagnostic_prompt(resume_text: str) -> str:
    return f"""
你是一位专注保研申请与导师面试的中文简历诊断专家。请根据简历文本生成严格 JSON，不要输出 markdown 或额外解释。
诊断要服务于保研面试场景，重点关注科研潜力、项目可信度、个人贡献、量化成果、导师可能追问风险。

JSON schema:
{{
  "overall_score": 82,
  "summary": "整体诊断摘要",
  "strengths": ["优势1", "优势2"],
  "weaknesses": ["问题1", "问题2"],
  "suggestions": [
    {{
      "priority": "high | medium | low",
      "problem": "具体问题",
      "advice": "修改建议",
      "example": "可参考的改写示例"
    }}
  ],
  "section_reviews": [
    {{
      "section": "教育背景/科研经历/项目经历/竞赛奖项/技能等",
      "score": 78,
      "comment": "该部分评价"
    }}
  ],
  "follow_up_questions": [
    "导师可能围绕简历追问的问题"
  ]
}}

简历文本：
{resume_text}
""".strip()
