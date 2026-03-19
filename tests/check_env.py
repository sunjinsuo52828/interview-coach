"""
测试环境准备检查

检查开发和测试环境是否就绪。
"""
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple


class EnvironmentChecker:
    """环境检查器"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()

    def check_all(self) -> Dict[str, any]:
        """检查所有环境项目"""
        results = {
            "project_structure": self.check_project_structure(),
            "dependencies": self.check_dependencies(),
            "test_config": self.check_test_config(),
            "test_infrastructure": self.check_test_infrastructure(),
            "agents": self.check_agents(),
            "models": self.check_models(),
        }

        return results

    def check_project_structure(self) -> Dict:
        """检查项目结构"""
        print("\n" + "=" * 60)
        print("📁 检查项目结构")
        print("=" * 60)

        required_dirs = [
            "agents",
            "models",
            "ui",
            "tests",
            "docs",
            "prompts"
        ]

        required_files = [
            "config.py",
            "requirements.txt",
            ".env.example",
            "README.md"
        ]

        results = {
            "dirs": {"present": [], "missing": []},
            "files": {"present": [], "missing": []}
        }

        # 检查目录
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                results["dirs"]["present"].append(dir_name)
                print(f"  ✅ {dir_name}/")
            else:
                results["dirs"]["missing"].append(dir_name)
                print(f"  ❌ {dir_name}/ (缺失)")

        # 检查文件
        for file_name in required_files:
            file_path = self.project_root / file_name
            if file_path.exists() and file_path.is_file():
                results["files"]["present"].append(file_name)
                print(f"  ✅ {file_name}")
            else:
                results["files"]["missing"].append(file_name)
                print(f"  ❌ {file_name} (缺失)")

        # 检查tests子目录
        test_subdirs = ["unit", "integration", "fixtures"]
        for subdir in test_subdirs:
            subdir_path = self.project_root / "tests" / subdir
            if subdir_path.exists():
                print(f"  ✅ tests/{subdir}/")
            else:
                print(f"  ⚠️  tests/{subdir}/ (建议创建)")

        return results

    def check_dependencies(self) -> Dict:
        """检查依赖包"""
        print("\n" + "=" * 60)
        print("📦 检查依赖包")
        print("=" * 60)

        required_packages = {
            "anthropic": "Claude API客户端",
            "streamlit": "Web UI",
            "pydantic": "数据验证",
            "pytest": "测试框架",
            "python-dotenv": "环境变量"
        }

        results = {"installed": [], "missing": []}

        for package, description in required_packages.items():
            try:
                __import__(package)
                results["installed"].append(package)
                print(f"  ✅ {package:15s} - {description}")
            except ImportError:
                results["missing"].append(package)
                print(f"  ❌ {package:15s} - {description} (未安装)")

        return results

    def check_test_config(self) -> Dict:
        """检查测试配置"""
        print("\n" + "=" * 60)
        print("⚙️  检查测试配置")
        print("=" * 60)

        results = {
            "pytest_config": None,
            "pyproject_toml": None,
            "setup_cfg": None,
            "conftest": None
        }

        # 检查pytest.ini
        pytest_ini = self.project_root / "pytest.ini"
        if pytest_ini.exists():
            results["pytest_config"] = "pytest.ini"
            print("  ✅ pytest.ini")
        else:
            print("  ⚠️  pytest.ini (建议创建)")

        # 检查pyproject.toml
        pyproject = self.project_root / "pyproject.toml"
        if pyproject.exists():
            results["pyproject_toml"] = "pyproject.toml"
            print("  ✅ pyproject.toml")
        else:
            print("  ⚠️  pyproject.toml (可选)")

        # 检查setup.cfg
        setup_cfg = self.project_root / "setup.cfg"
        if setup_cfg.exists():
            results["setup_cfg"] = "setup.cfg"
            print("  ✅ setup.cfg")
        else:
            print("  ⚠️  setup.cfg (可选)")

        # 检查conftest.py
        conftest = self.project_root / "tests" / "conftest.py"
        if conftest.exists():
            results["conftest"] = "tests/conftest.py"
            print("  ✅ tests/conftest.py")
        else:
            print("  ❌ tests/conftest.py (需要创建)")

        return results

    def check_test_infrastructure(self) -> Dict:
        """检查测试基础设施"""
        print("\n" + "=" * 60)
        print("🧪 检查测试基础设施")
        print("=" * 60)

        results = {
            "fixtures": False,
            "mocks": False,
            "helpers": False,
            "test_data": False
        }

        # 检查fixtures目录
        fixtures_dir = self.project_root / "tests" / "fixtures"
        if fixtures_dir.exists():
            fixtures = list(fixtures_dir.glob("*"))
            if fixtures:
                results["fixtures"] = True
                print(f"  ✅ fixtures/ ({len(fixtures)} 个文件)")
            else:
                print("  ⚠️  fixtures/ (空目录)")
        else:
            print("  ❌ fixtures/ (不存在)")

        # 检查__init__.py
        test_init = self.project_root / "tests" / "__init__.py"
        if test_init.exists():
            print("  ✅ tests/__init__.py")
        else:
            print("  ⚠️  tests/__init__.py (建议创建)")

        # 检查pytest运行
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"  ✅ pytest: {version}")
                results["pytest_works"] = True
            else:
                print("  ❌ pytest (无法运行)")
                results["pytest_works"] = False
        except Exception as e:
            print(f"  ❌ pytest: {e}")
            results["pytest_works"] = False

        return results

    def check_agents(self) -> Dict:
        """检查Agent模块"""
        print("\n" + "=" * 60)
        print("🤖 检查Agent模块")
        print("=" * 60)

        agent_files = [
            "base_agent.py",
            "parser_agent.py",
            "interview_agent.py",
            "evaluator_agent.py"
        ]

        results = {"present": [], "missing": []}

        for agent_file in agent_files:
            agent_path = self.project_root / "agents" / agent_file
            if agent_path.exists():
                results["present"].append(agent_file)
                print(f"  ✅ {agent_file}")
            else:
                results["missing"].append(agent_file)
                print(f"  ❌ {agent_file}")

        return results

    def check_models(self) -> Dict:
        """检查数据模型"""
        print("\n" + "=" * 60)
        print("📊 检查数据模型")
        print("=" * 60)

        model_file = self.project_root / "models" / "__init__.py"

        if model_file.exists():
            print("  ✅ models/__init__.py")

            # 尝试导入
            try:
                sys.path.insert(0, str(self.project_root))
                from models import (
                    ParsedResume, ParsedJD, GapAnalysis,
                    InterviewConfig, InterviewState, InterviewReport
                )
                print("  ✅ 所有模型类可导入")

                # 检查关键类
                classes = [ParsedResume, ParsedJD, GapAnalysis, InterviewConfig]
                for cls in classes:
                    print(f"  ✅ {cls.__name__}")

                return {"status": "ok", "models": len(classes)}
            except Exception as e:
                print(f"  ❌ 模型导入失败: {e}")
                return {"status": "import_error", "error": str(e)}
        else:
            print("  ❌ models/__init__.py (不存在)")
            return {"status": "missing"}


def print_summary(results: Dict):
    """打印检查摘要"""
    print("\n" + "=" * 60)
    print("📋 环境检查摘要")
    print("=" * 60)

    # 统计状态
    issues = []

    if results["project_structure"]["dirs"]["missing"]:
        issues.append(f"缺失目录: {results['project_structure']['dirs']['missing']}")

    if results["project_structure"]["files"]["missing"]:
        issues.append(f"缺失文件: {results['project_structure']['files']['missing']}")

    if results["dependencies"]["missing"]:
        issues.append(f"未安装包: {results['dependencies']['missing']}")

    if not results["test_infrastructure"].get("pytest_works"):
        issues.append("pytest无法运行")

    if not results.get("test_config", {}).get("conftest"):
        issues.append("缺少conftest.py")

    # 打印状态
    if not issues:
        print("\n✅ 环境检查通过！可以开始TDD开发。")
    else:
        print("\n⚠️  发现以下问题需要修复：")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")

    # 建议下一步
    print("\n" + "=" * 60)
    print("🎯 建议下一步")
    print("=" * 60)

    if issues:
        print("1. 运行: python tests/check_env.py --fix")
        print("2. 或手动修复上述问题")
        print("3. 然后运行: python tests/check_env.py 重新检查")
    else:
        print("1. 开始TDD开发: python tests/tdd_develop.py")
        print("2. 或查看TDD演示: python tests/tdd_demo.py demo")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="检查测试环境")
    parser.add_argument("--fix", action="store_true", help="自动修复问题")
    args = parser.parse_args()

    checker = EnvironmentChecker()
    results = checker.check_all()

    if args.fix:
        print("\n🔧 自动修复模式...")
        # TODO: 实现自动修复
        print("⚠️  自动修复功能待实现")

    print_summary(results)

    return 0 if not any([
        results["project_structure"]["dirs"]["missing"],
        results["project_structure"]["files"]["missing"],
        results["dependencies"]["missing"],
    ]) else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
