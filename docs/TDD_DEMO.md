# TDD开发流程 - 完整演示

## 流程概述

```
┌─────────────────────────────────────────────────────────────────┐
│                     TDD开发循环                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    │
│  │   RED   │ → │  GREEN  │ → │  TEST   │ → │  BLUE   │    │
│  │         │    │         │    │         │    │         │    │
│  │ Test    │    │ Code    │    │ Run     │    │ Review  │    │
│  │ Writer  │    │ Writer  │    │ Runner  │    │ Er      │    │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘    │
│       │              │              │              │          │
│       ▼              ▼              ▼              ▼          │
│  编写测试       编写代码       运行pytest      代码审查        │
│  测试失败       代码能通过     所有通过       质量检查         │
│                                                                 │
│  ↺ 循环直到: ✅ 测试通过 + ✅ 审查通过                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 实例演示：开发 gap_analysis 功能

### 功能规格

```json
{
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
  ]
}
```

---

## TDD循环 #1

### 🔴 Red Phase - 编写测试

**Agent**: TestWriterAgent

**任务**: 编写测试用例

```python
# tests/test_gap_analysis.py

import pytest
from agents.parser_agent import ParserAgent
from models import ParsedResume, ParsedJD, GapAnalysis, TechnicalSkills


class TestGapAnalysis:
    """Gap分析测试"""

    def setup_method(self):
        """每个测试前运行"""
        self.agent = ParserAgent()

    def test_normal_case_both_have_skills(self):
        """测试正常情况：简历和JD都有技能"""
        # Given
        resume = ParsedResume(
            technical_skills=TechnicalSkills(
                languages=["Java", "Python"],
                frameworks=["Spring Boot"],
                databases=["MySQL"]
            )
        )
        jd = ParsedJD(
            required_skills=["Java", "Spring Boot", "Redis", "Kafka"]
        )

        # When
        gap = self.agent.gap_analysis(resume, jd)

        # Then
        assert isinstance(gap, GapAnalysis)
        assert 0 <= gap.match_percentage <= 1
        assert isinstance(gap.matched_items, list)
        assert isinstance(gap.gap_items, list)
        assert "Redis" in gap.gap_items or "Kafka" in gap.gap_items

    def test_empty_resume(self):
        """测试边界情况：简历为空"""
        # Given
        resume = ParsedResume(technical_skills=TechnicalSkills())
        jd = ParsedJD(required_skills=["Java"])

        # When
        gap = self.agent.gap_analysis(resume, jd)

        # Then
        assert gap.match_percentage == 0
        assert len(gap.matched_items) == 0

    def test_empty_jd(self):
        """测试边界情况：JD为空"""
        # Given
        resume = ParsedResume(
            technical_skills=TechnicalSkills(languages=["Java"])
        )
        jd = ParsedJD(required_skills=[])

        # When
        gap = self.agent.gap_analysis(resume, jd)

        # Then
        assert gap.match_percentage == 1  # 空JD算100%匹配

    def test_perfect_match(self):
        """测试边界情况：完全匹配"""
        # Given
        resume = ParsedResume(
            technical_skills=TechnicalSkills(languages=["Java", "Python"])
        )
        jd = ParsedJD(required_skills=["Java", "Python"])

        # When
        gap = self.agent.gap_analysis(resume, jd)

        # Then
        assert gap.match_percentage == 1
        assert len(gap.gap_items) == 0

    def test_no_match(self):
        """测试边界情况：完全不匹配"""
        # Given
        resume = ParsedResume(
            technical_skills=TechnicalSkills(languages=["Python"])
        )
        jd = ParsedJD(required_skills=["Java", "Go"])

        # When
        gap = self.agent.gap_analysis(resume, jd)

        # Then
        assert gap.match_percentage < 0.5
        assert "Java" in gap.gap_items or "Go" in gap.gap_items
```

**输出**:
```
✅ 测试已写入: tests/test_gap_analysis.py
```

---

### 🟢 Green Phase - 编写代码

**Agent**: CodeWriterAgent

**任务**: 编写功能代码使测试通过

```python
# agents/parser_agent.py (gap_analysis方法)

def gap_analysis(
    self,
    resume: ParsedResume,
    jd: ParsedJD
) -> GapAnalysis:
    """
    Gap分析

    Args:
        resume: 解析后的简历
        jd: 解析后的JD

    Returns:
        GapAnalysis对象
    """
    resume_skills = resume.technical_skills.to_list()
    jd_required = jd.required_skills

    # 计算匹配项和差距项
    matched_items = [s for s in resume_skills if s in jd_required]
    gap_items = [s for s in jd_required if s not in resume_skills]

    # 计算匹配度百分比
    if not jd_required:
        match_percentage = 1.0  # 空JD算100%匹配
    elif not resume_skills:
        match_percentage = 0.0
    else:
        match_percentage = len(matched_items) / len(jd_required)

    return GapAnalysis(
        match_percentage=match_percentage,
        matched_items=matched_items,
        gap_items=gap_items,
        bonus_items=[s for s in resume_skills if s not in jd_required],
        interview_focus=gap_items.copy()
    )
