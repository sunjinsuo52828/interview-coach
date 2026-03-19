"""
TDD开发 - ParserAgent的parse_resume功能

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
from models import ParsedResume, TechnicalSkills, Project, Education
from tests.fixtures.test_data import SAMPLE_RESUME_TEXT, EMPTY_RESUME_TEXT, MINIMAL_RESUME_TEXT


class TestParseResumeTDD:
    """
    parse_resume的TDD测试

    测试策略：
    1. 正常场景 - 完整简历文本
    2. 边界场景 - 空简历、最小简历
    3. 数据提取 - 技能、项目、教育
    4. 数据类型 - 确保返回正确类型
    5. 特殊格式 - 处理各种简历格式
    """

    @pytest.fixture
    def parser(self):
        """创建ParserAgent实例"""
        return ParserAgent()

    # ========== 正常场景 ==========

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_resume_normal_case(self, mock_call, parser):
        """
        正常场景：完整简历文本

        Given: 完整的简历文本（包含姓名、技能、项目等）

        Expected:
          - 成功解析为ParsedResume对象
          - 提取正确的姓名、经验、职位
          - 提取所有技术栈
          - 提取项目经验
        """
        # Given - Mock Claude响应
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "name": "张三",
    "phone": "13800138000",
    "email": "zhangsan@example.com",
    "experience_years": 5,
    "current_role": "Java后端工程师",
    "technical_skills": {
        "languages": ["Java", "Python"],
        "frameworks": ["Spring Boot", "Spring Cloud"],
        "middleware": ["Redis", "Kafka"],
        "databases": ["MySQL"],
        "devops": ["Docker", "K8s"]
    },
    "projects": [
        {
            "name": "电商系统",
            "role": "核心开发",
            "duration": "2021-2023",
            "tech_stack": ["Spring Boot"],
            "description": "电商交易系统",
            "highlights": ["高并发处理"]
        }
    ],
    "education": []
}
""")]
        mock_call.return_value = mock_response.content[0].text

        # When - 解析简历
        resume_text = SAMPLE_RESUME_TEXT
        result = parser.parse_resume(resume_text)

        # Then - 验证结果
        assert isinstance(result, ParsedResume), "应该返回ParsedResume对象"
        assert result.name == "张三", "姓名应该正确提取"
        assert result.experience_years == 5, "经验年份应该正确提取"
        assert result.current_role == "Java后端工程师", "职位应该正确提取"

        # 验证技术栈
        assert isinstance(result.technical_skills, TechnicalSkills)
        assert "Java" in result.technical_skills.languages
        assert "Spring Boot" in result.technical_skills.frameworks

        # 验证项目经验
        assert len(result.projects) > 0, "应该提取项目经验"
        assert result.projects[0].name == "电商系统"

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_resume_extract_skills(self, mock_call, parser):
        """
        技能提取：正确提取各类技能

        Given: 简历包含各种技能

        Expected:
          - languages: 编程语言
          - frameworks: 框架
          - middleware: 中间件
          - databases: 数据库
          - devops: DevOps工具
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "technical_skills": {
        "languages": ["Java", "Python", "Go"],
        "frameworks": ["Spring", "Django", "FastAPI"],
        "middleware": ["Redis", "Kafka", "RabbitMQ"],
        "databases": ["MySQL", "PostgreSQL", "MongoDB"],
        "devops": ["Docker", "Kubernetes", "Jenkins", "Git"]
    }
}
""")]
        mock_call.return_value = mock_response.content[0].text

        resume_text = "Java开发，会Spring和Django"
        result = parser.parse_resume(resume_text)

        # Then
        assert len(result.technical_skills.languages) == 3
        assert len(result.technical_skills.frameworks) == 3
        assert len(result.technical_skills.middleware) == 3
        assert len(result.technical_skills.databases) == 3
        assert len(result.technical_skills.devops) == 4

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_resume_extract_projects(self, mock_call, parser):
        """
        项目提取：正确提取项目经验

        Given: 简历包含多个项目

        Expected:
          - 正确提取项目名称、角色、技术栈
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "projects": [
        {
            "name": "项目A",
            "role": "开发者",
            "duration": "2020-2022",
            "tech_stack": ["Java", "Spring"],
            "description": "描述A",
            "highlights": ["亮点A"]
        },
        {
            "name": "项目B",
            "role": "负责人",
            "duration": "2022-至今",
            "tech_stack": ["Python", "Django"],
            "description": "描述B",
            "highlights": ["亮点B"]
        }
    ]
}
""")]
        mock_call.return_value = mock_response.content[0].text

        resume_text = "项目A和项目B"
        result = parser.parse_resume(resume_text)

        # Then
        assert len(result.projects) == 2
        assert result.projects[0].name == "项目A"
        assert result.projects[1].role == "负责人"

    # ========== 边界场景 ==========

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_resume_empty_text(self, mock_call, parser):
        """
        边界场景：空文本

        Given: 空字符串

        Expected: 返回空的ParsedResume对象（不崩溃）
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="{}")]
        mock_call.return_value = mock_response.content[0].text

        # When
        result = parser.parse_resume("")

        # Then
        assert isinstance(result, ParsedResume), "空文本也应该返回对象"
        assert result.name == "", "空文本姓名为空"
        assert result.experience_years == 0

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_resume_no_skills(self, mock_call, parser):
        """
        边界场景：没有明确技能描述

        Given: 只有基本信息的简历

        Expected: 技能列表为空，但对象有效
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "name": "测试",
    "experience_years": 0,
    "technical_skills": {
        "languages": [],
        "frameworks": [],
        "middleware": [],
        "databases": [],
        "devops": []
    }
}
""")]
        mock_call.return_value = mock_response.content[0].text

        # When
        result = parser.parse_resume("姓名：测试")

        # Then
        assert isinstance(result, ParsedResume)
        assert result.name == "测试"
        assert len(result.technical_skills.to_list()) == 0

    # ========== 数据类型验证 ==========

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_resume_return_types(self, mock_call, parser):
        """
        数据类型：确保返回正确的数据结构

        Expected:
          - 返回ParsedResume对象
          - technical_skills是TechnicalSkills对象
          - projects是Project对象列表
          - education是Education对象列表
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "name": "测试",
    "technical_skills": {},
    "projects": [],
    "education": []
}
""")]
        mock_call.return_value = mock_response.content[0].text

        # When
        result = parser.parse_resume("测试简历")

        # Then - 验证类型
        assert type(result) == ParsedResume
        assert type(result.technical_skills) == TechnicalSkills
        assert type(result.projects) == list
        assert type(result.education) == list

    # ========== 错误处理 ==========

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_resume_invalid_json(self, mock_call, parser):
        """
        错误处理：Claude返回无效JSON

        Given: Claude返回的JSON解析失败

        Expected:
          - 不崩溃
          - 返回空的ParsedResume对象
          - raw_text被保存
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="invalid json{{}}")]
        mock_call.return_value = mock_response.content[0].text

        # When
        result = parser.parse_resume("一些简历文本")

        # Then
        assert isinstance(result, ParsedResume), "即使JSON无效也应该返回对象"
        assert result.raw_text == "一些简历文本", "原始文本应该被保存"

    # ========== 复杂场景 ==========

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_resume_mixed_format(self, mock_call, parser):
        """
        复杂场景：混合格式简历（中英文混合）

        Given: 中英文混合的简历

        Expected:
          - 正确解析
          - 处理中英文技能名称
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "name": "Alex Wang",
    "technical_skills": {
        "languages": ["Java", "Go"],
        "frameworks": ["Spring Boot", "Gin"]
    }
}
""")]
        mock_call.return_value = mock_response.content[0].text

        # When
        result = parser.parse_resume("Name: Alex, Skills: Java, Spring Boot")

        # Then
        assert result.name == "Alex Wang"
        assert "Java" in result.technical_skills.languages

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_resume_with_aliases(self, mock_call, parser):
        """
        技能别名：处理技能的各种别称

        Given: 技能使用别称（如reactjs vs React）

        Expected:
          - 正确识别技能
          - 标准化技能名称
        """
        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "name": "测试",
    "technical_skills": {
        "languages": ["JavaScript", "JS"],
        "frameworks": ["React", "reactjs", "Vue.js"],
        "databases": ["Postgres", "postgresql"]
    }
}
""")]
        mock_call.return_value = mock_response.content[0].text

        # When
        result = parser.parse_resume("JS开发者，熟悉React和Vue")

        # Then
        assert "JavaScript" in result.technical_skills.languages
        assert "React" in result.technical_skills.frameworks
        # 根据实现，可能去重或保留所有

    # ========== 性能测试 ==========

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_parse_resume_performance(self, mock_call, parser):
        """
        性能测试：解析大简历文本

        Given: 非常长的简历（5000+字）

        Expected:
          - 在合理时间内完成
          - 正确解析所有内容
        """
        import time

        # Given
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "name": "测试",
    "technical_skills": {
        "languages": ["Java"] * 100
    }
}
""")]
        mock_call.return_value = mock_response.content[0].text

        # When - 记录时间
        long_text = "Java " * 10000
        start = time.time()

        result = parser.parse_resume(long_text)

        elapsed = time.time() - start

        # Then
        assert isinstance(result, ParsedResume)
        assert elapsed < 10, f"解析应该在10秒内完成，实际: {elapsed:.2f}秒"


