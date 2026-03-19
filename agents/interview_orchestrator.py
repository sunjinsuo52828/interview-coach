"""
Interview Orchestrator - Agent路由器和状态管理器

实现State-based + LLM fallback的路由策略:
- State-based规则优先执行
- 无法处理时使用LLM判断
"""
from typing import Dict, Any, Optional, Literal
from datetime import datetime
import json
import logging

from agents.parser_agent import ParserAgent
from agents.interview_agent import InterviewerAgent
from agents.evaluator_agent import EvaluatorAgent
from models import (
    ParsedResume,
    ParsedJD,
    GapAnalysis,
    InterviewConfig,
    InterviewReport,
)

logger = logging.getLogger(__name__)


# ========== 路由决策类型 ==========
RouteDecision = Literal[
    "parser",      # 解析Agent
    "interviewer", # 面试Agent
    "evaluator",   # 评估Agent
    "waiting",     # 等待用户输入
    "completed",   # 流程完成
    "unknown"      # 未知状态（需要LLM判断）
]


# ========== 会话状态 ==========
class SessionState:
    """
    面试会话状态

    跟踪整个面试流程的状态，用于路由决策。
    """

    def __init__(self):
        # 用户输入状态
        self.resume_text: str = ""
        self.jd_text: str = ""

        # 解析结果状态
        self.resume: Optional[ParsedResume] = None
        self.jd: Optional[ParsedJD] = None
        self.gap_analysis: Optional[GapAnalysis] = None

        # 面试配置
        self.config: Optional[InterviewConfig] = None

        # 面试状态
        self.interview_started: bool = False
        self.interview_ended: bool = False
        self.conversation_turns: int = 0

        # 评估结果
        self.report: Optional[InterviewReport] = None

        # 用户最后输入（用于判断意图）
        self.last_user_input: str = ""
        self.last_input_time: Optional[datetime] = None

        # 当前Agent
        self.current_agent: Optional[str] = None

    @property
    def has_resume_text(self) -> bool:
        """是否有简历文本"""
        return bool(self.resume_text and len(self.resume_text.strip()) > 10)

    @property
    def has_jd_text(self) -> bool:
        """是否有JD文本"""
        return bool(self.jd_text and len(self.jd_text.strip()) > 10)

    @property
    def is_resume_parsed(self) -> bool:
        """是否已解析简历"""
        return self.resume is not None

    @property
    def is_jd_parsed(self) -> bool:
        """是否已解析JD"""
        return self.jd is not None

    @property
    def has_gap_analysis(self) -> bool:
        """是否有Gap分析"""
        return self.gap_analysis is not None

    @property
    def is_interview_in_progress(self) -> bool:
        """面试是否进行中"""
        return self.interview_started and not self.interview_ended

    @property
    def is_interview_completed(self) -> bool:
        """面试是否已完成"""
        return self.interview_ended

    @property
    def has_report(self) -> bool:
        """是否有评估报告"""
        return self.report is not None

    @property
    def is_workflow_complete(self) -> bool:
        """整个流程是否完成"""
        return (
            self.is_resume_parsed
            and self.is_jd_parsed
            and self.has_gap_analysis
            and self.is_interview_completed
            and self.has_report
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "resume_text": self.resume_text[:100] + "..." if len(self.resume_text) > 100 else self.resume_text,
            "jd_text": self.jd_text[:100] + "..." if len(self.jd_text) > 100 else self.jd_text,
            "is_resume_parsed": self.is_resume_parsed,
            "is_jd_parsed": self.is_jd_parsed,
            "has_gap_analysis": self.has_gap_analysis,
            "interview_started": self.interview_started,
            "interview_ended": self.interview_ended,
            "conversation_turns": self.conversation_turns,
            "has_report": self.has_report,
            "current_agent": self.current_agent,
            # 添加解析结果对象
            "resume": self.resume.to_dict() if self.resume else None,
            "jd": {
                "company": self.jd.company,
                "position": self.jd.position,
                "location": self.jd.location,
                "required_skills": self.jd.required_skills,
                "preferred_skills": self.jd.preferred_skills,
                "min_experience": self.jd.min_experience,
                "responsibilities": self.jd.responsibilities,
                "level": self.jd.level,
            } if self.jd else None,
        }


