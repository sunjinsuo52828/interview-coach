# Interview Coach - 架构设计文档

## 1. 架构总览

### 1.1 分阶段架构演进

```
┌─────────────────────────────────────────────────────────────────┐
│                      Interview Coach 架构演进                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Week 1-2 (MVP)          Week 3 (多Agent)         Week 4 (高级)  │
│                                                                 │
│  ┌─────────────┐       ┌──────────────┐        ┌─────────────┐ │
│  │ Single      │  -->  │ Multi-Agent  │  -->   │ ReAct + RAG │ │
│  │ Agent       │       │ + Orchestrator│        │ + Reflection│ │
│  │             │       │              │        │             │ │
│  └─────────────┘       └──────────────┘        └─────────────┘ │
│       ↓                      ↓                       ↓         │
│   可用产品              学习协作模式              学习高级模式    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 架构分层

```
┌─────────────────────────────────────────────────────────────────┐
│                        Presentation Layer                       │
│                      Streamlit Web UI                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ 简历上传  │ │ 面试配置  │ │ 聊天界面  │ │ 评估报告  │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         Agent Layer                             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Orchestrator Agent (Week 3)            │   │
│  │              任务路由 | Agent调度 | 结果聚合            │   │
│  └───┬────────┬────────┬────────┬────────┬────────┬─────────┘   │
│      │        │        │        │        │        │             │
│      ↓        ↓        ↓        ↓        ↓        ↓             │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌─────────┐    │
│  │Parser│ │Inter-│ │Eval-  │ │Know-  │ │Plan-  │ │ Reflex  │    │
│  │Agent │ │viewer │ │uator  │ │ledge  │ │ner    │ │ Agent   │    │
│  │Week 1│ │Week 1│ │Week 2│ │Week 3│ │Week 4│ │  Week 4 │    │
│  └───┬──┘ └───┬──┘ └───┬──┘ └───┬──┘ └───┬──┘ └────┬────┘    │
│      │        │        │        │        │        │          │
│      └────────┴────────┴────────┴────────┴────────┴──────────┘ │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                          Service Layer                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ 解析服务  │ │ 面试服务  │ │ 评估服务  │ │ 知识服务  │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────┬───────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                           Data Layer                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ JSON文件  │ │ SQLite   │ │ChromaDB  │ │ 题库JSON  │           │
│  │ (会话)    │ │ (元数据)  │ │ (向量)    │ │ (问题)    │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       External Services                          │
│  ┌──────────┐ ┌──────────────────────────────────────────┐       │
│  │Claude API│ │        File System                       │       │
│  └──────────┘ │  (知识库文档, 面试记录, 题库)             │       │
│               └──────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Week 1-2 MVP架构 (单Agent)

### 2.1 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                       Streamlit UI                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  st.text_area("简历")  st.text_area("JD")               │   │
│  │  st.select("面试官级别")  st.multiselect("考察重点")     │   │
│  │  st.chat_messages("对话")  st.button("结束面试")         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ↓ st.session_state
┌─────────────────────────────────────────────────────────────────┐
│                    InterviewAgent (单Agent)                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐             │   │
│  │  │ 解析器  │ -> │ 面试官  │ -> │ 评估器  │             │   │
│  │  │(内部)   │    │(核心)   │    │(内部)   │             │   │
│  │  └─────────┘    └─────────┘    └─────────┘             │   │
│  │                                                         │   │
│  │  方法:                                                  │   │
│  │  - parse_resume()                                      │   │
│  │  - parse_jd()                                          │   │
│  │  - gap_analysis()                                      │   │
│  │  - start_interview()                                   │   │
│  │  - chat(user_message) -> agent_message                 │   │
│  │  - end_interview() -> report                           │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ↓             ↓             ↓
         ┌──────────┐  ┌──────────┐  ┌──────────┐
         │ Claude   │  │   JSON   │  │   JSON   │
         │   API    │  │  题库    │  │ 面试记录  │
         └──────────┘  └──────────┘  └──────────┘
```

### 2.2 类设计

```python
# interview_agent.py

