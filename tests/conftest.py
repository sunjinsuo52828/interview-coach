"""
测试基础设施 - Fixtures和辅助函数

为pytest测试提供共享的fixtures和辅助函数。
"""
import sys
import os
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, MagicMock
import pytest
from dotenv import load_dotenv

# 加载.env文件 - 从项目根目录加载
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from models import (
    ParsedResume, ParsedJD, GapAnalysis, TechnicalSkills,
    Project, Education, InterviewConfig, InterviewState,
    ConversationTurn, InterviewReport, DimensionScore
)


# ========== ========== ========== ==========
# Fixtures
# ========== ========== ========== ==========

@pytest.fixture
def sample_resume() -> ParsedResume:
    """示例简历"""
    return ParsedResume(
        name="张三",
        phone="13800138000",
        email="zhangsan@example.com",
        experience_years=5,
        current_role="Java后端工程师",
        technical_skills=TechnicalSkills(
            languages=["Java", "Python", "JavaScript"],
            frameworks=["Spring Boot", "Spring Cloud", "MyBatis"],
            middleware=["Redis", "Kafka", "RabbitMQ"],
            databases=["MySQL", "PostgreSQL", "MongoDB"],
            devops=["Docker", "K8s", "Jenkins", "Git"]
        ),
        projects=[
            Project(
                name="电商交易系统",
                role="核心开发",
                duration="2021-2023",
                tech_stack=["Spring Boot", "Redis", "MySQL", "Kafka"],
                description="处理高并发交易，实现分布式锁",
                highlights=["解决并发问题", "性能优化30%"]
            ),
            Project(
                name="支付网关",
                role="技术负责人",
                duration="2023-至今",
                tech_stack=["Spring Cloud", "K8s", "ElasticSearch"],
                description="设计并实现支付网关架构",
                highlights=["系统可用性99.9%", "支撑日均千万级交易"]
            )
        ],
        education=[
            Education(
                school="XX大学",
                degree="本科",
                major="计算机科学与技术",
                graduation_year=2018
            )
        ]
    )


@pytest.fixture
def sample_jd() -> ParsedJD:
    """示例JD"""
    return ParsedJD(
        company="某互联网公司",
        position="Senior Java Engineer",
        location="北京",
        salary_range="30k-50k",
        required_skills=["Java", "Spring Boot", "Spring Cloud", "Redis", "Kafka"],
        preferred_skills=["ElasticSearch", "ClickHouse", "大数据处理"],
        min_experience=5,
        preferred_experience=8,
        responsibilities=[
            "负责核心业务系统开发",
            "参与系统架构设计",
            "解决高并发、高可用问题"
        ],
        business_domain="金融科技",
        level="Senior"
    )


@pytest.fixture
def sample_config() -> InterviewConfig:
    """示例面试配置"""
    return InterviewConfig(
        interviewer_level="senior_engineer",
        interviewer_style="professional",
        focus_areas=["technical_basics", "project_experience"],
        duration=45,
        language="zh"
    )


@pytest.fixture
def sample_gap_analysis() -> GapAnalysis:
    """示例Gap分析结果"""
    return GapAnalysis(
        match_percentage=0.7,
        matched_items=["Java", "Spring Boot", "Redis"],
        gap_items=["Kafka", "Spring Cloud"],
        bonus_items=["Python", "MongoDB"],
        interview_focus=["Kafka", "Spring Cloud", "分布式场景"]
    )


@pytest.fixture
def empty_resume() -> ParsedResume:
    """空简历（边界测试用）"""
    return ParsedResume(
        name="",
        technical_skills=TechnicalSkills()
    )


@pytest.fixture
def empty_jd() -> ParsedJD:
    """空JD（边界测试用）"""
    return ParsedJD(
        company="",
        position="",
        required_skills=[]
    )


@pytest.fixture
def mock_claude_client():
    """Mock Claude客户端"""
    client = Mock()
    # 模拟响应
    mock_response = Mock()
    mock_response.content = [Mock(text="模拟响应")]
    mock_response.usage = Mock(
        input_tokens=100,
        output_tokens=50
    )
    client.messages.create.return_value = mock_response
    return client


