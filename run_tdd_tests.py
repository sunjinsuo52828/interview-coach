"""
TDD测试自动运行器

运行所有TDD测试并生成报告
"""
import sys
import os
from pathlib import Path
import traceback

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_pytest_test(test_file_name, test_class_name, test_method_name=None):
    """手动运行单个测试"""
    print(f"\n{'='*70}")
    print(f"🧪 运行测试: {test_file_name}::{test_class_name}")
    if test_method_name:
        print(f"   方法: {test_method_name}")
    print('='*70)

    try:
        # 导入测试模块
        module_path = f"tests.unit.{test_file_name}"
        module = __import__(module_path, fromlist=[test_class_name])
        test_class = getattr(module, test_class_name)

        # 创建测试实例
        instance = test_class()

        # 运行setup fixture
        if hasattr(instance, 'setup_method'):
            instance.setup_method()

        # 运行测试方法
        if test_method_name:
            test_method = getattr(instance, test_method_name)
            test_method()
            print(f"✅ {test_method_name} - PASSED")
            return True, 1, 0
        else:
            # 运行所有测试方法
            passed = 0
            failed = 0
            for attr_name in dir(instance):
                if attr_name.startswith('test_'):
                    try:
                        test_method = getattr(instance, attr_name)
                        test_method()
                        print(f"✅ {attr_name} - PASSED")
                        passed += 1
                    except Exception as e:
                        print(f"❌ {attr_name} - FAILED: {e}")
                        failed += 1
            return failed == 0, passed, failed

    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        traceback.print_exc()
        return False, 0, 1


def run_gap_analysis_tests():
    """运行gap_analysis测试"""
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*20 + "ParserAgent.gap_analysis 测试" + " "*22 + "║")
    print("╚" + "═"*68 + "╝")

    results = []

    # 测试1: 正常场景
    success, p, f = run_pytest_test(
        'test_gap_analysis_tdd',
        'TestGapAnalysisTDD',
        'test_gap_analysis_normal_case'
    )
    results.append(('test_gap_analysis_normal_case', success))
    if success: print("    → 匹配度计算正确 ✓")

    # 测试2: 空简历
    success, p, f = run_pytest_test(
        'test_gap_analysis_tdd',
        'TestGapAnalysisTDD',
        'test_gap_analysis_empty_resume'
    )
    results.append(('test_gap_analysis_empty_resume', success))
    if success: print("    → 边界处理正确 ✓")

    # 测试3: 空JD
    success, p, f = run_pytest_test(
        'test_gap_analysis_tdd',
        'TestGapAnalysisTDD',
        'test_gap_analysis_empty_jd'
    )
    results.append(('test_gap_analysis_empty_jd', success))
    if success: print("    → 边界处理正确 ✓")

    # 测试4: 完全匹配
    success, p, f = run_pytest_test(
        'test_gap_analysis_tdd',
        'TestGapAnalysisTDD',
        'test_gap_analysis_perfect_match'
    )
    results.append(('test_gap_analysis_perfect_match', success))
    if success: print("    → 匹配逻辑正确 ✓")

    # 测试5: 完全不匹配
    success, p, f = run_pytest_test(
        'test_gap_analysis_tdd',
        'TestGapAnalysisTDD',
        'test_gap_analysis_no_match'
    )
    results.append(('test_gap_analysis_no_match', success))
    if success: print("    → 不匹配逻辑正确 ✓")

    # 测试6: 数据类型验证
    success, p, f = run_pytest_test(
        'test_gap_analysis_tdd',
        'TestGapAnalysisTDD',
        'test_gap_analysis_return_types'
    )
    results.append(('test_gap_analysis_return_types', success))
    if success: print("    → 返回类型正确 ✓")

    return results