class InterviewAgent:
    """单Agent版本 - 面试官Agent (Week 1-2)"""

    def __init__(self, claude_api_key: str):
        self.claude = Anthropic(api_key=claude_api_key)
        self.state = InterviewState()
        self.tools = self._init_tools()

    def _init_tools(self) -> List[Tool]:
        """初始化工具"""
        return [
            parse_resume,
            parse_jd,
            gap_analysis,
            get_question,
            evaluate_answer,
            save_round_result,
            generate_report
        ]

    # ========== 解析阶段 ==========

    def parse_resume(self, resume_text: str) -> ParsedResume:
        """解析简历 - 使用LLM"""
        prompt = self._build_parse_prompt(resume_text, "resume")
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return self._parse_resume_response(response.content[0].text)

    def parse_jd(self, jd_text: str) -> ParsedJD:
        """解析JD - 使用LLM"""
        prompt = self._build_parse_prompt(jd_text, "jd")
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return self._parse_jd_response(response.content[0].text)

    def gap_analysis(self, resume: ParsedResume, jd: ParsedJD) -> GapAnalysis:
        """Gap分析 - 使用LLM"""
        prompt = self._build_gap_prompt(resume, jd)
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        return self._parse_gap_response(response.content[0].text)

    # ========== 面试阶段 ==========

    def start_interview(self, config: InterviewConfig) -> str:
        """开始面试 - 返回开场白"""
        self.state.config = config
        system_prompt = self._build_interviewer_prompt(config)

        # 生成开场白
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": "请开始面试，先做自我介绍。"}]
        )

        self.state.conversation_history.append({
            "role": "assistant",
            "content": response.content[0].text
        })

        return response.content[0].text

    def chat(self, user_message: str) -> str:
        """对话循环 - 核心方法"""
        # 添加用户消息
        self.state.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # 构建消息列表（含渐进式摘要）
        messages = self._build_messages()

        # 调用Claude
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=self._build_interviewer_prompt(self.state.config),
            messages=messages
        )

        agent_message = response.content[0].text

        # 添加到历史
        self.state.conversation_history.append({
            "role": "assistant",
            "content": agent_message
        })

        # 检查是否需要摘要
        if len(self.state.conversation_history) >= 20:
            self._generate_summary()

        return agent_message

    def _build_messages(self) -> List[Dict]:
        """构建消息列表（处理摘要）"""
        if self.state.summary:
            # 有摘要时，摘要 + 最近5轮对话
            recent = self.state.conversation_history[-10:]
            return [
                {"role": "user", "content": f"之前的面试摘要：\n{self.state.summary}"},
                *recent
            ]
        else:
            # 无摘要时，全部对话
            return self.state.conversation_history

    def _generate_summary(self):
        """渐进式摘要"""
        summary_prompt = f"""
请对以下面试对话生成摘要，包含：
1. 已问过的题目和评分
2. 候选人的优势
3. 候选人的弱项
4. 尚未考察的维度

对话记录：
{json.dumps(self.state.conversation_history, ensure_ascii=False)}
"""
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": summary_prompt}]
        )
        self.state.summary = response.content[0].text

    # ========== 评估阶段 ==========

    def end_interview(self) -> InterviewReport:
        """结束面试，生成评估报告"""
        # 生成报告
        prompt = self._build_evaluator_prompt()
        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )

        report = self._parse_report_response(response.content[0].text)

        # 保存
        self._save_report(report)

        return report
```

### 2.3 数据流图

```
用户操作                    Streamlit状态                  Agent调用
─────────────────────────────────────────────────────────────────

1. 粘贴简历
   st.text_area ──────────► st.session_state.resume_text ─────►
                                                           │
                                                           ▼
                                                    agent.parse_resume()
                                                           │
                                                           ▼
                                                    ParsedResume

2. 粘贴JD
   st.text_area ──────────► st.session_state.jd_text ───────►
                                                           │
                                                           ▼
                                                     agent.parse_jd()
                                                           │
                                                           ▼
                                                      ParsedJD

3. 配置面试
   st.select ─────────────► st.session_state.config ────────►
                                                           │
                                                           ▼
                                                   agent.start_interview()
                                                           │
                                                           ▼
                                                     开场白消息

4. 面试对话循环
   st.chat_input ─────────► st.session_state.user_input ────►
                                                           │
                                                           ▼
                                                      agent.chat()
                                                           │
                                                           ├─────────► Claude API
                                                           │
                                                           ▼
                                                    agent_message
                                                           │
                                                           ▼
                                       st.session_state.messages.append()

5. 结束面试
   st.button ─────────────► st.session_state.ended ──────────►
                                                           │
                                                           ▼
                                                  agent.end_interview()
                                                           │
                                                           ▼
                                                    InterviewReport
                                                           │
                                                           ▼
                                                   st.markdown(报告)