# ========== 路由器 ==========
class InterviewRouter:
    """
    Agent路由器

    根据会话状态决定下一步应该调用哪个Agent。
    """

    # State-based 路由规则（优先级从高到低）
    ROUTING_RULES = [
        # 规则1: 简历为空且用户粘贴了文本 → Parser Agent
        {
            "name": "resume_parsing",
            "condition": lambda s: not s.is_resume_parsed and s.has_resume_text,
            "action": "parser",
            "reason": "用户提供了简历文本，需要解析"
        },
        # 规则2: JD为空且用户粘贴了文本（且简历已解析或有简历文本） → Parser Agent
        {
            "name": "jd_parsing",
            "condition": lambda s: (
                not s.is_jd_parsed and s.has_jd_text and
                (s.is_resume_parsed or s.has_resume_text)
            ),
            "action": "parser",
            "reason": "用户提供了JD文本，需要解析"
        },
        # 规则3: Gap分析为空 → Parser Agent（自动触发）
        {
            "name": "gap_analysis",
            "condition": lambda s: s.is_resume_parsed and s.is_jd_parsed and not s.has_gap_analysis,
            "action": "parser",
            "reason": "简历和JD已解析，自动执行Gap分析"
        },
        # 规则4: 面试未结束 → Interviewer Agent
        {
            "name": "interview_in_progress",
            "condition": lambda s: s.has_gap_analysis and not s.is_interview_completed and s.config is not None,
            "action": "interviewer",
            "reason": "面试进行中"
        },
        # 规则5: 面试已结束且无报告 → Evaluator Agent
        {
            "name": "generate_report",
            "condition": lambda s: s.is_interview_completed and not s.has_report,
            "action": "evaluator",
            "reason": "面试已完成，生成评估报告"
        },
        # 规则6: 流程完成 → 完成
        {
            "name": "workflow_complete",
            "condition": lambda s: s.is_workflow_complete,
            "action": "completed",
            "reason": "整个流程已完成"
        },
    ]

    def __init__(self, enable_llm_fallback: bool = True):
        """
        初始化路由器

        Args:
            enable_llm_fallback: 是否启用LLM fallback
        """
        self.enable_llm_fallback = enable_llm_fallback
        self.routing_history: list = []

    def decide(self, state: SessionState, user_input: str = "") -> tuple[RouteDecision, str]:
        """
        根据状态决定下一步路由

        Args:
            state: 当前会话状态
            user_input: 用户最新输入

        Returns:
            (路由决策, 决策原因)
        """
        # 更新用户输入
        if user_input:
            state.last_user_input = user_input
            state.last_input_time = datetime.now()

        # 尝试匹配state-based规则
        for rule in self.ROUTING_RULES:
            if rule["condition"](state):
                decision = rule["action"]
                reason = rule["reason"]
                self.routing_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "rule": rule["name"],
                    "decision": decision,
                    "reason": reason
                })
                logger.info(f"路由决策: {decision} ({rule['name']}): {reason}")
                return decision, reason

        # State-based规则无法处理，尝试LLM fallback
        if self.enable_llm_fallback:
            return self._llm_fallback_decide(state)

        # 默认等待用户输入
        return "waiting", "等待用户输入"

    def _llm_fallback_decide(self, state: SessionState) -> tuple[RouteDecision, str]:
        """
        LLM fallback决策

        当State-based规则无法处理时，使用LLM判断用户意图。

        Args:
            state: 当前会话状态

        Returns:
            (路由决策, 决策原因)
        """
        # 分析用户输入的意图
        user_input = state.last_user_input.lower()

        # 简单的关键词匹配（可以替换为LLM调用）
        intent_patterns = {
            "parser": ["简历", "jd", "解析", "粘贴"],
            "interviewer": ["开始面试", "面试", "提问", "回答"],
            "evaluator": ["报告", "评估", "结束"],
        }

        for agent, patterns in intent_patterns.items():
            if any(pattern in user_input for pattern in patterns):
                return agent, f"LLM识别意图: {agent}"

        # 无法判断，等待输入
        return "waiting", "LLM无法判断意图，等待用户输入"