```

**输出**:
```
✅ 代码已写入: agents/parser_agent.py
```

---

### 🧪 Test Phase - 运行测试

**Agent**: TestRunnerAgent

**任务**: 运行pytest

```bash
$ pytest tests/test_gap_analysis.py -v

========================= test session starts ==========================
collected 5 items

test_gap_analysis.py::TestGapAnalysis::test_empty_jd PASSED    [ 20%]
test_gap_analysis.py::TestGapAnalysis::test_empty_resume PASSED [ 40%]
test_gap_analysis.py::TestGapAnalysis::test_no_match PASSED    [ 60%]
test_gap_analysis.py::TestGapAnalysis::test_normal_case PASSED [ 80%]
test_gap_analysis.py::TestGapAnalysis::test_perfect_match PASSED [100%]

========================= 5 passed in 0.5s ===========================
```

**输出**:
```
✅ 所有测试通过！
  总计: 5 | 通过: 5 | 失败: 0 | 错误: 0
```

---

### 🔵 Blue Phase - 代码审查

**Agent**: CodeReviewerAgent

**任务**: 审查代码质量

**审查报告**:
```json
{
  "overall_score": 85,
  "categories": {
    "correctness": {
      "score": 95,
      "issues": [],
      "praise": [
        "正确处理了边界情况",
        "匹配度计算逻辑清晰"
      ]
    },
    "readability": {
      "score": 90,
      "issues": [
        "变量命名可以更清晰"
      ],
      "praise": [
        "代码结构清晰",
        "注释完善"
      ]
    },
    "maintainability": {
      "score": 80,
      "issues": [
        "考虑增加更多测试场景"
      ],
      "praise": [
        "函数职责单一",
        "易于扩展"
      ]
    },
    "performance": {
      "score": 85,
      "issues": [],
      "praise": [
        "时间复杂度O(n)合理"
      ]
    },
    "security": {
      "score": 90,
      "issues": [],
      "praise": [
        "无明显安全问题"
      ]
    },
    "testing": {
      "score": 90,
      "issues": [],
      "praise": [
        "测试覆盖充分",
        "边界情况已测试"
      ]
    }
  },
  "critical_issues": [],
  "suggestions": [
    "可以添加更多维度的匹配分析",
    "考虑添加技能权重的支持"
  ],
  "approval": "APPROVED"
}
```

**输出**:
```
✅ 代码审查通过！
📊 审查评分: 85/100
✍️ 审查结果: APPROVED
```

---

## 🎉 结果

```
══════════════════════════════════════════════════════════════
🎉 功能 gap_analysis 开发完成！
══════════════════════════════════════════════════════════════

✅ 功能: gap_analysis
🔄 TDD循环次数: 1
📁 测试文件: tests/test_gap_analysis.py
📁 代码文件: agents/parser_agent.py
📊 审查评分: 85/100
✍️ 审查结果: APPROVED

══════════════════════════════════════════════════════════════
📜 开发历史
══════════════════════════════════════════════════════════════

1. [10:23:15] write_test
   文件: tests/test_gap_analysis.py

2. [10:25:32] write_code
   文件: agents/parser_agent.py

3. [10:26:45] run_test
   结果: 通过5/5

4. [10:28:10] review
   评分: 85/100 - APPROVED
```

---

## Agent协调总结

### 各Agent职责

| Agent | 阶段 | 职责 | 工具使用 |
|-------|------|------|---------|
| **TestWriterAgent** | 🔴 Red | 编写测试用例 | Claude API |
| **CodeWriterAgent** | 🟢 Green | 编写/修复代码 | Claude API |
| **TestRunnerAgent** | 🧪 Test | 运行pytest | subprocess |
| **CodeReviewerAgent** | 🔵 Blue | 审查代码质量 | Claude API |
| **TDDOrchestrator** | - | 协调工作流 | - |

### 工作流控制

```python
# TDD循环伪代码
for cycle in range(max_cycles):
    # 1. Red: 编写测试
    test = TestWriterAgent.write_test(spec)
    write_file(test_file, test)

    # 2. Green: 编写代码
    code = CodeWriterAgent.write_code(test)
    write_file(code_file, code)

    # 3. Test: 运行测试
    result = TestRunnerAgent.run_tests(test_file)

    if result.success:
        # 4. Blue: 代码审查
        review = CodeReviewerAgent.review(code)

        if review.approval == "APPROVED":
            return SUCCESS
        else:
            # 重构
            code = CodeWriterAgent.refactor(code, review.suggestions)
    else:
        # 修复
        code = CodeWriterAgent.fix_code(code, result.errors)
```

---

## 扩展：并行Agent协作

对于更复杂的场景，可以并行执行多个Agent：

```
┌─────────────────────────────────────────────────────────────┐
│                     并行开发模式                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Feature1 ─┬─> TestWriter ─> CodeWriter ─> TestRunner    │
│             │                                             │
│   Feature2 ─┼─> TestWriter ─> CodeWriter ─> TestRunner    │
│             │     ↓              ↓              ↓            │
│   Feature3 ─┴─> TestWriter ─> CodeWriter ─> TestRunner    │
│                      ↓              ↓                         │
│                  CodeReviewer (批量审查)                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