```

---

## 3. Week 3 多Agent架构

### 3.1 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                       Streamlit UI                              │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  职责：                                                  │   │
│  │  1. 接收用户请求                                         │   │
│  │  2. 意图识别（用户想做什么？）                            │   │
│  │  3. 任务路由（调用哪个子Agent？）                        │   │
│  │  4. 结果聚合（组合子Agent返回的结果）                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  prompt_template: """                                           │
│  你是面试协调器。根据用户请求，决定调用哪个子Agent：             │
│  - 解析请求 → Parser Agent                                      │
│  - 面试对话 → Interviewer Agent                                 │
│  - 生成报告 → Evaluator Agent                                    │
│  - 知识查询 → Knowledge Agent                                    │
│  返回格式: {agent: 'parser|interviewer|evaluator|knowledge'}     │
│  """                                                             │
└───┬────────┬────────┬────────┬────────┬─────────────────────────┘
    │        │        │        │        │
    ↓        ↓        ↓        ↓        ↓
┌────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐
│Parser  │ │Inter-│ │Eval- │ │Know- │ │ Planner  │
│Agent   │ │viewer│ │uator │ │ledge │ │ (Week 4) │
├────────┤ ├──────┤ ├──────┤ ├──────┤ ├──────────┤
│解析简历│ │对话  │ │评估  │ │RAG   │ │生成计划  │
│解析JD  │ │追问  │ │报告  │ │检索  │ │          │
│Gap分析 │ │ReAct │ │建议  │ │知识  │ │          │
└────────┘ └──────┘ └──────┘ └──────┘ └──────────┘
    │         │        │        │
    └─────────┴────────┴────────┘
                  │
                  ↓
         ┌─────────────────┐
         │  Shared State   │
         │  - Session      │
         │  - Memory       │
         │  - Context      │
         └─────────────────┘
```

### 3.2 Orchestrator设计

```python
# orchestrator.py

class OrchestratorAgent:
    """协调器Agent - 负责任务路由和结果聚合"""

    def __init__(self):
        self.claude = Anthropic(api_key=settings.CLAUDE_API_KEY)
        self.agents = {
            "parser": ParserAgent(),
            "interviewer": InterviewerAgent(),
            "evaluator": EvaluatorAgent(),
            "knowledge": KnowledgeAgent()
        }
        self.state = SharedState()

    def route(self, user_input: str, context: Dict) -> Dict:
        """路由用户请求到合适的Agent"""

        # 1. 意图识别
        intent = self._detect_intent(user_input, context)

        # 2. 路由到对应Agent
        agent = self.agents[intent["agent"]]

        # 3. 执行并获取结果
        result = agent.execute(intent["action"], context)

        # 4. 结果处理
        return self._process_result(result, intent)

    def _detect_intent(self, user_input: str, context: Dict) -> Dict:
        """意图识别"""

        # 使用Claude进行意图识别
        prompt = f"""
你是面试协调器的意图识别模块。根据用户输入判断其意图。

用户输入：{user_input}

当前上下文：
- 阶段：{context.get('stage')}
- 会话ID：{context.get('session_id')}

可能的意图：
1. parse - 解析简历或JD
2. interview - 进行面试对话
3. evaluate - 生成评估报告
4. knowledge - 查询知识库

返回JSON格式：
{{"agent": "parser|interviewer|evaluator|knowledge", "action": "...", "params": {{...}}}}
"""

        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(response.content[0].text)

    def _process_result(self, result: Any, intent: Dict) -> Dict:
        """处理Agent返回的结果"""

        # 根据不同Agent返回不同格式
        if intent["agent"] == "parser":
            return {"type": "parse_result", "data": result}
        elif intent["agent"] == "interviewer":
            return {"type": "chat_response", "message": result}
        elif intent["agent"] == "evaluator":
            return {"type": "report", "report": result}
        elif intent["agent"] == "knowledge":
            return {"type": "knowledge", "items": result}
```

### 3.3 各子Agent接口

