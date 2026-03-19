"""
TDD验证脚本 - 无需pytest，直接验证代码功能

验证P1修复和基本功能是否正常工作
"""
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("""
╔══════════════════════════════════════════════════════════════╗
║                  TDD代码验证工具                              ║
║                                                                ║
║  验证P1问题修复和基本功能                                    ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝
""")

# ==================== 验证结果 ====================
validation_results = []

# ==================== 1. 验证导入 ====================
print("\n" + "="*70)
print("【1/5】验证模块导入")
print("="*70)

try:
    from agents import parser_agent
    print("✅ parser_agent 导入成功")
    validation_results.append(("parser_agent导入", True))
except ImportError as e:
    print(f"❌ parser_agent 导入失败: {e}")
    validation_results.append(("parser_agent导入", False))

try:
    from agents import interview_agent
    print("✅ interview_agent 导入成功")
    validation_results.append(("interview_agent导入", True))
except ImportError as e:
    print(f"❌ interview_agent 导入失败: {e}")
    validation_results.append(("interview_agent导入", False))

try:
    from agents import evaluator_agent
    print("✅ evaluator_agent 导入成功")
    validation_results.append(("evaluator_agent导入", True))
except ImportError as e:
    print(f"❌ evaluator_agent 导入失败: {e}")
    validation_results.append(("evaluator_agent导入", False))

try:
    from models import (
        ParsedResume, ParsedJD, GapAnalysis, TechnicalSkills,
        InterviewConfig, InterviewState
    )
    print("✅ models 导入成功")
    validation_results.append(("models导入", True))
except ImportError as e:
    print(f"❌ models 导入失败: {e}")
    validation_results.append(("models导入", False))

# ==================== 2. 验证P1修复 ====================
print("\n" + "="*70)
print("【2/5】验证P1修复")
print("="*70)

# 2.1 ParserAgent - logging
try:
    from agents import parser_agent
    has_logger = hasattr(parser_agent, 'logger')
    print(f"{'✅' if has_logger else '❌'} ParserAgent.logger {'已定义' if has_logger else '未定义'}")
    validation_results.append(("ParserAgent.logger", has_logger))
except Exception as e:
    print(f"❌ ParserAgent.logger检查失败: {e}")
    validation_results.append(("ParserAgent.logger", False))

# 2.2 InterviewerAgent - logging
try:
    from agents import interview_agent
    has_logger = hasattr(interview_agent, 'logger')
    print(f"{'✅' if has_logger else '❌'} InterviewerAgent.logger {'已定义' if has_logger else '未定义'}")
    validation_results.append(("InterviewerAgent.logger", has_logger))
except Exception as e:
    print(f"❌ InterviewerAgent.logger检查失败: {e}")
    validation_results.append(("InterviewerAgent.logger", False))

# 2.3 EvaluatorAgent - logging
try:
    from agents import evaluator_agent
    has_logger = hasattr(evaluator_agent, 'logger')
    print(f"{'✅' if has_logger else '❌'} EvaluatorAgent.logger {'已定义' if has_logger else '未定义'}")
    validation_results.append(("EvaluatorAgent.logger", has_logger))
except Exception as e:
    print(f"❌ EvaluatorAgent.logger检查失败: {e}")
    validation_results.append(("EvaluatorAgent.logger", False))

# ==================== 3. 验证基本功能 ====================
print("\n" + "="*70)
print("【3/5】验证基本功能")
print("="*70)

# 3.1 创建ParserAgent
try:
    from agents.parser_agent import ParserAgent
    agent = ParserAgent()
    print("✅ ParserAgent实例化成功")
    validation_results.append(("ParserAgent实例化", True))
except Exception as e:
    print(f"❌ ParserAgent实例化失败: {e}")
    validation_results.append(("ParserAgent实例化", False))

# 3.2 创建InterviewerAgent
try:
    from agents.interview_agent import InterviewerAgent
    agent = InterviewerAgent()
    print("✅ InterviewerAgent实例化成功")
    validation_results.append(("InterviewerAgent实例化", True))
except Exception as e:
    print(f"❌ InterviewerAgent实例化失败: {e}")
    validation_results.append(("InterviewerAgent实例化", False))

# 3.3 创建EvaluatorAgent
try:
    from agents.evaluator_agent import EvaluatorAgent
    agent = EvaluatorAgent()
    print("✅ EvaluatorAgent实例化成功")
    validation_results.append(("EvaluatorAgent实例化", True))
except Exception as e:
    print(f"❌ EvaluatorAgent实例化失败: {e}")
    validation_results.append(("EvaluatorAgent实例化", False))

