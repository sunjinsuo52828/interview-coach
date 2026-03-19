# Interview Coach - 详细设计文档

## 1. 功能模块详细设计

### 1.1 模块总览

```
┌─────────────────────────────────────────────────────────────┐
│                    Interview Coach                          │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   解析模块   │   面试模块   │   评估模块   │   知识库模块   │
│              │              │              │   (Week 3)     │
├──────────────┼──────────────┼──────────────┼────────────────┤
│• 简历解析    │• 面试配置    │• 实时评分    │• 文档导入      │
│• JD解析      │• 动态Prompt  │• 维度评分    │• 向量检索      │
│• Gap分析     │• 对话循环    │• 报告生成    │• 知识问答      │
│              │• 追问策略树  │• 学习建议    │• 题目关联      │
└──────────────┴──────────────┴──────────────┴────────────────┘
```

### 1.2 解析模块设计

#### 1.2.1 简历解析器 (ResumeParser)

**输入**：纯文本格式的简历

**输出结构**：
```python
@dataclass
class ParsedResume:
    # 基本信息
    name: str
    phone: str
    email: str
    experience_years: int
    current_role: str

    # 技术栈
    technical_skills: TechnicalSkills

    # 项目经验
    projects: List[Project]

    # 教育背景
    education: List[Education]

@dataclass
class TechnicalSkills:
    # 编程语言
    languages: List[str]  # ["Java", "Python", "JavaScript"]

    # 框架
    frameworks: List[str]  # ["Spring Boot", "Spring Cloud", "MyBatis"]

    # 中间件
    middleware: List[str]  # ["Redis", "Kafka", "RabbitMQ"]

    # 数据库
    databases: List[str]  # ["MySQL", "PostgreSQL", "MongoDB"]

    # DevOps
    devops: List[str]  # ["Docker", "K8s", "Jenkins", "Git"]

@dataclass
class Project:
    name: str
    role: str
    duration: str
    tech_stack: List[str]
    description: str
    highlights: List[str]  # 亮点成就

@dataclass
class Education:
    school: str
    degree: str
    major: str
    graduation_year: int
```

**解析规则**：
```python
RESUME_PATTERNS = {
    "name": r"(?:姓名|Name)[:：]\s*([A-Za-z\u4e00-\u9fa5]+)",
    "phone": r"1[3-9]\d{9}",
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "experience": r"(\d+)\s*年",
}
```

#### 1.2.2 JD解析器 (JDParser)

**输入**：纯文本格式的JD

**输出结构**：
```python
@dataclass
class ParsedJD:
    # 基本信息
    company: str
    position: str
    location: str
    salary_range: str

    # 技能要求
    required_skills: List[str]   # 必须技能
    preferred_skills: List[str]  # 加分技能

    # 经验要求
    min_experience: int
    preferred_experience: int

    # 岗位职责
    responsibilities: List[str]

    # 业务领域
    business_domain: str  # "金融", "电商", "游戏" 等

    # 岗位级别
    level: str  # "Junior", "Senior", "Lead", "Principal"
```

#### 1.2.3 Gap分析器 (GapAnalyzer)

**输入**：ParsedResume + ParsedJD

**输出结构**：
```python
@dataclass
class GapAnalysis:
    # 匹配度
    match_percentage: float  # 0.0 - 1.0

    # 匹配项（简历满足JD的部分）
    matched_items: List[str]

    # 差距项（JD要求但简历未体现）
    gap_items: List[str]

    # 加分项（简历有但JD没要求的）
    bonus_items: List[str]

    # 面试重点建议
    interview_focus: List[str]

    # 匹配详情
    match_details: Dict[str, MatchDetail]

@dataclass
class MatchDetail:
    category: str  # "skill", "experience", "domain"
    required: str
    has_match: bool
    match_score: float
```

### 1.3 面试模块设计

#### 1.3.1 面试配置 (InterviewConfig)

```python
@dataclass
class InterviewConfig:
    # 面试官配置
    interviewer_level: str  # "senior_engineer", "tech_lead", ...
    interviewer_style: str  # "friendly", "professional", "challenging", "open"
    custom_title: Optional[str] = None

    # 考察重点
    focus_areas: List[str]  # ["technical_basics", "project_experience", ...]

    # 面试参数
    duration: int = 45  # 分钟
    language: str = "zh"  # "zh", "en", "mixed"

    # 难度
    difficulty: str = "medium"  # "easy", "medium", "hard"
```

#### 1.3.2 追问策略树