```python
# 各子Agent统一接口

class BaseAgent(ABC):
    """Agent基类"""

    @abstractmethod
    def execute(self, action: str, context: Dict) -> Any:
        """执行动作"""
        pass


class ParserAgent(BaseAgent):
    """解析Agent"""

    def execute(self, action: str, context: Dict) -> Any:
        if action == "parse_resume":
            return self.parse_resume(context["resume_text"])
        elif action == "parse_jd":
            return self.parse_jd(context["jd_text"])
        elif action == "gap_analysis":
            return self.gap_analysis(context["resume"], context["jd"])


class InterviewerAgent(BaseAgent):
    """面试官Agent"""

    def execute(self, action: str, context: Dict) -> Any:
        if action == "start":
            return self.start_interview(context["config"])
        elif action == "chat":
            return self.chat(context["user_message"])
        elif action == "end":
            return self.end_interview()


class EvaluatorAgent(BaseAgent):
    """评估Agent"""

    def execute(self, action: str, context: Dict) -> Any:
        if action == "evaluate":
            return self.evaluate(context["conversation"])
        elif action == "generate_report":
            return self.generate_report(context["session_id"])


class KnowledgeAgent(BaseAgent):
    """知识库Agent"""

    def execute(self, action: str, context: Dict) -> Any:
        if action == "search":
            return self.search(context["query"])
        elif action == "index":
            return self.index_document(context["file_path"])
```

### 3.4 使用LangGraph实现

```python
# 使用LangGraph构建多Agent状态图

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from operator import add

class MultiAgentState(TypedDict):
    """多Agent共享状态"""
    user_input: str
    stage: str  # "parse", "interview", "evaluate"
    session_id: str

    # 解析结果
    resume: dict
    jd: dict
    gap: dict

    # 面试状态
    conversation: Annotated[list, add]
    interview_ended: bool

    # 评估结果
    report: dict


def orchestrator_node(state: MultiAgentState) -> MultiAgentState:
    """协调器节点 - 路由决策"""
    user_input = state["user_input"]
    stage = state["stage"]

    # 意图识别
    if stage == "parse" or "简历" in user_input or "JD" in user_input:
        return {"next_agent": "parser"}
    elif stage == "interview" or state.get("interview_ended") == False:
        return {"next_agent": "interviewer"}
    elif "报告" in user_input or state.get("interview_ended") == True:
        return {"next_agent": "evaluator"}

    return {"next_agent": "interviewer"}


def parser_node(state: MultiAgentState) -> MultiAgentState:
    """解析节点"""
    parser = ParserAgent()
    resume = parser.parse_resume(state.get("resume_text", ""))
    jd = parser.parse_jd(state.get("jd_text", ""))
    gap = parser.gap_analysis(resume, jd)

    return {
        "resume": resume,
        "jd": jd,
        "gap": gap,
        "stage": "interview"
    }


def interviewer_node(state: MultiAgentState) -> MultiAgentState:
    """面试官节点"""
    interviewer = InterviewerAgent()

    if not state.get("conversation"):
        # 首次进入，开始面试
        response = interviewer.start_interview(state.get("config", {}))
    else:
        # 继续对话
        response = interviewer.chat(state["user_input"])

    return {
        "conversation": [{"role": "assistant", "content": response}],
        "interview_ended": "面试到这里" in response or "今天的面试" in response
    }


def evaluator_node(state: MultiAgentState) -> MultiAgentState:
    """评估节点"""
    evaluator = EvaluatorAgent()
    report = evaluator.generate_report(state["session_id"])
    return {"report": report}


# 构建状态图
workflow = StateGraph(MultiAgentState)

# 添加节点
workflow.add_node("orchestrator", orchestrator_node)
workflow.add_node("parser", parser_node)
workflow.add_node("interviewer", interviewer_node)
workflow.add_node("evaluator", evaluator_node)

# 设置入口
workflow.set_entry_point("orchestrator")

# 添加条件边
workflow.add_conditional_edges(
    "orchestrator",
    lambda x: x["next_agent"],
    {
        "parser": "parser",
        "interviewer": "interviewer",
        "evaluator": "evaluator"
    }
)

# 添加结束边
workflow.add_edge("parser", "orchestrator")
workflow.add_edge("interviewer", "orchestrator")
workflow.add_edge("evaluator", END)

# 编译
multi_agent_app = workflow.compile()
```

---

## 4. Week 4 高级特性架构

### 4.1 ReAct推理循环

