"""
EvaluatorAgent - 评估Agent

负责面试评估、报告生成、学习建议。
"""
from typing import Dict, Any, List
from datetime import datetime
import json
import logging

from agents.base_agent import BaseAgent
from config import settings
from models import (
    InterviewState,
    InterviewReport,
    QuestionResult,
    DimensionScore,
    AnswerGrade,
    Recommendation,
)

logger = logging.getLogger(__name__)


class EvaluatorAgent(BaseAgent):
    """评估Agent"""

    def __init__(self):
        super().__init__(name="EvaluatorAgent")

    def _setup_tools(self):
        """设置工具"""
        self.register_tool("evaluate", self.evaluate)
        self.register_tool("generate_report", self.generate_report)

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """获取System Prompt"""
        return """你是专业的面试评估专家。你的任务是根据面试对话记录，生成客观、全面的评估报告。

评估维度：
1. 技术深度 (35%) - 对技术原理的理解程度，是否知其所以然
2. 项目经验 (25%) - 项目经历的深度和广度，解决问题的能力
3. 问题解决 (20%) - 分析问题的逻辑，解决方案的设计
4. 沟通表达 (10%) - 表达的清晰度、逻辑性、条理性
5. 学习能力 (10%) - 对新技术的关注，学习方法和习惯

输出必须是JSON格式。
"""

    def execute(self, action: str, context: Dict[str, Any]) -> Any:
        """执行动作"""
        if action == "evaluate":
            return self.evaluate(context)
        elif action == "generate_report":
            return self.generate_report(context)
        else:
            raise ValueError(f"Unknown action: {action}")

    # ========== 评估方法 ==========

    def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估面试表现（使用Chain of Thought深度分析）

        Args:
            context: 上下文（包含state或interviewer等）

        Returns:
            评估结果字典
        """
        # 获取state
        state = context.get("state")
        interviewer = context.get("interviewer")

        # 如果没有state，尝试从interviewer获取
        if not state and interviewer:
            state = interviewer.state

        if not state:
            return {"error": "No interview state provided"}

        # 构建对话记录
        conversation = self._format_conversation(state)

        # 检查是否有对话内容
        if "无对话记录" in conversation and not state.summary:
            return self._default_evaluation()

        # 获取基本信息
        resume = state.resume if hasattr(state, 'resume') else None
        jd = state.jd if hasattr(state, 'jd') else jd
        gap = state.gap if hasattr(state, 'gap') else None
        config = state.config if hasattr(state, 'config') else None

        # 构建详细的评估Prompt（Chain of Thought）
        prompt = f"""请深度分析以下面试表现，逐步思考并给出评估。

## 面试配置
- 面试官级别：{config.interviewer_level if config else 'N/A'}
- 考察重点：{', '.join(config.focus_areas if config else [])}
- 面试时长：{config.duration if config else 'N/A'}分钟

## 候选人信息
{f"- 姓名：{resume.name}" if resume else ''}
{f"- 经验：{resume.experience_years}年" if resume else ''}
{f"- 当前职位：{resume.current_role}" if resume else ''}
{f"- 技术栈：{', '.join(resume.technical_skills.to_list()[:10])}" if resume else ''}

## 目标岗位要求
{f"- 职位：{jd.position}" if jd else ''}
{f"- 级别：{jd.level}" if jd else ''}
{f"- 必须技能：{', '.join(jd.required_skills)}" if jd else ''}

## Gap分析参考
{f"- 匹配度：{gap.match_percentage*100:.0f}%" if gap else ''}
{f"- 差距项：{', '.join(gap.gap_items[:5])}" if gap and gap.gap_items else ''}

## 面试对话记录
{conversation}

请按以下步骤思考（Chain of Thought）：

**步骤1：整体印象评估**
- 候选人的表达清晰度如何？
- 回答是否切中要害？
- 是否展现了与岗位匹配的素质？

**步骤2：技术深度分析（35%权重）**
- 对技术原理的理解程度？
- 能否解释技术选型的原因？
- 是否了解技术的边界和适用场景？
- 找出2-3个具体证据

**步骤3：项目经验分析（25%权重）**
- 项目经历的深度（不只是参与，而是主导/核心）？
- 解决问题的能力和思路？
- 项目规模和复杂度是否足够？
- 找出2-3个具体证据

**步骤4：问题解决能力（20%权重）**
- 分析问题的逻辑是否清晰？
- 解决方案是否全面可行？
- 是否考虑了边界条件和异常情况？
- 找出1-2个具体证据

**步骤5：沟通表达（10%权重）**
- 表达是否清晰、有条理？
- 能否用简洁的语言解释复杂概念？
- 是否主动澄清问题？
- 找出1-2个具体证据

