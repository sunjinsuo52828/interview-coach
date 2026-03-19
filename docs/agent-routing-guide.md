# Agent路由系统 - 使用指南

## 概述

InterviewOrchestrator实现了State-based + LLM fallback的路由策略，确保Agent按既定规则执行动作和职责。

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                   InterviewOrchestrator                      │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │ SessionState  │───▶│ InterviewRouter│───▶│   Agent     │  │
│  │ (状态管理)     │    │ (路由决策)   │    │ (执行动作)   │  │
│  └───────────────┘    └─────────────┘    └─────────────┘  │
│                                                              │
│  状态跟踪                     规则匹配              Agent调用│
└─────────────────────────────────────────────────────────────┘
```

## State-based路由规则

| 优先级 | 条件 | 目标Agent | 说明 |
|-------|------|----------|------|
| 1 | `!resume_parsed && has_resume_text` | Parser | 解析简历 |
| 2 | `resume_parsed && !jd_parsed && has_jd_text` | Parser | 解析JD |
| 3 | `resume_parsed && jd_parsed && !gap_analysis` | Parser | Gap分析 |
| 4 | `has_gap_analysis && !interview_ended && has_config` | Interviewer | 面试进行中 |
| 5 | `interview_ended && !report` | Evaluator | 生成报告 |
| 6 | `has_report` | Completed | 流程完成 |

## 使用示例

### 基本使用

```python
from agents import InterviewOrchestrator

# 创建编排器
orchestrator = InterviewOrchestrator()

# 更新简历文本
orchestrator.update_resume_text("张三\n高级Java工程师")

# 路由并执行 - 会自动路由到Parser解析简历
result = orchestrator.route_and_execute()
# {"agent": "parser", "actions": ["parse_resume"], ...}

# 更新JD文本
orchestrator.update_jd_text("招聘Java工程师")

# 路由并执行 - 会自动解析JD和执行Gap分析
result = orchestrator.route_and_execute()
# {"agent": "parser", "actions": ["parse_jd", "gap_analysis"], ...}

# 更新配置
orchestrator.update_config(InterviewConfig(...))

# 路由并执行 - 会启动面试
result = orchestrator.route_and_execute()
# {"agent": "interviewer", "action": "start_interview", ...}
```

### 查询状态

```python
# 获取当前状态
state = orchestrator.get_state()
# {
#     "is_resume_parsed": True,
#     "is_jd_parsed": True,
#     "has_gap_analysis": True,
#     "interview_started": True,
#     ...
# }

# 获取路由历史
history = orchestrator.get_routing_history()

# 重置会话
orchestrator.reset()
```

## SessionState属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `resume_text` | str | 用户粘贴的简历文本 |
| `jd_text` | str | 用户粘贴的JD文本 |
| `resume` | ParsedResume | 解析后的简历对象 |
| `jd` | ParsedJD | 解析后的JD对象 |
| `gap_analysis` | GapAnalysis | Gap分析结果 |
| `config` | InterviewConfig | 面试配置 |
| `interview_started` | bool | 面试是否已开始 |
| `interview_ended` | bool | 面试是否已结束 |
| `report` | InterviewReport | 评估报告 |

### 计算属性

```python
state.has_resume_text      # 简历文本是否有效(>10字符)
state.is_resume_parsed     # 简历是否已解析
state.has_gap_analysis     # 是否有Gap分析
state.is_workflow_complete # 整个流程是否完成
```

## LLM Fallback

当State-based规则无法处理时，系统使用LLM判断用户意图：

```python
# 简单关键词匹配实现
intent_patterns = {
    "parser": ["简历", "jd", "解析", "粘贴"],
    "interviewer": ["开始面试", "面试", "提问"],
    "evaluator": ["报告", "评估", "结束"],
}
```

## 扩展路由规则

如需添加新路由规则，修改`InterviewRouter.ROUTING_RULES`：

```python
ROUTING_RULES = [
    # 现有规则...

    # 新规则示例：当用户请求学习建议时
    {
        "name": "learning_suggestions",
        "condition": lambda s: (
            s.is_workflow_complete and
            "学习" in s.last_user_input
        ),
        "action": "learning_agent",  # 需要实现
        "reason": "生成学习建议"
    },
]
```

## 测试

运行路由器测试：

```bash
pytest tests/unit/test_orchestrator_tdd.py -v
```

测试覆盖：
- SessionState: 10个测试 ✅
- InterviewRouter: 11个测试 ✅
- InterviewOrchestrator: 8个测试 ✅
