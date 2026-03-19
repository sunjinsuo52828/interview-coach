# Interview Coach - Agent实现总结

## 已实现的Agent

### 1. BaseAgent (基类)
- **文件**: `agents/base_agent.py`
- **功能**: 定义Agent统一接口
- **特性**:
  - 抽象方法：`execute()`, `get_system_prompt()`
  - Claude API调用封装
  - 统计信息（token使用、调用次数）
  - 消息创建、思考记录（ReAct）

### 2. ToolEnabledAgent (支持工具的Agent)
- **继承**: BaseAgent
- **功能**: 支持工具注册和调用
- **特性**:
  - 工具注册: `register_tool()`
  - 工具调用: `call_tool()`
  - 工具描述生成

### 3. StatefulAgent (有状态的Agent)
- **继承**: ToolEnabledAgent
- **功能**: 支持记忆和状态管理
- **特性**:
  - 状态更新: `update_state()`
  - 记忆管理: `add_to_memory()`, `get_memory()`

### 4. ParserAgent (解析Agent)
- **文件**: `agents/parser_agent.py`
- **继承**: ToolEnabledAgent
- **工具**:
  - `parse_resume()`: 解析简历
  - `parse_jd()`: 解析JD
  - `gap_analysis()`: Gap分析
- **使用方式**:
```python
from agents import ParserAgent, parse_resume

# 方式1：使用Agent
parser = ParserAgent()
resume = parser.parse_resume(text)

# 方式2：使用便捷函数
resume = parse_resume(text)
```

### 5. InterviewerAgent (面试官Agent)
- **文件**: `agents/interview_agent.py`
- **继承**: StatefulAgent
- **核心方法**:
  - `start_interview()`: 开始面试，返回开场白
  - `chat()`: 对话循环，处理用户输入
  - `end_interview()`: 结束面试
  - `evaluate_answer()`: 评估回答质量（追问答疑）
  - `generate_follow_up()`: 生成追问
- **特性**:
  - 动态System Prompt生成
  - 渐进式摘要（长对话）
  - 自动检测面试结束

### 6. EvaluatorAgent (评估Agent)
- **文件**: `agents/evaluator_agent.py`
- **继承**: BaseAgent
- **工具**:
  - `evaluate()`: 评估面试表现
  - `generate_report()`: 生成评估报告
- **评估维度**:
  - 技术深度 (35%)
  - 项目经验 (25%)
  - 问题解决 (20%)
  - 沟通表达 (10%)
  - 学习能力 (10%)

## 使用示例

```python
from agents import (
    ParserAgent,
    InterviewerAgent,
    EvaluatorAgent
)

# 1. 解析简历和JD
parser = ParserAgent()
resume = parser.parse_resume(resume_text)
jd = parser.parse_jd(jd_text)
gap = parser.gap_analysis(resume, jd)

# 2. 开始面试
interviewer = InterviewerAgent()
greeting = interviewer.start_interview({
    "config": interview_config,
    "resume": resume,
    "jd": jd,
    "gap": gap
})
print(greeting)  # 开场白

# 3. 对话循环
while not interviewer.state.is_ended:
    user_input = input("你的回答: ")
    response = interviewer.chat({"user_message": user_input})
    print(f"面试官: {response}")

# 4. 生成报告
evaluator = EvaluatorAgent()
report = evaluator.generate_report({
    "state": interviewer.state
})
print(report.overall_grade)  # A/B/C/D
```

## 下一步

Week 3将添加：
- KnowledgeAgent (知识库RAG)
- OrchestratorAgent (协调器)
- LangGraph状态图实现
