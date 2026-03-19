"""
End-to-End Integration Tests for Interview Coach MVP

Tests the complete flow:
1. Parse Resume
2. Parse JD
3. Gap Analysis
4. Start Interview
5. Chat
6. End Interview
7. Generate Report
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

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


class TestE2EIntegration:
    """
    End-to-End Integration Tests

    Test the complete user journey through the application.
    All Agent calls are mocked to avoid API costs.
    """

    @pytest.fixture
    def sample_resume_text(self):
        """Sample resume for testing"""
        return """
        张三
        高级Java工程师
        5年经验

        技术栈：
        - 语言：Java, Python
        - 框架：Spring Boot, MyBatis
        - 数据库：MySQL, Redis
        - 中间件：Kafka

        项目经验：
        1. 电商平台后端
           - 负责订单系统开发
           - 使用Spring Boot + MySQL
           - QPS 1000+
        """

    @pytest.fixture
    def sample_jd_text(self):
        """Sample JD for testing"""
        return """
        高级Java工程师

        职位要求：
        - 3年以上Java开发经验
        - 熟悉Spring Boot, MyBatis
        - 熟悉MySQL, Redis
        - 有Kafka使用经验优先
        - 了解微服务架构

        公司：某科技公司
        """

    @pytest.fixture
    def sample_config(self):
        """Sample interview configuration"""
        return InterviewConfig(
            interviewer_level="senior_engineer",
            interviewer_style="professional",
            focus_areas=["technical_basics", "project_experience"],
            duration=30,
            language="zh"
        )

    # ========== Test: Complete Flow ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_complete_interview_flow(self, mock_claude, sample_resume_text, sample_jd_text, sample_config):
        """
        Test the complete interview flow from resume parsing to report generation.

        This is the core MVP flow that should work end-to-end.
        """
        # ========== Step 1: Parse Resume ==========
        # Mock the Claude response for resume parsing
        mock_claude.return_value = """{
    "name": "张三",
    "phone": "",
    "email": "",
    "experience_years": 5,
    "current_role": "高级Java工程师",
    "technical_skills": {
        "languages": ["Java", "Python"],
        "frameworks": ["Spring Boot", "MyBatis"],
        "databases": ["MySQL", "Redis"],
        "middleware": ["Kafka"],
        "devops": []
    },
    "projects": [
        {
            "name": "电商平台后端",
            "role": "",
            "duration": "",
            "tech_stack": ["Spring Boot", "MySQL"],
            "description": "",
            "highlights": []
        }
    ],
    "education": [],
    "raw_text": ""
}"""

        parser = ParserAgent()
        resume = parser.parse_resume(sample_resume_text)

        assert isinstance(resume, ParsedResume)
        assert resume.name == "张三"
        assert "Java" in resume.technical_skills.languages
        print("✅ Step 1: Resume parsed successfully")

        # ========== Step 2: Parse JD ==========
        mock_claude.return_value = """{
    "company": "某科技公司",
    "position": "高级Java工程师",
    "location": "",
    "salary_range": "",
    "required_skills": ["Java", "Spring Boot", "MyBatis", "MySQL", "Redis"],
    "preferred_skills": ["Kafka", "微服务"],
    "min_experience": 3,
    "preferred_experience": 5,
    "responsibilities": [],
    "business_domain": "",
    "level": "",
    "raw_text": ""
}"""

        jd = parser.parse_jd(sample_jd_text)

        assert isinstance(jd, ParsedJD)
        assert jd.position == "高级Java工程师"
        assert "Java" in jd.required_skills
        print("✅ Step 2: JD parsed successfully")

        # ========== Step 3: Gap Analysis ==========
        mock_claude.return_value = """{
    "match_percentage": 80,
    "matched_items": ["Java", "Spring Boot", "MyBatis", "MySQL", "Redis"],
    "gap_items": ["微服务"],
    "bonus_items": ["Python", "Kafka"],
    "interview_focus": ["微服务"],
    "match_details": {}
}"""

        gap = parser.gap_analysis(resume, jd)

        assert isinstance(gap, GapAnalysis)
        assert gap.match_percentage > 0.7  # 80% match expected
        assert "Java" in gap.matched_items
        print("✅ Step 3: Gap analysis completed")

        # ========== Step 4: Start Interview ==========
        interviewer = InterviewerAgent()

        mock_claude.return_value = """你好，我是今天的面试官。我看过你的简历了，
你在Java开发方面有5年的经验，技术栈涵盖Spring Boot、MySQL、Redis等。

我们先从项目经验开始聊聊，能介绍一下你做过的电商平台项目吗？"""

        greeting = interviewer.start_interview({
            "config": sample_config,
            "resume": resume,
            "jd": jd,
            "gap": gap
        })

        assert isinstance(greeting, str)
        assert len(greeting) > 10
        assert interviewer.state.session_id != ""
        assert interviewer.state.current_turn == 1
        print("✅ Step 4: Interview started")

        # ========== Step 5: Chat (Multiple turns) ==========
        # User's first answer
        mock_claude.return_value = """好的，你提到了QPS 1000+，那能详细说说：
