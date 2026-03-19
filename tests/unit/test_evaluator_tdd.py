"""
TDD开发 - EvaluatorAgent功能

按照TDD流程：
1. 🔴 Red: 先写测试（测试失败）
2. 🟢 Green: 实现代码（测试通过）
3. 🔵 Blue: 审查重构
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.evaluator_agent import EvaluatorAgent, evaluate_interview, generate_report
from models import (
    InterviewState,
    InterviewConfig,
    InterviewReport,
    QuestionResult,
    DimensionScore,
    ParsedResume,
    ParsedJD,
    GapAnalysis,
    TechnicalSkills,
    ConversationTurn,
    InterviewerLevel,
    FocusArea,
    AnswerGrade,
    Recommendation
)


class TestEvaluateTDD:
    """
    evaluate的TDD测试

    测试策略：
    1. 正常场景 - 完整面试状态
    2. 边界场景 - 空状态、无对话
    3. 数据提取 - 验证评估结果结构
    4. 错误处理 - JSON解析失败
    """

    @pytest.fixture
    def evaluator(self):
        """创建EvaluatorAgent实例"""
        return EvaluatorAgent()

    @pytest.fixture
    def sample_state(self):
        """示例面试状态"""
        return InterviewState(
            session_id="test-session-123",
            started_at=datetime.now().isoformat(),
            config=InterviewConfig(
                interviewer_level=InterviewerLevel.SENIOR_ENGINEER.value,
                focus_areas=[FocusArea.TECHNICAL_BASICS.value, FocusArea.PROJECT_EXPERIENCE.value],
                duration=30
            ),
            resume=ParsedResume(
                name="张三",
                experience_years=5,
                current_role="Java后端工程师",
                technical_skills=TechnicalSkills(
                    languages=["Java", "Python"],
                    frameworks=["Spring Boot", "Spring Cloud"],
                    databases=["MySQL", "Redis"]
                )
            ),
            jd=ParsedJD(
                company="某科技公司",
                position="Senior Java Engineer",
                required_skills=["Java", "Spring Boot", "Redis", "Kafka"]
            ),
            gap=GapAnalysis(
                match_percentage=0.75,
                matched_items=["Java", "Spring Boot", "Redis"],
                gap_items=["Kafka"]
            ),
            conversation_history=[
                ConversationTurn(
                    turn_number=1,
                    question_id="q1",
                    question_text="请介绍一下你的项目经验",
                    question_domain="项目经验",
                    user_answer="我做了一个电商系统，用Spring Boot开发的",
                    score="A",
                    evaluation_notes=["回答完整", "有实际项目经验"]
                )
            ]
        )

    # ========== 正常场景 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_evaluate_normal_case(self, mock_call, evaluator, sample_state):
        """
        正常场景：完整面试状态评估

        Given: 完整的面试状态（有对话记录）

        Expected:
          - 返回评估结果字典
          - 包含overall_score
          - 包含dimension_scores
          - 包含strengths和weaknesses
        """
        # Given - Mock Claude响应
        mock_call.return_value = '''{
            "overall_score": 85,
            "overall_grade": "A",
            "recommendation": "HIRE",
            "dimension_scores": {
                "technical_depth": {"score": 90, "grade": "A", "evidence": ["对Spring原理理解深入"]},
                "project_experience": {"score": 85, "grade": "A", "evidence": ["有完整的电商项目经验"]},
                "problem_solving": {"score": 80, "grade": "B", "evidence": ["能分析问题"]},
                "communication": {"score": 85, "grade": "A", "evidence": ["表达清晰"]},
                "learning_ability": {"score": 80, "grade": "B", "evidence": ["关注新技术"]}
            },
            "strengths": ["技术基础扎实", "项目经验丰富", "沟通能力强"],
            "weaknesses": ["Kafka经验不足"],
            "learning_suggestions": ["建议学习Kafka等消息队列"],
            "recommended_resources": ["Kafka官方文档"]
        }'''

        # When
        result = evaluator.evaluate({"state": sample_state})

        # Then - 验证结果结构
        assert isinstance(result, dict)
        assert "overall_score" in result
        assert "overall_grade" in result
        assert "recommendation" in result
        assert "dimension_scores" in result
        assert "strengths" in result
        assert "weaknesses" in result
        assert "learning_suggestions" in result
        assert "recommended_resources" in result

        # 验证具体值
        assert result["overall_score"] == 85
        assert result["overall_grade"] == "A"
        assert result["recommendation"] == "HIRE"
        assert len(result["strengths"]) == 3
        assert len(result["weaknesses"]) >= 1

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_evaluate_dimension_scores(self, mock_call, evaluator, sample_state):
        """
        维度评分：验证所有5个维度都有评分

        Expected:
          - 5个维度都有评分
          - 每个维度包含score, grade, evidence
        """
        # Given
        mock_call.return_value = '''{
            "overall_score": 75,
            "overall_grade": "B",
            "recommendation": "HIRE_WITH_CONDITIONS",
            "dimension_scores": {
                "technical_depth": {"score": 80, "grade": "B", "evidence": ["技术基础"]},
                "project_experience": {"score": 75, "grade": "B", "evidence": ["项目经验"]},
                "problem_solving": {"score": 70, "grade": "C", "evidence": ["问题解决"]},
                "communication": {"score": 75, "grade": "B", "evidence": ["沟通"]},
                "learning_ability": {"score": 75, "grade": "B", "evidence": ["学习"]}
            },
            "strengths": [],
            "weaknesses": [],
            "learning_suggestions": [],
            "recommended_resources": []
        }'''

        # When
        result = evaluator.evaluate({"state": sample_state})

        # Then - 验证所有维度
        dimensions = result["dimension_scores"]
        expected_dimensions = [
            "technical_depth",
            "project_experience",
            "problem_solving",
            "communication",
            "learning_ability"
        ]

        for dim in expected_dimensions:
            assert dim in dimensions, f"缺少维度: {dim}"
            assert "score" in dimensions[dim]
            assert "grade" in dimensions[dim]
            assert "evidence" in dimensions[dim]
            assert isinstance(dimensions[dim]["score"], (int, float))
            assert isinstance(dimensions[dim]["evidence"], list)

    # ========== 边界场景 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_evaluate_no_state(self, mock_call, evaluator):
        """
        边界场景：没有提供state

        Given: context中没有state

        Expected:
          - 返回错误信息
          - 不调用Claude
        """
        # Given
        context = {}

        # When
        result = evaluator.evaluate(context)

        # Then
        assert result == {"error": "No interview state provided"}
        mock_call.assert_not_called()

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_evaluate_no_conversation(self, mock_call, evaluator, sample_state):
        """
        边界场景：没有对话记录

        Given: state中conversation_history为空

        Expected:
          - 仍然能调用evaluate
          - 格式化对话返回"无对话记录"
        """
        # Given
        sample_state.conversation_history = []
        mock_call.return_value = '{"overall_score": 50, "overall_grade": "C"}'

        # When
        result = evaluator.evaluate({"state": sample_state})

        # Then
        assert isinstance(result, dict)

    # ========== 错误处理 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_evaluate_invalid_json(self, mock_call, evaluator, sample_state):
        """
        错误处理：Claude返回无效JSON

        Given: Claude返回的JSON解析失败

        Expected:
          - 不崩溃
          - 返回默认评估结果
        """
        # Given
        mock_call.return_value = "invalid json{{}}"

        # When
        result = evaluator.evaluate({"state": sample_state})

        # Then - 验证返回默认评估
        assert isinstance(result, dict)
        assert "overall_score" in result
        assert result["overall_score"] == 50.0
        assert result["overall_grade"] == "C"
        assert result["recommendation"] == "NO_HIRE"

    # ========== 评分等级 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_evaluate_grades(self, mock_call, evaluator):
        """
        评分等级：测试不同的overall_grade

        Expected:
          - A/B/C/D各种等级都能处理
        """
        for grade in ["A", "B", "C", "D"]:
            # Given
            state = InterviewState(
                session_id="test",
                started_at=datetime.now().isoformat(),
                config=InterviewConfig(),
                resume=ParsedResume(name="测试"),
                jd=ParsedJD(position="测试"),
                conversation_history=[]
            )

            mock_call.return_value = f'{{"overall_score": 50, "overall_grade": "{grade}", "recommendation": "NO_HIRE", "dimension_scores": {{}}, "strengths": [], "weaknesses": [], "learning_suggestions": [], "recommended_resources": []}}'

            # When
            result = evaluator.evaluate({"state": state})

            # Then
            assert result["overall_grade"] == grade

    # ========== 录用建议 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_evaluate_recommendations(self, mock_call, evaluator):
        """
        录用建议：测试不同的recommendation

        Expected:
          - HIRE/NO_HIRE/HIRE_WITH_CONDITIONS都能处理
        """
        recommendations = ["HIRE", "NO_HIRE", "HIRE_WITH_CONDITIONS"]

        for rec in recommendations:
            # Given
            state = InterviewState(
                session_id="test",
                started_at=datetime.now().isoformat(),
                config=InterviewConfig(),
                resume=ParsedResume(name="测试"),
                jd=ParsedJD(position="测试"),
                conversation_history=[]
            )

            mock_call.return_value = f'{{"overall_score": 70, "overall_grade": "B", "recommendation": "{rec}", "dimension_scores": {{}}, "strengths": [], "weaknesses": [], "learning_suggestions": [], "recommended_resources": []}}'

            # When
            result = evaluator.evaluate({"state": state})

            # Then
            assert result["recommendation"] == rec


class TestGenerateReportTDD:
    """
    generate_report的TDD测试

    测试策略：
    1. 正常场景 - 生成完整报告
    2. 边界场景 - 只有evaluation没有state
    3. 数据类型 - 返回InterviewReport对象
    4. 时间戳 - 验证generated_at
    """

    @pytest.fixture
    def evaluator(self):
        return EvaluatorAgent()

    @pytest.fixture
    def sample_evaluation(self):
        """示例评估结果"""
        return {
            "overall_score": 85,
            "overall_grade": "A",
            "recommendation": "HIRE",
            "dimension_scores": {
                "technical_depth": {
                    "score": 90,
                    "grade": "A",
                    "evidence": ["理解深入"]
                },
                "project_experience": {
                    "score": 85,
                    "grade": "A",
                    "evidence": ["项目丰富"]
                },
                "problem_solving": {
                    "score": 80,
                    "grade": "B",
                    "evidence": ["分析能力"]
                },
                "communication": {
                    "score": 85,
                    "grade": "A",
                    "evidence": ["表达清晰"]
                },
                "learning_ability": {
                    "score": 80,
                    "grade": "B",
                    "evidence": ["学习积极"]
                }
            },
            "strengths": [
                "技术基础扎实",
                "项目经验丰富",
                "沟通能力强"
            ],
            "weaknesses": [
                "消息队列经验较少"
            ],
            "learning_suggestions": [
                "建议深入学习Kafka",
                "关注分布式系统最佳实践"
            ],
            "recommended_resources": [
                "Kafka官方文档",
                "《设计数据密集型应用》"
            ]
        }

    @pytest.fixture
    def sample_state(self):
        """示例面试状态"""
        return InterviewState(
            session_id="test-session-456",
            started_at=datetime.now().isoformat(),
            config=InterviewConfig(),
            resume=ParsedResume(name="张三"),
            jd=ParsedJD(position="Java工程师"),
            conversation_history=[
                ConversationTurn(
                    turn_number=1,
                    question_id="q1",
                    question_text="自我介绍",
                    question_domain="基本介绍",
                    user_answer="我是张三，有5年Java经验",
                    score=85,
                    evaluation_notes=["回答完整"]
                )
            ]
        )

    # ========== 正常场景 ==========

    def test_generate_report_with_evaluation(self, evaluator, sample_evaluation, sample_state):
        """
        正常场景：有evaluation和state

        Given: 完整的evaluation和state

        Expected:
          - 返回InterviewReport对象
          - 所有字段正确填充
        """
        # Given
        context = {
            "evaluation": sample_evaluation,
            "state": sample_state
        }

        # When
        report = evaluator.generate_report(context)

        # Then - 验证返回类型
        assert isinstance(report, InterviewReport)

        # 验证基本字段
        assert report.session_id == "test-session-456"
        assert report.overall_score == 85
        assert report.overall_grade == "A"
        assert report.recommendation == "HIRE"

        # 验证时间戳
        try:
            datetime.fromisoformat(report.generated_at)
        except ValueError:
            pytest.fail("generated_at不是有效的ISO时间格式")

    def test_generate_report_dimension_scores(self, evaluator, sample_evaluation, sample_state):
        """
        维度评分：验证维度评分正确转换

        Expected:
          - dimension_scores是DimensionScore对象字典
        """
        # Given
        context = {
            "evaluation": sample_evaluation,
            "state": sample_state
        }

        # When
        report = evaluator.generate_report(context)

        # Then - 验证维度评分
        assert isinstance(report.dimension_scores, dict)
        assert len(report.dimension_scores) == 5

        for dim_name, dim_score in report.dimension_scores.items():
            assert isinstance(dim_score, DimensionScore)
            assert dim_score.dimension == dim_name
            assert isinstance(dim_score.score, (int, float))
            assert isinstance(dim_score.grade, str)
            assert isinstance(dim_score.evidence, list)

    def test_generate_report_question_results(self, evaluator, sample_evaluation, sample_state):
        """
        问题结果：验证问题结果正确转换

        Expected:
          - question_results包含所有对话轮次
        """
        # Given
        context = {
            "evaluation": sample_evaluation,
            "state": sample_state
        }

        # When
        report = evaluator.generate_report(context)

        # Then
        assert isinstance(report.question_results, list)
        assert len(report.question_results) == len(sample_state.conversation_history)

        for q_result in report.question_results:
            assert isinstance(q_result, QuestionResult)
            assert q_result.question_id is not None
            assert q_result.question_text is not None

    def test_generate_report_strengths_weaknesses(self, evaluator, sample_evaluation, sample_state):
        """
        优势弱项：验证优势和弱项正确提取

        Expected:
          - strengths列表正确
          - weaknesses列表正确
        """
        # Given
        context = {
            "evaluation": sample_evaluation,
            "state": sample_state
        }

        # When
        report = evaluator.generate_report(context)

        # Then
        assert isinstance(report.strengths, list)
        assert isinstance(report.weaknesses, list)
        assert len(report.strengths) == 3
        assert len(report.weaknesses) == 1
        assert "技术基础扎实" in report.strengths
        assert "消息队列" in report.weaknesses[0]

    def test_generate_report_learning_suggestions(self, evaluator, sample_evaluation, sample_state):
        """
        学习建议：验证学习建议和推荐资源

        Expected:
          - learning_suggestions列表正确
          - recommended_resources列表正确
        """
        # Given
        context = {
            "evaluation": sample_evaluation,
            "state": sample_state
        }

        # When
        report = evaluator.generate_report(context)

        # Then
        assert isinstance(report.learning_suggestions, list)
        assert isinstance(report.recommended_resources, list)
        assert len(report.learning_suggestions) == 2
        assert len(report.recommended_resources) == 2
        assert "Kafka" in report.learning_suggestions[0]

    # ========== 边界场景 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_generate_report_only_evaluation(self, mock_call, evaluator, sample_evaluation):
        """
        边界场景：只有evaluation，没有state

        Given: context只有evaluation

        Expected:
          - 仍然能生成报告
          - 缺少的字段用空值
        """
        # Given
        mock_call.return_value = '{"overall_score": 75}'
        context = {"evaluation": sample_evaluation}

        # When
        report = evaluator.generate_report(context)

        # Then
        assert isinstance(report, InterviewReport)
        assert report.session_id == ""
        assert report.question_results == []

    def test_generate_report_no_evaluation_no_state(self, evaluator):
        """
        边界场景：既没有evaluation也没有state

        Expected:
          - 返回空的InterviewReport
        """
        # Given
        context = {}

        # When
        report = evaluator.generate_report(context)

        # Then
        assert isinstance(report, InterviewReport)
        assert report.session_id == ""
        assert report.overall_score == 0

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_generate_report_state_without_evaluation(self, mock_call, evaluator, sample_state):
        """
        边界场景：有state但没有evaluation

        Given: context只有state

        Expected:
          - 自动调用evaluate
          - 生成完整报告
        """
        # Given - Mock evaluate返回值
        mock_call.return_value = '''{
            "overall_score": 80,
            "overall_grade": "B",
            "recommendation": "HIRE_WITH_CONDITIONS",
            "dimension_scores": {},
            "strengths": [],
            "weaknesses": [],
            "learning_suggestions": [],
            "recommended_resources": []
        }'''

        context = {"state": sample_state}

        # When
        report = evaluator.generate_report(context)

        # Then
        assert isinstance(report, InterviewReport)
        assert report.overall_score == 80
        assert mock_call.called  # 验证调用了evaluate


class TestHelperMethodsTDD:
    """
    辅助方法的TDD测试

    测试策略：
    1. get_grade_from_score - 分数转等级
    2. get_recommendation_from_score - 分数转录用建议
    3. _format_conversation - 对话格式化
    4. _default_evaluation - 默认评估
    """

    @pytest.fixture
    def evaluator(self):
        return EvaluatorAgent()

    # ========== get_grade_from_score ==========

    def test_get_grade_a_score(self, evaluator):
        """A等级：90分及以上"""
        for score in [90, 95, 100]:
            grade = evaluator.get_grade_from_score(score)
            assert grade == "A", f"{score}分应该是A等级"

    def test_get_grade_b_score(self, evaluator):
        """B等级：75-89分"""
        for score in [75, 80, 89]:
            grade = evaluator.get_grade_from_score(score)
            assert grade == "B", f"{score}分应该是B等级"

    def test_get_grade_c_score(self, evaluator):
        """C等级：60-74分"""
        for score in [60, 65, 74]:
            grade = evaluator.get_grade_from_score(score)
            assert grade == "C", f"{score}分应该是C等级"

    def test_get_grade_d_score(self, evaluator):
        """D等级：60分以下"""
        for score in [0, 30, 59]:
            grade = evaluator.get_grade_from_score(score)
            assert grade == "D", f"{score}分应该是D等级"

    # ========== get_recommendation_from_score ==========

    def test_get_recommendation_hire(self, evaluator):
        """HIRE建议：85分及以上"""
        for score in [85, 90, 100]:
            rec = evaluator.get_recommendation_from_score(score)
            assert rec == "HIRE", f"{score}分应该建议录用"

    def test_get_recommendation_hire_with_conditions(self, evaluator):
        """HIRE_WITH_CONDITIONS建议：70-84分"""
        for score in [70, 75, 84]:
            rec = evaluator.get_recommendation_from_score(score)
            assert rec == "HIRE_WITH_CONDITIONS", f"{score}分应该有条件录用"

    def test_get_recommendation_no_hire(self, evaluator):
        """NO_HIRE建议：70分以下"""
        for score in [0, 50, 69]:
            rec = evaluator.get_recommendation_from_score(score)
            assert rec == "NO_HIRE", f"{score}分应该不录用"

    # ========== _format_conversation ==========

    def test_format_conversation_normal(self, evaluator):
        """正常对话格式化"""
        turns = [
            ConversationTurn(
                turn_number=1,
                question_id="q1",
                question_text="介绍项目",
                question_domain="项目经验",
                user_answer="做了电商系统",
                score=80,
                evaluation_notes=["完整"]
            )
        ]

        formatted = evaluator._format_conversation(turns)

        assert "介绍项目" in formatted
        assert "做了电商系统" in formatted
        assert "80" in formatted
        assert "完整" in formatted

    def test_format_conversation_empty(self, evaluator):
        """空对话列表"""
        formatted = evaluator._format_conversation([])
        assert formatted == "无对话记录"

    def test_format_conversation_multiple_turns(self, evaluator):
        """多轮对话格式化"""
        turns = [
            ConversationTurn(
                turn_number=i,
                question_id=f"q{i}",
                question_text=f"问题{i}",
                question_domain="技术",
                user_answer=f"回答{i}",
                score="B",
                evaluation_notes=[f"备注{i}"]
            )
            for i in range(1, 4)
        ]

        formatted = evaluator._format_conversation(turns)

        # 验证所有轮次都被格式化
        for i in range(1, 4):
            assert f"问题{i}" in formatted
            assert f"回答{i}" in formatted
            assert f"第{i}轮" in formatted

    # ========== _default_evaluation ==========

    def test_default_evaluation_structure(self, evaluator):
        """默认评估结构验证"""
        default = evaluator._default_evaluation()

        assert isinstance(default, dict)
        assert "overall_score" in default
        assert "overall_grade" in default
        assert "recommendation" in default
        assert "dimension_scores" in default
        assert "strengths" in default
        assert "weaknesses" in default
        assert "learning_suggestions" in default
        assert "recommended_resources" in default

    def test_default_evaluation_values(self, evaluator):
        """默认评估数值验证"""
        default = evaluator._default_evaluation()

        assert default["overall_score"] == 50.0
        assert default["overall_grade"] == "C"
        assert default["recommendation"] == "NO_HIRE"

        # 验证所有维度都是50分
        for dim_data in default["dimension_scores"].values():
            assert dim_data["score"] == 50
            assert dim_data["grade"] == "C"


# ========== 便捷函数测试 ==========

class TestConvenienceFunctions:
    """便捷函数测试"""

    @pytest.fixture
    def sample_state(self):
        return InterviewState(
            session_id="test",
            started_at=datetime.now().isoformat(),
            config=InterviewConfig(),
            resume=ParsedResume(name="测试"),
            jd=ParsedJD(position="测试"),
            conversation_history=[]
        )

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_evaluate_interview_function(self, mock_call, sample_state):
        """便捷函数evaluate_interview"""
        mock_call.return_value = '{"overall_score": 80, "overall_grade": "B", "recommendation": "HIRE_WITH_CONDITIONS", "dimension_scores": {}, "strengths": [], "weaknesses": [], "learning_suggestions": [], "recommended_resources": []}'

        result = evaluate_interview(sample_state)

        assert isinstance(result, dict)
        assert result["overall_score"] == 80

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_generate_report_function(self, mock_call, sample_state):
        """便捷函数generate_report"""
        mock_call.return_value = '{"overall_score": 85, "overall_grade": "A", "recommendation": "HIRE", "dimension_scores": {}, "strengths": [], "weaknesses": [], "learning_suggestions": [], "recommended_resources": []}'

        report = generate_report(sample_state)

        assert isinstance(report, InterviewReport)
        assert report.overall_score == 85


# ========== 运行说明 ==========

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║              TDD测试 - Evaluator Agent                       ║
║                                                                ║
║  运行方式：                                                     ║
║  pytest tests/unit/test_evaluator_tdd.py -v                  ║
║                                                                ║
║  状态：                                                         ║
║  🔴 Red   → 测试已编写（等待验证）                          ║
║  🟢 Green → EvaluatorAgent方法已实现                          ║
║  🔵 Blue  → 等待代码审查                                      ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝
""")

    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
