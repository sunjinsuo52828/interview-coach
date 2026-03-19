# Interview Coach - 快速开始指南

## 🚀 5分钟上手

### 1. 环境准备

```bash
# 进入项目目录
cd C:/Practice/learning/interview-coach

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的Claude API密钥
# ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### 3. 启动应用

```bash
streamlit run ui/app.py
```

访问 http://localhost:8501

---

## 📖 使用流程

### Step 1: 粘贴简历和JD

在"📝 配置"页面：

```
简历内容示例：

姓名：张三
电话：13800138000
邮箱：zhangsan@example.com
工作经验：5年
当前职位：Java后端工程师

技术栈：
- 语言：Java, Python, JavaScript
- 框架：Spring Boot, Spring Cloud, MyBatis
- 中间件：Redis, Kafka, RabbitMQ
- 数据库：MySQL, PostgreSQL, MongoDB
- DevOps：Docker, K8s, Jenkins, Git

项目经验：
项目1：电商交易系统
- 角色：核心开发
- 时长：2021-2023
- 技术栈：Spring Boot, Redis, MySQL, Kafka
- 亮点：实现分布式锁解决并发问题

项目2：支付网关
- 角色：技术负责人
- 时长：2023-至今
- 技术栈：Spring Cloud, K8s, ElasticSearch
- 亮点：系统可用性达到99.9%
```

```
JD内容示例：

公司：某互联网公司
职位：Senior Java Engineer
地点：北京
薪资：30k-50k

必须技能：
- Java, Spring Boot, Spring Cloud
- MySQL, Redis
- Kafka, RabbitMQ
- 分布式系统设计
- Docker, K8s

加分技能：
- ElasticSearch, ClickHouse
- 大数据处理经验
- 金融行业经验

岗位职责：
1. 负责核心业务系统开发
2. 参与系统架构设计
3. 解决高并发、高可用问题

经验要求：
- 5年以上Java开发经验
- 有大型分布式系统经验
```

### Step 2: 查看Gap分析

系统会自动分析：
- 匹配度百分比
- 匹配项列表
- 差距项列表（重点考察）

### Step 3: 配置面试

- **面试官级别**：选择Senior Engineer / Tech Lead / Architect等
- **面试风格**：友好轻松 / 专业严谨 / 高压挑战
- **考察重点**：技术基础 / 源码原理 / 项目经验 / 系统设计等
- **时长**：30/45/60分钟
- **语言**：中文/English/混合

### Step 4: 开始面试

面试官会：
1. 自我介绍
2. 从简历切入提问
3. 根据你的回答追问
4. 控制节奏完成面试

### Step 5: 查看报告

面试结束后生成评估报告：
- 总体评分（A/B/C/D）
- 各维度评分
- 优势列表
- 待改进列表
- 学习建议

---

## 💡 使用技巧

### 1. 充分利用Gap分析
Gap分析中的"差距项"就是面试官会重点考察的内容。提前准备！

### 2. 尝试不同面试官级别
- **Senior Engineer**：关注代码质量、工程实践
- **Tech Lead**：关注技术深度、项目管理
- **Architect**：关注架构设计、技术选型

### 3. 模拟高压面试
选择"高压挑战"风格，训练抗压能力。

### 4. 利用追问机制
回答不完整时，面试官会追问。这是学习深挖的好机会。

### 5. 复盘报告
仔细看报告中的"待改进"和"学习建议"，针对性补强。

---

## 🧪 测试示例

### 测试简历（短版本）
```
姓名：李四
经验：3年Java开发
技术栈：Java, Spring Boot, MySQL, Redis
项目：用户管理系统（单体架构）
```

### 测试JD（短版本）
```
职位：Java后端工程师
必须技能：Java, Spring, MySQL, Redis, Kafka
职责：负责后端接口开发
```

### 预期Gap分析结果
```
匹配度：60%
匹配项：Java, Spring, MySQL, Redis
差距项：Kafka（重点考察）
```

---

## ⚠️ 常见问题

### Q: Claude API从哪里获取？
A: 访问 https://console.anthropic.com/ 注册并获取API密钥。

### Q: 对话响应慢怎么办？
A:
1. 检查网络连接
2. 检查API密钥是否正确
3. 当前模型是claude-sonnet-4，速度正常在2-5秒

### Q: 解析结果不准确怎么办？
A:
1. 确保粘贴的是纯文本格式
2. 格式尽量清晰（换行分隔不同部分）
3. 项目经验用列表形式更易解析

### Q: 面试官不会追问怎么办？
A:
1. 确保回答有一定长度（太短会被判定为"不会"）
2. 可以故意给出不完整的回答触发追问
3. 追问最多2-3层，之后会换题

### Q: 报告生成失败怎么办？
A:
1. 确保对话至少进行了3轮以上
2. 检查API调用次数是否超限
3. 查看终端错误日志

---

## 📚 进阶使用

### 编程方式调用

```python
from agents import (
    ParserAgent,
    InterviewerAgent,
    EvaluatorAgent
)

# 解析
parser = ParserAgent()
resume = parser.parse_resume(resume_text)
jd = parser.parse_jd(jd_text)
gap = parser.gap_analysis(resume, jd)

# 面试
interviewer = InterviewerAgent()
greeting = interviewer.start_interview({
    "config": config,
    "resume": resume,
    "jd": jd,
    "gap": gap
})

# 对话
response = interviewer.chat({"user_message": user_input})

# 评估
evaluator = EvaluatorAgent()
report = evaluator.generate_report({"state": interviewer.state})
```

### 自定义Prompt

修改 `agents/interview_agent.py` 中的 `get_system_prompt()` 方法，自定义面试官人设。

---

## 🎯 下一步

- Week 3: 多Agent架构 + 知识库RAG
- Week 4: ReAct推理循环 + 反思机制
- 查看文档：`docs/` 目录
- 提交Issue：报告bug或建议