```
┌─────────────────────────────────────────────────────────────────┐
│                      ReAct 推理循环                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    THOUGHT                              │   │
│   │  分析用户回答，思考下一步行动                            │   │
│   │  - 回答完整吗？                                          │   │
│   │  - 需要追问吗？                                          │   │
│   │  - 应该追问什么？                                        │   │
│   │  - 还是换下一题？                                        │   │
│   └─────────────────────┬───────────────────────────────────┘   │
│                         │                                       │
│                         ▼                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    ACTION                               │   │
│   │  选择并执行行动                                          │   │
│   │  - ask_follow_up()                                      │   │
│   │  - ask_next_question()                                  │   │
│   │  - provide_answer()                                     │   │
│   │  - end_interview()                                      │   │
│   └─────────────────────┬───────────────────────────────────┘   │
│                         │                                       │
│                         ▼                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                  OBSERVATION                            │   │
│   │  观察行动结果                                            │   │
│   │  - 用户如何回应？                                        │   │
│   │  - 评分多少？                                            │   │
│   │  - 是否达到预期？                                        │   │
│   └─────────────────────┬───────────────────────────────────┘   │
│                         │                                       │
│                         └─────────────────────────────────       │
│                                   │                             │
│                                   ▼                             │
│                         继续下一轮循环                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 ReAct实现

```python
# react_interviewer.py

class ReActInterviewer:
    """使用ReAct模式的面试官Agent"""

    def __init__(self):
        self.claude = Anthropic(api_key=settings.CLAUDE_API_KEY)
        self.state = InterviewState()

    def react_loop(self, user_input: str) -> str:
        """ReAct推理循环"""

        while True:
            # ========== THOUGHT ==========
            thought = self._think(user_input)

            # ========== ACTION ==========
            action = self._decide_action(thought)

            # 执行行动
            if action["type"] == "ask_follow_up":
                response = self._ask_follow_up(action["question"])
            elif action["type"] == "ask_next_question":
                response = self._ask_next_question(action["domain"])
            elif action["type"] == "provide_answer":
                response = self._provide_answer(action["question_id"])
            elif action["type"] == "end_interview":
                return self._end_interview()

            # ========== OBSERVATION ==========
            observation = self._observe(response)

            # 更新状态
            self._update_state(observation)

            # 如果是追问，继续循环；如果是新问题，返回等待用户输入
            if action["type"] in ["ask_next_question", "provide_answer", "end_interview"]:
                return response

    def _think(self, user_input: str) -> Dict:
        """思考阶段 - 分析用户回答"""

        prompt = f"""
你是面试官的思考模块。分析候选人的回答。

当前问题：{self.state.current_question}
候选人回答：{user_input}

请分析：
1. 回答质量（complete_correct / partial_correct / vague / wrong / no_answer）
2. 关键点是否覆盖
3. 需要追问什么
4. 还是应该换下一题

返回JSON：
{{
  "quality": "partial_correct",
  "missing_points": ["红黑树", "扩容机制"],
  "should_follow_up": true,
  "follow_up_focus": "红黑树引入的原因",
  "depth": 1
}}
"""

        response = self.claude.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(response.content[0].text)

    def _decide_action(self, thought: Dict) -> Dict:
        """决策阶段 - 根据思考结果选择行动"""

        quality = thought["quality"]

        if quality == "complete_correct":
            return {"type": "ask_next_question", "domain": self._next_domain()}
        elif quality == "partial_correct":
            return {"type": "ask_follow_up", "question": self._generate_follow_up(thought)}
        elif quality == "vague":
            return {"type": "ask_follow_up", "question": "能具体举个例子吗？"}
        elif quality == "wrong":
            return {"type": "ask_follow_up", "question": self._give_hint(thought)}
        elif quality == "no_answer":
            return {"type": "provide_answer", "question_id": self.state.current_question_id}

    def _observe(self, response: str) -> Dict:
        """观察阶段 - 评估行动结果"""

        # 如果是追问，等待用户输入
        # 如果是换题，更新状态
        return {
            "response": response,
            "awaiting_user": True
        }

    def _update_state(self, observation: Dict):
        """更新状态"""
        self.state.conversation_history.append(observation)
```

### 4.3 反思机制 (Reflection)

```
┌─────────────────────────────────────────────────────────────────┐
│                      反思循环 (Reflection)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  面试结束后，Agent自我反思：                                     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  1. 复盘本次面试                                        │   │
│  │     - 哪些问题问得好？                                  │   │
│  │     - 哪些问题可以改进？                                │   │
│  │     - 是否充分考察了候选人？                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                         │                                       │
│                         ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  2. 识别自身问题                                        │   │
│  │     - 是否有遗漏的知识点？                              │   │
│  │     - 追问深度是否合适？                                │   │
│  │     - 节奏控制如何？                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                         │                                       │
│                         ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  3. 生成改进建议                                        │   │
│  │     - 下次面试应该注意什么？                            │   │
│  │     - Prompt需要如何调整？                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. 技术栈选型

