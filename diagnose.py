"""
简单诊断脚本 - 找出问题所在
"""
import sys
import os

print("=== 脚本开始执行 ===")

# 打印Python版本
print(f"Python版本: {sys.version}")

# 打印工作目录
print(f"工作目录: {os.getcwd()}")

# 添加项目路径
project_root = os.path.dirname(os.path.abspath(__file__))
print(f"项目根目录: {project_root}")
sys.path.insert(0, project_root)

print("=== 开始导入模块 ===")

try:
    print("1. 导入config...")
    import config
    print("   ✅ config导入成功")
except Exception as e:
    print(f"   ❌ config导入失败: {e}")
    sys.exit(1)

try:
    print("2. 导入models...")
    from models import ParsedResume
    print("   ✅ models导入成功")
except Exception as e:
    print(f"   ❌ models导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("3. 导入agents.base_agent...")
    from agents.base_agent import BaseAgent
    print("   ✅ base_agent导入成功")
except Exception as e:
    print(f"   ❌ base_agent导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("4. 导入agents.parser_agent...")
    from agents.parser_agent import ParserAgent
    print("   ✅ parser_agent导入成功")
except Exception as e:
    print(f"   ❌ parser_agent导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("5. 创建ParserAgent实例...")
    agent = ParserAgent()
    print(f"   ✅ ParserAgent创建成功: {agent}")
except Exception as e:
    print(f"   ❌ ParserAgent创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== 所有检查通过 ===")
print("✅ 基本功能正常")
