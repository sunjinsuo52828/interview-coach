"""
TDD开发Agent - 代码编写Agent

负责编写/修改功能代码。
"""
from typing import Dict, Any
import json

from agents.base_agent import BaseAgent


class CodeWriterAgent(BaseAgent):
    """代码编写Agent"""

    def __init__(self):
        super().__init__(name="CodeWriterAgent")

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """获取System Prompt"""
        return """你是专业的Python开发工程师，擅长编写高质量代码。

你的任务：
1. 根据测试用例编写功能代码
2. 确保代码能通过测试
3. 遵循Python最佳实践（PEP 8）
4. 添加必要的类型注解和文档字符串
5. 编写简洁、可读的代码

输出格式：完整的Python代码
"""

    def execute(self, action: str, context: Dict[str, Any]) -> Any:
        """执行动作"""
        if action == "write_code":
            return self.write_code(context)
        elif action == "fix_code":
            return self.fix_code(context)
        elif action == "refactor":
            return self.refactor(context)
        else:
            raise ValueError(f"Unknown action: {action}")

    def write_code(self, context: Dict[str, Any]) -> str:
        """
        编写功能代码

        Args:
            context: 包含test_code, requirements, existing_code等

        Returns:
            功能代码
        """
        test_code = context.get("test_code", "")
        requirements = context.get("requirements", [])
        existing_code = context.get("existing_code", "")

        prompt = f"""请编写功能代码，使其通过以下测试。

测试代码：
```python
{test_code}
```

需求：
{chr(10).join(f"- {r}" for r in requirements)}

现有代码（如果有）：
```python
{existing_code}
```

请编写/修改功能代码：
1. 确保能通过测试
2. 遵循Python最佳实践
3. 添加类型注解和文档字符串
4. 处理边界情况

直接返回完整Python代码，不要其他内容。
"""

        response = self.call_claude(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.3
        )

        return self._extract_python_code(response)

    def fix_code(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        修复代码

        Args:
            context: 包含test_code, function_code, error_message等

        Returns:
            修复结果
        """
        test_code = context.get("test_code", "")
        function_code = context.get("function_code", "")
        error_message = context.get("error_message", "")
        test_output = context.get("test_output", "")

        prompt = f"""请修复以下代码中的问题。

测试代码：
```python
{test_code}
```

当前功能代码：
```python
{function_code}
```

错误信息：
{error_message}

测试输出：
{test_output}

请分析问题并修复代码。返回JSON格式：
{{
    "analysis": "问题分析",
    "fixed_code": "修复后的完整代码",
    "changes_made": ["所做的修改"]
}}
"""

        response = self.call_claude(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.3
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "analysis": "无法解析响应",
                "fixed_code": response,
                "changes_made": []
            }

    def refactor(self, context: Dict[str, Any]) -> str:
        """
        重构代码

        Args:
            context: 包含code, refactoring_goals等

        Returns:
            重构后的代码
        """
        code = context.get("code", "")
        goals = context.get("refactoring_goals", [])

        prompt = f"""请重构以下代码。

原始代码：
```python
{code}
```

重构目标：
{chr(10).join(f"- {g}" for g in goals)}

请重构代码：
1. 保持功能不变
2. 提高可读性
3. 提高可维护性
4. 遵循SOLID原则

直接返回重构后的完整Python代码。
"""

        response = self.call_claude(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.5
        )

        return self._extract_python_code(response)

    def _extract_python_code(self, text: str) -> str:
        """从文本中提取Python代码"""
        if "```python" in text:
            start = text.find("```python")
            end = text.find("```", start + 9)
            if end > start:
                return text[start + 9:end].strip()
        elif "```" in text:
            start = text.find("```")
            end = text.find("```", start + 3)
            if end > start:
                return text[start + 3:end].strip()
        return text.strip()


class CodeReviewerAgent(BaseAgent):
    """代码审查Agent"""

    def __init__(self):
        super().__init__(name="CodeReviewerAgent")

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """获取System Prompt"""
        return """你是专业的代码审查专家。

你的任务：
1. 审查代码质量
2. 指出潜在问题
3. 提供改进建议
4. 遵循代码审查最佳实践
"""

    def execute(self, action: str, context: Dict[str, Any]) -> Any:
        """执行动作"""
        if action == "review":
            return self.review(context)
        else:
            raise ValueError(f"Unknown action: {action}")

    def review(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        审查代码

        Args:
            context: 包含code, test_code等

        Returns:
            审查报告
        """
        code = context.get("code", "")
        test_code = context.get("test_code", "")
        requirements = context.get("requirements", [])

        prompt = f"""请审查以下代码。

需求：
{chr(10).join(f"- {r}" for r in requirements)}

功能代码：
```python
{code}
```

测试代码（如果有）：
```python
{test_code}
```

请从以下维度审查：
1. 正确性 - 代码是否正确实现需求
2. 可读性 - 代码是否清晰易懂
3. 可维护性 - 代码是否易于维护
4. 性能 - 是否存在性能问题
5. 安全性 - 是否存在安全隐患
6. 测试覆盖 - 测试是否充分

返回JSON格式：
{{
    "overall_score": 评分(0-100),
    "categories": {{
        "correctness": {{"score": 分数, "issues": [], "praise": []}},
        "readability": {{"score": 分数, "issues": [], "praise": []}},
        "maintainability": {{"score": 分数, "issues": [], "praise": []}},
        "performance": {{"score": 分数, "issues": [], "praise": []}},
        "security": {{"score": 分数, "issues": [], "praise": []}},
        "testing": {{"score": 分数, "issues": [], "praise": []}}
    }},
    "critical_issues": ["严重问题列表"],
    "suggestions": ["改进建议列表"],
    "approval": "APPROVED/NEEDS_REVISION/REJECTED"
}}
"""

        response = self.call_claude(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2500,
            temperature=0.3
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "overall_score": 50,
                "categories": {},
                "critical_issues": ["无法解析审查结果"],
                "suggestions": [],
                "approval": "NEEDS_REVISION"
            }


class TestRunnerAgent(BaseAgent):
    """测试运行Agent（本地执行，非LLM）"""

    def __init__(self):
        super().__init__(name="TestRunnerAgent")
        self.test_results = []

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """获取System Prompt"""
        return "测试运行Agent（本地执行）"

    def execute(self, action: str, context: Dict[str, Any]) -> Any:
        """执行动作"""
        if action == "run_tests":
            return self.run_tests(context)
        else:
            raise ValueError(f"Unknown action: {action}")

    def run_tests(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行测试

        Args:
            context: 包含test_file, verbose等

        Returns:
            测试结果
        """
        import subprocess
        import sys

        test_file = context.get("test_file", "")
        verbose = context.get("verbose", True)

        try:
            # 构建pytest命令
            cmd = [sys.executable, "-m", "pytest", test_file]
            if verbose:
                cmd.append("-v")
            cmd.append("--tb=short")

            # 运行测试
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            # 解析结果
            return self._parse_test_result(result)
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "测试超时",
                "output": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output": ""
            }

    def _parse_test_result(self, result: subprocess.CompletedProcess) -> Dict:
        """解析测试结果"""
        output = result.stdout + result.stderr
        success = result.returncode == 0

        # 统计测试数量
        passed = output.count("PASSED")
        failed = output.count("FAILED")
        errors = output.count("ERROR")

        return {
            "success": success,
            "returncode": result.returncode,
            "output": output,
            "summary": {
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "total": passed + failed + errors
            }
        }
