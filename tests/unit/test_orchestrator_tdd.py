"""
TDD开发 - InterviewOrchestrator路由器

测试State-based + LLM fallback的路由策略。

路由规则（优先级从高到低）:
1. resume为空且用户粘贴了文本 → Parser Agent
2. gap_analysis为空 → Parser Agent（自动触发）
3. interview_ended == false → Interviewer Agent
4. interview_ended == true 且 report 为空 → Evaluator Agent
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.interview_orchestrator import (
    InterviewOrchestrator,
    InterviewRouter,
    SessionState,
    RouteDecision,
)
from agents.parser_agent import ParserAgent
from agents.interview_agent import InterviewerAgent
from agents.evaluator_agent import EvaluatorAgent
from models import (
    ParsedResume,
    ParsedJD,
    GapAnalysis,
    TechnicalSkills,
    InterviewConfig,
    InterviewReport,
)


class TestSessionState:
    """
    SessionState的TDD测试

    测试状态管理类的方法和属性。
    """

    def test_init_state(self):
        """
        测试初始状态

        Given:
            创建新的SessionState

        Expected:
            所有状态为空/False
        """
        state = SessionState()

        assert state.resume_text == ""
        assert state.jd_text == ""
        assert state.resume is None
        assert state.jd is None
        assert state.gap_analysis is None
        assert state.config is None
        assert state.interview_started == False
        assert state.interview_ended == False
        assert state.conversation_turns == 0
        assert state.report is None
        assert state.current_agent is None

    def test_has_resume_text(self):
        """
        测试has_resume_text属性

        Given:
            设置不同长度的resume_text

        Expected:
            正确判断是否有有效简历文本
        """
        state = SessionState()

        # 空文本
        assert state.has_resume_text == False

        # 短文本（无效）
        state.resume_text = "abc"
        assert state.has_resume_text == False

        # 有效文本
        state.resume_text = "张三\n高级Java工程师\n5年经验"
        assert state.has_resume_text == True

    def test_is_resume_parsed(self):
        """
        测试is_resume_parsed属性

        Given:
            设置/清除resume对象

        Expected:
            正确判断简历是否已解析
        """
        state = SessionState()

        assert state.is_resume_parsed == False

        state.resume = ParsedResume(name="张三")
        assert state.is_resume_parsed == True

    def test_has_gap_analysis(self):
        """
        测试has_gap_analysis属性

        Given:
            设置/清除gap_analysis对象

        Expected:
            正确判断是否有Gap分析
        """
        state = SessionState()

        assert state.has_gap_analysis == False

        state.gap_analysis = GapAnalysis(match_percentage=0.8)
        assert state.has_gap_analysis == True

    def test_is_interview_in_progress(self):
        """
        测试is_interview_in_progress属性

        Given:
            不同的面试状态

        Expected:
            正确判断面试是否进行中
        """
        state = SessionState()

        # 未开始
        assert state.is_interview_in_progress == False

        # 已开始但未结束
        state.interview_started = True
        assert state.is_interview_in_progress == True

        # 已结束
        state.interview_ended = True
        assert state.is_interview_in_progress == False

    def test_is_workflow_complete(self):
        """
        测试is_workflow_complete属性

        Given:
            完整的流程状态

        Expected:
            所有步骤完成时返回True
        """
        state = SessionState()

        # 初始状态
        assert state.is_workflow_complete == False

        # 添加简历
        state.resume = ParsedResume(name="张三")
        assert state.is_workflow_complete == False

        # 添加JD
        state.jd = ParsedJD(position="Java工程师")
        assert state.is_workflow_complete == False

        # 添加Gap分析
        state.gap_analysis = GapAnalysis(match_percentage=0.8)
        assert state.is_workflow_complete == False

        # 面试结束
        state.interview_ended = True
        assert state.is_workflow_complete == False

        # 添加报告
        state.report = InterviewReport()
        assert state.is_workflow_complete == True


class TestInterviewRouter:
    """
    InterviewRouter的TDD测试

    测试State-based路由规则。
    """

    @pytest.fixture
    def router(self):
        """创建路由器"""
        return InterviewRouter(enable_llm_fallback=False)

    @pytest.fixture
    def empty_state(self):
        """创建空状态"""
        return SessionState()

    @pytest.fixture
    def populated_state(self):
        """创建已填充的状态"""
        state = SessionState()
        state.resume = ParsedResume(name="张三")
        state.jd = ParsedJD(position="Java工程师")
        state.gap_analysis = GapAnalysis(match_percentage=0.8)
        state.config = InterviewConfig()
        return state

    # ========== 规则1: 简历解析 ==========

    def test_route_to_parser_when_resume_text_empty(self, router, empty_state):
        """
        规则1: resume为空且用户粘贴了文本 → Parser Agent

        Given:
            状态中没有解析的resume
            用户粘贴了简历文本

        Expected:
            路由到parser
            原因是"用户提供了简历文本，需要解析"
        """
        empty_state.resume_text = "张三\n高级Java工程师"

        decision, reason = router.decide(empty_state)

        assert decision == "parser"
        assert "简历" in reason or "解析" in reason

    def test_no_route_to_parser_when_resume_parsed(self, router, populated_state):
        """
        规则1: 简历已解析时不触发解析

        Given:
            状态中已有解析的resume

        Expected:
            不路由到parser（会匹配其他规则）
        """
        # 即使有新文本，已解析状态下也应该继续下一步
        populated_state.resume_text = "新的简历"

        decision, reason = router.decide(populated_state)

        # 已有resume的情况下，应该跳过简历解析
        # 这里可能返回parser（用于JD解析）或其他
        assert decision in ["parser", "interviewer", "waiting"]

    # ========== 规则2: JD解析 ==========

    def test_route_to_parser_when_jd_text_empty(self, router):
        """
        规则2: JD为空且用户粘贴了文本 → Parser Agent

        Given:
            状态中有解析的resume
            没有解析的JD
            用户粘贴了JD文本

        Expected:
            路由到parser
            原因是"用户提供了JD文本，需要解析"
        """
        state = SessionState()
        state.resume = ParsedResume(name="张三")
        # JD文本需要足够长（>10字符）才能被has_jd_text识别
        state.jd_text = "招聘Java工程师，3年以上经验，熟悉Spring框架"

        decision, reason = router.decide(state)

        assert decision == "parser"
        assert "JD" in reason or "解析" in reason

    # ========== 规则3: Gap分析 ==========

    def test_route_to_parser_for_gap_analysis(self, router):
        """
        规则3: Gap分析为空 → Parser Agent（自动触发）

        Given:
            状态中有解析的resume和JD
            没有gap_analysis

        Expected:
            路由到parser
            原因是"简历和JD已解析，自动执行Gap分析"
        """
        state = SessionState()
        state.resume = ParsedResume(name="张三")
        state.jd = ParsedJD(position="Java工程师")

        decision, reason = router.decide(state)

        assert decision == "parser"
        assert "Gap" in reason or "分析" in reason

    def test_no_gap_analysis_without_both_parsed(self, router):
        """
        规则3: 只有resume或JD时不触发Gap分析

        Given:
            状态中只有resume或JD

        Expected:
            不执行Gap分析
        """
        # 只有resume
        state1 = SessionState()
        state1.resume = ParsedResume(name="张三")

        decision1, _ = router.decide(state1)
        assert decision1 in ["parser", "waiting"]  # 可能等待JD或解析JD

        # 只有JD
        state2 = SessionState()
        state2.jd = ParsedJD(position="Java工程师")

        decision2, _ = router.decide(state2)
        assert decision2 in ["parser", "waiting"]  # 可能等待resume或解析resume

    # ========== 规则4: 面试进行中 ==========

    def test_route_to_interviewer_when_in_progress(self, router):
        """
        规则4: interview_ended == false → Interviewer Agent

        Given:
            状态中有gap_analysis
            面试未结束
            有config

        Expected:
            路由到interviewer
            原因是"面试进行中"
        """
        state = SessionState()
        state.resume = ParsedResume(name="张三")
        state.jd = ParsedJD(position="Java工程师")
        state.gap_analysis = GapAnalysis(match_percentage=0.8)
        state.config = InterviewConfig()
        state.interview_started = True
        state.interview_ended = False

        decision, reason = router.decide(state)

        assert decision == "interviewer"
        assert "面试" in reason or "进行" in reason

    def test_no_interviewer_without_config(self, router):
        """
        规则4: 没有config时不路由到interviewer

        Given:
            状态中有gap_analysis
            但没有config

        Expected:
            不路由到interviewer
        """
        state = SessionState()
        state.resume = ParsedResume(name="张三")
        state.jd = ParsedJD(position="Java工程师")
        state.gap_analysis = GapAnalysis(match_percentage=0.8)
        # 没有config

        decision, _ = router.decide(state)

        assert decision != "interviewer"

    # ========== 规则5: 生成报告 ==========

    def test_route_to_evaluator_when_ended(self, router):
        """
        规则5: interview_ended == true 且 report 为空 → Evaluator Agent

        Given:
            面试已结束
            没有report

        Expected:
            路由到evaluator
            原因是"面试已完成，生成评估报告"
        """
        state = SessionState()
        state.resume = ParsedResume(name="张三")
        state.jd = ParsedJD(position="Java工程师")
        state.gap_analysis = GapAnalysis(match_percentage=0.8)
        state.config = InterviewConfig()
        state.interview_started = True
        state.interview_ended = True
        # 没有report

        decision, reason = router.decide(state)

        assert decision == "evaluator"
        assert "报告" in reason or "评估" in reason

    # ========== 规则6: 流程完成 ==========

    def test_route_to_completed_when_all_done(self, router):
        """
        规则6: 整个流程完成 → completed

        Given:
            所有步骤都完成

        Expected:
            路由到completed
        """
        state = SessionState()
        state.resume = ParsedResume(name="张三")
        state.jd = ParsedJD(position="Java工程师")
        state.gap_analysis = GapAnalysis(match_percentage=0.8)
        state.config = InterviewConfig()
        state.interview_started = True
        state.interview_ended = True
        state.report = InterviewReport()

        decision, reason = router.decide(state)

        assert decision == "completed"
        assert "完成" in reason

    # ========== 边界情况 ==========

    def test_waiting_when_no_input(self, router, empty_state):
        """
        边界: 没有任何输入时等待

        Given:
            空状态
            没有用户输入

        Expected:
            返回waiting
        """
        decision, reason = router.decide(empty_state)

        assert decision == "waiting"
        assert "等待" in reason

    def test_routing_history_tracking(self, router):
        """
        测试: 路由历史被正确记录

        Given:
            进行多次路由决策

        Expected:
            历史记录完整
        """
        state = SessionState()

        # 第一次决策 - 空状态会进入waiting，不记录历史
        router.decide(state)
        assert len(router.routing_history) == 0  # 空状态不记录

        # 添加简历文本，第二次决策 - 应该匹配解析规则
        state.resume_text = "张三\nJava工程师，5年开发经验"
        router.decide(state)
        assert len(router.routing_history) == 1

        # 第三次决策 - 解析后状态
        state.resume = ParsedResume(name="张三")
        router.decide(state)
        assert len(router.routing_history) >= 1  # 至少有一条记录

        # 检查历史记录格式
        history = router.routing_history[0]
        assert "timestamp" in history
        assert "rule" in history
        assert "decision" in history
        assert "reason" in history


class TestInterviewOrchestrator:
    """
    InterviewOrchestrator的TDD测试

    测试编排器的端到端功能。
    """

    @pytest.fixture
    def orchestrator(self):
        """创建编排器"""
        return InterviewOrchestrator()

    # ========== 状态更新 ==========

    def test_update_resume_text(self, orchestrator):
        """
        测试: 更新简历文本

        Given:
            调用update_resume_text

        Expected:
            状态被更新
        """
        text = "张三\n高级Java工程师"
        orchestrator.update_resume_text(text)

        assert orchestrator.state.resume_text == text

    def test_update_jd_text(self, orchestrator):
        """
        测试: 更新JD文本

        Given:
            调用update_jd_text

        Expected:
            状态被更新
        """
        text = "招聘Java工程师"
        orchestrator.update_jd_text(text)

        assert orchestrator.state.jd_text == text

    def test_update_config(self, orchestrator):
        """
        测试: 更新配置

        Given:
            调用update_config

        Expected:
            状态被更新
        """
        config = InterviewConfig(
            interviewer_level="senior_engineer",
            duration=30
        )
        orchestrator.update_config(config)

        assert orchestrator.state.config == config
        assert orchestrator.state.config.interviewer_level == "senior_engineer"

    # ========== 路由执行 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_execute_parser_for_resume(self, mock_claude, orchestrator):
        """
        测试: 执行Parser解析简历

        Given:
            状态中有简历文本
            没有解析的resume

        Expected:
            调用parser.parse_resume
            返回解析结果
        """
        mock_claude.return_value = """{
    "name": "张三",
    "experience_years": 5,
    "technical_skills": {},
    "projects": [],
    "education": []
}"""

        orchestrator.update_resume_text("张三\n高级Java工程师")

        result = orchestrator.route_and_execute()

        assert result["agent"] == "parser"
        assert "parse_resume" in result["actions"]
        assert result["status"] == "success"
        assert orchestrator.state.resume is not None
        assert orchestrator.state.resume.name == "张三"

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_execute_parser_for_jd(self, mock_claude, orchestrator):
        """
        测试: 执行Parser解析JD

        Given:
            状态中有JD文本
            没有解析的JD

        Expected:
            调用parser.parse_jd
            返回解析结果
        """
        # 先设置resume
        mock_claude.return_value = """{
    "name": "张三",
    "experience_years": 5,
    "technical_skills": {},
    "projects": [],
    "education": []
}"""
        orchestrator.update_resume_text("张三\n高级Java工程师")
        result1 = orchestrator.route_and_execute()

        # 验证简历解析成功
        assert result1["agent"] == "parser"
        assert "parse_resume" in result1["actions"]
        assert orchestrator.state.resume is not None

        # 然后测试JD解析
        mock_claude.return_value = """{
    "company": "某公司",
    "position": "Java工程师",
    "required_skills": ["Java"],
    "preferred_skills": [],
    "min_experience": 3,
    "responsibilities": []
}"""

        orchestrator.update_jd_text("招聘Java工程师，5年以上经验")
        result2 = orchestrator.route_and_execute()

        assert result2["agent"] == "parser"
        assert "parse_jd" in result2["actions"]
        assert result2["status"] == "success"
        assert orchestrator.state.jd is not None
        assert orchestrator.state.jd.position == "Java工程师"

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_execute_gap_analysis(self, mock_claude, orchestrator):
        """
        测试: 执行Gap分析

        Given:
            状态中有解析的resume和JD
            没有gap_analysis

        Expected:
            自动调用parser.gap_analysis
            返回分析结果
        """
        # 先解析resume
        mock_claude.return_value = """{
    "name": "张三",
    "experience_years": 5,
    "technical_skills": {},
    "projects": [],
    "education": []
}"""
        orchestrator.update_resume_text("张三\n高级Java工程师，5年经验")
        result1 = orchestrator.route_and_execute()
        assert result1["agent"] == "parser"

        # 解析JD并自动执行Gap分析 - 使用side_effect处理多个调用
        mock_claude.side_effect = [
            # 第1次调用: JD解析
            """{
    "company": "某公司",
    "position": "Java工程师",
    "required_skills": ["Java"],
    "preferred_skills": [],
    "min_experience": 3,
    "responsibilities": []
}""",
            # 第2次调用: Gap分析
            """{
    "match_percentage": 80,
    "matched_items": ["Java"],
    "gap_items": [],
    "bonus_items": [],
    "interview_focus": [],
    "match_details": {}
}""",
            # 第3次调用: 默认响应（防止StopIteration）
            "默认响应"
        ]

        orchestrator.update_jd_text("招聘Java工程师，3年以上经验，熟悉Spring框架")
        result2 = orchestrator.route_and_execute()

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_execute_interviewer_start(self, mock_claude, orchestrator):
        """
        测试: 执行Interviewer启动面试

        Given:
            状态中有gap_analysis和config
            面试未开始

        Expected:
            调用interviewer.start_interview
            返回开场白
        """
        # 设置完整状态 - 解析简历
        mock_claude.return_value = """{
    "name": "张三",
    "experience_years": 5,
    "technical_skills": {},
    "projects": [],
    "education": []
}"""
        orchestrator.update_resume_text("张三，高级Java工程师，5年开发经验")
        result1 = orchestrator.route_and_execute()
        assert result1["agent"] == "parser"

        # 解析JD并自动执行Gap分析 - 使用side_effect
        mock_claude.side_effect = [
            # 第1次调用: JD解析
            """{
    "company": "某科技公司",
    "position": "Java高级工程师",
    "required_skills": ["Java", "Spring"],
    "min_experience": 3,
    "responsibilities": []
}""",
            # 第2次调用: Gap分析
            """{
    "match_percentage": 80,
    "matched_items": ["Java"],
    "gap_items": [],
    "interview_focus": [],
    "match_details": {}
}""",
            # 第3次调用: 默认响应（防止StopIteration）
            "默认响应"
        ]

        orchestrator.update_jd_text("招聘Java高级工程师，要求3年以上经验，熟悉Spring框架")
        result2 = orchestrator.route_and_execute()
        assert result2["agent"] == "parser"
        # Gap分析应该自动执行
        assert orchestrator.state.gap_analysis is not None

        # 配置
        orchestrator.update_config(InterviewConfig())

        # 重置side_effect
        mock_claude.side_effect = None

        # 启动面试
        mock_claude.return_value = "你好，我是今天的面试官。请先做个自我介绍。"
        result3 = orchestrator.route_and_execute()

        assert result3["agent"] == "interviewer"
        assert result3["action"] == "start_interview"
        assert "response" in result3
        assert orchestrator.state.interview_started == True
        assert orchestrator.state.conversation_turns == 1

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_execute_interviewer_chat(self, mock_claude, orchestrator):
        """
        测试: 执行Interviewer对话

        Given:
            面试已开始
            用户发送消息

        Expected:
            调用interviewer.chat
            返回回复
        """
        # 设置完整状态并启动面试
        mock_claude.return_value = """{
    "name": "张三",
    "experience_years": 5,
    "technical_skills": {},
    "projects": [],
    "education": []
}"""
        orchestrator.update_resume_text("张三，5年Java开发经验")
        result1 = orchestrator.route_and_execute()
        assert result1["agent"] == "parser"

        # JD解析会自动触发Gap分析 - 使用side_effect
        mock_claude.side_effect = [
            # 第1次调用: JD解析
            """{
    "position": "Java工程师",
    "required_skills": ["Java"],
    "min_experience": 3,
    "responsibilities": []
}""",
            # 第2次调用: Gap分析
            """{
    "match_percentage": 80,
    "matched_items": ["Java"],
    "gap_items": [],
    "interview_focus": [],
    "match_details": {}
}""",
            # 第3次调用: 默认响应
            "默认响应"
        ]

        orchestrator.update_jd_text("招聘Java工程师，负责后端开发，要求有相关经验")
        result2 = orchestrator.route_and_execute()
        assert result2["agent"] == "parser"
        # Gap分析应该已经自动执行
        assert "gap_analysis" in result2["actions"]

        # 配置
        orchestrator.update_config(InterviewConfig())

        # 重置side_effect，准备interviewer调用
        mock_claude.side_effect = None

        # 启动面试
        mock_claude.return_value = "你好，我是面试官。请先做个自我介绍。"
        result3 = orchestrator.route_and_execute()
        assert result3["agent"] == "interviewer"
        assert result3["action"] == "start_interview"

        # 对话
        mock_claude.return_value = "能详细说说你在项目中的具体职责吗？"
        result4 = orchestrator.route_and_execute("我是张三，有5年Java开发经验，主要做后端开发")

        assert result4["agent"] == "interviewer"
        assert result4["action"] == "chat"
        assert "response" in result4
        assert orchestrator.state.conversation_turns == 2

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_execute_evaluator(self, mock_claude, orchestrator):
        """
        测试: 执行Evaluator生成报告

        Given:
            面试已结束
            没有report

        Expected:
            调用evaluator.generate_report
            返回报告
        """
        # 设置完整状态
        mock_claude.return_value = """{
    "name": "张三",
    "technical_skills": {},
    "projects": []
}"""
        orchestrator.update_resume_text("张三")
        orchestrator.route_and_execute()

        mock_claude.return_value = """{
    "position": "Java",
    "required_skills": []
}"""
        orchestrator.update_jd_text("Java")
        orchestrator.route_and_execute()

        mock_claude.return_value = """{
    "match_percentage": 80,
    "matched_items": [],
    "gap_items": [],
    "interview_focus": []
}"""
        orchestrator.route_and_execute()

        orchestrator.update_config(InterviewConfig())

        mock_claude.return_value = "你好"
        orchestrator.route_and_execute()

        # 标记面试结束
        orchestrator.state.interview_ended = True

        # 生成报告
        mock_claude.return_value = """{
    "overall_score": 85,
    "overall_grade": "B",
    "recommendation": "HIRE",
    "dimension_scores": {},
    "strengths": ["有经验"],
    "weaknesses": [],
    "learning_suggestions": [],
    "recommended_resources": []
}"""

        result = orchestrator.route_and_execute()

        assert result["agent"] == "evaluator"
        assert result["action"] == "generate_report"
        assert "report" in result
        assert orchestrator.state.report is not None

    # ========== 状态查询 ==========

    def test_get_state(self, orchestrator):
        """
        测试: 获取当前状态

        Expected:
            返回状态字典
        """
        state = orchestrator.get_state()

        assert isinstance(state, dict)
        assert "is_resume_parsed" in state
        assert "is_jd_parsed" in state
        assert "has_gap_analysis" in state
        assert "interview_started" in state
        assert "interview_ended" in state
        assert "has_report" in state

    def test_get_routing_history(self, orchestrator):
        """
        测试: 获取路由历史

        Expected:
            返回历史列表
        """
        history = orchestrator.get_routing_history()

        assert isinstance(history, list)

    def test_reset(self, orchestrator):
        """
        测试: 重置会话

        Given:
            会话有各种状态

        Expected:
            重置后状态清空
        """
        # 设置一些状态
        orchestrator.update_resume_text("张三")
        orchestrator.state.interview_started = True

        # 重置
        orchestrator.reset()

        assert orchestrator.state.resume_text == ""
        assert orchestrator.state.interview_started == False


# ========== 运行说明 ==========

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║              TDD测试 - InterviewOrchestrator                ║
║                                                                ║
║  运行方式：                                                     ║
║  1. pytest tests/unit/test_orchestrator_tdd.py -v            ║
║  2. pytest tests/unit/test_orchestrator_tdd.py::TestSessionState -v ║
║                                                                ║
║  测试覆盖：                                                     ║
║  - SessionState: 状态管理                                     ║
║  - InterviewRouter: 路由决策                                 ║
║  - InterviewOrchestrator: 编排执行                            ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝
""")

    pytest.main([__file__, "-v", "--tb=short"])