```python
@dataclass
class FollowUpStrategy:
    """追问策略"""
    trigger_condition: str  # 触发条件
    follow_up_type: str     # 追问类型
    follow_up_action: str   # 追问动作

FOLLOW_UP_STRATEGIES = {
    "complete_correct": {
        "type": "level_up",
        "action": "升维追问 - 考察更高难度或更广视角",
        "examples": [
            "HashMap讲得很好，那ConcurrentHashMap呢？",
            "单机场景理解了，那分布式场景呢？"
        ]
    },
    "partial_correct": {
        "type": "guided_completion",
        "action": "定向补全 - 引导补充缺失要点",
        "examples": [
            "你提到了数组+链表，还有一种数据结构？",
            "这个方案还有其他考虑因素吗？"
        ]
    },
    "correct_but_vague": {
        "type": "detail_drill",
        "action": "细节深挖 - 要求举例/给数据/讲场景",
        "examples": [
            "能说说在你的项目中具体怎么做的吗？",
            "这个数据量大概多少？响应时间多少？"
        ]
    },
    "wrong": {
        "type": "corrective_guidance",
        "action": "纠正引导 - 给提示，再给一次机会",
        "examples": [
            "不太对，提示一下：考虑并发场景...",
            "思路有问题，再想想：如果多个客户端同时..."
        ]
    },
    "no_answer": {
        "type": "provide_answer",
        "action": "给参考答案 + 标记弱项 + 下一题",
        "examples": [
            "没关系，这道题考察的是...",
            "这个知识点建议你回去补一下：..."
        ]
    }
}
```

#### 1.3.3 对话状态管理

```python
@dataclass
class ConversationTurn:
    """单轮对话"""
    turn_id: str
    timestamp: str

    # 问题
    question_id: str
    question_text: str
    question_domain: str

    # 回答
    user_answer: str

    # 评估
    score: str  # "A", "B", "C", "D"
    follow_up_count: int
    evaluation_notes: List[str]

@dataclass
class InterviewState:
    """面试状态"""
    session_id: str
    config: InterviewConfig
    resume: ParsedResume
    jd: ParsedJD
    gap: GapAnalysis

    # 进度
    started_at: str
    current_turn: int
    estimated_total_turns: int
    is_ended: bool = False

    # 对话历史
    conversation_history: List[ConversationTurn] = field(default_factory=list)

    # 实时追踪
    questions_asked: List[str] = field(default_factory=list)
    covered_domains: List[str] = field(default_factory=list)
    pending_domains: List[str] = field(default_factory=list)

    # 动态评估
    skill_mastery: Dict[str, int] = field(default_factory=dict)
    weaknesses: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)

    # 摘要（用于长对话）
    summary: Optional[str] = None
```

### 1.4 评估模块设计

#### 1.4.1 评分维度

```python
@dataclass
class DimensionScore:
    """维度评分"""
    dimension: str
    score: float  # 0.0 - 100.0
    grade: str   # "A", "B", "C", "D"
    evidence: List[str]  # 评分依据

EVALUATION_DIMENSIONS = {
    "technical_depth": {
        "name": "技术深度",
        "weight": 0.35,
        "description": "对技术原理的理解程度，是否知其所以然"
    },
    "project_experience": {
        "name": "项目经验",
        "weight": 0.25,
        "description": "项目经历的深度和广度，解决问题的能力"
    },
    "problem_solving": {
        "name": "问题解决",
        "weight": 0.20,
        "description": "分析和解决问题的思路和方法"
    },
    "communication": {
        "name": "沟通表达",
        "weight": 0.10,
        "description": "表达的清晰度、逻辑性、条理性"
    },
    "learning_ability": {
        "name": "学习能力",
        "weight": 0.10,
        "description": "对新技术的学习能力和好奇心"
    }
}
```

#### 1.4.2 评估报告

```python
@dataclass
class InterviewReport:
    """面试评估报告"""
    session_id: str
    generated_at: str

    # 总体评分
    overall_score: float
    overall_grade: str  # "A", "B", "C", "D"
    recommendation: str  # "HIRE", "NO_HIRE", "HIRE_WITH_CONDITIONS"

    # 维度评分
    dimension_scores: Dict[str, DimensionScore]

    # 题目详情
    question_results: List[QuestionResult]

    # 优势与弱项
    strengths: List[str]
    weaknesses: List[str]

    # 学习建议
    learning_suggestions: List[str]
    recommended_resources: List[str]

@dataclass
class QuestionResult:
    """单题结果"""
    question_id: str
    question_text: str
    domain: str
    user_answer: str
    score: str
    evaluator_notes: str
    follow_ups: List[str]
```

---

## 2. 数据模型设计

### 2.1 文件结构

