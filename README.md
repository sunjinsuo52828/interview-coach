# Interview Coach

> AI驱动的技术面试模拟平台，帮助求职者通过多场景面试练习提升能力。

## 项目简介

Interview Coach 是一个基于Claude AI的面试模拟器，能够根据求职者的简历和目标岗位JD，自动生成个性化的面试场景，并提供实时评估和学习建议。

### 核心特性

- 📋 **智能解析**：自动提取简历和JD中的关键信息
- 🎯 **Gap分析**：识别技能差距，确定面试重点
- 🤖 **动态面试官**：支持多级别面试官角色（Senior/Lead/Architect等）
- 💬 **智能追问**：根据回答质量自动追问2-3层
- 📊 **评估报告**：多维度评分，给出针对性学习建议
- 🧠 **知识库RAG**：基于个人学习资料的知识检索（V1.1）
- 🔄 **ReAct推理**：可观察的Agent推理过程（V1.2）

## 快速开始

### 安装

```bash
# 克隆项目
git clone <repo-url>
cd interview-coach

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env，填入你的Claude API密钥
```

### 运行

```bash
# 启动Streamlit应用
streamlit run ui/app.py
```

访问 http://localhost:8501 开始使用。

## 项目结构

```
interview-coach/
├── agents/                 # Agent模块
│   ├── base_agent.py      # Agent基类
│   ├── interview_agent.py # 面试官Agent
│   ├── parser_agent.py    # 解析Agent
│   ├── evaluator_agent.py # 评估Agent
│   └── knowledge_agent.py # 知识库Agent
├── tools/                 # 工具函数
├── models/                # 数据模型
├── prompts/               # Prompt模板
├── ui/                    # Streamlit UI
├── utils/                 # 工具函数
├── data/                  # 数据目录
│   ├── question_bank/     # 题库
│   ├── interviews/        # 面试记录
│   └── knowledge_base/    # 知识库
├── docs/                  # 文档
│   ├── 01-detailed-design.md
│   ├── 02-architecture-design.md
│   └── 03-roadmap.md
├── config.py              # 配置
└── requirements.txt       # 依赖
```

## 开发计划

- [x] 详细设计
- [x] 架构设计
- [x] Roadmap
- [x] Week 1: MVP开发（单Agent）
- [x] Week 2: MVP完善（多Agent + Chain of Thought）
- [ ] Week 3: 高级特性（可选）

## 🚀 Streamlit Cloud 部署

### 方法 1: 通过网页部署（推荐）

1. 访问 [share.streamlit.io](https://share.streamlit.io)
2. 点击 "New app"
3. 连接你的 GitHub 仓库
4. 配置：
   - **Main file path**: `ui/app.py`
   - **Python version**: `3.11`
5. 点击 "Deploy"

### 方法 2: 通过 CLI 部署

```bash
# 安装 Streamlit CLI
pip install streamlit

# 部署
streamlit run ui/app.py
# 首次使用会提示登录，按提示操作即可
```

### 环境变量配置

在 Streamlit Cloud 中配置以下 Secret：

```bash
GLM_API_KEY=your_glm_api_key_here
```

在 `.streamlit/config.toml` 中配置（可选）：

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

## 技术栈

- **LLM**: Claude API (claude-sonnet-4-20250514)
- **Agent框架**: LangGraph
- **Web UI**: Streamlit
- **向量库**: ChromaDB
- **语言**: Python 3.10+

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License
