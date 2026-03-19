"""
InterviewerAgent - 面试官Agent

核心功能：面试对话、追问、Prompt生成。
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import uuid
import logging

from agents.base_agent import StatefulAgent
from config import (
    settings,
    INTERVIEWER_LEVELS,
    INTERVIEWER_STYLES,
    FOCUS_AREAS,
    FOLLOW_UP_STRATEGIES,
)
from models import (
    InterviewConfig,
    InterviewState,
    ConversationTurn,
    AnswerGrade,
    AgentMessage,
    AgentThought,
    AgentResponse,
)

logger = logging.getLogger(__name__)


class InterviewerAgent(StatefulAgent):
    """面试官Agent"""

    def __init__(self):
        super().__init__(name="InterviewerAgent")

    def _setup_tools(self):
        """设置工具"""
        self.register_tool("start_interview", self.start_interview)
        self.register_tool("chat", self.chat)
        self.register_tool("end_interview", self.end_interview)

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """获取动态System Prompt（基于Gap分析的针对性面试）"""
        config = context.get("config", InterviewConfig())
        resume = context.get("resume")
        jd = context.get("jd")
        gap = context.get("gap")

        # 获取角色描述
        level_desc = INTERVIEWER_LEVELS.get(
            config.interviewer_level,
            INTERVIEWER_LEVELS["senior_engineer"]
        )

        # 获取风格描述
        style_desc = INTERVIEWER_STYLES.get(
            config.interviewer_style,
            INTERVIEWER_STYLES["professional"]
        )

        # 获取考察重点
        focus_list = "\n".join(
            f"  - {FOCUS_AREAS.get(f, f)}"
            for f in config.focus_areas
            if f in FOCUS_AREAS
        )

        # 语言要求
        lang_req = {
            "zh": "请全程使用中文",
            "en": "Please conduct in English",
            "mixed": "中英混合，技术术语可用英文"
        }.get(config.language, "请全程使用中文")

        # 构建详细的候选人画像
        resume_details = ""
        if resume:
            projects_detail = "\n".join([
                f"  - {p.name}: {p.description[:80] if p.description else ''} (技术栈: {', '.join(p.tech_stack[:5]) if p.tech_stack else 'N/A'})"
                for p in resume.projects[:3]
            ])
            resume_details = f"""
### 候选人详细画像
  姓名: {resume.name or '候选人'}
  工作年限: {resume.experience_years} 年
  当前职位: {resume.current_role or 'N/A'}

  技术栈:
    编程语言: {', '.join(resume.technical_skills.languages)}
    框架: {', '.join(resume.technical_skills.frameworks)}
    中间件: {', '.join(resume.technical_skills.middleware)}
    数据库: {', '.join(resume.technical_skills.databases)}
    DevOps: {', '.join(resume.technical_skills.devops)}

  核心项目经验:
{projects_detail}
"""

        # 构建详细的JD要求
        jd_details = ""
        if jd:
            responsibilities_detail = "\n".join([
                f"  - {r}"
                for r in (jd.responsibilities[:5] if jd.responsibilities else [])
            ])
            jd_details = f"""
### 目标岗位详细要求
  职位: {jd.position or 'N/A'}
  公司: {jd.company or 'N/A'}
  级别: {jd.level or 'N/A'}

  必须技能（硬性要求）: {', '.join(jd.required_skills)}

  加分技能: {', '.join(jd.preferred_skills)}

  核心职责:
{responsibilities_detail}
"""

        # 构建Gap分析详细说明
        gap_analysis_detail = ""
        interview_focus_areas = []
        if gap:
            # 匹配项
            matched_detail = "\n".join([f"  - {m}" for m in gap.matched_items[:10]])

            # 差距项（重点考察）
            gap_detail = "\n".join([f"  ⚠️ {g}" for g in gap.gap_items])

            # 面试重点（从interview_focus提取）
            focus_items = []
            for item in gap.interview_focus[:8]:
                focus_items.append(f"  🔍 {item}")
            interview_focus_detail = "\n".join(focus_items)

            # 匹配度详情
            match_details = []
            for key, detail in gap.match_details.items():
                if isinstance(detail, dict):
                    match_details.append(f"  - {detail.get('category', key)}: {detail.get('notes', 'N/A')}")

            gap_analysis_detail = f"""
### Gap分析结果（匹配度: {gap.match_percentage*100:.0f}%）

#### ✅ 简历满足的技能
{matched_detail}

#### ⚠️ JD要求但简历未体现的差距项（需要重点考察）
{gap_detail}

#### 🔍 面试考察重点（基于Gap分析）
{interview_focus_detail}

#### 📊 各维度匹配详情
{chr(10).join(match_details) if match_details else ''}
"""

            # 提取面试重点供后续使用
            interview_focus_areas = gap.interview_focus[:5]

        prompt = f"""你正在进行一场针对性的技术面试。