```
interview-coach/
├── data/
│   ├── question_bank/           # 题库
│   │   ├── java_core.json
│   │   ├── spring.json
│   │   ├── distributed.json
│   │   └── ...
│   ├── interviews/              # 面试记录
│   │   └── {session_id}.json
│   ├── chroma_db/               # 向量库 (Week 3)
│   │   ├── chroma.sqlite3
│   │   └── ...
│   ├── knowledge_base/          # 知识库文档 (Week 3)
│   │   ├── java/
│   │   ├── spring/
│   │   └── ...
│   └── user_stats.json          # 用户统计
├── agents/
│   ├── __init__.py
│   ├── base_agent.py            # Agent基类
│   ├── interview_agent.py       # 面试官Agent
│   ├── parser_agent.py          # 解析Agent (Week 3)
│   ├── evaluator_agent.py       # 评估Agent (Week 3)
│   ├── knowledge_agent.py       # 知识库Agent (Week 3)
│   └── orchestrator.py          # 协调器 (Week 3)
├── prompts/
│   ├── __init__.py
│   ├── interviewer_system.txt
│   ├── interviewer_user.txt
│   ├── parser_prompt.txt
│   ├── evaluator_prompt.txt
│   └── orchestrator_prompt.txt
├── tools/
│   ├── __init__.py
│   ├── parser_tools.py
│   ├── interview_tools.py
│   ├── knowledge_tools.py
│   └── evaluator_tools.py
├── ui/
│   └── app.py                   # Streamlit应用
├── models/
│   ├── __init__.py
│   ├── interview.py             # 数据模型
│   └── state.py                 # 状态模型
├── utils/
│   ├── __init__.py
│   ├── llm.py                   # LLM客户端
│   └── logger.py                # 日志
├── config.py                    # 配置
├── main.py                      # 入口
└── requirements.txt
```

### 2.2 数据库Schema (Week 3+ - SQLite)

```sql
-- 用户表
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 面试会话表
CREATE TABLE interview_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT,
    company TEXT,
    position TEXT,
    resume_summary TEXT,  -- JSON
    jd_summary TEXT,      -- JSON
    gap_analysis TEXT,    -- JSON
    config TEXT,          -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 面试记录表
CREATE TABLE interview_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    turn_number INTEGER,
    question_id TEXT,
    question_text TEXT,
    user_answer TEXT,
    score TEXT,
    evaluator_notes TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES interview_sessions(session_id)
);

-- 评估报告表
CREATE TABLE evaluation_reports (
    session_id TEXT PRIMARY KEY,
    overall_score REAL,
    overall_grade TEXT,
    recommendation TEXT,
    dimension_scores TEXT,  -- JSON
    strengths TEXT,        -- JSON array
    weaknesses TEXT,       -- JSON array
    suggestions TEXT,      -- JSON array
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES interview_sessions(session_id)
);

-- 知识状态表 (Week 3)
CREATE TABLE knowledge_status (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    topic TEXT,
    domain TEXT,
    status TEXT,  -- 'mastered', 'reviewing', 'not_learned'
    query_count INTEGER DEFAULT 0,
    last_queried TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. API接口设计

### 3.1 Agent内部接口

```python
# ============ 解析工具接口 ============

@tool
def parse_resume(resume_text: str) -> ParsedResume:
    """解析简历文本，提取结构化信息"""
    pass

@tool
def parse_jd(jd_text: str) -> ParsedJD:
    """解析JD文本，提取结构化信息"""
    pass

@tool
def gap_analysis(
    resume_skills: List[str],
    jd_requirements: List[str],
    resume_experience_years: int,
    jd_experience_years: int
) -> GapAnalysis:
    """对比简历和JD，输出匹配度分析"""
    pass


# ============ 面试工具接口 ============

@tool
def get_question(
    domain: str,
    difficulty: str = "medium",
    exclude_ids: List[str] = None
) -> Question:
    """从题库获取面试题"""
    pass

@tool
def evaluate_answer(
    question_id: str,
    question_text: str,
    user_answer: str,
    reference_answer: str = None
) -> AnswerEvaluation:
    """评估用户回答质量"""
    pass

@tool
def generate_questions_from_jd(
    jd_summary: ParsedJD,
    resume_summary: ParsedResume,
    domains: List[str],
    count_per_domain: int = 5
) -> List[Question]:
    """根据JD和简历动态生成面试题"""
    pass


# ============ 评估工具接口 ============

@tool
def save_round_result(
    session_id: str,
    interviewer_level: str,
    score: str,
    strengths: List[str],
    weaknesses: List[str],
    questions: List[QuestionResult],
    recommendation: str
) -> bool:
    """保存单轮面试结果"""
    pass

