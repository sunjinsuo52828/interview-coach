"""
TDD开发 - ParserAgent的gap_analysis功能

按照TDD流程：
1. 🔴 Red: 先写测试（测试失败）
2. 🟢 Green: 实现代码（测试通过）
3. 🔵 Blue: 审查重构
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.parser_agent import ParserAgent
from models import ParsedResume, ParsedJD, GapAnalysis, TechnicalSkills


class TestGapAnalysisTDD:
    """
    Gap分析的TDD测试

    测试策略：
    1. 正常场景 - 正常的简历和JD
    2. 边界场景 - 空简历、空JD
    3. 边界场景 - 完全匹配
    4. 边界场景 - 完全不匹配
    5. 数据类型 - 确保返回正确类型
    """

    @pytest.fixture
    def parser(self):
        """创建ParserAgent实例"""
        return ParserAgent()

    # ========== 正常场景 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_gap_analysis_normal_case(self, mock_claude, parser):
        """
        正常场景：简历和JD都有技能，部分匹配

        Given:
            简历有技能: Java, Spring Boot, MySQL
            JD要求: Java, Spring Boot, Redis, Kafka

        Expected:
            match_percentage: 0.5 (2/4)
            matched_items: Java, Spring Boot
            gap_items: Redis, Kafka
        """
        # Given - 准备测试数据和mock响应
        mock_claude.return_value = """{
    "match_percentage": 50,
    "matched_items": ["Java", "Spring Boot"],
    "gap_items": ["Redis", "Kafka"],
    "bonus_items": [],
    "interview_focus": ["Redis", "Kafka"],
    "match_details": {}
}"""

        resume = ParsedResume(
            technical_skills=TechnicalSkills(
                languages=["Java"],
                frameworks=["Spring Boot"],
                databases=["MySQL"]
            )
        )

        jd = ParsedJD(
            required_skills=["Java", "Spring Boot", "Redis", "Kafka"]
        )

        # When - 执行测试
        gap = parser.gap_analysis(resume, jd)

        # Then - 断言结果
        assert isinstance(gap, GapAnalysis), "应该返回GapAnalysis对象"
        assert gap.match_percentage == pytest.approx(0.5, rel=0.1), "匹配度应该是50%"
        assert "Java" in gap.matched_items, "Java应该在匹配项中"
        assert "Spring Boot" in gap.matched_items, "Spring Boot应该在匹配项中"
        assert "Redis" in gap.gap_items, "Redis应该在差距项中"
        assert "Kafka" in gap.gap_items, "Kafka应该在差距项中"

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_gap_analysis_with_bonus_skills(self, mock_claude, parser):
        """
        正常场景：简历有JD要求的技能，还有额外技能

        Given:
            简历有技能: Java, Python, Redis
            JD要求: Java, Redis

        Expected:
            match_percentage: 1.0 (2/2)
            bonus_items: Python (简历有但JD没要求)
        """
        # Given - 设置mock响应
        mock_claude.return_value = """{
    "match_percentage": 100,
    "matched_items": ["Java", "Redis"],
    "gap_items": [],
    "bonus_items": ["Python"],
    "interview_focus": [],
    "match_details": {}
}
"""

        resume = ParsedResume(
            technical_skills=TechnicalSkills(
                languages=["Java", "Python"],
                middleware=["Redis"]
            )
        )

        jd = ParsedJD(
            required_skills=["Java", "Redis"]
        )

        # When
        gap = parser.gap_analysis(resume, jd)

        # Then
        assert gap.match_percentage == pytest.approx(1.0, rel=0.1), "应该完全匹配"
        assert "Python" in gap.bonus_items, "Python应该在加分项中"

    # ========== 边界场景 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_gap_analysis_empty_resume(self, mock_claude, parser):
        """
        边界场景：简历为空

        Given:
            简历没有任何技能
            JD要求: Java

        Expected:
            match_percentage: 0.0
            matched_items: 空列表
        """
        # Given - 设置mock响应
        mock_claude.return_value = """
{
    "match_percentage": 0.0,
    "matched_items": [],
    "gap_items": ["Java"],
    "bonus_items": [],
    "interview_focus": ["Java"],
    "match_details": {}
}
"""

        resume = ParsedResume(
            technical_skills=TechnicalSkills()  # 空技能
        )

        jd = ParsedJD(
            required_skills=["Java"]
        )

        # When
        gap = parser.gap_analysis(resume, jd)

        # Then
        assert gap.match_percentage == 0.0, "空简历匹配度应该是0"
        assert len(gap.matched_items) == 0, "不应该有匹配项"
        assert "Java" in gap.gap_items, "JD要求的技能应该在差距项中"

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_gap_analysis_empty_jd(self, mock_claude, parser):
        """
        边界场景：JD为空

        Given:
            简历有技能: Java, Spring
            JD没有任何要求

        Expected:
            match_percentage: 1.0 (空JD算100%匹配)
            gap_items: 空列表
        """
        # Given - 设置mock响应
        mock_claude.return_value = """{
    "match_percentage": 100,
    "matched_items": [],
    "gap_items": [],
    "bonus_items": ["Java", "Spring"],
    "interview_focus": [],
    "match_details": {}
}
"""

        resume = ParsedResume(
            technical_skills=TechnicalSkills(
                languages=["Java"],
                frameworks=["Spring"]
            )
        )

        jd = ParsedJD(
            required_skills=[]  # 空要求
        )

        # When
        gap = parser.gap_analysis(resume, jd)

        # Then
        assert gap.match_percentage == 1.0, "空JD应该100%匹配"
        assert len(gap.gap_items) == 0, "不应该有差距项"

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_gap_analysis_perfect_match(self, mock_claude, parser):
        """
        边界场景：完全匹配

        Given:
            简历: Java, MySQL
            JD要求: Java, MySQL

        Expected:
            match_percentage: 1.0
            gap_items: 空列表
        """
        # Given - 设置mock响应
        mock_claude.return_value = """{
    "match_percentage": 100,
    "matched_items": ["Java", "MySQL"],
    "gap_items": [],
    "bonus_items": [],
    "interview_focus": [],
    "match_details": {}
}
"""

        resume = ParsedResume(
            technical_skills=TechnicalSkills(
                languages=["Java"],
                databases=["MySQL"]
            )
        )

        jd = ParsedJD(
            required_skills=["Java", "MySQL"]
        )

        # When
        gap = parser.gap_analysis(resume, jd)

        # Then
        assert gap.match_percentage == 1.0, "完全匹配应该是100%"
        assert len(gap.gap_items) == 0, "完全匹配不应该有差距项"

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_gap_analysis_no_match(self, mock_claude, parser):
        """
        边界场景：完全不匹配

        Given:
            简历: Python, Django
            JD要求: Java, Spring

        Expected:
            match_percentage: 0.0
            所有JD要求的技能在gap_items中
        """
        # Given - 设置mock响应
        mock_claude.return_value = """
{
    "match_percentage": 0.0,
    "matched_items": [],
    "gap_items": ["Java", "Spring"],
    "bonus_items": ["Python", "Django"],
    "interview_focus": ["Java", "Spring"],
    "match_details": {}
}
"""

        resume = ParsedResume(
            technical_skills=TechnicalSkills(
                languages=["Python"],
                frameworks=["Django"]
            )
        )

        jd = ParsedJD(
            required_skills=["Java", "Spring"]
        )

        # When
        gap = parser.gap_analysis(resume, jd)

        # Then
        assert gap.match_percentage == 0.0, "完全不匹配应该是0%"
        assert len(gap.matched_items) == 0, "不应该有匹配项"
        assert "Java" in gap.gap_items or "Spring" in gap.gap_items, "JD要求应该在差距项中"

    # ========== 数据类型验证 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_gap_analysis_return_types(self, mock_claude, parser):
        """
        数据类型：确保返回正确的数据类型

        Expected:
            所有属性都是正确的类型
        """
        # Given - 设置mock响应
        mock_claude.return_value = """
{
    "match_percentage": 1.0,
    "matched_items": ["Java"],
    "gap_items": [],
    "bonus_items": [],
    "interview_focus": [],
    "match_details": {}
}
"""

        resume = ParsedResume(
            technical_skills=TechnicalSkills(languages=["Java"])
        )
        jd = ParsedJD(required_skills=["Java"])

        # When
        gap = parser.gap_analysis(resume, jd)

        # Then - 验证数据类型
        assert isinstance(gap, GapAnalysis)
        assert isinstance(gap.match_percentage, (int, float))
        assert isinstance(gap.matched_items, list)
        assert isinstance(gap.gap_items, list)
        assert isinstance(gap.bonus_items, list)
        assert isinstance(gap.interview_focus, list)

        # 验证列表内容类型
        for item in gap.matched_items:
            assert isinstance(item, str)
        for item in gap.gap_items:
            assert isinstance(item, str)

    # ========== 复杂场景 ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_gap_analysis_complex_case(self, mock_claude, parser):
        """
        复杂场景：多技能，部分匹配，部分不匹配

        Given:
            简历: Java, Spring Boot, MySQL, Redis, Python
            JD要求: Java, Spring Cloud, Kafka, Redis, Go

        Expected:
            正确识别匹配项和差距项
        """
        # Given - 设置mock响应
        mock_claude.return_value = """
{
    "match_percentage": 0.4,
    "matched_items": ["Java", "Redis"],
    "gap_items": ["Spring Cloud", "Kafka", "Go"],
    "bonus_items": ["Spring Boot", "MySQL", "Python"],
    "interview_focus": ["Spring Cloud", "Kafka", "Go"],
    "match_details": {}
}
"""

        resume = ParsedResume(
            technical_skills=TechnicalSkills(
                languages=["Java", "Python"],
                frameworks=["Spring Boot"],
                middleware=["Redis"],
                databases=["MySQL"]
            )
        )

        jd = ParsedJD(
            required_skills=["Java", "Spring Cloud", "Kafka", "Redis", "Go"]
        )

        # When
        gap = parser.gap_analysis(resume, jd)

        # Then
        assert 0 < gap.match_percentage < 1, "应该部分匹配"
        assert "Java" in gap.matched_items, "Java应该匹配"
        assert "Redis" in gap.matched_items, "Redis应该匹配"
        assert "Spring Cloud" in gap.gap_items or "Kafka" in gap.gap_items, "差距项应该包含Spring Cloud或Kafka"

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_gap_analysis_interview_focus_generation(self, mock_claude, parser):
        """
        面试重点：差距项应该成为面试重点

        Expected:
            interview_focus应该包含gap_items
        """
        # Given - 设置mock响应
        mock_claude.return_value = """
{
    "match_percentage": 0.33,
    "matched_items": ["Java"],
    "gap_items": ["Kafka", "Redis"],
    "bonus_items": [],
    "interview_focus": ["Kafka", "Redis"],
    "match_details": {}
}
"""

        resume = ParsedResume(
            technical_skills=TechnicalSkills(languages=["Java"])
        )
        jd = ParsedJD(
            required_skills=["Java", "Kafka", "Redis"]
        )

        # When
        gap = parser.gap_analysis(resume, jd)

        # Then
        assert len(gap.interview_focus) > 0, "应该有面试重点"
        # 差距项应该包含在面试重点中
        for gap_item in gap.gap_items:
            assert gap_item in gap.interview_focus, f"{gap_item}应该在面试重点中"


# ========== 运行说明 ==========

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║              TDD测试 - Gap Analysis                          ║
║                                                                ║
║  运行方式：                                                     ║
║  1. pytest tests/unit/test_gap_analysis_tdd.py -v             ║
║  2. pytest tests/unit/test_gap_analysis_tdd.py::TestGapAnalysisTDD::test_gap_analysis_normal_case -v ║
║                                                                ║
║  状态：                                                         ║
║  🔴 Red   → 测试已编写（预期失败）                          ║
║  🟢 Green → 等待实现gap_analysis方法                          ║
║  🔵 Blue  → 等待代码审查                                      ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝
""")

    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