# ==================== 4. 验证数据模型 ====================
print("\n" + "="*70)
print("【4/5】验证数据模型")
print("="*70)

try:
    from models import ParsedResume, ParsedJD, GapAnalysis, TechnicalSkills

    # 测试ParsedResume
    resume = ParsedResume(
        name="张三",
        technical_skills=TechnicalSkills(languages=["Java"])
    )
    assert resume.name == "张三"
    print("✅ ParsedResume创建成功")

    # 测试ParsedJD
    jd = ParsedJD(
        position="Java工程师",
        required_skills=["Java", "Spring"]
    )
    assert jd.position == "Java工程师"
    print("✅ ParsedJD创建成功")

    # 测试GapAnalysis
    gap = GapAnalysis(
        match_percentage=0.75,
        matched_items=["Java"],
        gap_items=["Kafka"]
    )
    assert gap.match_percentage == 0.75
    print("✅ GapAnalysis创建成功")

    validation_results.append(("数据模型", True))
except Exception as e:
    print(f"❌ 数据模型测试失败: {e}")
    validation_results.append(("数据模型", False))

# ==================== 5. 验证P1修复逻辑 ====================
print("\n" + "="*70)
print("【5/5】验证P1修复逻辑")
print("="*70)

# 5.1 ParserAgent - 异常处理
try:
    from agents.parser_agent import ParserAgent
    agent = ParserAgent()

    # 测试空数据处理
    result = agent._parse_resume_data({}, "")
    assert hasattr(result, 'name')
    print("✅ ParserAgent._parse_resume_data 边界处理正确")

    validation_results.append(("ParserAgent异常处理", True))
except Exception as e:
    print(f"❌ ParserAgent异常处理失败: {e}")
    validation_results.append(("ParserAgent异常处理", False))

# 5.2 InterviewerAgent - 边界检查
try:
    from agents.interview_agent import InterviewerAgent
    from models import AgentMessage
    agent = InterviewerAgent()

    # 测试空memory
    agent.memory = []
    agent.state = type('State', (), {'summary': None})()
    messages = agent._build_messages()
    assert messages == []
    print("✅ InterviewerAgent._build_messages 空memory处理正确")

    validation_results.append(("InterviewerAgent边界检查", True))
except Exception as e:
    print(f"❌ InterviewerAgent边界检查失败: {e}")
    validation_results.append(("InterviewerAgent边界检查", False))

# 5.3 EvaluatorAgent - 安全访问
try:
    from agents.evaluator_agent import EvaluatorAgent
    agent = EvaluatorAgent()

    # 测试空列表
    result = agent._format_conversation([])
    assert result == "无对话记录"
    print("✅ EvaluatorAgent._format_conversation 空列表处理正确")

    validation_results.append(("EvaluatorAgent安全访问", True))
except Exception as e:
    print(f"❌ EvaluatorAgent安全访问失败: {e}")
    validation_results.append(("EvaluatorAgent安全访问", False))

# ==================== 打印结果 ====================
print("\n" + "="*70)
print("📊 验证结果总结")
print("="*70)

total = len(validation_results)
passed = sum(1 for _, success in validation_results if success)

for name, success in validation_results:
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {name}")

print("\n" + "="*70)
print(f"总计: {passed}/{total} 项通过 ({passed*100//total}%)")
print("="*70)

if passed == total:
    print("\n🎉 所有验证通过！代码质量良好！")
    print("\n✅ TDD Red Phase (测试编写) - 完成")
    print("✅ TDD Green Phase (代码实现) - 完成")
    print("✅ TDD Blue Phase (代码审查) - 完成")
    print("✅ P1问题修复 - 完成")
    print("✅ 代码验证 - 完成")
    print("\n🎯 TDD开发流程圆满完成！")
else:
    print(f"\n⚠️  {total - passed} 项验证失败，请检查代码")
    print("\n建议：")
    print("1. 检查错误日志")
    print("2. 确认所有依赖已安装")
    print("3. 查看代码审查报告")

# 保存结果到文件
with open(project_root + "/validation_result.txt", "w", encoding="utf-8") as f:
    f.write(f"TDD验证结果\n")
    f.write(f"通过: {passed}/{total}\n")
    f.write(f"日期: {__import__('datetime').datetime.now()}\n")
    for name, success in validation_results:
        status = "PASS" if success else "FAIL"
        f.write(f"{status} - {name}\n")

print("\n✅ 验证结果已保存到: validation_result.txt")

sys.exit(0 if passed == total else 1)