### 5.1 技术栈总表

| 层级 | Week 1-2 | Week 3 | Week 4 | 说明 |
|------|---------|--------|--------|------|
| **LLM** | Claude API | Claude API | Claude API | 200K上下文，function calling |
| **Agent框架** | 手写 | LangGraph | LangGraph | 状态图、多Agent协作 |
| **Web UI** | Streamlit | Streamlit | Streamlit | 快速原型 |
| **向量库** | - | ChromaDB | ChromaDB | 本地运行，轻量级 |
| **数据库** | JSON | JSON+SQLite | JSON+SQLite | 元数据存储 |
| **Prompt管理** | 字符串 | 文件模板 | 文件模板 | 版本控制 |
| **日志** | logging | logging+structlog | structlog | 结构化日志 |
| **测试** | pytest | pytest+pytest-async | pytest | 单元测试 |
| **依赖管理** | pip | poetry | poetry | 依赖锁定 |

### 5.2 Claude API选型理由

```
Claude vs 其他LLM：

┌───────────────┬──────────┬──────────┬──────────┬──────────┐
│      特性     │  Claude  │  GPT-4   │   Gemini │   本地   │
├───────────────┼──────────┼──────────┼──────────┼──────────┤
│ 上下文长度    │  200K    │   128K   │   1M     │  取决于  │
│ Function Call │   ✅     │    ✅    │    ✅    │    ❌    │
│ 中文支持      │   ✅     │    ✅    │    ✅    │    ❌    │
│ API稳定性     │   ✅     │    ✅    │    ✅    │    N/A   │
│ 成本          │  中等   │   高     │   低     │   免费   │
│ 速度          │  快     │   中     │   很快   │   慢     │
└───────────────┴──────────┴──────────┴──────────┴──────────┘

选择Claude的原因：
1. 200K上下文 → 长对话无需摘要
2. 优秀的function calling → 工具调用更稳定
3. 中文表现好 → 技术面试场景
4. API文档清晰 → 开发效率高
```

### 5.3 LangGraph选型理由

```
LangGraph vs LangChain vs 手写：

┌──────────────┬──────────┬───────────┬──────────┐
│     特性     │ LangGraph│ LangChain │   手写   │
├──────────────┼──────────┼───────────┼──────────┤
│ 状态图支持   │    ✅    │    ❌     │   需实现 │
│ 多Agent协作  │    ✅    │   困难    │   需实现 │
│ 可视化       │    ✅    │    ❌     │   需实现 │
│ 学习曲线     │   中等   │   陡峭   │   平缓   │
│ 灵活性       │    中    │    低     │   很高   │
└──────────────┴──────────┴───────────┴──────────┘

选择LangGraph的原因：
1. 天然支持状态图 → 面试流程建模
2. 多Agent协作简单 → Week 3核心需求
3. 可视化调试 → 理解Agent行为
4. 活跃社区 → 问题易解决
```

---

## 6. 部署架构

### 6.1 本地开发环境

```
┌─────────────────────────────────────────────────────────────────┐
│                       开发机环境                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  开发者浏览器                             │   │
│  │           http://localhost:8501                         │   │
│  └─────────────────────┬───────────────────────────────────┘   │
│                        │                                        │
│                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Streamlit Server                        │   │
│  │                    streamlit run ui/app.py              │   │
│  └─────────────────────┬───────────────────────────────────┘   │
│                        │                                        │
│                        ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Interview Coach App                    │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│  │  │   Agents    │ │  Services   │ │   Models    │        │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘        │   │
│  └─────────────────────┬───────────────────────────────────┘   │
│                        │                                        │
│         ┌──────────────┼──────────────┐                        │
│         ▼              ▼              ▼                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                    │
│  │Claude API│  │JSON Files│  │ChromaDB  │                    │
│  │(远程)    │  │(本地)    │  │(本地)    │                    │
│  └──────────┘  └──────────┘  └──────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 环境变量配置

```bash
# .env.example

# Claude API
ANTHROPIC_API_KEY=sk-ant-xxxxx
CLAUDE_MODEL=claude-sonnet-4-20250514

# 应用配置
APP_ENV=development
APP_PORT=8501
APP_LOG_LEVEL=DEBUG