def verify_basic_functionality():
    """验证基本功能（不需要mock的简单测试）"""
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*25 + "基本功能验证" + " "*25 + "║")
    print("╚" + "═"*68 + "╝")

    results = []

    # 1. 验证ParserAgent可以创建
    try:
        from agents.parser_agent import ParserAgent
        agent = ParserAgent()
        print("✅ ParserAgent实例化 - PASSED")
        results.append(("ParserAgent实例化", True))
    except Exception as e:
        print(f"❌ ParserAgent实例化 - FAILED: {e}")
        results.append(("ParserAgent实例化", False))

    # 2. 验证InterviewerAgent可以创建
    try:
        from agents.interview_agent import InterviewerAgent
        agent = InterviewerAgent()
        print("✅ InterviewerAgent实例化 - PASSED")
        results.append(("InterviewerAgent实例化", True))
    except Exception as e:
        print(f"❌ InterviewerAgent实例化 - FAILED: {e}")
        results.append(("InterviewerAgent实例化", False))

    # 3. 验证EvaluatorAgent可以创建
    try:
        from agents.evaluator_agent import EvaluatorAgent
        agent = EvaluatorAgent()
        print("✅ EvaluatorAgent实例化 - PASSED")
        results.append(("EvaluatorAgent实例化", True))
    except Exception as e:
        print(f"❌ EvaluatorAgent实例化 - FAILED: {e}")
        results.append(("EvaluatorAgent实例化", False))

    # 4. 验证模型可以创建
    try:
        from models import (
            ParsedResume, ParsedJD, GapAnalysis,
            TechnicalSkills, InterviewConfig, InterviewState
        )

        # 创建ParsedResume
        resume = ParsedResume(
            name="测试",
            technical_skills=TechnicalSkills()
        )
        assert resume.name == "测试"
        print("✅ ParsedResume创建 - PASSED")
        results.append(("ParsedResume创建", True))

        # 创建ParsedJD
        jd = ParsedJD(
            position="测试职位",
            required_skills=["Java"]
        )
        assert jd.position == "测试职位"
        print("✅ ParsedJD创建 - PASSED")
        results.append(("ParsedJD创建", True))

        # 创建GapAnalysis
        gap = GapAnalysis(
            match_percentage=0.5,
            matched_items=["Java"],
            gap_items=["Kafka"]
        )
        assert gap.match_percentage == 0.5
        print("✅ GapAnalysis创建 - PASSED")
        results.append(("GapAnalysis创建", True))

    except Exception as e:
        print(f"❌ 模型创建 - FAILED: {e}")
        results.append(("模型创建", False))

    return results


def verify_data_parsing():
    """验证数据解析逻辑（不需要Claude API）"""
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*25 + "数据解析验证" + " "*25 + "║")
    print("╚" + "═"*68 + "╝")

    results = []

    try:
        from agents.parser_agent import ParserAgent
        from models import ParsedResume, ParsedJD, GapAnalysis, TechnicalSkills

        agent = ParserAgent()

        # 测试_parse_resume_data的边界处理
        print("\n📝 测试: _parse_resume_data边界处理")

        # 1. 空数据
        result = agent._parse_resume_data({}, "")
        assert isinstance(result, ParsedResume)
        assert result.name == ""
        print("  ✅ 空数据处理正确")

        # 2. 完整数据
        full_data = {
            "name": "张三",
            "phone": "13800138000",
            "email": "test@example.com",
            "experience_years": 5,
            "current_role": "工程师",
            "technical_skills": {
                "languages": ["Java", "Python"],
                "frameworks": ["Spring"],
                "middleware": [],
                "databases": ["MySQL"],
                "devops": []
            },
            "projects": [
                {
                    "name": "项目A",
                    "role": "开发",
                    "duration": "2020-2023",
                    "tech_stack": ["Java"],
                    "description": "描述",
                    "highlights": ["亮点"]
                }
            ],
            "education": []
        }

        result = agent._parse_resume_data(full_data, "原始文本")
        assert result.name == "张三"
        assert "Java" in result.technical_skills.languages
        assert len(result.projects) == 1
        print("  ✅ 完整数据处理正确")

        # 3. 无效项目数据（测试P1修复）
        invalid_data = {
            "name": "测试",
            "projects": [
                {"name": "有效项目"},  # 有效
                {"invalid": "项目"},    # 缺少必要字段
                None,                   # None值
            ]
        }

        result = agent._parse_resume_data(invalid_data, "")
        # 应该跳过无效项目，只保留有效的
        assert len(result.projects) == 1
        print("  ✅ 无效数据跳过正确（P1修复验证）")

        results.append(("_parse_resume_data", True))

    except Exception as e:
        print(f"  ❌ _parse_resume_data测试失败: {e}")
        traceback.print_exc()
        results.append(("_parse_resume_data", False))

    return results


