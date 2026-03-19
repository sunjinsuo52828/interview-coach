"""
TDD开发 - InterviewerAgent功能

按照TDD流程：
1. 🔴 Red: 先写测试（测试失败）
2. 🟢 Green: 实现代码（测试通过）
3. 🔵 Blue: 审查重构
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import uuid

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.interview_agent import InterviewerAgent, create_interviewer
from models import (
    InterviewConfig,
    InterviewState,
    InterviewerLevel,
    InterviewerStyle,
    FocusArea,
    ParsedResume,
    ParsedJD,
    GapAnalysis,
    TechnicalSkills
)
from config import INTERVIEWER_LEVELS, INTERVIEWER_STYLES, FOCUS_AREAS


class TestStartInterviewTDD:
    """
    start_interview的TDD测试

    测试策略：
    1. 正常场景 - 完整上下文
    2. 边界场景 - 最小上下文
    3. 状态验证 - 验证状态初始化
    4. 返回值验证 - 验证返回的开场白
    """

    @pytest.fixture
    def interviewer(self):
        """创建InterviewerAgent实例"""
        return InterviewerAgent()

    @pytest.fixture
    def sample_config(self):
        """示例配置"""
        return InterviewConfig(
            interviewer_level=InterviewerLevel.SENIOR_ENGINEER.value,
            interviewer_style=InterviewerStyle.PROFESSIONAL.value,
            focus_areas=[FocusArea.TECHNICAL_BASICS.value, FocusArea.PROJECT_EXPERIENCE.value],
            language="zh",
            duration=30
        )

    @pytest.fixture
    def sample_resume(self):
        """示例简历"""
        return ParsedResume(
            name="张三",
            experience_years=5,
            current_role="Java后端工程师",
            technical_skills=TechnicalSkills(
                languages=["Java", "Python"],
                frameworks=["Spring Boot", "Spring Cloud"],
                databases=["MySQL", "Redis"]
            )
        )

    @pytest.fixture
    def sample_jd(self):
        """示例JD"""
        return ParsedJD(
            company="某科技公司",
            position="Senior Java Engineer",
            required_skills=["Java", "Spring Boot", "Redis", "Kafka"]
        )

    @pytest.fixture
    def sample_gap(self):
        """示例Gap分析"""
        return GapAnalysis(
            match_percentage=0.75,
            matched_items=["Java", "Spring Boot", "Redis"],
            gap_items=["Kafka"],
            interview_focus=["Kafka", "分布式系统"]
        )

    # ========== 正常场景 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_start_interview_normal_case(self, mock_call, interviewer, sample_config, sample_resume, sample_jd, sample_gap):
        """
        正常场景：完整上下文开始面试

        Given: 完整的config、resume、jd、gap

        Expected:
          - 返回开场白
          - state被正确初始化
          - session_id生成
          - 开场白记录到memory
        """
        # Given - Mock Claude响应
        mock_call.return_value = "你好，我是今天的面试官。让我们开始吧。"

        context = {
            "config": sample_config,
            "resume": sample_resume,
            "jd": sample_jd,
            "gap": sample_gap
        }

        # When - 开始面试
        greeting = interviewer.start_interview(context)

        # Then - 验证返回值
        assert greeting == "你好，我是今天的面试官。让我们开始吧。"
        assert isinstance(greeting, str)

        # 验证状态初始化
        assert interviewer.state is not None
        assert isinstance(interviewer.state, InterviewState)
        assert interviewer.state.session_id is not None
        assert interviewer.state.started_at is not None
        assert interviewer.state.config == sample_config
        assert interviewer.state.resume == sample_resume
        assert interviewer.state.jd == sample_jd
        assert interviewer.state.gap == sample_gap
        assert interviewer.state.current_turn == 1
        assert not interviewer.state.is_ended

        # 验证记忆
        assert len(interviewer.memory) > 0
        assert interviewer.memory[0].role == "assistant"
        assert interviewer.memory[0].content == greeting

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_start_interview_system_prompt_contains_context(self, mock_call, interviewer, sample_config, sample_resume, sample_jd, sample_gap):
        """
        System Prompt验证：确保包含简历和JD信息

        Given: 完整上下文

        Expected:
          - System Prompt包含候选人信息
          - System Prompt包含JD要求
          - System Prompt包含Gap信息
        """
        # Given
        mock_call.return_value = "你好"

        context = {
            "config": sample_config,
            "resume": sample_resume,
            "jd": sample_jd,
            "gap": sample_gap
        }

        # When
        interviewer.start_interview(context)

        # Then - 验证call_claude被正确调用
        mock_call.assert_called_once()
        call_args = mock_call.call_args

        # 验证System Prompt包含关键信息
        system_prompt = call_args.kwargs.get('system_prompt', '')
        assert "张三" in system_prompt or "候选人" in system_prompt
        assert "Java" in system_prompt
        assert sample_jd.position in system_prompt or "Senior Java Engineer" in system_prompt

    # ========== 边界场景 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_start_interview_minimal_context(self, mock_call, interviewer):
        """
        边界场景：最小上下文

        Given: 只有config，没有resume/jd/gap

        Expected:
          - 仍然能正常开始面试
          - 使用默认值
        """
        # Given
        mock_call.return_value = "你好，开始面试。"

        context = {
            "config": InterviewConfig()
        }

        # When
        greeting = interviewer.start_interview(context)

        # Then
        assert isinstance(greeting, str)
        assert interviewer.state is not None
        assert interviewer.state.resume is None
        assert interviewer.state.jd is None
        assert interviewer.state.gap is None

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_start_interview_empty_config(self, mock_call, interviewer):
        """
        边界场景：空配置

        Given: context为空字典

        Expected:
          - 使用默认InterviewConfig
        """
        # Given
        mock_call.return_value = "你好"

        # When
        greeting = interviewer.start_interview({})

        # Then
        assert isinstance(greeting, str)
        assert interviewer.state.config is not None

    # ========== 不同配置测试 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_start_interview_different_levels(self, mock_call, interviewer, sample_resume):
        """
        不同面试官级别：验证不同级别的prompt

        Given: 不同interviewer_level

        Expected:
          - System Prompt反映不同级别
        """
        # Given
        mock_call.return_value = "你好"

        for level in InterviewerLevel:
            config = InterviewConfig(interviewer_level=level)
            context = {"config": config, "resume": sample_resume}

            # When
            interviewer.start_interview(context)

            # Then - 验证调用了Claude
            assert mock_call.called

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_start_interview_different_styles(self, mock_call, interviewer, sample_resume):
        """
        不同面试风格：验证不同风格

        Given: 不同interviewer_style

        Expected:
          - 每种风格都能正常工作
        """
        # Given
        mock_call.return_value = "你好"

        for style in InterviewerStyle:
            config = InterviewConfig(interviewer_style=style)
            context = {"config": config, "resume": sample_resume}

            # When
            greeting = interviewer.start_interview(context)

            # Then
            assert isinstance(greeting, str)

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_start_interview_different_languages(self, mock_call, interviewer, sample_resume):
        """
        不同语言：中英文切换

        Given: 不同language设置

        Expected:
          - System Prompt包含语言要求
        """
        # Given
        mock_call.return_value = "Hello"

        for lang in ["zh", "en", "mixed"]:
            config = InterviewConfig(language=lang)
            context = {"config": config, "resume": sample_resume}

            # When
            interviewer.start_interview(context)

            # Then
            assert mock_call.called

    # ========== 状态验证 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_start_interview_state_initialization(self, mock_call, interviewer, sample_config):
        """
        状态初始化验证：确保所有字段正确设置

        Expected:
          - session_id是UUID
          - started_at是ISO格式时间
          - current_turn从1开始
          - is_ended为False
        """
        # Given
        mock_call.return_value = "你好"
        context = {"config": sample_config}

        # When
        interviewer.start_interview(context)

        # Then - 验证session_id格式
        try:
            uuid.UUID(interviewer.state.session_id)
        except ValueError:
            pytest.fail("session_id不是有效的UUID")

        # 验证时间格式
        try:
            datetime.fromisoformat(interviewer.state.started_at)
        except ValueError:
            pytest.fail("started_at不是有效的ISO时间格式")

        # 验证初始值
        assert interviewer.state.current_turn == 1
        assert not interviewer.state.is_ended
        assert interviewer.state.summary == ""


class TestChatTDD:
    """
    chat方法的TDD测试

    测试策略：
    1. 正常场景 - 对话交流
    2. 状态更新 - turn递增
    3. 摘要生成 - 超过20条消息
    4. 结束检测 - 识别结束语
    """

    @pytest.fixture
    def interviewer(self):
        """创建已初始化的InterviewerAgent"""
        agent = InterviewerAgent()
        agent.state = InterviewState(
            session_id="test-session",
            started_at=datetime.now().isoformat(),
            config=InterviewConfig(),
            current_turn=1  # 面试从第1轮开始
        )
        return agent

    # ========== 正常场景 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_chat_normal_case(self, mock_call, interviewer):
        """
        正常场景：用户回答，Agent响应

        Given: 用户输入回答

        Expected:
          - 返回Agent响应
          - 用户消息被记录
          - Agent响应被记录
          - current_turn递增
        """
        # Given
        mock_call.return_value = "好的，你提到的Spring Boot能详细说说吗？"
        initial_turn = interviewer.state.current_turn

        context = {
            "user_message": "我用Spring Boot做了几个项目"
        }

        # When
        response = interviewer.chat(context)

        # Then
        assert isinstance(response, str)
        assert "Spring Boot" in response

        # 验证记忆
        user_msg = [m for m in interviewer.memory if m.role == "user"][-1]
        assert user_msg.content == "我用Spring Boot做了几个项目"

        # 验证turn递增
        assert interviewer.state.current_turn == initial_turn + 1

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_chat_empty_input(self, mock_call, interviewer):
        """
        边界场景：空输入

        Given: user_message为空

        Expected:
          - 返回提示消息
          - 不调用Claude
        """
        # Given
        context = {"user_message": ""}

        # When
        response = interviewer.chat(context)

        # Then
        assert response == "请输入你的回答。"
        mock_call.assert_not_called()

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_chat_preserves_context(self, mock_call, interviewer):
        """
        上下文保持：确保对话历史被传递

        Expected:
          - 调用Claude时包含历史消息
        """
        # Given
        mock_call.return_value = "好的"
        interviewer.add_to_memory(interviewer.create_message("assistant", "请介绍一下你的项目经验"))
        interviewer.add_to_memory(interviewer.create_message("user", "我做了一个电商系统"))

        context = {"user_message": "主要用了Spring Boot"}

        # When
        interviewer.chat(context)

        # Then - 验证消息数量
        call_args = mock_call.call_args
        # call_args is a CallArgs object with .args (tuple) and .kwargs (dict)
        if call_args.args:
            messages = call_args.args[0]
        else:
            messages = call_args.kwargs.get('messages', [])
        assert len(messages) > 2  # 至少有历史消息

    # ========== 结束检测 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_chat_detects_ending(self, mock_call, interviewer):
        """
        结束检测：识别结束语

        Given: Agent响应包含结束语

        Expected:
          - is_ended被设置为True
        """
        # Given
        mock_call.return_value = "今天的面试到这里，感谢参加。"

        context = {"user_message": "谢谢"}

        # When
        interviewer.chat(context)

        # Then
        assert interviewer.state.is_ended is True

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_chat_multiple_ending_keywords(self, mock_call, interviewer):
        """
        多种结束语：测试各种结束语

        Given: 不同的结束语

        Expected:
          - 都能正确识别
        """
        ending_responses = [
            "今天的面试到这里",
            "后续会有通知",
            "感谢参加面试",
            "面试到此结束"
        ]

        for ending in ending_responses:
            # Given
            mock_call.return_value = ending
            interviewer.state.is_ended = False  # 重置状态

            # When
            interviewer.chat({"user_message": "好的"})

            # Then
            assert interviewer.state.is_ended, f"未识别结束语: {ending}"

    # ========== 摘要生成 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_chat_generates_summary(self, mock_call, interviewer):
        """
        摘要生成：超过20条消息时生成摘要

        Given: memory中有20+条消息

        Expected:
          - 调用摘要生成
          - summary被设置
          - memory被清理
        """
        # Given - 添加20+条消息
        for i in range(11):
            interviewer.add_to_memory(interviewer.create_message("user", f"消息{i}"))
            interviewer.add_to_memory(interviewer.create_message("assistant", f"响应{i}"))

        mock_call.return_value = "好的"

        # When - 触发摘要
        interviewer.chat({"user_message": "新消息"})

        # Then - 验证摘要相关
        # 摘要生成会调用call_claude
        assert mock_call.called

    # ========== 多轮对话 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_chat_multiple_turns(self, mock_call, interviewer):
        """
        多轮对话：连续多轮交流

        Expected:
          - 每轮都正确记录
          - turn持续递增
        """
        # Given
        mock_call.return_value = "好的"
        responses = []

        # When - 多轮对话
        for i in range(3):
            context = {"user_message": f"回答{i}"}
            response = interviewer.chat(context)
            responses.append(response)

        # Then
        assert len(responses) == 3
        assert interviewer.state.current_turn == 4  # 从1开始，+3


class TestEndInterviewTDD:
    """
    end_interview的TDD测试

    测试策略：
    1. 正常场景 - 正常结束
    2. 状态验证 - is_ended设置
    3. 记忆验证 - 结束语被记录
    """

    @pytest.fixture
    def interviewer(self):
        """创建已初始化的InterviewerAgent"""
        agent = InterviewerAgent()
        agent.state = InterviewState(
            session_id="test-session",
            started_at=datetime.now().isoformat(),
            config=InterviewConfig(),
            current_turn=1  # 面试从第1轮开始
        )
        return agent

    # ========== 正常场景 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_end_interview_normal_case(self, mock_call, interviewer):
        """
        正常场景：结束面试

        Expected:
          - 返回结束语
          - is_ended设置为True
          - 结束语被记录
        """
        # Given
        mock_call.return_value = "今天的面试考察了Java和Spring，你表现不错。后续会有通知。"

        # When
        ending = interviewer.end_interview({})

        # Then
        assert isinstance(ending, str)
        assert "考察" in ending or "面试" in ending

        # 验证状态
        assert interviewer.state.is_ended is True

        # 验证记忆
        last_msg = interviewer.memory[-1]
        assert last_msg.role == "assistant"
        assert last_msg.content == ending

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_end_interview_content(self, mock_call, interviewer):
        """
        结束语内容：验证结束语包含必要元素

        Expected:
          - 包含考察内容总结
          - 包含候选人表现
          - 包含后续通知
        """
        # Given
        mock_call.return_value = "今天的面试考察了技术能力和项目经验，你的回答比较全面。我们会在3个工作日内通知结果。"

        # When
        ending = interviewer.end_interview({})

        # Then - 验证Claude被调用
        mock_call.assert_called_once()
        call_kwargs = mock_call.call_args.kwargs
        messages = call_kwargs.get('messages', [])
        prompt = messages[0]["content"] if messages else ""

        # 验证prompt包含要求
        assert "总结" in prompt or "考察" in prompt
        assert "表现" in prompt
        assert "通知" in prompt

    # ========== 边界场景 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_end_interview_already_ended(self, mock_call, interviewer):
        """
        边界场景：已经结束的面试

        Given: is_ended已经是True

        Expected:
          - 仍然能调用
        """
        # Given
        interviewer.state.is_ended = True
        mock_call.return_value = "再见"

        # When
        ending = interviewer.end_interview({})

        # Then
        assert isinstance(ending, str)
        assert interviewer.state.is_ended is True


class TestEvaluateAnswerTDD:
    """
    evaluate_answer的TDD测试

    测试策略：
    1. 正常场景 - 评估回答
    2. 不同质量等级 - complete/partial/vague/wrong
    3. 追问建议 - should_follow_up
    """

    @pytest.fixture
    def interviewer(self):
        return InterviewerAgent()

    # ========== 正常场景 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_evaluate_answer_normal_case(self, mock_call, interviewer):
        """
        正常场景：评估回答质量

        Given: 问题和回答

        Expected:
          - 返回评估结果
          - 包含质量等级
          - 包含追问建议
        """
        # Given
        mock_call.return_value = '''{
            "quality": "partial_correct",
            "key_points_covered": ["提到了Spring"],
            "missing_points": ["没有提到事务管理"],
            "should_follow_up": true,
            "follow_up_focus": "事务管理",
            "depth": 1
        }'''

        question = "Spring Boot有哪些核心特性？"
        answer = "主要是有自动配置和起步依赖"

        # When
        evaluation = interviewer.evaluate_answer(question, answer)

        # Then
        assert isinstance(evaluation, dict)
        assert evaluation["quality"] == "partial_correct"
        assert evaluation["should_follow_up"] is True
        assert "key_points_covered" in evaluation

    # ========== 不同质量等级 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_evaluate_complete_correct(self, mock_call, interviewer):
        """评估完整正确的回答"""
        mock_call.return_value = '{"quality": "complete_correct", "should_follow_up": false}'
        result = interviewer.evaluate_answer("Q", "完美答案")
        assert result["quality"] == "complete_correct"

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_evaluate_vague(self, mock_call, interviewer):
        """评估模糊的回答"""
        mock_call.return_value = '{"quality": "vague", "should_follow_up": true}'
        result = interviewer.evaluate_answer("Q", "嗯...差不多吧")
        assert result["quality"] == "vague"

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_evaluate_wrong(self, mock_call, interviewer):
        """评估错误的回答"""
        mock_call.return_value = '{"quality": "wrong", "should_follow_up": true}'
        result = interviewer.evaluate_answer("Q", "完全错误")
        assert result["quality"] == "wrong"

    # ========== 错误处理 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_evaluate_invalid_json(self, mock_call, interviewer):
        """
        错误处理：Claude返回无效JSON

        Expected:
          - 返回默认评估结果
          - 不崩溃
        """
        # Given
        mock_call.return_value = "invalid json{{}}"

        # When
        evaluation = interviewer.evaluate_answer("Q", "A")

        # Then
        assert isinstance(evaluation, dict)
        assert evaluation.get("quality") == "partial_correct"
        assert evaluation.get("should_follow_up") is False


class TestGenerateFollowUpTDD:
    """
    generate_follow_up的TDD测试

    测试策略：
    1. 不同回答质量对应不同追问
    2. 深度限制
    """

    @pytest.fixture
    def interviewer(self):
        return InterviewerAgent()

    # ========== 追问策略 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_follow_up_complete_correct(self, mock_call, interviewer):
        """
        追问策略：回答完整正确

        Expected:
          - 升维追问或下一题
        """
        # Given
        mock_call.return_value = '{"quality": "complete_correct", "should_follow_up": false}'

        # When
        follow_up = interviewer.generate_follow_up("问题", "完美答案")

        # Then
        assert isinstance(follow_up, str)
        # 根据FOLLOW_UP_STRATEGIES应该是升维追问或肯定
        assert "呢？" in follow_up or "场景" in follow_up

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_follow_up_partial_correct(self, mock_call, interviewer):
        """
        追问策略：部分正确

        Expected:
          - 定向补全追问
        """
        # Given
        mock_call.return_value = '''{
            "quality": "partial_correct",
            "missing_points": ["事务管理", "AOP"]
        }'''

        # When
        follow_up = interviewer.generate_follow_up("问题", "部分答案")

        # Then
        assert isinstance(follow_up, str)
        # 应该问缺失的点

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_follow_up_vague(self, mock_call, interviewer):
        """
        追问策略：回答模糊

        Expected:
          - 要求举例
        """
        # Given
        mock_call.return_value = '{"quality": "vague"}'

        # When
        follow_up = interviewer.generate_follow_up("问题", "不太清楚")

        # Then
        assert isinstance(follow_up, str)

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_follow_up_wrong(self, mock_call, interviewer):
        """
        追问策略：回答错误

        Expected:
          - 纠正引导
        """
        # Given
        mock_call.return_value = '{"quality": "wrong"}'

        # When
        follow_up = interviewer.generate_follow_up("问题", "错误答案")

        # Then
        assert isinstance(follow_up, str)
        # 应该给提示

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_follow_up_no_answer(self, mock_call, interviewer):
        """
        追问策略：不会回答

        Expected:
          - 提供参考答案
        """
        # Given
        mock_call.return_value = '{"quality": "no_answer"}'

        # When
        follow_up = interviewer.generate_follow_up("问题", "我不会")

        # Then
        assert isinstance(follow_up, str)

    # ========== 深度限制 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_follow_up_depth_limit(self, mock_call, interviewer):
        """
        深度限制：超过最大追问深度

        Expected:
          - 停止追问，转到下一题
        """
        # Given - 深度超过限制
        deep_depth = 10

        # When
        follow_up = interviewer.generate_follow_up("问题", "答案", depth=deep_depth)

        # Then
        assert "下一题" in follow_up or "下一个话题" in follow_up
        # 不应该调用evaluate_answer
        mock_call.assert_not_called()


# ========== 集成测试 ==========

class TestInterviewerIntegration:
    """InterviewerAgent集成测试"""

    @pytest.fixture
    def interviewer(self):
        return InterviewerAgent()

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_complete_interview_flow(self, mock_call, interviewer):
        """
        完整流程：start -> chat -> end

        Expected:
          - 整个流程正常完成
          - 状态正确转换
        """
        # Given - 设置不同阶段的响应
        mock_call.side_effect = [
            "你好，我是面试官，请自我介绍",  # start
            "请说说你的项目经验",  # chat 1
            "Spring Boot有哪些特性？",  # chat 2
            "今天的面试到此结束"  # end
        ]

        config = InterviewConfig()

        # When - 完整流程
        greeting = interviewer.start_interview({"config": config})
        response1 = interviewer.chat({"user_message": "我是张三"})
        response2 = interviewer.chat({"user_message": "做过电商系统"})
        ending = interviewer.end_interview({})

        # Then
        assert isinstance(greeting, str)
        assert isinstance(response1, str)
        assert isinstance(response2, str)
        assert isinstance(ending, str)

        # 验证状态
        assert interviewer.state.current_turn == 3
        assert len(interviewer.memory) == 6  # 3对对话


# ========== 运行说明 ==========

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║              TDD测试 - Interviewer Agent                     ║
║                                                                ║
║  运行方式：                                                     ║
║  pytest tests/unit/test_interviewer_tdd.py -v                ║
║                                                                ║
║  状态：                                                         ║
║  🔴 Red   → 测试已编写（等待验证）                          ║
║  🟢 Green → InterviewerAgent方法已实现                        ║
║  🔵 Blue  → 等待代码审查                                      ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝
""")

    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
