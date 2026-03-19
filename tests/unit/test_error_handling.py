"""
测试错误处理机制

验证当API调用失败时，系统能够返回正确的错误信息。
"""
import sys
sys.path.insert(0, '.')

import pytest
from unittest.mock import patch, Mock
from agents import create_orchestrator


class TestErrorHandling:
    """错误处理测试"""

    def test_parser_api_401_error(self):
        """测试API 401认证错误"""
        orchestrator = create_orchestrator()

        # Mock API调用返回401错误
        with patch('agents.base_agent.BaseAgent.call_claude') as mock_claude:
            mock_claude.side_effect = Exception("401 Unauthorized")

            orchestrator.update_resume_text("测试简历内容")
            result = orchestrator.route_and_execute()

            assert result["status"] == "error"
            assert result["agent"] == "parser"
            assert "API密钥" in result["message"]

    def test_parser_api_rate_limit_error(self):
        """测试API频率限制错误"""
        orchestrator = create_orchestrator()

        with patch('agents.base_agent.BaseAgent.call_claude') as mock_claude:
            mock_claude.side_effect = Exception("429 Rate limit exceeded")

            orchestrator.update_resume_text("测试简历内容")
            result = orchestrator.route_and_execute()

            assert result["status"] == "error"
            assert "频率" in result["message"] or "rate" in result["message"].lower()

    def test_parser_api_timeout_error(self):
        """测试API超时错误"""
        orchestrator = create_orchestrator()

        with patch('agents.base_agent.BaseAgent.call_claude') as mock_claude:
            mock_claude.side_effect = Exception("Request timeout")

            orchestrator.update_resume_text("测试简历内容")
            result = orchestrator.route_and_execute()

            assert result["status"] == "error"
            assert "超时" in result["message"] or "timeout" in result["message"].lower()

    def test_interviewer_api_error(self):
        """测试面试官Agent API错误"""
        orchestrator = create_orchestrator()

        # 先设置好解析数据
        with patch('agents.base_agent.BaseAgent.call_claude') as mock_claude:
            mock_claude.return_value = '{"name": "测试", "technical_skills": {"languages": ["Python"]}}'

            orchestrator.update_resume_text("简历")
            orchestrator.update_jd_text("JD")
            orchestrator.route_and_execute()  # 解析简历和JD

            # 清空mock，准备测试面试官错误
            mock_claude.side_effect = Exception("401 Unauthorized")
            mock_claude.reset_mock()

            # 尝试启动面试
            from models import InterviewConfig
            config = InterviewConfig(
                interviewer_level="senior",
                interviewer_style="professional",
                focus_areas=["technical"],
                duration=30,
                language="zh"
            )
            orchestrator.update_config(config)

            result = orchestrator.route_and_execute()

            assert result["status"] == "error"
            assert result["agent"] == "interviewer"
            assert "API" in result["message"] or "密钥" in result["message"]

    def test_evaluator_api_error(self):
        """测试评估Agent API错误"""
        orchestrator = create_orchestrator()

        # 设置面试已结束状态
        with patch('agents.base_agent.BaseAgent.call_claude') as mock_claude:
            # 正常解析
            mock_claude.return_value = '{"name": "测试"}'
            orchestrator.update_resume_text("简历")
            orchestrator.update_jd_text("JD")
            orchestrator.route_and_execute()

            # 模拟面试已结束
            orchestrator.state.interview_ended = True

            # 测试报告生成失败
            mock_claude.side_effect = Exception("401 Unauthorized")
            mock_claude.reset_mock()

            result = orchestrator.route_and_execute()

            assert result["status"] == "error"
            assert result["agent"] == "evaluator"

    def test_unknown_error_message(self):
        """测试未知错误的处理"""
        orchestrator = create_orchestrator()

        with patch('agents.base_agent.BaseAgent.call_claude') as mock_claude:
            # 模拟一个未知错误
            mock_claude.side_effect = Exception("Some unknown error occurred")

            orchestrator.update_resume_text("测试简历")
            result = orchestrator.route_and_execute()

            assert result["status"] == "error"
            assert "error" in result["message"].lower()
            assert result.get("error_type") == "Exception"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