# 数据存储
DATA_DIR=./data
INTERVIEW_DIR=./data/interviews
QUESTION_BANK_DIR=./data/question_bank
KNOWLEDGE_BASE_DIR=./data/knowledge_base
CHROMA_DB_DIR=./data/chroma_db

# Agent配置
MAX_CONTEXT_LENGTH=180000  # Claude 200K，留余量
SUMMARY_INTERVAL=10        # 每10轮对话摘要一次
MAX_FOLLOW_UP_DEPTH=3      # 最大追问深度
```

### 6.3 目录权限

```
interview-coach/
├── data/                    # chmod 755
│   ├── interviews/          # chmod 755
│   ├── question_bank/       # chmod 755 (只读)
│   ├── chroma_db/           # chmod 755
│   └── knowledge_base/      # chmod 755
├── logs/                    # chmod 755
└── .env                     # chmod 600 (敏感信息)
```

---

## 7. 性能优化

### 7.1 缓存策略

```python
# cache.py

from functools import lru_cache
import hashlib
import json

class CacheManager:
    """缓存管理器"""

    # LRU缓存：简历解析结果
    @staticmethod
    @lru_cache(maxsize=100)
    def parse_resume_cached(resume_text: str) -> ParsedResume:
        """简历解析缓存 - 相同简历不重复解析"""
        return parse_resume(resume_text)

    # 缓存：JD解析结果
    @staticmethod
    @lru_cache(maxsize=100)
    def parse_jd_cached(jd_text: str) -> ParsedJD:
        """JD解析缓存"""
        return parse_jd(jd_text)

    # 缓存：题库（内存中）
    _question_cache: Dict[str, Question] = {}

    @classmethod
    def load_questions(cls, domain: str) -> List[Question]:
        """加载题目到缓存"""
        if domain not in cls._question_cache:
            with open(f"data/question_bank/{domain}.json") as f:
                questions = json.load(f)
                cls._question_cache[domain] = {
                    q["id"]: Question(**q) for q in questions
                }
        return list(cls._question_cache[domain].values())

    # 缓存：向量检索结果
    _vector_cache: Dict[str, List] = {}

    @classmethod
    def search_vector_cached(cls, query: str, top_k: int = 3) -> List:
        """向量检索缓存 - 5分钟有效期"""
        key = hashlib.md5(query.encode()).hexdigest()
        if key in cls._vector_cache:
            result, timestamp = cls._vector_cache[key]
            if time.time() - timestamp < 300:  # 5分钟
                return result

        result = search_vector(query, top_k)
        cls._vector_cache[key] = (result, time.time())
        return result
```

### 7.2 并发处理

```python
# concurrent.py

import asyncio
from concurrent.futures import ThreadPoolExecutor

class ConcurrentProcessor:
    """并发处理器"""

    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def parse_concurrent(
        self,
        resume_text: str,
        jd_text: str
    ) -> Tuple[ParsedResume, ParsedJD]:
        """并发解析简历和JD"""

        loop = asyncio.get_event_loop()

        # 并发执行
        resume_future = loop.run_in_executor(
            self.executor,
            parse_resume,
            resume_text
        )
        jd_future = loop.run_in_executor(
            self.executor,
            parse_jd,
            jd_text
        )

        # 等待结果
        resume, jd = await asyncio.gather(resume_future, jd_future)

        return resume, jd

    async def batch_evaluate(
        self,
        questions: List[Tuple[str, str]]  # [(question, answer), ...]
    ) -> List[AnswerEvaluation]:
        """批量评估回答"""

        loop = asyncio.get_event_loop()

        tasks = [
            loop.run_in_executor(
                self.executor,
                evaluate_answer,
                q_id,
                q_text,
                a_text
            )
            for q_id, q_text, a_text in questions
        ]

        return await asyncio.gather(*tasks)
```

### 7.3 Token管理

```python
# token_manager.py

class TokenManager:
    """Token管理器"""

    def __init__(self, max_tokens: int = 180000):
        self.max_tokens = max_tokens

    def estimate_tokens(self, text: str) -> int:
        """估算token数量（中文约1.5字符=1token，英文约4字符=1token）"""
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        other_chars = len(text) - chinese_chars
        return int(chinese_chars / 1.5 + other_chars / 4)

    def should_summarize(self, conversation: List[Dict]) -> bool:
        """判断是否需要摘要"""
        total_tokens = sum(
            self.estimate_tokens(msg["content"])
            for msg in conversation
        )
        return total_tokens > self.max_tokens * 0.7  # 超过70%时摘要

    def compress_conversation(
        self,
        conversation: List[Dict],
        summary: str
    ) -> List[Dict]:
        """压缩对话"""
        # 保留最近5轮
        recent = conversation[-10:] if len(conversation) > 10 else conversation

        # 插入摘要
        return [
            {"role": "system", "content": f"对话摘要：{summary}"},
            *recent
        ]