# ========== 编排器 ==========
class InterviewOrchestrator:
    """
    Interview编排器

    协调ParserAgent、InterviewerAgent、EvaluatorAgent的工作。
    """

    def __init__(self):
        """初始化编排器"""
        self.state = SessionState()
        self.router = InterviewRouter(enable_llm_fallback=True)

        # 初始化Agent
        self.parser = ParserAgent()
        self.interviewer = InterviewerAgent()
        self.evaluator = EvaluatorAgent()

        logger.info("InterviewOrchestrator初始化完成")

    # ========== 状态更新接口 ==========

    def update_resume_text(self, text: str):
        """更新简历文本"""
        self.state.resume_text = text
        logger.info(f"简历文本已更新，长度: {len(text)}")

    def update_jd_text(self, text: str):
        """更新JD文本"""
        self.state.jd_text = text
        logger.info(f"JD文本已更新，长度: {len(text)}")

    def update_config(self, config: InterviewConfig):
        """更新面试配置"""
        self.state.config = config
        logger.info(f"面试配置已更新: {config}")

    # ========== 路由执行 ==========

    def route_and_execute(self, user_input: str = "") -> Dict[str, Any]:
        """
        路由并执行Agent动作

        Args:
            user_input: 用户输入

        Returns:
            执行结果
        """
        # 获取路由决策
        decision, reason = self.router.decide(self.state, user_input)

        # 执行对应的Agent
        if decision == "parser":
            return self._execute_parser(reason)
        elif decision == "interviewer":
            return self._execute_interviewer(user_input, reason)
        elif decision == "evaluator":
            return self._execute_evaluator(reason)
        elif decision == "completed":
            return self._return_completed()
        else:  # waiting
            return self._return_waiting(reason)

    def _execute_parser(self, reason: str) -> Dict[str, Any]:
        """执行ParserAgent"""
        self.state.current_agent = "parser"
        logger.info(f"执行ParserAgent: {reason}")

        result = {"agent": "parser", "actions": []}

        try:
            # 1. 解析简历（如果需要）
            if not self.state.is_resume_parsed and self.state.has_resume_text:
                logger.info("开始解析简历...")
                self.state.resume = self.parser.parse_resume(self.state.resume_text)
                result["actions"].append("parse_resume")
                result["resume"] = self.state.resume.to_dict()
                logger.info(f"简历解析完成: {self.state.resume.name}")

            # 2. 解析JD（如果需要）
            if self.state.is_resume_parsed and not self.state.is_jd_parsed and self.state.has_jd_text:
                logger.info("开始解析JD...")
                self.state.jd = self.parser.parse_jd(self.state.jd_text)
                result["actions"].append("parse_jd")
                result["jd"] = {
                    "position": self.state.jd.position,
                    "company": self.state.jd.company,
                    "required_skills": self.state.jd.required_skills
                }
                logger.info(f"JD解析完成: {self.state.jd.position}")

            # 3. Gap分析（如果可以）
            if self.state.is_resume_parsed and self.state.is_jd_parsed and not self.state.has_gap_analysis:
                logger.info("开始Gap分析...")
                self.state.gap_analysis = self.parser.gap_analysis(
                    self.state.resume,
                    self.state.jd
                )
                result["actions"].append("gap_analysis")
                result["gap_analysis"] = {
                    "match_percentage": self.state.gap_analysis.match_percentage,
                    "matched_items": self.state.gap_analysis.matched_items[:5],
                    "gap_items": self.state.gap_analysis.gap_items[:5],
                    "interview_focus": self.state.gap_analysis.interview_focus[:5]
                }
                logger.info(f"Gap分析完成: {self.state.gap_analysis.match_percentage*100:.0f}%")

            result["status"] = "success"
            result["reason"] = reason
            return result

        except Exception as e:
            # 处理API错误
            error_msg = str(e)
            logger.error(f"Parser执行失败: {error_msg}")

            # 检查常见错误
            if "401" in error_msg or "authentication" in error_msg.lower():
                message = "API密钥无效。请在.env文件中设置有效的ANTHROPIC_API_KEY"
            elif "rate" in error_msg.lower() or "429" in error_msg:
                message = "API调用频率限制，请稍后重试"
            elif "timeout" in error_msg.lower():
                message = "API请求超时，请检查网络连接"
            elif "insufficient" in error_msg.lower() or "quota" in error_msg.lower():
                message = "API配额不足，请充值或稍后重试"
            else:
                message = f"解析失败: {error_msg[:100]}"

            return {
                "status": "error",
                "agent": "parser",
                "message": message,
                "error_type": type(e).__name__
            }

    def _execute_interviewer(self, user_input: str, reason: str) -> Dict[str, Any]:
        """执行InterviewerAgent"""
        self.state.current_agent = "interviewer"
        logger.info(f"执行InterviewerAgent: {reason}")

        result = {"agent": "interviewer", "reason": reason}

        try:
            # 首次启动面试
            if not self.state.interview_started:
                logger.info("首次启动面试...")
                response = self.interviewer.start_interview({
                    "config": self.state.config,
                    "resume": self.state.resume,
                    "jd": self.state.jd,
                    "gap": self.state.gap_analysis
                })
                self.state.interview_started = True
                self.state.conversation_turns = 1
                result["action"] = "start_interview"
                result["response"] = response
                result["turn"] = 1
                logger.info(f"面试已启动，第{self.state.conversation_turns}轮")

            # 继续对话
            elif not self.state.interview_ended:
                logger.info(f"继续对话，第{self.state.conversation_turns + 1}轮...")
                response = self.interviewer.chat({
                    "user_message": user_input
                })
                self.state.conversation_turns += 1

                # 检查是否结束
                if self.interviewer.state.is_ended:
                    self.state.interview_ended = True
                    result["interview_ended"] = True
                    logger.info("面试已结束")

                result["action"] = "chat"
                result["response"] = response
                result["turn"] = self.state.conversation_turns
                logger.info(f"对话完成，第{self.state.conversation_turns}轮")

            result["status"] = "success"
            return result

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Interviewer执行失败: {error_msg}")

            if "401" in error_msg or "authentication" in error_msg.lower():
                message = "API密钥无效，请检查.env配置"
            elif "rate" in error_msg.lower() or "429" in error_msg:
                message = "API调用频率限制，请稍后重试"
            else:
                message = f"面试失败: {error_msg[:100]}"

            return {
                "status": "error",
                "agent": "interviewer",
                "message": message,
                "error_type": type(e).__name__
            }

    def _execute_evaluator(self, reason: str) -> Dict[str, Any]:
        """执行EvaluatorAgent"""
        self.state.current_agent = "evaluator"
        logger.info(f"执行EvaluatorAgent: {reason}")

        result = {"agent": "evaluator", "reason": reason}

        try:
            # 生成报告
            self.state.report = self.evaluator.generate_report({
                "state": self.interviewer.state
            })

            result["action"] = "generate_report"
            result["report"] = {
                "overall_score": self.state.report.overall_score,
                "overall_grade": self.state.report.overall_grade,
                "recommendation": self.state.report.recommendation,
                "strengths": self.state.report.strengths[:3],
                "weaknesses": self.state.report.weaknesses[:3],
            }
            result["status"] = "success"

            logger.info(f"报告生成完成: {self.state.report.overall_grade}")
            return result

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Evaluator执行失败: {error_msg}")

            if "401" in error_msg or "authentication" in error_msg.lower():
                message = "API密钥无效，请检查.env配置"
            elif "rate" in error_msg.lower() or "429" in error_msg:
                message = "API调用频率限制，请稍后重试"
            else:
                message = f"报告生成失败: {error_msg[:100]}"

            return {
                "status": "error",
                "agent": "evaluator",
                "message": message,
                "error_type": type(e).__name__
            }

    def _return_completed(self) -> Dict[str, Any]:
        """返回完成状态"""
        logger.info("整个流程已完成")
        return {
            "status": "completed",
            "agent": None,
            "message": "面试流程已完成，感谢使用！",
            "summary": self.state.to_dict()
        }

    def _return_waiting(self, reason: str) -> Dict[str, Any]:
        """返回等待状态"""
        return {
            "status": "waiting",
            "agent": None,
            "message": reason,
            "state": self.state.to_dict()
        }

    # ========== 状态查询 ==========

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return self.state.to_dict()

    def get_routing_history(self) -> list:
        """获取路由历史"""
        return self.router.routing_history

    def reset(self):
        """重置会话"""
        self.state = SessionState()
        self.interviewer = InterviewerAgent()  # 重置面试官
        logger.info("会话已重置")


# ========== 便捷函数 ==========

def create_orchestrator() -> InterviewOrchestrator:
    """创建Interview编排器"""
    return InterviewOrchestrator()