## 你的身份
{level_desc}

{style_desc}

## 语言要求
{lang_req}

## 考察重点（来自配置）
{focus_list}

## 面试时长
{config.duration} 分钟

{resume_details}

{jd_details}

{gap_analysis_detail}

## 面试策略（基于Gap分析的针对性提问）

### 提问原则
1. **优先验证差距项**: 对"JD要求但简历未体现"的技能重点考察
2. **深挖匹配项**: 对简历声称掌握的技能，通过实际项目细节验证真实水平
3. **场景化提问**: 结合JD的业务场景和候选人的项目经验
4. **递进式追问**: 从概念→实践→深度→边界条件

### 具体提问方向
{f'''
- 必须考察的差距项: {', '.join(gap.gap_items[:3])}
- 需要验证的核心技能: {', '.join(jd.required_skills[:5]) if jd else ''}
- 结合项目的场景问题: 从候选人项目经验出发
- 技术深度问题: 架构设计、技术选型、性能优化
''' if gap else '- 从候选人的技术栈和项目经验出发提问'}

### 面试流程
1. 自我介绍（1分钟）
2. 从**差距项**切入，了解候选人实际掌握程度
3. 结合**JD核心要求**和候选人**项目经验**深入提问
4. 根据候选人回答质量决定是否追问：
   - 回答完整正确 → 升维追问或下一题
   - 部分正确 → 追问细节，引导补充
   - 回答模糊 → 要求举例说明
   - 明显错误 → 给提示再给机会
   - 不会 → 给参考答案，标记弱项
5. 每个问题最多追问2-3层
6. 控制节奏，在时间内完成所有考察维度
7. 面试结束时总结考察内容

## 重要提醒
- 你的目标是**评估候选人是否真正适合这个岗位**，不只是聊天
- 对差距项要温和但坚定地考察，给候选人展示能力的机会
- 关注候选人解决问题的思路，不只是标准答案
- 面试结束时总结一下今天的考察内容和初步评估

现在开始面试吧！
"""
        return prompt

    def execute(self, action: str, context: Dict[str, Any]) -> Any:
        """执行动作"""
        if action == "start":
            return self.start_interview(context)
        elif action == "chat":
            return self.chat(context)
        elif action == "end":
            return self.end_interview(context)
        else:
            raise ValueError(f"Unknown action: {action}")

    # ========== 面试流程 ==========

    def start_interview(self, context: Dict[str, Any]) -> str:
        """
        开始面试

        Args:
            context: 上下文（包含config, resume, jd, gap）

        Returns:
            开场白
        """
        # 初始化状态
        self.state = InterviewState(
            session_id=str(uuid.uuid4()),
            started_at=datetime.now().isoformat(),
            config=context.get("config", InterviewConfig()),
            resume=context.get("resume"),
            jd=context.get("jd"),
            gap=context.get("gap"),
            current_turn=1  # 面试从第1轮开始
        )

        # 获取System Prompt
        system_prompt = self.get_system_prompt(context)

        # 生成开场白
        response = self.call_claude(
            messages=[{
                "role": "user",
                "content": "请开始面试，先做自我介绍。"
            }],
            system_prompt=system_prompt,
            max_tokens=500,
            temperature=0.8
        )

        # 记录到对话历史
        self.add_to_memory(self.create_message("assistant", response))
        self.state.current_turn = 1

        return response

    def chat(self, context: Dict[str, Any]) -> str:
        """
        对话循环

        Args:
            context: 上下文（包含user_message）

        Returns:
            Agent响应
        """
        user_input = context.get("user_message", "")
        if not user_input:
            return "请输入你的回答。"

        # 添加用户消息到记忆
        self.add_to_memory(self.create_message("user", user_input))

        # 构建消息列表
        messages = self._build_messages()

        # 获取System Prompt
        system_prompt = self.get_system_prompt({
            "config": self.state.config,
            "resume": self.state.resume,
            "jd": self.state.jd,
            "gap": self.state.gap
        })

        # 调用Claude
        response = self.call_claude(
            messages=messages,
            system_prompt=system_prompt,
            max_tokens=1000,
            temperature=0.7
        )

        # 检查是否结束
        is_ended = self._check_if_ended(response)

        # 添加Agent响应到记忆
        self.add_to_memory(self.create_message("assistant", response))

        # 更新状态
        self.state.current_turn += 1
        self.state.is_ended = is_ended

        # 检查是否需要摘要
        if len(self.memory) >= 20:  # 10轮对话
            self._generate_summary()

        return response

    def end_interview(self, context: Dict[str, Any]) -> str:
        """
        结束面试

        Args:
            context: 上下文

        Returns:
            结束语
        """
        ending_prompt = """请给候选人一个总结，包括：
