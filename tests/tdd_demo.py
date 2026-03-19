"""
TDD开发演示

使用多个Agent协调，以TDD方式开发功能。
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.tdd_orchestrator import TDDOrchestrator


def demo_tdd_development():
    """演示TDD开发流程"""

    print("""
╔══════════════════════════════════════════════════════════════╗
║           TDD开发演示 - 多Agent协调工作流                      ║
║                                                                ║
║  🔴 Red   → TestWriterAgent  编写测试                          ║
║  🟢 Green → CodeWriterAgent  编写代码                          ║
║  🧪 Test  → TestRunnerAgent   运行测试                          ║
║  🔵 Blue  → CodeReviewerAgent 代码审查                          ║
║                                                                ║
║  循环直到：✅ 测试通过 + ✅ 代码审查通过                        ║
╚══════════════════════════════════════════════════════════════╝
""")

    # 定义要开发的功能规格
    feature_spec = {
        "name": "gap_analysis",
        "module": "parser_agent",
        "description": "Gap分析 - 对比简历和JD，输出匹配度和差距项",
        "requirements": [
            "输入：ParsedResume对象和ParsedJD对象",
            "输出：GapAnalysis对象，包含匹配度百分比、匹配项、差距项",
            "需要提取简历中的技能列表",
            "需要提取JD中的技能要求列表",
            "计算匹配度百分比",
            "识别匹配项和差距项"
        ],
        "test_requirements": [
            "测试正常情况：简历和JD都有技能",
            "测试边界情况：简历为空",
            "测试边界情况：JD为空",
            "测试边界情况：完全匹配",
            "测试边界情况：完全不匹配"
        ]
    }

    # 创建TDD编排器
    orchestrator = TDDOrchestrator(
        project_root=str(Path(__file__).parent.parent)
    )

    # 执行TDD开发
    result = orchestrator.develop_feature(
        feature_spec=feature_spec,
        max_cycles=5
    )

    # 打印结果
    print("\n" + "=" * 60)
    print("📊 开发结果汇总")
    print("=" * 60)

    if result["success"]:
        print(f"✅ 功能: {result['feature']}")
        print(f"🔄 TDD循环次数: {result['cycles']}")
        print(f"📁 测试文件: {result['test_file']}")
        print(f"📁 代码文件: {result['code_file']}")
        print(f"📊 审查评分: {result['review'].get('overall_score', 'N/A')}/100")
        print(f"✍️ 审查结果: {result['review'].get('approval', 'N/A')}")
        print("\n✨ 开发成功！")
    else:
        print(f"❌ 开发失败: {result['reason']}")
        print(f"📝 详情: {result.get('detail', {})}")

    # 打印历史记录
    print("\n" + "=" * 60)
    print("📜 开发历史")
    print("=" * 60)

    for i, entry in enumerate(result.get("history", []), 1):
        phase = entry["phase"]
        timestamp = entry["timestamp"].split("T")[1][:8]
        print(f"{i}. [{timestamp}] {phase}")

        if "file" in entry:
            print(f"   文件: {entry['file']}")
        if "result" in entry:
            r = entry["result"]
            summary = r.get("summary", {})
            if summary:
                print(f"   结果: 通过{summary['passed']}/{summary['total']}")

    return result


def interactive_tdd():
    """交互式TDD开发"""

    print("""
╔══════════════════════════════════════════════════════════════╗
║          交互式TDD开发                                       ║
║                                                                ║
║  你可以输入要开发的功能规格，系统将使用TDD流程开发。          ║
║                                                                ║
╚══════════════════════════════════════════════════════════════╝
""")

    while True:
        print("\n请选择：")
        print("  1. 演示TDD流程（gap_analysis功能）")
        print("  2. 自定义功能开发")
        print("  3. 查看已有功能列表")
        print("  q. 退出")

        choice = input("\n请选择 (1-3/q): ").strip()

        if choice == "1":
            demo_tdd_development()
        elif choice == "2":
            custom_feature_tdd()
        elif choice == "3":
            list_available_features()
        elif choice.lower() == "q":
            print("\n👋 再见！")
            break
        else:
            print("❌ 无效选择，请重试")


def custom_feature_tdd():
    """自定义功能TDD开发"""
    print("\n" + "=" * 60)
    print("📝 自定义功能开发")
    print("=" * 60)

    # 收集功能信息
    name = input("功能名称 (如: calculate_match_score): ").strip()
    if not name:
        print("❌ 功能名称不能为空")
        return

    print("\n请输入功能需求（每行一个，空行结束）:")
    requirements = []
    while True:
        req = input("  > ").strip()
        if not req:
            break
        requirements.append(req)

    if not requirements:
        print("❌ 至少需要一个需求")
        return

    # 构建功能规格
    feature_spec = {
        "name": name,
        "module": input("模块路径 (如: parser_agent，直接回车跳过): ").strip() or None,
        "description": input("功能描述: ").strip(),
        "requirements": requirements
    }

    # 执行TDD
    orchestrator = TDDOrchestrator()
    result = orchestrator.develop_feature(feature_spec)

    if result["success"]:
        print(f"\n✅ 功能 '{name}' 开发成功！")
        print(f"📁 测试文件: {result['test_file']}")
        print(f"📁 代码文件: {result['code_file']}")
    else:
        print(f"\n❌ 功能 '{name}' 开发失败: {result['reason']}")


def list_available_features():
    """列出可用功能"""
    print("\n" + "=" * 60)
    print("📋 可用功能列表")
    print("=" * 60)

    features = [
        {
            "name": "gap_analysis",
            "description": "Gap分析 - 对比简历和JD",
            "module": "parser_agent",
            "status": "✅ 已实现"
        },
        {
            "name": "parse_resume",
            "description": "简历解析 - 提取技术栈和项目",
            "module": "parser_agent",
            "status": "✅ 已实现"
        },
        {
            "name": "parse_jd",
            "description": "JD解析 - 提取技能要求",
            "module": "parser_agent",
            "status": "✅ 已实现"
        },
        {
            "name": "interview_chat",
            "description": "面试对话 - 处理用户输入",
            "module": "interview_agent",
            "status": "✅ 已实现"
        },
        {
            "name": "generate_report",
            "description": "评估报告 - 生成面试结果",
            "module": "evaluator_agent",
            "status": "✅ 已实现"
        },
        {
            "name": "knowledge_search",
            "description": "知识库搜索 - RAG检索 (Week 3)",
            "module": "knowledge_agent",
            "status": "⏳ 待开发"
        },
        {
            "name": "react_loop",
            "description": "ReAct推理循环 (Week 4)",
            "module": "interview_agent",
            "status": "⏳ 待开发"
        }
    ]

    for i, feature in enumerate(features, 1):
        status = feature["status"]
        print(f"{i}. {status} {feature['name']}")
        print(f"   描述: {feature['description']}")
        print(f"   模块: {feature['module']}")
        print()


if __name__ == "__main__":
    import sys

    # 支持命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_tdd_development()
    else:
        try:
            interactive_tdd()
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，再见！")
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()