# ========== 测试集合 ==========

class TestParseResumeEdgeCases:
    """parse_resume边界测试集合"""

    @pytest.fixture
    def parser(self):
        return ParserAgent()

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_resume_with_special_characters(self, mock_call, parser):
        """特殊字符：简历包含特殊字符和表情"""
        mock_response = Mock()
        mock_response.content = [Mock(text='{"name": "张三🎉", "phone": "+86-138-001-38000"}')]
        mock_call.return_value = mock_response.content[0].text

        result = parser.parse_resume("姓名：张三🎉")

        assert isinstance(result, ParsedResume)

    @patch('agents.parser_agent.ParserAgent.call_claude')
    def test_resume_markdown_format(self, mock_call, parser):
        """Markdown格式：简历是Markdown格式"""
        mock_response = Mock()
        mock_response.content = [Mock(text="""
{
    "name": "张三",
    "technical_skills": {"languages": ["Java"]}
}
""")]
        mock_call.return_value = mock_response.content[0].text

        markdown_resume = """
# 张三

## 技能
- Java
- Spring Boot

## 项目
### 项目A
"""
        result = parser.parse_resume(markdown_resume)

        assert isinstance(result, ParsedResume)


# ========== 运行说明 ==========

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║              TDD测试 - Parse Resume                          ║
║                                                                ║
║  运行方式：                                                     ║
║  pytest tests/unit/test_parse_resume_tdd.py -v               ║
║                                                                ║
║  状态：                                                         ║
║  🔴 Red   → 测试已编写（等待实现）                          ║
║  🟢 Green → 等待parse_resume方法确认                         ║
║  🔵 Blue  → 等待代码审查                                      ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝
""")

    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
