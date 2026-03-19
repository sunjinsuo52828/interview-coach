"""
运行TDD测试并生成报告
"""
import subprocess
import sys
from pathlib import Path

def run_tests(test_file: str = "tests/unit/test_gap_analysis_tdd.py"):
    """运行测试"""
    project_root = Path(__file__).parent
    test_path = project_root / test_file

    cmd = [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short"]

    print(f"🧪 运行测试: {' '.join(cmd)}")
    print("=" * 60)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ 测试超时")
        return False
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
