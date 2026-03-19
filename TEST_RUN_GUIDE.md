# TDD测试运行指南

**项目**: Interview Coach
**测试框架**: pytest
**测试路径**: `C:\Practice\learning\interview-coach\tests\unit\`

---

## 🚀 快速开始

### Windows命令提示符

```batch
# 方法1: 运行所有TDD测试
cd C:\Practice\learning\interview-coach
python -m pytest tests/unit/ -v

# 方法2: 运行单个测试文件
python -m pytest tests/unit/test_gap_analysis_tdd.py -v

# 方法3: 运行自定义测试脚本
python run_tdd_tests.py
```

### PowerShell

```powershell
cd C:\Practice\learning\interview-coach
pytest tests/unit/ -v
```

### VS Code终端

```bash
# 在VS Code中打开项目文件夹，然后在终端中运行
pytest tests/unit/ -v
```

---

## 📊 测试文件列表

| 测试文件 | 测试数 | 覆盖功能 |
|---------|--------|----------|
| `test_gap_analysis_tdd.py` | 9 | Gap分析 |
| `test_parse_resume_tdd.py` | 10+ | 简历解析 |
| `test_parse_jd_tdd.py` | 10+ | JD解析 |
| `test_interviewer_tdd.py` | 15+ | 面试流程 |
| `test_evaluator_tdd.py` | 12+ | 评估报告 |
| **总计** | **56+** | **全功能** |

---

## 🧪 预期测试结果

### 成功输出示例

```
tests/unit/test_gap_analysis_tdd.py::TestGapAnalysisTDD::test_gap_analysis_normal_case PASSED
tests/unit/test_gap_analysis_tdd.py::TestGapAnalysisTDD::test_gap_analysis_empty_resume PASSED
tests/unit/test_gap_analysis_tdd.py::TestGapAnalysisTDD::test_gap_analysis_empty_jd PASSED
tests/unit/test_gap_analysis_tdd.py::TestGapAnalysisTDD::test_gap_analysis_perfect_match PASSED
tests/unit/test_gap_analysis_tdd.py::TestGapAnalysisTDD::test_gap_analysis_no_match PASSED
tests/unit/test_gap_analysis_tdd.py::TestGapAnalysisTDD::test_gap_analysis_return_types PASSED
tests/unit/test_gap_analysis_tdd.py::TestGapAnalysisTDD::test_gap_analysis_complex_case PASSED
tests/unit/test_gap_analysis_tdd.py::TestGapAnalysisTDD::test_gap_analysis_interview_focus_generation PASSED

====================== 9 passed in 2.5s =======================
```

### 全部测试成功

```
====================== test session starts =======================
collected 56 items

tests/unit/test_gap_analysis_tdd.py ........ 9
tests/unit/test_parse_resume_tdd.py ........ 10
tests/unit/test_parse_jd_tdd.py ........ 10
tests/unit/test_interviewer_tdd.py ........ 15
tests/unit/test_evaluator_tdd.py ........ 12

====================== 56 passed in 15.3s =====================
```

---

## 🔧 常见问题解决

### 问题1: pytest未安装

```batch
pip install pytest
```

### 问题2: 模块导入错误

```batch
# 设置PYTHONPATH
set PYTHONPATH=C:\Practice\learning\interview-coach

# 或在项目根目录运行
cd C:\Practice\learning\interview-coach
```

### 问题3: Claude API未配置

部分测试需要mock Claude API，测试会自动处理。如果出现API错误：

```batch
# 检查环境变量
set ANTHROPIC_API_KEY=your_key_here
```

### 问题4: 编码错误

```batch
# 设置UTF-8编码
set PYTHONUTF8=1
```

---

## 📋 测试检查清单

运行测试后，请确认以下项目：

- [ ] 所有56+测试用例通过
- [ ] 无ERROR或FAIL
- [ ] 测试执行时间合理（<30秒）
- [ ] 无警告信息

---

## 📝 测试报告模板

测试完成后，请记录结果：

### 测试执行日期
- 日期: _____________
- 执行人: _____________

### 测试结果
- 总测试数: 56
- 通过: _____
- 失败: _____
- 跳过: _____

### 失败测试详情
如有失败，请记录：
1. 测试名称: _____________
   错误信息: _____________

2. 测试名称: _____________
   错误信息: _____________

### 结论
- [ ] 所有测试通过 → 继续P2优化或Week 3开发
- [ ] 有测试失败 → 记录错误并修复

---

## 🎯 测试通过后下一步

测试全部通过后，可以选择：

**A. P2优化** - 完成12项建议优化
- 提取魔法数字为类常量
- 添加更多日志记录
- 添加输入验证

**B. Week 3开发** - 多Agent编排
- 实现OrchestratorAgent
- 多Agent协作模式

**C. 集成UI** - Streamlit Web界面
- 完整用户界面
- 端到端测试

---

*如有问题，请查看 docs/code_reviews/ 中的详细代码审查报告*
