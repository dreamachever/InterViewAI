from app.schemas.ai import ExperienceInsightResult, NextQuestionResult, ReportResult, ResumeAnalysis, ResumeDiagnosticResult


class MockProvider:
    def analyze_resume(self, resume_text: str) -> ResumeAnalysis:
        return ResumeAnalysis(
            summary="候选人具备保研面试所需的基础经历，适合围绕科研经历、项目贡献和申请动机展开追问。",
            education="教育背景信息可用于判断专业基础，建议面试中补充课程、排名和目标方向匹配度。",
            projects=[
                {
                    "name": "简历核心项目",
                    "description": "候选人在简历中提到的核心项目，可能涉及算法、工程实现或科研探索。",
                    "possible_questions": ["你在项目中具体负责哪一部分？", "项目使用了哪些评价指标，结果相比 baseline 提升多少？"],
                    "risks": ["个人贡献描述可能不够具体", "缺少可量化结果或复盘"],
                }
            ],
            strengths=["经历与目标方向有一定相关性", "具备继续深挖的项目素材"],
            risks=["项目细节需要验证", "部分成果可能缺少量化指标"],
            recommended_focus=["自我介绍", "科研潜力", "项目个人贡献", "专业基础", "申请动机"],
        )

    def generate_next_question(
        self,
        turn_count: int,
        stage: str,
        latest_answer: str,
        experience_context: list[dict] | None = None,
    ) -> NextQuestionResult:
        questions = [
            "请先做一个 1 分钟自我介绍，并重点说明你的核心经历和申请动机。",
            "你刚才提到的项目里，你本人最核心的贡献是什么？请具体一点。",
            "这个项目的数据来源、评价指标和最终结果分别是什么？",
            "如果重新做这个项目，你会优先改进哪一个环节？为什么？",
            "请解释一个与你目标方向相关的基础概念，并举一个实际应用例子。",
            "你为什么选择这个目标院校和专业方向？它和你的长期规划有什么关系？",
            "我觉得你的回答里量化结果还不够清楚。你能用更简洁的方式重新说明吗？",
            "最后，请你用三句话总结自己最适合这个机会的理由。",
        ]
        if experience_context:
            real_questions = [
                item.get("question")
                for experience in experience_context
                for item in experience.get("real_questions", [])
                if isinstance(item, dict) and item.get("question")
            ]
            if real_questions:
                questions[2] = real_questions[0]
        index = min(turn_count, len(questions) - 1)
        quality = "poor" if len(latest_answer.strip()) < 30 else "medium"
        issues = ["回答偏短，缺少细节"] if quality == "poor" else ["可以继续补充量化结果"]
        return NextQuestionResult(
            answer_quality=quality,
            detected_issues=issues,
            action="follow_up" if quality == "poor" else "next_question",
            stage=stage,
            interviewer_reply=questions[index],
            brief_feedback="候选人回答基本相关，但还需要更多结构化细节和量化结果。",
        )

    def generate_report(self) -> ReportResult:
        return ReportResult(
            total_score=78,
            dimension_scores={
                "表达逻辑": {"score": 16, "max": 20, "comment": "表达较清楚，但部分回答缺少结构。"},
                "专业能力": {"score": 18, "max": 25, "comment": "能说明基本概念，但项目细节仍需加强。"},
                "经历匹配": {"score": 17, "max": 20, "comment": "经历与目标方向有相关性，动机可以更具体。"},
                "抗压表现": {"score": 12, "max": 15, "comment": "面对追问能继续回答，但证据链略弱。"},
                "发展潜力": {"score": 15, "max": 20, "comment": "具备学习潜力，建议强化复盘表达。"},
            },
            overall_comment="整体表现中等偏上。候选人能够围绕经历展开回答，但项目数据、个人贡献和结果复盘需要进一步打磨。",
            strengths=["自我介绍自然", "项目背景说明较清楚", "目标方向基本明确"],
            weaknesses=["项目细节不足", "缺少量化指标", "回答结构有时不够稳定"],
            resume_risks=["简历中项目贡献描述不够具体", "部分经历缺少结果指标支撑"],
            question_reviews=[
                {
                    "question": "请介绍一下你的核心项目。",
                    "answer_summary": "用户说明了项目目标和个人参与内容，但数据集、baseline 和结果对比不充分。",
                    "score": 7,
                    "comment": "回答方向正确，但细节不足。",
                    "improved_answer_suggestion": "建议按照背景、方法、个人贡献、结果、反思五段式回答。",
                }
            ],
            next_training_plan=["重新准备 1 分钟自我介绍", "补充每个项目的数据集、指标和个人贡献", "练习压力追问下的简洁回答"],
        )

    def diagnose_resume(self) -> ResumeDiagnosticResult:
        return ResumeDiagnosticResult(
            overall_score=78,
            summary="简历具备保研面试的基础素材，但需要进一步突出科研问题、个人贡献和量化成果。",
            strengths=["经历方向较集中", "具备项目或科研经历", "适合围绕动机与项目细节展开面试准备"],
            weaknesses=["部分经历缺少个人贡献描述", "结果指标不够量化", "导师可能追问实验细节与复盘"],
            suggestions=[
                {
                    "priority": "high",
                    "problem": "项目描述偏过程化",
                    "advice": "补充背景问题、个人负责模块、方法选择、结果指标和复盘。",
                    "example": "负责数据清洗与对比实验，使模型 F1 相比 baseline 提升 3.2%。",
                },
                {
                    "priority": "medium",
                    "problem": "科研动机表达不足",
                    "advice": "把经历和目标导师方向、未来研究兴趣建立联系。",
                    "example": "这段经历让我开始关注多模态信息融合在教育场景中的应用。",
                },
            ],
            section_reviews=[
                {"section": "科研经历", "score": 76, "comment": "方向可用，但需要补充方法选择和结果可信度。"},
                {"section": "项目经历", "score": 80, "comment": "素材较完整，建议强化个人贡献和量化结果。"},
            ],
            follow_up_questions=[
                "你在这个项目中具体负责哪一部分？",
                "为什么选择这个方法，而不是其他 baseline？",
                "实验结果如何验证，是否有消融实验？",
                "这段经历如何支撑你的保研申请方向？",
            ],
        )

    def extract_experience_insights(self, raw_content: str, metadata: dict | None = None) -> ExperienceInsightResult:
        target = metadata or {}
        school = target.get("target_school") or "目标院校"
        major = target.get("target_major") or "目标专业"
        return ExperienceInsightResult(
            summary=f"这篇面经主要围绕 {school} {major} 的自我介绍、科研追问和专业基础展开，适合用于模拟保研复试训练。",
            interview_process=["候场", "自我介绍", "科研经历追问", "专业基础问题", "英语问答", "自由提问"],
            question_categories=[
                {
                    "category": "科研经历",
                    "frequency": "high",
                    "questions": ["你在项目中具体负责什么？", "你的实验结果如何验证？"],
                },
                {
                    "category": "专业基础",
                    "frequency": "medium",
                    "questions": ["请解释一个核心专业概念，并结合场景说明。"],
                },
            ],
            real_questions=[
                {
                    "question": "请介绍一下你的科研项目。",
                    "category": "科研经历",
                    "difficulty": "medium",
                    "source_context": "经验贴中提到导师会围绕项目背景、方法和结果连续追问。",
                }
            ],
            focus_points=["科研经历真实性", "个人贡献", "专业基础", "研究方向匹配度"],
            risk_points=[
                {
                    "level": "high",
                    "point": "项目细节容易被深挖",
                    "suggestion": "提前准备数据集、baseline、指标、误差分析和失败复盘。",
                }
            ],
            suggested_strategy=["自我介绍主动埋下科研线索", "每个项目按背景、方法、贡献、结果、反思五层准备答案"],
            timeline=[
                {
                    "step": "自我介绍",
                    "estimated_minutes": 1,
                    "notes": "通常先介绍研究兴趣和相关背景。",
                }
            ],
        )