def verify_interviewer_fixes():
    """验证InterviewerAgent的P1修复"""
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*25 + "Interviewer修复验证" + " "*24 + "║")
    print("╚" + "═"*68 + "╝")

    results = []

    try:
        from agents.interview_agent import InterviewerAgent
        from models import AgentMessage

        agent = InterviewerAgent()

        # 测试_build_messages边界处理
        print("\n📝 测试: _build_messages边界处理（P1修复）")

        # 1. 空memory
        agent.memory = []
        agent.state = type('State', (), {'summary': None})()
        messages = agent._build_messages()
        assert messages == []
        print("  ✅ 空memory返回空列表")

        # 2. 有memory无summary
        agent.memory = [
            AgentMessage(role="user", content="你好"),
            AgentMessage(role="assistant", content="请自我介绍")
        ]
        messages = agent._build_messages()
        assert len(messages) == 2
        print("  ✅ 无summary使用完整memory")

        # 3. 有summary
        agent.state.summary = "之前的面试摘要"
        messages = agent._build_messages()
        assert len(messages) == 3  # summary + 2条消息
        assert "之前的面试摘要" in messages[0]["content"]
        print("  ✅ 有summary使用摘要+最近消息")

        results.append(("_build_messages边界检查", True))

    except Exception as e:
        print(f"  ❌ _build_messages测试失败: {e}")
        traceback.print_exc()
        results.append(("_build_messages边界检查", False))

    return results


def verify_evaluator_fixes():
    """验证EvaluatorAgent的P1修复"""
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*25 + "Evaluator修复验证" + " "*25 + "║")
    print("╚" + "═"*68 + "╝")

    results = []

    try:
        from agents.evaluator_agent import EvaluatorAgent
        from models import ConversationTurn

        agent = EvaluatorAgent()

        # 测试_format_conversation边界处理
        print("\n📝 测试: _format_conversation边界处理（P1修复）")

        # 1. 空列表
        result = agent._format_conversation([])
        assert result == "无对话记录"
        print("  ✅ 空列表返回提示文本")

        # 2. 包含None的列表
        class MockTurn:
            def __init__(self, valid=True):
                if valid:
                    self.question_text = "问题"
                    self.user_answer = "回答"
                    self.score = 80
                    self.evaluation_notes = ["备注"]

        turns = [
            MockTurn(True),
            None,  # None值
            MockTurn(True),
        ]

        result = agent._format_conversation(turns)
        assert "第1轮" in result
        assert "第3轮" in result
        # 应该跳过None（第2轮）
        lines = result.split("\n")
        round_count = sum(1 for line in lines if "第" in line and "轮" in line)
        assert round_count == 2  # 只有2轮有效
        print("  ✅ None值正确跳过")

        # 3. 缺少属性的turn（测试getattr）
        class PartialTurn:
            def __init__(self):
                self.question_text = "问题"
                # 缺少其他属性

        turns = [PartialTurn()]
        result = agent._format_conversation(turns)
        assert "N/A" in result  # 应该使用默认值
        print("  ✅ 缺少属性使用默认值（P1修复验证）")

        results.append(("_format_conversation", True))

    except Exception as e:
        print(f"  ❌ _format_conversation测试失败: {e}")
        traceback.print_exc()
        results.append(("_format_conversation", False))

    return results


def print_final_summary(all_results):
    """打印最终总结"""
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*20 + "测试结果总结" + " "*24 + "║")
    print("╚" + "═"*68 + "╝")

    total = 0
    passed = 0

    for category, results in all_results.items():
        print(f"\n【{category}】")
        for test_name, success in results:
            total += 1
            if success:
                passed += 1
                print(f"  ✅ {test_name}")
            else:
                print(f"  ❌ {test_name}")

    print("\n" + "="*70)
    print(f"总计: {passed}/{total} 项通过 ({passed*100//total if total > 0 else 0}%)")
    print("="*70)

    if passed == total:
        print("\n🎉 所有测试通过！TDD开发成功完成！")
        return True
    else:
        print(f"\n⚠️  {total - passed} 项测试失败，需要修复")
        return False


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  TDD自动测试运行器                              ║
║                                                                ║
║  无需pytest，直接运行测试验证代码                              ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝
""")

    all_results = {}

    # 1. 基本功能验证
    all_results["基本功能"] = verify_basic_functionality()

    # 2. 数据解析验证
    all_results["数据解析"] = verify_data_parsing()

    # 3. Interviewer修复验证
    all_results["Interviewer修复"] = verify_interviewer_fixes()

    # 4. Evaluator修复验证
    all_results["Evaluator修复"] = verify_evaluator_fixes()

    # 5. gap_analysis测试
    all_results["Gap分析"] = run_gap_analysis_tests()

    # 打印总结
    success = print_final_summary(all_results)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
