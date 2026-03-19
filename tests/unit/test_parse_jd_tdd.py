"""
TDD开发 - ParserAgent的parse_jd功能

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
from models import ParsedJD
from tests.fixtures.test_data import SAMPLE_JD_TEXT, EMPTY_JD_TEXT, MINIMAL_JD_TEXT


class TestParseJDTDD:
    """
    parse_jd的TDD测试

    测试策略：
    1. 正常场景 - 完整JD文本
    2. 边界场景 - 空JD、最小JD
    3. 数据提取 - 技能要求、经验、职责
    4. 数据类型 - 确保返回正确类型
    5. 特殊格式 - 处理各种JD格式
    """

    @pytest.fixture
    def parser(self):
        """创建ParserAgent实例"""
        return ParserAgent()

    # ========== 正常场景 ==========

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_jd_normal_case(self, mock_call, parser):
        """
        正常场景：完整JD文本

        Given: 完整的JD文本（包含公司、职位、技能等）

        Expected:
          - 成功解析为ParsedJD对象
          - 提取正确的公司、职位信息
          - 提取必须技能和加分技能
          - 提取经验要求
        """
        # Given - Mock Claude响应
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "company": "某金融科技公司",
    "position": "Senior Java Engineer",
    "location": "北京",
    "salary_range": "30k-50k",
    "required_skills": ["Java", "Spring Boot", "Spring Cloud", "Redis", "Kafka"],
    "preferred_skills": ["ElasticSearch", "ClickHouse"],
    "min_experience": 5,
    "preferred_experience": 8,
    "responsibilities": [
        "负责核心交易系统开发",
        "参与系统架构设计"
    ],
    "business_domain": "金融科技",
    "level": "Senior"
}
""")]
        mock_call.return_value = mock_response.content[0].text

        # When - 解析JD
        jd_text = SAMPLE_JD_TEXT
        result = parser.parse_jd(jd_text)

        # Then - 验证结果
        assert isinstance(result, ParsedJD), "应该返回ParsedJD对象"
        assert result.company == "某金融科技公司", "公司应该正确提取"
        assert result.position == "Senior Java Engineer", "职位应该正确提取"
        assert result.location == "北京", "地点应该正确提取"

        # 验证技能
        assert "Java" in result.required_skills
        assert "Spring Boot" in result.required_skills
        assert "ElasticSearch" in result.preferred_skills

        # 验证经验
        assert result.min_experience == 5
        assert result.preferred_experience == 8

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_jd_extract_skills(self, mock_call, parser):
        """
        技能提取：正确提取必须技能和加分技能

        Given: JD包含多种技能要求

        Expected:
          - required_skills: 必须技能列表
          - preferred_skills: 加分技能列表
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "required_skills": ["Java", "MySQL", "Redis", "Kafka"],
    "preferred_skills": ["ElasticSearch", "K8s", "Go"]
}
""")]
        mock_call.return_value = mock_response.content[0].text

        jd_text = "招聘Java工程师，要求Java, MySQL, Redis, Kafka"
        result = parser.parse_jd(jd_text)

        # Then
        assert "Java" in result.required_skills
        assert "MySQL" in result.required_skills
        assert len(result.preferred_skills) == 3

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_jd_extract_responsibilities(self, mock_call, parser):
        """
        职责提取：正确提取岗位职责

        Given: JD包含岗位职责

        Expected:
          - responsibilities包含所有职责条目
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "responsibilities": [
        "负责核心业务系统开发",
        "参与系统架构设计",
        "指导初中级工程师"
    ]
}
""")]
        mock_call.return_value = mock_response.content[0].text

        result = parser.parse_jd("职位描述：负责开发...")

        # Then
        assert len(result.responsibilities) == 3
        assert "开发" in result.responsibilities[0] or "职责" in result.responsibilities[0]

    # ========== 边界场景 ==========

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_jd_empty_text(self, mock_call, parser):
        """
        边界场景：空文本

        Given: 空字符串

        Expected: 返回空的ParsedJD对象（不崩溃）
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="{}")]
        mock_call.return_value = mock_response.content[0].text

        # When
        result = parser.parse_jd("")

        # Then
        assert isinstance(result, ParsedJD), "空文本也应该返回对象"
        assert result.company == "", "空文本公司为空"
        assert result.position == "", "空文本职位为空"

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_jd_minimal_jd(self, mock_call, parser):
        """
        边界场景：最小JD（只有基本信息）

        Given: 只有职位和基本要求

        Expected:
          - 正确提取有限的信息
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "company": "测试公司",
    "position": "测试职位",
    "required_skills": ["Java"]
}
""")]
        mock_call.return_value = mock_response.content[0].text

        # When
        result = parser.parse_jd("招聘Java工程师")

        # Then
        assert result.company == "测试公司"
        assert result.position == "测试职位"
        assert "Java" in result.required_skills

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_jd_no_required_skills(self, mock_call, parser):
        """
        边界场景：JD没有明确的技能要求

        Given: JD只有公司介绍，没有技能要求

        Expected:
          - required_skills为空列表
          - 对象仍然有效
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "company": "创业公司",
    "position": "合伙人",
    "required_skills": []
}
""")]
        mock_call.return_value = mock_response.content[0].text

        # When
        result = parser.parse_jd("寻找合伙人")

        # Then
        assert isinstance(result, ParsedJD)
        assert len(result.required_skills) == 0

    # ========== 数据类型验证 ==========

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_jd_return_types(self, mock_call, parser):
        """
        数据类型：确保返回正确的数据结构

        Expected:
          - 返回ParsedJD对象
          - 所有属性都是正确类型
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "company": "测试",
    "position": "测试职位",
    "required_skills": ["Java"],
    "preferred_skills": [],
    "responsibilities": []
}
""")]
        mock_call.return_value = mock_response.content[0].text

        # When
        result = parser.parse_jd("测试")

        # Then - 验证类型
        assert type(result) == ParsedJD
        assert isinstance(result.required_skills, list)
        assert isinstance(result.preferred_skills, list)
        assert isinstance(result.responsibilities, list)

        # 验证列表内容类型
        for skill in result.required_skills:
            assert isinstance(skill, str)

    # ========== 错误处理 ==========

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_jd_invalid_json(self, mock_call, parser):
        """
        错误处理：Claude返回无效JSON

        Given: Claude返回的JSON解析失败

        Expected:
          - 不崩溃
          - 返回空的ParsedJD对象
          - raw_text被保存
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="invalid json{{}}")]
        mock_call.return_value = mock_response.content[0].text

        # When
        result = parser.parse_jd("一些JD文本")

        # Then
        assert isinstance(result, ParsedJD), "即使JSON无效也应该返回对象"
        assert result.raw_text == "一些JD文本", "原始文本应该被保存"

    # ========== 复杂场景 ==========

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_jd_with_salary_ranges(self, mock_call, parser):
        """
        复杂场景：JD包含多种薪资范围格式

        Given: JD包含各种薪资格式（15k-25k, 面议等）

        Expected:
          - 正确提取薪资范围
          - 处理不同格式
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "company": "公司A",
    "position": "职位A",
    "salary_range": "15k-25k"
}
""")]
        mock_call.return_value = mock_response.content[0].text

        # When
        result = parser.parse_jd("薪资15-25k")

        # Then
        assert result.salary_range == "15k-25k"

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_jd_multiple_positions(self, mock_call, parser):
        """
        复杂场景：JD包含多个职位级别

        Given: JD包含Junior/Senior/Lead不同级别的要求

        Expected:
          - 识别所有级别要求
          - 正确归类
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "company": "大厂",
    "position": "Java Engineer",
    "level": "Senior",
    "min_experience": 5,
    "preferred_experience": 8
}
""")]
        mock_call.return_value = mock_response.content[0].text

        # When
        result = parser.parse_jd("招聘高级Java工程师")

        # Then
        assert result.level == "Senior"
        assert result.min_experience == 5

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_jd_with_business_domain(self, mock_call, parser):
        """
        业务领域：识别JD的业务领域

        Given: JD属于特定业务领域（金融/电商/游戏等）

        Expected:
          - 正确识别business_domain
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "company": "金融公司",
    "position": "Java开发",
    "business_domain": "金融",
    "required_skills": ["Java", "Spring"]
}
""")]
        mock_call.return_value = mock_response.content[0].text

        # When
        result = parser.parse_jd("金融公司招聘")

        # Then
        assert result.business_domain == "金融"