**步骤6：学习能力（10%权重）**
- 对新技术的关注和学习能力？
- 是否有持续学习的证据？
- 面对不会的问题时的态度？
- 找出1-2个具体证据

**步骤7：综合评估**
- 结合Gap分析，候选人是否满足岗位要求？
- 优势是什么（至少3条）？
- 弱项是什么（至少3条）？
- 给出针对性的学习建议（根据Gap和弱项）
- 给出录用建议（考虑整体匹配度和潜力）

返回JSON格式：
{{
  "overall_score": 总分(0-100),
  "overall_grade": "A/B/C/D",
  "recommendation": "HIRE/NO_HIRE/HIRE_WITH_CONDITIONS",
  "dimension_scores": {{
    "technical_depth": {{"score": 分数(0-100), "grade": "A/B/C/D", "evidence": ["具体证据1", "具体证据2"]}},
    "project_experience": {{"score": 分数(0-100), "grade": "A/B/C/D", "evidence": ["具体证据1", "具体证据2"]}},
    "problem_solving": {{"score": 分数(0-100), "grade": "A/B/C/D", "evidence": ["具体证据1"]}},
    "communication": {{"score": 分数(0-100), "grade": "A/B/C/D", "evidence": ["具体证据1"]}},
    "learning_ability": {{"score": 分数(0-100), "grade": "A/B/C/D", "evidence": ["具体证据1"]}}
  }},
  "strengths": ["优势1（具体说明）", "优势2（具体说明）", "优势3（具体说明）"],
  "weaknesses": ["弱项1（具体说明）", "弱项2（具体说明）", "弱项3（具体说明）"],
  "learning_suggestions": [
    "针对弱项1的具体学习建议（资源/方向）",
    "针对弱项2的具体学习建议（资源/方向）",
    "针对Gap分析的差距项的学习建议"
  ],
  "recommended_resources": [
    "具体书籍/课程/文档1",
    "具体书籍/课程/文档2"
  ]
}}

只返回JSON，不要其他内容。
"""

        response = self.call_claude(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,  # 增加以支持更详细的评估
            temperature=0.5
        )

        try:
            # 清理可能的Markdown格式
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                parts = cleaned_response.split("```")
                if len(parts) >= 2:
                    cleaned_response = parts[1]
                    if cleaned_response.startswith("json"):
                        cleaned_response = cleaned_response[4:]
            cleaned_response = cleaned_response.strip()

            return json.loads(cleaned_response)
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"评估JSON解析失败: {e}, 响应: {response[:200]}")
            # 解析失败，返回默认评估
            return self._default_evaluation()

    def generate_report(self, context: Dict[str, Any]) -> InterviewReport:
        """
        生成评估报告

        Args:
            context: 上下文（包含state或evaluation结果）

        Returns:
            InterviewReport对象
        """
        state = context.get("state")
        evaluation = context.get("evaluation")

        if not evaluation and state:
            # 如果没有evaluation，先评估
            evaluation = self.evaluate({"state": state})

        if not evaluation:
            return InterviewReport()

        # 构建问题结果
        question_results = []
        if state:
            for turn in state.conversation_history:
                result = QuestionResult(
                    question_id=turn.question_id or str(len(question_results) + 1),
                    question_text=turn.question_text,
                    domain=turn.question_domain,
                    user_answer=turn.user_answer,
                    score=turn.score,
                    evaluator_notes="; ".join(turn.evaluation_notes),
                    follow_ups=[]
                )
                question_results.append(result)

        # 构建维度评分
        dimension_scores = {}
        for dim, data in evaluation.get("dimension_scores", {}).items():
            dimension_scores[dim] = DimensionScore(
                dimension=dim,
                score=data.get("score", 0),
                grade=data.get("grade", "C"),
                evidence=data.get("evidence", [])
            )

        # 构建报告
        report = InterviewReport(
            session_id=state.session_id if state else "",
            generated_at=datetime.now().isoformat(),
            overall_score=evaluation.get("overall_score", 0),
            overall_grade=evaluation.get("overall_grade", "C"),
            recommendation=evaluation.get("recommendation", "NO_HIRE"),
            dimension_scores=dimension_scores,
            question_results=question_results,
            strengths=evaluation.get("strengths", []),
            weaknesses=evaluation.get("weaknesses", []),
            learning_suggestions=evaluation.get("learning_suggestions", []),
            recommended_resources=evaluation.get("recommended_resources", [])
        )

        return report

    # ========== 辅助方法 ==========

    def _format_conversation(self, state) -> str:
        """格式化对话记录（支持AgentMessage和ConversationTurn）

        Args:
            state: InterviewState对象

        Returns:
            格式化后的对话文本
        """
        # 优先从memory获取对话（InterviewerAgent存储方式）
        if hasattr(state, 'summary') and state.summary:
            formatted = [f"面试摘要：\n{state.summary}\n"]

        # 获取对话记录
        turns = None
        if hasattr(state, 'memory') and state.memory:
            # 从InterviewerAgent的memory获取
            turns = state.memory
        elif hasattr(state, 'conversation_history') and state.conversation_history:
            # 从conversation_history获取
            turns = state.conversation_history

        if not turns:
            return "无对话记录"

        formatted = []
        for i, turn in enumerate(turns):
            # 跳过无效turn
            if not turn:
                continue

            # 处理AgentMessage格式
            if hasattr(turn, 'role') and hasattr(turn, 'content'):
                role = turn.role
                content = turn.content
                if role == "assistant":
                    formatted.append(f"面试官: {content}")
                elif role == "user":
                    formatted.append(f"候选人: {content}")
                continue

            # 处理ConversationTurn格式
            question_text = getattr(turn, 'question_text', 'N/A')
            user_answer = getattr(turn, 'user_answer', 'N/A')
            score = getattr(turn, 'score', 'N/A')
            notes = getattr(turn, 'evaluation_notes', [])

            formatted.append(f"""
