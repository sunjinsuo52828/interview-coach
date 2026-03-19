"""
运行所有TDD测试并生成报告
"""
import subprocess
import sys
from pathlib import Path

def run_test_file(test_file: str) -> tuple:
    """运行单个测试文件，返回(成功, 输出)"""
    project_root = Path(__file__).parent
    test_path = project_root / test_file

    cmd = [sys.executable, "-m", "pytest", str(test_path), "-v", "--tb=short"]

    print(f"\n{'='*70}")
    print(f"🧪 运行: {test_file}")
    print(f"{'='*70}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8',
            errors='replace'
        )

        output = result.stdout
        if result.stderr:
            output += "\n[STDERR]\n" + result.stderr

        success = result.returncode == 0
        return success, output
    except subprocess.TimeoutExpired:
        return False, "❌ 测试超时"
    except Exception as e:
        return False, f"❌ 运行失败: {e}"


def main():
    """运行所有TDD测试"""
    test_files = [
        "tests/unit/test_gap_analysis_tdd.py",
        "tests/unit/test_parse_resume_tdd.py",
        "tests/unit/test_parse_jd_tdd.py",
    ]

    print("""
╔══════════════════════════════════════════════════════════════╗
║                  TDD 测试套件执行                             ║
╚══════════════════════════════════════════════════════════════╝
""")

    results = {}
    for test_file in test_files:
        success, output = run_test_file(test_file)
        results[test_file] = (success, output)
        print(output)

        if success:
            print(f"✅ {test_file} - 通过")
        else:
            print(f"❌ {test_file} - 失败")

    # 汇总结果
    print(f"\n{'='*70}")
    print("📊 测试结果汇总")
    print(f"{'='*70}")

    passed = sum(1 for s, _ in results.values() if s)
    total = len(results)

    for test_file, (success, _) in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_file}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试文件失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