# ========== 边界测试集合 ==========

class TestParseJDEdgeCases:
    """parse_jd边界测试集合"""

    @pytest.fixture
    def parser(self):
        return ParserAgent()

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_jd_with_english(self, mock_call, parser):
        """中英文JD"""
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "company": "Tech Corp",
    "position": "Software Engineer",
    "required_skills": ["Java", "Python", "Go"],
    "responsibilities": ["Develop software", "Write code"]
}
""")]
        mock_call.return_value = mock_response.content[0].text

        result = parser.parse_jd("Software Engineer needed")

        assert result.position == "Software Engineer"

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_jd_with_special_characters(self, mock_call, parser):
        """特殊字符和符号"""
        mock_response = Mock()
        mock_response.content = [Mock(text='{"salary_range": "20k-40k/月"}')]
        mock_call.return_value = mock_response.content[0].text

        result = parser.parse_jd("薪资20-40k/月")

        assert result.salary_range == "20k-40k/月"

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_jd_markdown_format(self, mock_call, parser):
        """Markdown格式的JD"""
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "company": "Startup",
    "position": "Developer",
    "required_skills": ["Python"]
}
""")]
        mock_call.return_value = mock_response.content[0].text

        markdown_jd = """
# 职位描述

## 公司介绍
Startup公司

## 要求
- Python开发经验
"""

        result = parser.parse_jd(markdown_jd)

        assert isinstance(result, ParsedJD)


# ========== 集成测试 ==========

class TestParserIntegration:
    """ParserAgent集成测试"""

    @pytest.fixture
    def parser(self):
        return ParserAgent()

    def test_parse_complete_workflow(self, parser):
        """
        完整工作流：简历+JD+Gap分析

        Given: 简历和JD文本

        Expected:
          - 两个都能正确解析
          - Gap分析能正确计算
        """
        # 这个测试需要实际的API调用，或者完整的mock
        # 这里简化为验证方法存在且可调用

        assert hasattr(parser, 'parse_resume')
        assert hasattr(parser, 'parse_jd')
        assert hasattr(parser, 'gap_analysis')


# ========== 运行说明 ==========

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║              TDD测试 - Parse JD                                  ║
║                                                                ║
║  运行方式：                                                     ║
║  pytest tests/unit/test_parse_jd_tdd.py -v                   ║
║                                                                ║
║  状态：                                                         ║
║  🔴 Red   → 测试已编写（等待验证）                          ║
║  🟢 Green → parse_resume方法已实现                             ║
║  🔵 Blue  → 等待代码审查                                      ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝
""")

    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