@tool
def generate_report(session_id: str) -> InterviewReport:
    """生成评估报告"""
    pass


# ============ 知识库工具接口 (Week 3) ============

@tool
def search_knowledge_base(
    query: str,
    top_k: int = 3
) -> List[KnowledgeChunk]:
    """语义搜索知识库"""
    pass

@tool
def get_related_questions(topic: str) -> List[Question]:
    """根据知识点获取相关面试题"""
    pass

@tool
def index_document(
    file_path: str,
    domain: str,
    tags: List[str] = None
) -> bool:
    """导入文档到知识库"""
    pass
```

### 3.2 Web UI接口 (Streamlit)

```python
# Streamlit页面状态
class StreamlitState:
    # 页面导航
    current_page: str  # "setup", "interview", "report"

    # 设置阶段
    resume_text: str
    jd_text: str
    parsed_resume: ParsedResume
    parsed_jd: ParsedJD
    gap_analysis: GapAnalysis

    # 配置阶段
    interviewer_level: str
    focus_areas: List[str]
    interviewer_style: str
    duration: int
    language: str

    # 面试阶段
    session_id: str
    conversation_history: List[Dict]
    current_question: str
    is_interview_ended: bool

    # 报告阶段
    report: InterviewReport
```

---

## 4. Prompt模板设计

### 4.1 面试官System Prompt

```
# interview_system.txt

你是一名专业的技术面试官，正在对候选人进行面试。

## 你的身份
{interviewer_persona}

你是一名{interviewer_level}，面试风格是{interviewer_style}。

## 面试规则
1. **开场**：先自我介绍，说明今天的面试流程
2. **提问**：从候选人的简历切入，逐步深入
3. **追问**：根据回答质量决定是否追问
4. **控制**：保持合适的节奏，在{duration}分钟内完成面试
5. **结束**：告知候选人面试结束，并说明下一步

## 追问策略
根据候选人回答的质量，选择合适的追问方式：

- 回答完整正确 → 升维追问（考察更高难度）
- 部分正确 → 定向补全（引导补充要点）
- 方向正确但模糊 → 细节深挖（要求举例说明）
- 明显错误 → 纠正引导（给提示再给机会）
- 完全不会 → 给参考答案 + 换题

每个问题最多追问2-3层，避免死缠。

## 考察重点
{focus_areas}

## 候选人信息
简历摘要：
- 技术栈：{resume_skills}
- 项目：{resume_projects}

JD要求：
- 岗位：{position}
- 公司：{company}
- 核心要求：{jd_requirements}

## 差距分析
以下技能是JD要求但简历未充分体现的，需要重点考察：
{gap_items}

## 语言要求
{language_requirement}

## 重要提醒
- 不要一次性给出所有问题的答案
- 让候选人充分表达，不要急于打断
- 保持专业，同时营造轻松的氛围
- 每个话题控制在3-5个问题内

现在，开始面试吧！
```

### 4.2 评估Agent Prompt

```
# evaluator_prompt.txt

你是一名专业的面试评估专家。你的任务是根据面试对话记录，生成客观、全面的评估报告。

## 评估维度
请从以下维度评估候选人（每项0-100分）：

1. **技术深度 (35%)**
   - 对技术原理的理解程度
   - 是否知其所以然
   - 能否举一反三

2. **项目经验 (25%)**
   - 项目经历的深度
   - 解决问题的能力
   - 技术选型思路

3. **问题解决 (20%)**
   - 分析问题的逻辑
   - 解决方案的设计
   - 考虑是否全面

4. **沟通表达 (10%)**
   - 表达的清晰度
   - 逻辑性和条理性
   - 术语使用准确

5. **学习能力 (10%)**
   - 对新技术的关注
   - 学习方法和习惯
   - 好奇心和求知欲

## 输出格式
请按以下JSON格式输出：

```json
{
  "overall_score": 85.0,
  "overall_grade": "B+",
  "recommendation": "HIRE",
  "dimension_scores": {
    "technical_depth": {"score": 80, "grade": "B", "evidence": [...]},
    "project_experience": {"score": 90, "grade": "A", "evidence": [...]},
    ...
  },
  "strengths": [
    "Spring生态非常熟悉",
    "项目经验丰富，能解决实际问题"
  ],
  "weaknesses": [
    "分布式经验较少",
    "对JVM原理理解不够深入"
  ],
  "learning_suggestions": [
    "建议深入学习Kafka的原理和使用场景",
    "可以补充一些分布式系统的理论知识"
  ]
}
```

