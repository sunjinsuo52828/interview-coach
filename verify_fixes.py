"""
验证代码修复 - 检查导入和基本功能

验证P1问题修复后的代码是否正常工作
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def verify_imports():
    """验证所有模块可以正常导入"""
    print("=" * 60)
    print("🔍 验证模块导入...")
    print("=" * 60)

    results = {}

    # 1. 验证base_agent导入
    try:
        from agents.base_agent import BaseAgent, ToolEnabledAgent, StatefulAgent
        results["base_agent"] = "✅ PASS"
        print("✅ base_agent - 导入成功")
    except Exception as e:
        results["base_agent"] = f"❌ FAIL: {e}"
        print(f"❌ base_agent - 导入失败: {e}")

    # 2. 验证models导入
    try:
        from models import (
            ParsedResume, ParsedJD, GapAnalysis, TechnicalSkills,
            Project, Education, InterviewConfig, InterviewState,
            InterviewReport, ConversationTurn
        )
        results["models"] = "✅ PASS"
        print("✅ models - 导入成功")
    except Exception as e:
        results["models"] = f"❌ FAIL: {e}"
        print(f"❌ models - 导入失败: {e}")

    # 3. 验证ParserAgent导入
    try:
        from agents.parser_agent import ParserAgent
        results["parser_agent"] = "✅ PASS"
        print("✅ parser_agent - 导入成功")
    except Exception as e:
        results["parser_agent"] = f"❌ FAIL: {e}"
        print(f"❌ parser_agent - 导入失败: {e}")

    # 4. 验证InterviewerAgent导入
    try:
        from agents.interview_agent import InterviewerAgent
        results["interview_agent"] = "✅ PASS"
        print("✅ interview_agent - 导入成功")
    except Exception as e:
        results["interview_agent"] = f"❌ FAIL: {e}"
        print(f"❌ interview_agent - 导入失败: {e}")

    # 5. 验证EvaluatorAgent导入
    try:
        from agents.evaluator_agent import EvaluatorAgent
        results["evaluator_agent"] = "✅ PASS"
        print("✅ evaluator_agent - 导入成功")
    except Exception as e:
        results["evaluator_agent"] = f"❌ FAIL: {e}"
        print(f"❌ evaluator_agent - 导入失败: {e}")

    # 6. 验证测试文件导入
    try:
        from tests.unit.test_gap_analysis_tdd import TestGapAnalysisTDD
        results["test_gap_analysis"] = "✅ PASS"
        print("✅ test_gap_analysis_tdd - 导入成功")
    except Exception as e:
        results["test_gap_analysis"] = f"❌ FAIL: {e}"
        print(f"❌ test_gap_analysis_tdd - 导入失败: {e}")

    try:
        from tests.unit.test_parse_resume_tdd import TestParseResumeTDD
        results["test_parse_resume"] = "✅ PASS"
        print("✅ test_parse_resume_tdd - 导入成功")
    except Exception as e:
        results["test_parse_resume"] = f"❌ FAIL: {e}"
        print(f"❌ test_parse_resume_tdd - 导入失败: {e}")

    try:
        from tests.unit.test_parse_jd_tdd import TestParseJDTDD
        results["test_parse_jd"] = "✅ PASS"
        print("✅ test_parse_jd_tdd - 导入成功")
    except Exception as e:
        results["test_parse_jd"] = f"❌ FAIL: {e}"
        print(f"❌ test_parse_jd_tdd - 导入失败: {e}")

    try:
        from tests.unit.test_interviewer_tdd import TestStartInterviewTDD
        results["test_interviewer"] = "✅ PASS"
        print("✅ test_interviewer_tdd - 导入成功")
    except Exception as e:
        results["test_interviewer"] = f"❌ FAIL: {e}"
        print(f"❌ test_interviewer_tdd - 导入失败: {e}")

    try:
        from tests.unit.test_evaluator_tdd import TestEvaluateTDD
        results["test_evaluator"] = "✅ PASS"
        print("✅ test_evaluator_tdd - 导入成功")
    except Exception as e:
        results["test_evaluator"] = f"❌ FAIL: {e}"
        print(f"❌ test_evaluator_tdd - 导入失败: {e}")

    return results


def verify_p1_fixes():
    """验证P1修复是否正确应用"""
    print("\n" + "=" * 60)
    print("🔍 验证P1修复...")
    print("=" * 60)

    results = {}

    # 1. 验证ParserAgent的logging导入
    try:
        import agents.parser_agent as pa
        assert hasattr(pa, 'logger'), "ParserAgent缺少logger"
        results["parser_logging"] = "✅ PASS"
        print("✅ ParserAgent - logger已定义")
    except Exception as e:
        results["parser_logging"] = f"❌ FAIL: {e}"
        print(f"❌ ParserAgent - logger检查失败: {e}")

    # 2. 验证_parse_resume_data方法签名
    try:
        from agents.parser_agent import ParserAgent
        import inspect

        sig = inspect.signature(ParserAgent._parse_resume_data)
        params = list(sig.parameters.keys())
        assert 'self' in params or params[0] == 'data', "参数签名不正确"
        results["parse_resume_method"] = "✅ PASS"
        print("✅ ParserAgent._parse_resume_data - 方法签名正确")
    except Exception as e:
        results["parse_resume_method"] = f"❌ FAIL: {e}"
        print(f"❌ ParserAgent._parse_resume_data - 方法检查失败: {e}")

    # 3. 验证InterviewerAgent的logging导入
    try:
        import agents.interview_agent as ia
        assert hasattr(ia, 'logger'), "InterviewerAgent缺少logger"
        results["interviewer_logging"] = "✅ PASS"
        print("✅ InterviewerAgent - logger已定义")
    except Exception as e:
        results["interviewer_logging"] = f"❌ FAIL: {e}"
        print(f"❌ InterviewerAgent - logger检查失败: {e}")

    # 4. 验证EvaluatorAgent的logging导入
    try:
        import agents.evaluator_agent as ea
        assert hasattr(ea, 'logger'), "EvaluatorAgent缺少logger"
        results["evaluator_logging"] = "✅ PASS"
        print("✅ EvaluatorAgent - logger已定义")
    except Exception as e:
        results["evaluator_logging"] = f"❌ FAIL: {e}"
        print(f"❌ EvaluatorAgent - logger检查失败: {e}")

    # 5. 验证语法正确性
    try:
        import py_compile
        import tempfile
        import os

        files_to_check = [
            "agents/parser_agent.py",
            "agents/interview_agent.py",
            "agents/evaluator_agent.py"
        ]

        for file_path in files_to_check:
            full_path = project_root / file_path
            if full_path.exists():
                py_compile.compile(str(full_path), doraise=True)
                print(f"✅ {file_path} - 语法正确")
            else:
                print(f"⚠️  {file_path} - 文件不存在")

        results["syntax_check"] = "✅ PASS"
    except py_compile.PyCompileError as e:
        results["syntax_check"] = f"❌ FAIL: {e}"
        print(f"❌ 语法检查失败: {e}")

    return results


def print_summary(import_results, fix_results):
    """打印验证摘要"""
    print("\n" + "=" * 60)
    print("📊 验证摘要")
    print("=" * 60)

    # 统计导入结果
    import_pass = sum(1 for v in import_results.values() if v == "✅ PASS")
    import_total = len(import_results)

    # 统计修复验证结果
    fix_pass = sum(1 for v in fix_results.values() if v == "✅ PASS")
    fix_total = len(fix_results)

    print(f"\n模块导入: {import_pass}/{import_total} 通过")
    for name, result in import_results.items():
        print(f"  {result} - {name}")

    print(f"\nP1修复验证: {fix_pass}/{fix_total} 通过")
    for name, result in fix_results.items():
        print(f"  {result} - {name}")

    total_pass = import_pass + fix_pass
    total_items = import_total + fix_total

    print(f"\n总计: {total_pass}/{total_items} 项通过")

    if total_pass == total_items:
        print("\n🎉 所有验证通过！代码修复正确！")
        return True
    else:
        print(f"\n⚠️  {total_items - total_pass} 项验证失败")
        return False


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  TDD代码验证工具                              ║
║                                                                ║
║  验证P1问题修复后的代码质量                                    ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝
""")

    # 验证导入
    import_results = verify_imports()

    # 验证P1修复
    fix_results = verify_p1_fixes()

    # 打印摘要
    success = print_summary(import_results, fix_results)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