@pytest.fixture
def sample_interview_state(sample_resume, sample_jd, sample_config, sample_gap_analysis):
    """示例面试状态"""
    return InterviewState(
        session_id="test-session-001",
        started_at="2026-03-17T10:00:00",
        current_turn=1,
        config=sample_config,
        resume=sample_resume,
        jd=sample_jd,
        gap=sample_gap_analysis,
        conversation_history=[
            ConversationTurn(
                turn_id="1",
                timestamp="2026-03-17T10:01:00",
                question_id="q1",
                question_text="请自我介绍一下",
                question_domain="behavioral",
                user_answer="我是张三，有5年Java开发经验...",
                score="B",
                follow_up_count=0,
                evaluation_notes=["回答完整"]
            )
        ]
    )


# ========== ========== ========== ==========
# Mock数据生成器
# ========== ========== ========== ==========

class MockDataGenerator:
    """Mock数据生成器"""

    @staticmethod
    def create_resume(name: str = "李四", **kwargs) -> ParsedResume:
        """创建简历"""
        return ParsedResume(
            name=name,
            phone=kwargs.get("phone", "13900139000"),
            email=kwargs.get("email", "lisi@example.com"),
            experience_years=kwargs.get("experience_years", 3),
            current_role=kwargs.get("current_role", "Java开发工程师"),
            technical_skills=TechnicalSkills(
                languages=kwargs.get("languages", ["Java"]),
                frameworks=kwargs.get("frameworks", []),
                middleware=kwargs.get("middleware", []),
                databases=kwargs.get("databases", ["MySQL"]),
                devops=kwargs.get("devops", [])
            )
        )

    @staticmethod
    def create_jd(position: str = "Java工程师", **kwargs) -> ParsedJD:
        """创建JD"""
        return ParsedJD(
            company=kwargs.get("company", "某公司"),
            position=position,
            required_skills=kwargs.get("required_skills", ["Java", "MySQL"]),
            preferred_skills=kwargs.get("preferred_skills", [])
        )

    @staticmethod
    def create_claude_response(text: str = "测试响应", tokens: int = 100) -> Mock:
        """创建Claude响应Mock"""
        response = Mock()
        response.content = [Mock(text=text)]
        response.usage = Mock(
            input_tokens=tokens,
            output_tokens=tokens // 2
        )
        return response


# ========== ========== ========== ==========
# 测试辅助函数
# ========== ========== ========== ==========

class TestHelpers:
    """测试辅助函数"""

    @staticmethod
    def assert_valid_gap_analysis(gap: GapAnalysis):
        """断言Gap分析结果有效"""
        assert isinstance(gap, GapAnalysis)
        assert 0 <= gap.match_percentage <= 1
        assert isinstance(gap.matched_items, list)
        assert isinstance(gap.gap_items, list)
        assert isinstance(gap.bonus_items, list)
        assert isinstance(gap.interview_focus, list)

    @staticmethod
    def count_test_runs() -> int:
        """统计测试运行次数"""
        # 可以通过pytest插件或环境变量获取
        return 0

    @staticmethod
    def create_temp_resume_file(content: str) -> Path:
        """创建临时简历文件"""
        import tempfile
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False
        ) as f:
            f.write(content)
            return Path(f.name)

    @staticmethod
    def create_temp_jd_file(content: str) -> Path:
        """创建临时JD文件"""
        import tempfile
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False
        ) as f:
            f.write(content)
            return Path(f.name)


# ========== ========== ========== ==========
# Pytest配置和钩子
# ========== ========== ========== ==========

def pytest_configure(config):
    """Pytest配置钩子"""
    # 自定义标记
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "tdd: TDD cycle tests"
    )


def pytest_collection_modifyitems(config, items):
    """测试收集钩子 - 自动标记测试"""
    for item in items:
        # 根据文件路径自动标记
        if "unit/" in str(item.fspath):
            item.add_marker("unit")
        elif "integration/" in str(item.fspath):
            item.add_marker("integration")


# ========== ========== ========== ==========
# 测试数据文件路径
# ========== ========== ========== ==========

TEST_DATA_DIR = Path(__file__).parent / "fixtures"

def get_test_data_path(filename: str) -> Path:
    """获取测试数据文件路径"""
    return TEST_DATA_DIR / filename
