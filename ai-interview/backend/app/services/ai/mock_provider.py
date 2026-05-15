from app.schemas.ai import NextQuestionResult, ReportResult, ResumeAnalysis


class MockProvider:
    def analyze_resume(self, resume_text: str) -> ResumeAnalysis:
        return ResumeAnalysis(
            summary="候选人具备计算机相关学习背景，简历中包含项目或科研经历，适合围绕项目贡献、技术细节和动机匹配度展开。",
            education="教育背景信息较完整，但仍建议在面试中核实课程基础、成绩排名和目标方向匹配度。",
            projects=[
                {
                    "name": "简历核心项目",
                    "description": "候选人在简历中提到的核心项目，可能涉及算法、工程实现或科研探索。",
                    "possible_questions": ["你在项目中具体负责哪一部分？", "项目使用了哪些评价指标，结果相比 baseline 提升多少？"],
                    "risks": ["个人贡献描述可能不够具体", "缺少可量化结果或复盘"],
                }
            ],
            strengths=["经历与目标方向有一定相关性", "具备继续深挖的项目材料"],
            risks=["项目细节需要验证", "部分成果可能缺少量化指标"],
            recommended_focus=["自我介绍", "项目个人贡献", "专业基础", "申请/求职动机"],
        )

    def generate_next_question(self, turn_count: int, stage: str, latest_answer: str) -> NextQuestionResult:
        questions = [
            "请先做一个 1 分钟自我介绍，并重点说明你的核心经历和申请动机。",
            "你刚才提到的项目里，你本人最核心的贡献是什么？请具体一点。",
            "这个项目的数据来源、评价指标和最终结果分别是什么？",
            "如果重新做这个项目，你会优先改进哪一个环节？为什么？",
            "请解释一个与你目标方向相关的基础概念，并举一个实际应用例子。",
            "你为什么选择这个目标院校或岗位？它和你的长期规划有什么关系？",
            "我觉得你的回答里量化结果还不够清楚。你能用更简洁的方式重新说明吗？",
            "最后，请你用三句话总结自己最适合这个机会的理由。",
        ]
        index = min(turn_count, len(questions) - 1)
        quality = "poor" if len(latest_answer.strip()) < 30 else "medium"
        issues = ["回答偏短，缺少细节"] if quality == "poor" else ["可继续补充量化结果"]
        return NextQuestionResult(
            answer_quality=quality,
            detected_issues=issues,
            action="follow_up" if quality == "poor" else "next_question",
            stage=stage,
            interviewer_reply=questions[index],
            brief_feedback="候选人回答基本相关，但需要更多结构化细节和量化结果。",
        )

    def generate_report(self) -> ReportResult:
        return ReportResult(
            total_score=78,
            dimension_scores={
                "表达逻辑": {"score": 16, "max": 20, "comment": "表达较清楚，但部分回答缺少结构。"},
                "专业能力": {"score": 18, "max": 25, "comment": "能说明基本概念，但项目细节仍需加强。"},
                "经历匹配": {"score": 17, "max": 20, "comment": "经历与目标方向有相关性，动机可以更具体。"},
                "抗压表现": {"score": 12, "max": 15, "comment": "面对追问能够继续回答，但证据链略弱。"},
                "发展潜力": {"score": 15, "max": 20, "comment": "具备学习潜力，建议强化复盘表达。"},
            },
            overall_comment="整体表现中等偏上。候选人能够围绕经历展开回答，但项目数据、个人贡献和结果复盘需要进一步打磨。",
            strengths=["自我介绍自然", "项目背景说明较清楚", "目标方向基本明确"],
            weaknesses=["项目细节不足", "缺少量化指标", "回答结构有时不够稳定"],
            resume_risks=["简历中项目贡献描述不够具体", "部分经历缺少结果指标支撑"],
            question_reviews=[
                {
                    "question": "请介绍一下你的核心项目。",
                    "answer_summary": "用户说明了项目目标和个人参与内容，但数据集、baseline 和结果对比不足。",
                    "score": 7,
                    "comment": "回答方向正确，但细节不足。",
                    "improved_answer_suggestion": "建议按照背景、方法、个人贡献、结果、反思五段式回答。",
                }
            ],
            next_training_plan=["重新准备 1 分钟自我介绍", "补充每个项目的数据集、指标和个人贡献", "练习压力追问下的简洁回答"],
        )