1. 今天的面试考察了哪些方面
2. 候选人的表现如何
3. 后续会有通知

保持专业和礼貌。"""

        response = self.call_claude(
            messages=[{
                "role": "user",
                "content": ending_prompt
            }],
            max_tokens=500,
            temperature=0.7
        )

        self.state.is_ended = True
        self.add_to_memory(self.create_message("assistant", response))

        return response

    # ========== 内部方法 ==========

    def _build_messages(self) -> List[Dict[str, str]]:
        """构建消息列表

        Returns:
            消息列表，用于Claude API调用
        """
        # 边界检查
        if not self.memory:
            logger.warning("memory为空，返回空消息列表")
            return []

        # 有摘要时：摘要 + 最近对话
        if self.state.summary:
            recent_count = min(10, len(self.memory))
            recent = [
                {"role": m.role, "content": m.content}
                for m in self.memory[-recent_count:]
            ]
            messages = [
                {"role": "user", "content": f"之前的面试摘要：\n{self.state.summary}"}
            ] + recent
            logger.debug(f"使用摘要模式，recent_count={recent_count}")
            return messages

        # 无摘要时：全部对话
        messages = [
            {"role": m.role, "content": m.content}
            for m in self.memory
        ]
        logger.debug(f"使用完整模式，memory_count={len(self.memory)}")
        return messages

    def _check_if_ended(self, response: str) -> bool:
        """检查面试是否结束"""
        ending_keywords = ["面试到这里", "今天的面试", "后续", "感谢参加", "面试到此结束", "感谢参加面试", "后续通知", "会有通知"]
        return any(keyword in response for keyword in ending_keywords)

    def _generate_summary(self):
        """生成渐进式摘要"""
        conversation_text = "\n".join([
            f"{m.role}: {m.content}"
            for m in self.memory
        ])

        summary_prompt = f"""请对以下面试对话生成摘要，包含：

1. 已问过的题目列表
2. 候选人的优势
3. 候选人的弱项
4. 尚未考察的维度

对话记录：
{conversation_text}

摘要：
"""

        summary = self.call_claude(
            messages=[{"role": "user", "content": summary_prompt}],
            max_tokens=1000,
            temperature=0.3
        )

        self.state.summary = summary

        # 清理旧记忆，保留最近5条
        self.memory = self.memory[-10:]

    def evaluate_answer(
        self,
        question: str,
        answer: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        评估回答质量（用于追问答疑）

        Args:
            question: 问题
            answer: 回答
            context: 额外上下文

        Returns:
            评估结果
        """
        prompt = f"""请评估候选人回答的质量。

问题：{question}
候选人回答：{answer}

请评估：
1. 回答质量（complete_correct / partial_correct / vague / wrong / no_answer）
2. 关键点是否覆盖
3. 是否需要追问
4. 如果需要追问，追问什么

返回JSON格式：
{{
  "quality": "回答质量",
  "key_points_covered": ["覆盖的关键点"],
  "missing_points": ["缺失的关键点"],
  "should_follow_up": true/false,
  "follow_up_focus": "追问重点",
  "depth": 当前追问深度
}}
"""

        response = self.call_claude(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "quality": "partial_correct",
                "should_follow_up": False
            }

    def generate_follow_up(
        self,
        question: str,
        answer: str,
        depth: int = 1
    ) -> str:
        """
        生成追问

        Args:
            question: 原问题
            answer: 用户回答
            depth: 当前追问深度

        Returns:
            追问内容
        """
        # 超过最大追问深度 - 直接返回，不调用API
        if depth >= settings.max_follow_up_depth:
            return "好的，我们来看下一个话题。"

        # 评估回答
        evaluation = self.evaluate_answer(question, answer)

        # 根据评估生成追问
        quality = evaluation.get("quality", "partial_correct")

        if quality == "complete_correct":
            # 升维追问
            strategy = FOLLOW_UP_STRATEGIES["complete_correct"]
            examples = strategy["examples"]
            return examples[0] if examples else "讲得不错，我们继续。"

        elif quality == "partial_correct":
            # 定向补全
            missing = evaluation.get("missing_points", [])
            if missing:
                return f"你提到了一些点，那{missing[0]}呢？"
            return "还有其他考虑吗？"

        elif quality == "vague":
            # 细节深挖
            return "能具体举个栗子吗？"

        elif quality == "wrong":
            # 纠正引导
            return "不太对，提示一下："

        else:  # no_answer
            # 提供答案
            return "没关系，这道题考察的是...我们来看下一题。"


# ========== 便捷函数 ==========

def create_interviewer() -> InterviewerAgent:
    """创建面试官Agent"""
    return InterviewerAgent()
