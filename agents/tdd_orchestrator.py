"""
TDD工作流编排器

协调TestWriter、CodeWriter、CodeReviewer、TestRunner等Agent进行TDD开发。
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json

from agents.dev_agent import (
    TestWriterAgent,
    CodeWriterAgent,
    CodeReviewerAgent,
    TestRunnerAgent
)


class TDDOrchestrator:
    """TDD工作流编排器"""

    def __init__(self, project_root: str = None):
        """
        初始化TDD编排器

        Args:
            project_root: 项目根目录
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.test_dir = self.project_root / "tests"
        self.src_dir = self.project_root / "agents"

        # 初始化Agent
        self.test_writer = TestWriterAgent()
        self.code_writer = CodeWriterAgent()
        self.code_reviewer = CodeReviewerAgent()
        self.test_runner = TestRunnerAgent()

        # 工作流状态
        self.current_cycle = 0
        self.history = []

    def develop_feature(
        self,
        feature_spec: Dict[str, Any],
        max_cycles: int = 5
    ) -> Dict[str, Any]:
        """
        使用TDD流程开发功能

        Args:
            feature_spec: 功能规格
            max_cycles: 最大TDD循环次数

        Returns:
            开发结果
        """
        feature_name = feature_spec.get("name", "unknown")
        print(f"\n🚀 开始开发功能: {feature_name}")
        print("=" * 60)

        for cycle in range(max_cycles):
            self.current_cycle = cycle + 1
            print(f"\n📋 TDD循环 #{cycle + 1}")
            print("-" * 40)

            # ========== Red: 编写测试 ==========
            print("\n🔴 Red: 编写测试...")
            test_result = self._write_test_phase(feature_spec)
            if not test_result["success"]:
                return self._failure_result("测试编写失败", test_result)

            test_file = test_result["test_file"]
            print(f"✅ 测试已写入: {test_file}")

            # ========== Green: 编写代码 ==========
            print("\n🟢 Green: 编写代码使测试通过...")
            code_result = self._write_code_phase(feature_spec, test_result)
            if not code_result["success"]:
                return self._failure_result("代码编写失败", code_result)

            code_file = code_result["code_file"]
            print(f"✅ 代码已写入: {code_file}")

            # ========== 运行测试 ==========
            print("\n🧪 运行测试...")
            test_run_result = self._run_test_phase(test_file)
            self._print_test_result(test_run_result)

            # 检查是否通过
            if test_run_result["success"]:
                print("\n✅ 所有测试通过！")

                # ========== Refactor: 代码审查和重构 ==========
                print("\n🔵 Refactor: 代码审查...")
                review_result = self._review_phase(code_result["code"], test_result["test"])

                if review_result["approval"] == "APPROVED":
                    print("\n✅ 代码审查通过！")
                    print("\n" + "=" * 60)
                    print(f"🎉 功能 {feature_name} 开发完成！")
                    return self._success_result(feature_spec, test_result, code_result, review_result)
                else:
                    print(f"\n⚠️  代码需要改进: {review_result['approval']}")
                    print("建议:")
                    for suggestion in review_result.get("suggestions", [])[:3]:
                        print(f"  - {suggestion}")

                    # 是否继续重构
                    if cycle < max_cycles - 1:
                        print("\n🔄 继续下一轮TDD循环...")
                        feature_spec["existing_code"] = code_result["code"]
                        feature_spec["refactoring_goals"] = review_result.get("suggestions", [])
                        continue
                    else:
                        return self._failure_result("达到最大循环次数", review_result)
            else:
                # 测试失败，分析原因并修复
                print("\n❌ 测试失败")
                print(f"输出: {test_run_result['output'][:500]}")

                if cycle < max_cycles - 1:
                    print("\n🔧 尝试修复...")
                    fix_result = self._fix_code_phase(
                        code_result["code"],
                        test_result["test"],
                        test_run_result["output"]
                    )

                    if fix_result["success"]:
                        print("✅ 代码已修复")
                        feature_spec["existing_code"] = fix_result["fixed_code"]
                        continue
                    else:
                        return self._failure_result("代码修复失败", fix_result)
                else:
                    return self._failure_result("测试未通过", test_run_result)

        return self._failure_result("达到最大循环次数", {})

    def _write_test_phase(self, spec: Dict) -> Dict:
        """编写测试阶段"""
        function_name = spec.get("name", "")
        requirements = spec.get("requirements", [])

        # 生成测试代码
        test_code = self.test_writer.write_test({
            "function_name": function_name,
            "requirements": requirements,
            "existing_code": spec.get("existing_code", "")
        })

        # 写入测试文件
        test_file = self.test_dir / f"test_{function_name}.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)

        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_code)

        # 记录历史
        self.history.append({
            "cycle": self.current_cycle,
            "phase": "write_test",
            "file": str(test_file),
            "timestamp": datetime.now().isoformat()
        })

        return {
            "success": True,
            "test_file": str(test_file),
            "test_code": test_code
        }

    def _write_code_phase(self, spec: Dict, test_result: Dict) -> Dict:
        """编写代码阶段"""
        function_name = spec.get("name", "")
        requirements = spec.get("requirements", [])

        # 生成功能代码
        code = self.code_writer.write_code({
            "test_code": test_result["test_code"],
            "requirements": requirements,
            "existing_code": spec.get("existing_code", "")
        })

        # 写入代码文件
        if "module" in spec:
            module_path = spec["module"].replace(".", "/") + ".py"
            code_file = self.src_dir / module_path
        else:
            code_file = self.src_dir / f"{function_name}.py"

        code_file.parent.mkdir(parents=True, exist_ok=True)

        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code)

        # 记录历史
        self.history.append({
            "cycle": self.current_cycle,
            "phase": "write_code",
            "file": str(code_file),
            "timestamp": datetime.now().isoformat()
        })

        return {
            "success": True,
            "code_file": str(code_file),
            "code": code
        }

    def _run_test_phase(self, test_file: str) -> Dict:
        """运行测试阶段"""
        result = self.test_runner.run_tests({
            "test_file": test_file,
            "verbose": True
        })

        self.history.append({
            "cycle": self.current_cycle,
            "phase": "run_test",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })

        return result

    def _review_phase(self, code: str, test: str) -> Dict:
        """代码审查阶段"""
        review = self.code_reviewer.review({
            "code": code,
            "test_code": test,
            "requirements": []
        })

        self.history.append({
            "cycle": self.current_cycle,
            "phase": "review",
            "review": review,
            "timestamp": datetime.now().isoformat()
        })

        return review

    def _fix_code_phase(self, code: str, test: str, error_output: str) -> Dict:
        """修复代码阶段"""
        fix_result = self.code_writer.fix_code({
            "test_code": test,
            "function_code": code,
            "error_message": "",
            "test_output": error_output
        })

        # 更新代码文件
        if fix_result.get("fixed_code"):
            # 这里需要知道原文件位置，简化处理
            return {
                "success": True,
                "fixed_code": fix_result["fixed_code"]
            }

        return {
            "success": False,
            "error": "修复失败"
        }

    def _print_test_result(self, result: Dict):
        """打印测试结果"""
        summary = result.get("summary", {})
        if summary:
            total = summary.get("total", 0)
            passed = summary.get("passed", 0)
            failed = summary.get("failed", 0)
            errors = summary.get("errors", 0)

            print(f"  总计: {total} | 通过: {passed} | 失败: {failed} | 错误: {errors}")

        if result.get("output"):
            output = result["output"]
            if len(output) > 500:
                print(f"  输出: {output[:500]}...")
            else:
                print(f"  输出: {output}")

    def _success_result(self, spec: Dict, test: Dict, code: Dict, review: Dict) -> Dict:
        """成功结果"""
        return {
            "success": True,
            "feature": spec.get("name"),
            "cycles": self.current_cycle,
            "test_file": test.get("test_file"),
            "code_file": code.get("code_file"),
            "review": review,
            "history": self.history
        }

    def _failure_result(self, reason: str, detail: Dict) -> Dict:
        """失败结果"""
        return {
            "success": False,
            "reason": reason,
            "detail": detail,
            "cycles": self.current_cycle,
            "history": self.history
        }


# ========== 便捷函数 ==========

def develop_with_tdd(feature_spec: Dict, max_cycles: int = 5) -> Dict:
    """
    使用TDD流程开发功能

    Args:
        feature_spec: 功能规格
        max_cycles: 最大循环次数

    Returns:
        开发结果
    """
    orchestrator = TDDOrchestrator()
    return orchestrator.develop_feature(feature_spec, max_cycles)