```

---

## 8. 安全设计

### 8.1 数据安全

```python
# security.py

import os
from cryptography.fernet import Fernet

class SecurityManager:
    """安全管理器"""

    @staticmethod
    def encrypt_sensitive_data(data: str) -> str:
        """加密敏感数据"""
        key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
        fernet = Fernet(key)
        return fernet.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt_sensitive_data(encrypted_data: str) -> str:
        """解密敏感数据"""
        key = os.getenv("ENCRYPTION_KEY")
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data.encode()).decode()

    @staticmethod
    def sanitize_resume(resume_text: str) -> str:
        """脱敏简历（移除手机号、邮箱等）"""
        import re
        text = re.sub(r'1[3-9]\d{9}', '[PHONE]', resume_text)
        text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]', text)
        return text
```

### 8.2 API密钥管理

```python
# config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """配置管理"""

    # Claude API
    anthropic_api_key: str

    # 应用配置
    app_env: str = "development"
    app_port: int = 8501
    debug: bool = False

    # 数据路径
    data_dir: str = "./data"
    interview_dir: str = "./data/interviews"
    question_bank_dir: str = "./data/question_bank"

    # Agent配置
    max_context_length: int = 180000
    summary_interval: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
```

---

## 9. 监控与日志

### 9.1 日志设计

```python
# logger.py

import structlog
from datetime import datetime

def setup_logger():
    """配置结构化日志"""

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )

    return structlog.get_logger()

logger = setup_logger()

# 使用示例
logger.info(
    "interview_started",
    session_id="2026-03-17-001",
    interviewer_level="senior_engineer",
    focus_areas=["technical_basics", "project_experience"]
)
```

### 9.2 指标收集

```python
# metrics.py

from collections import defaultdict
from datetime import datetime

class MetricsCollector:
    """指标收集器"""

    def __init__(self):
        self.metrics = defaultdict(list)

    def record_llm_call(self, model: str, tokens: int, latency: float):
        """记录LLM调用"""
        self.metrics["llm_calls"].append({
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "tokens": tokens,
            "latency_ms": latency * 1000
        })

    def record_interview(self, session_id: str, duration: int, questions: int):
        """记录面试指标"""
        self.metrics["interviews"].append({
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "duration_seconds": duration,
            "questions_asked": questions
        })

    def get_summary(self) -> dict:
        """获取指标摘要"""
        llm_calls = self.metrics["llm_calls"]
        return {
            "total_llm_calls": len(llm_calls),
            "total_tokens": sum(c["tokens"] for c in llm_calls),
            "avg_latency_ms": sum(c["latency_ms"] for c in llm_calls) / len(llm_calls) if llm_calls else 0
        }
```

---

## 10. 架构决策记录 (ADR)

### ADR-001: 使用Claude而非GPT-4

| 状态 | 日期 | 决策 |
|------|------|------|
| 提议 | 2026-03-17 | 使用Claude API |
| 理由 | - 200K上下文，适合长对话 |
| | - Function Calling稳定 |
| | - 中文表现优秀 |
| 后果 | - 依赖Anthropic服务稳定性 |
| | - API费用可控 |

### ADR-002: 单Agent起步，多Agent演进

| 状态 | 日期 | 决策 |
|------|------|------|
| 提议 | 2026-03-17 | Week 1-2单Agent，Week 3+多Agent |
| 理由 | - MVP快速交付 |
| | - 循序渐进学习Agent机制 |
| | - 便于对比两种模式差异 |
| 后果 | - Week 3需要重构 |
| | - 可以保留单Agent作为轻量版本 |

### ADR-003: 使用ChromaDB而非Pinecone

| 状态 | 日期 | 决策 |
|------|------|------|
| 提议 | 2026-03-17 | 使用ChromaDB |
| 理由 | - 本地运行，无需云服务 |
| | - 开源免费 |
| | - Python原生支持 |
| 后果 | - 需要自行管理向量库 |
| | - 无需担心API限流 |