1. 订单系统有哪些核心表？
2. 如何保证订单数据一致性？
3. 有没有遇到过性能问题，如何优化的？"""

        response1 = interviewer.chat({
            "user_message": "我在电商平台负责订单系统开发，使用Spring Boot + MySQL架构，QPS能达到1000+。"
        })

        assert isinstance(response1, str)
        assert len(response1) > 10
        # Memory: greeting (1) + user msg (1) + response (1) = 3 items
        assert len(interviewer.memory) >= 3
        print("✅ Step 5a: First chat turn completed")

        # User's second answer
        mock_claude.return_value = """很好，MySQL索引讲得不错。

下一个话题，你在简历中提到用过Redis，能说说：
1. Redis在项目中用在哪里？
2. 有没有遇到过缓存穿透、击穿的问题？"""

        response2 = interviewer.chat({
            "user_message": "订单表有订单主表、订单明细表、商品表。我们用分布式事务保证一致性，性能方面主要做了数据库索引优化。"
        })

        assert isinstance(response2, str)
        # current_turn: start(1) + chat1(+1) + chat2(+1) = 3
        assert interviewer.state.current_turn >= 3
        print("✅ Step 5b: Second chat turn completed")

        # ========== Step 6: End Interview ==========
        mock_claude.return_value = """感谢参加今天的面试。

今天的面试主要考察了：
1. 项目经验 - 电商平台订单系统
2. 数据库技术 - MySQL索引优化
3. 缓存技术 - Redis使用

整体表现不错，我们后续会有HR联系你。

祝好！"""

        ending = interviewer.end_interview({})

        assert isinstance(ending, str)
        assert "面试" in ending or "感谢" in ending
        assert interviewer.state.is_ended == True
        print("✅ Step 6: Interview ended")

        # ========== Step 7: Generate Report ==========
        evaluator = EvaluatorAgent()

        mock_claude.return_value = """{
    "overall_score": 82,
    "overall_grade": "B",
    "recommendation": "HIRE",
    "dimension_scores": {
        "technical_depth": {
            "dimension": "technical_depth",
            "score": 80,
            "grade": "B",
            "evidence": ["MySQL索引理解正确", "Redis使用场景清晰"]
        },
        "project_experience": {
            "dimension": "project_experience",
            "score": 85,
            "grade": "B",
            "evidence": ["电商平台经验", "QPS 1000+"]
        }
    },
    "strengths": ["有实际项目经验", "技术栈匹配"],
    "weaknesses": ["微服务经验不足"],
    "learning_suggestions": ["建议学习微服务架构"],
    "recommended_resources": ["《微服务设计》", "Spring Cloud实战"]
}"""

        report = evaluator.generate_report({
            "state": interviewer.state
        })

        assert isinstance(report, InterviewReport)
        assert report.overall_score > 0
        assert report.overall_grade in ["A", "B", "C", "D"]
        assert report.recommendation in ["HIRE", "NO_HIRE", "HIRE_WITH_CONDITIONS"]
        print("✅ Step 7: Report generated")

        print("\n🎉 Complete E2E Integration Test PASSED!")
        print(f"   - Resume: {resume.name}")
        print(f"   - JD: {jd.position}")
        print(f"   - Match: {gap.match_percentage*100:.0f}%")
        print(f"   - Interview Turns: {interviewer.state.current_turn}")
        print(f"   - Score: {report.overall_score} ({report.overall_grade})")

    # ========== Test: Error Handling ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_flow_with_empty_inputs(self, mock_claude):
        """
        Test the flow handles empty/invalid inputs gracefully.
        """
        # Mock returns empty response
        mock_claude.return_value = """{
    "name": "",
    "experience_years": 0,
    "technical_skills": {},
    "projects": [],
    "education": []
}"""

        parser = ParserAgent()
        resume = parser.parse_resume("")

        # Should still return a valid object
        assert isinstance(resume, ParsedResume)
        print("✅ Empty input handled gracefully")

    # ========== Test: State Persistence ==========

    @patch('agents.base_agent.BaseAgent.call_claude')
    def test_interviewer_state_persistence(self, mock_claude):
        """
        Test that interviewer state is preserved across chat turns.
        """
        mock_claude.return_value = "你好，我是面试官。请介绍一下你自己。"

        interviewer = InterviewerAgent()
        interviewer.start_interview({
            "config": InterviewConfig(),
            "resume": ParsedResume(name="Test"),
            "jd": ParsedJD(position="Test"),
            "gap": GapAnalysis()
        })

        initial_turn = interviewer.state.current_turn
        initial_session = interviewer.state.session_id

        # Chat
        mock_claude.return_value = "能详细说说吗？"
        interviewer.chat({"user_message": "我是测试候选人"})

        # State should be updated
        assert interviewer.state.current_turn > initial_turn
        assert interviewer.state.session_id == initial_session  # Session ID unchanged
        print("✅ Interviewer state persists correctly")


# ========== Run Instructions ==========

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║         E2E Integration Tests - Interview Coach MVP         ║
║                                                              ║
║  Test Coverage:                                             ║
║  ✅ Parse Resume                                            ║
║  ✅ Parse JD                                                 ║
║  ✅ Gap Analysis                                             ║
║  ✅ Start Interview                                          ║
║  ✅ Chat Flow                                                ║
║  ✅ End Interview                                            ║
║  ✅ Generate Report                                          ║
║                                                              ║
║  Run: pytest tests/integration/test_e2e_integration.py -v   ║
╚══════════════════════════════════════════════════════════════╝
""")

    pytest.main([__file__, "-v", "--tb=short"])