## 输入数据
面试对话记录：
{conversation_history}

JD要求：
{jd_requirements}

请开始评估。
```

---

## 5. 题库结构设计

### 5.1 题目分类

```python
QUESTION_DOMAINS = {
    # Java基础
    "java_core": {
        "name": "Java核心",
        "subdomains": ["集合", "并发", "IO/NIO", "JVM", "异常"]
    },
    # Spring生态
    "spring": {
        "name": "Spring框架",
        "subdomains": ["Spring Core", "Spring Boot", "Spring Cloud", "Spring MVC"]
    },
    # 数据库
    "database": {
        "name": "数据库",
        "subdomains": ["MySQL", "Redis", "MongoDB", "SQL优化"]
    },
    # 中间件
    "middleware": {
        "name": "中间件",
        "subdomains": ["Kafka", "RabbitMQ", "RocketMQ", "Elasticsearch"]
    },
    # 分布式
    "distributed": {
        "name": "分布式系统",
        "subdomains": ["CAP", "一致性", "分布式锁", "分布式事务", "RPC"]
    },
    # 系统设计
    "system_design": {
        "name": "系统设计",
        "subdomains": ["高并发", "高可用", "容量规划", "架构设计"]
    },
    # 算法
    "algorithm": {
        "name": "算法编程",
        "subdomains": ["数据结构", "算法", "复杂度分析"]
    },
    # 行为面试
    "behavioral": {
        "name": "行为面试",
        "subdomains": ["团队协作", "冲突处理", "领导力", "职业规划"]
    }
}
```

### 5.2 题目结构

```python
@dataclass
class Question:
    """面试题"""
    id: str                           # 唯一标识
    domain: str                       # 领域
    subdomain: str                    # 子领域
    difficulty: str                   # 难度: easy/medium/hard

    question: str                     # 题目文本
    reference_answer: str             # 参考答案
    key_points: List[str]             # 关键点

    follow_ups: List[str]             # 追问建议

    # 适用场景
    suitable_levels: List[str]        # 适用的面试官级别
    suitable_rounds: List[str]        # 适用的轮次

    # 元数据
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
```

### 5.3 示例题目

```json
{
  "id": "java_hashmap_001",
  "domain": "java_core",
  "subdomain": "集合",
  "difficulty": "medium",
  "question": "HashMap的底层数据结构是什么？ JDK7和JDK8有什么区别？",
  "reference_answer": "HashMap的底层数据结构是数组+链表+红黑树（JDK8+）。\n\nJDK7: 数组+链表\nJDK8: 数组+链表+红黑树（链表长度超过8且数组长度超过64时转为红黑树）\n\n关键点：\n1. 数组初始容量16，负载因子0.75\n2. hash计算：(h = key.hashCode()) ^ (h >>> 16)\n3. 扰动处理：减少hash冲突\n4. 扩容：2倍扩容，重新计算hash\n5. 红黑树：提高查询效率，O(n)→O(logn)",
  "key_points": [
    "数组+链表+红黑树",
    "hash计算和扰动处理",
    "扩容机制",
    "红黑树转换条件"
  ],
  "follow_ups": [
    "为什么JDK8引入红黑树？",
    "HashMap是线程安全的吗？",
    "ConcurrentHashMap是如何实现的？"
  ],
  "suitable_levels": ["senior_engineer", "tech_lead"],
  "suitable_rounds": ["技术基础", "源码原理"],
  "tags": ["Java", "集合", "HashMap", "数据结构"]
}
```

---

## 6. 错误处理设计

### 6.1 错误分类

```python
class InterviewCoachError(Exception):
    """基础异常"""
    pass

class ParseError(InterviewCoachError):
    """解析错误"""
    pass

class InterviewError(InterviewCoachError):
    """面试流程错误"""
    pass

class LLMError(InterviewCoachError):
    """LLM调用错误"""
    pass

class KnowledgeBaseError(InterviewCoachError):
    """知识库错误"""
    pass
```

### 6.2 重试策略

```python
RETRY_CONFIG = {
    "llm_call": {
        "max_retries": 3,
        "backoff": "exponential",
        "initial_delay": 1.0
    },
    "knowledge_search": {
        "max_retries": 2,
        "backoff": "fixed",
        "delay": 0.5
    }
}
```

---

## 7. 性能指标

| 指标 | 目标值 |
|------|--------|
| 解析响应时间 | < 2秒 |
| 面试对话响应 | < 3秒 |
| 报告生成时间 | < 5秒 |
| 知识库检索 | < 500ms |
| 内存占用 | < 500MB |
| 支持并发会话 | 10+ |