第{i+1}轮：
问题：{question_text}
回答：{user_answer}
评分：{score}
备注：{'; '.join(notes) if notes else '无'}
""")

        return "\n".join(formatted)

    def _default_evaluation(self) -> Dict[str, Any]:
        """默认评估（解析失败时）"""
        return {
            "overall_score": 50.0,
            "overall_grade": "C",
            "recommendation": "NO_HIRE",
            "dimension_scores": {
                "technical_depth": {"score": 50, "grade": "C", "evidence": ["无法评估"]},
                "project_experience": {"score": 50, "grade": "C", "evidence": ["无法评估"]},
                "problem_solving": {"score": 50, "grade": "C", "evidence": ["无法评估"]},
                "communication": {"score": 50, "grade": "C", "evidence": ["无法评估"]},
                "learning_ability": {"score": 50, "grade": "C", "evidence": ["无法评估"]},
            },
            "strengths": ["数据不足，无法评估"],
            "weaknesses": ["数据不足，无法评估"],
            "learning_suggestions": ["建议完成完整面试后再评估"],
            "recommended_resources": []
        }

    def get_grade_from_score(self, score: float) -> str:
        """根据分数获取等级"""
        if score >= 90:
            return AnswerGrade.A.value
        elif score >= 75:
            return AnswerGrade.B.value
        elif score >= 60:
            return AnswerGrade.C.value
        else:
            return AnswerGrade.D.value

    def get_recommendation_from_score(self, score: float) -> str:
        """根据分数获取录用建议"""
        if score >= 85:
            return Recommendation.HIRE.value
        elif score >= 70:
            return Recommendation.HIRE_WITH_CONDITIONS.value
        else:
            return Recommendation.NO_HIRE.value

    def evaluate_single_turn(
        self,
        question: str,
        answer: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        评估单轮回答（实时反馈）

        Args:
            question: 面试问题
            answer: 候选人回答
            context: 上下文信息（resume, jd, gap等）

        Returns:
            单轮评估结果
        """
        ctx = context or {}

        # 构建评估Prompt
        prompt = f"""请评估以下面试回答的质量。

## 面试问题
{question}

## 候选人回答
{answer}

## 参考信息
{f"- 候选人经验：{ctx.get('experience_years', 'N/A')}年" if 'experience_years' in ctx else ''}
{f"- 目标岗位：{ctx.get('position', 'N/A')}" if 'position' in ctx else ''}
{f"- 相关技能：{', '.join(ctx.get('relevant_skills', []))}" if 'relevant_skills' in ctx else ''}

## 评估维度

**回答完整性（30%）**
- 是否完整回答了问题的各个部分？
- 是否遗漏了关键点？

**技术准确性（40%）**
- 技术描述是否准确？
- 是否有明显错误或模糊表述？

**深度和细节（20%）**
- 是否有具体的例子或经验支撑？
- 是否深入到了技术细节？

**表达清晰度（10%）**
- 表达是否清晰有条理？
- 是否容易理解？

请评估并返回JSON：
{{
  "score": 总分(0-100),
  "grade": "A/B/C/D",
  "completeness": {{"score": 完整性分数, "feedback": "反馈"}},
  "accuracy": {{"score": 准确性分数, "feedback": "反馈"}},
  "depth": {{"score": 深度分数, "feedback": "反馈"}},
  "clarity": {{"score": 清晰度分数, "feedback": "反馈"}},
  "strengths": ["这轮回答的优点"],
  "weaknesses": ["这轮回答的不足"],
  "should_follow_up": true/false,
  "follow_up_suggestions": ["建议追问的方向"]
}}

只返回JSON，不要其他内容。
"""

        response = self.call_claude(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.5
        )

        try:
            # 清理可能的Markdown格式
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                parts = cleaned_response.split("```")
                if len(parts) >= 2:
                    cleaned_response = parts[1]
                    if cleaned_response.startswith("json"):
                        cleaned_response = cleaned_response[4:]
            cleaned_response = cleaned_response.strip()

            return json.loads(cleaned_response)
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"单轮评估JSON解析失败: {e}")
            return {
                "score": 50,
                "grade": "C",
                "completeness": {"score": 50, "feedback": "无法评估"},
                "accuracy": {"score": 50, "feedback": "无法评估"},
                "depth": {"score": 50, "feedback": "无法评估"},
                "clarity": {"score": 50, "feedback": "无法评估"},
                "strengths": [],
                "weaknesses": [],
                "should_follow_up": False,
                "follow_up_suggestions": []
            }

    def generate_learning_suggestions(
        self,
        weaknesses: List[str],
        gap_items: List[str] = None,
        career_goal: str = None
    ) -> List[str]:
        """
        生成针对性学习建议

        Args:
            weaknesses: 面试中的弱项
            gap_items: Gap分析的差距项
            career_goal: 职业目标

        Returns:
            学习建议列表
        """
        gap_info = f"\n差距项：{', '.join(gap_items)}" if gap_items else ""
        goal_info = f"\n职业目标：{career_goal}" if career_goal else ""

        prompt = f"""请根据以下信息，生成具体可执行的学习建议。

## 候选人弱项
{', '.join(weaknesses)}
{gap_info}
{goal_info}

请为每个弱项生成：
1. 具体的学习方向（明确技术栈或能力）
2. 推荐的学习资源（书籍/课程/文档/项目实践）
3. 预计学习时间
4. 如何验证学习效果

返回JSON格式：
{{
  "suggestions": [
    {{
      "area": "弱项领域",
      "current_level": "当前水平评估",
      "target_level": "目标水平",
      "learning_path": [
        "步骤1：具体的学习内容和资源",
        "步骤2：具体的学习内容和资源",
        "步骤3：实践项目建议"
      ],
      "resources": [
        {{"type": "book/course/doc", "title": "资源名称", "url": "链接（如果有）"}},
        {{"type": "book/course/doc", "title": "资源名称", "url": "链接（如果有）"}}
      ],
      "estimated_weeks": 预计周数,
      "success_criteria": "如何判断学会了的指标"
    }}
  ]
}}

只返回JSON，不要其他内容。
"""

        response = self.call_claude(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.6
        )

        try:
            # 清理可能的Markdown格式
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                parts = cleaned_response.split("```")
                if len(parts) >= 2:
                    cleaned_response = parts[1]
                    if cleaned_response.startswith("json"):
                        cleaned_response = cleaned_response[4:]
            cleaned_response = cleaned_response.strip()

            data = json.loads(cleaned_response)
            suggestions = data.get("suggestions", [])

            # 格式化为字符串列表
            formatted = []
            for s in suggestions:
                area = s.get("area", "")
                path = s.get("learning_path", [])
                resources = s.get("resources", [])
                weeks = s.get("estimated_weeks", 0)

                formatted.append(f"**{area}** (预计{weeks}周)")
                formatted.extend([f"  - {p}" for p in path])

                if resources:
                    formatted.append("  推荐资源:")
                    for r in resources:
                        title = r.get("title", "")
                        r_type = r.get("type", "")
                        formatted.append(f"    - [{r_type}] {title}")

                criteria = s.get("success_criteria", "")
                if criteria:
                    formatted.append(f"  验证标准：{criteria}")

            return formatted

        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"学习建议生成失败: {e}")
            # 返回默认建议
            return [
                f"**{w}** - 建议通过在线课程和项目实践提升"
                for w in weaknesses[:3]
            ]


# ========== 便捷函数 ==========

def evaluate_interview(state: InterviewState) -> Dict[str, Any]:
    """便捷函数：评估面试"""
    agent = EvaluatorAgent()
    return agent.evaluate({"state": state})


def generate_report(state: InterviewState) -> InterviewReport:
    """便捷函数：生成报告"""
    agent = EvaluatorAgent()
    return agent.generate_report({"state": state})
