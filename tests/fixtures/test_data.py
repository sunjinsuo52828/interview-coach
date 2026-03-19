"""
示例测试数据 - 简历和JD文本
"""

# ========== 示例简历 ==========

SAMPLE_RESUME_TEXT = """
姓名：张三
电话：13800138000
邮箱：zhangsan@example.com
工作经验：5年
当前职位：Java后端工程师

技术栈：
- 编程语言：Java, Python, JavaScript
- 框架：Spring Boot, Spring Cloud, MyBatis, Hibernate
- 中间件：Redis, Kafka, RabbitMQ, Elasticsearch
- 数据库：MySQL, PostgreSQL, MongoDB
- DevOps：Docker, Kubernetes, Jenkins, Git, Maven

项目经验：

项目1：电商交易系统
- 角色：核心开发
- 时间：2021.06 - 2023.05
- 技术栈：Spring Boot, Redis, MySQL, Kafka, Docker
- 描述：
  负责电商交易系统的后端开发，处理高并发交易场景。
  使用Redis实现分布式缓存，Kafka实现异步解耦。
- 亮点：
  * 实现分布式锁解决并发问题
  * 性能优化30%，响应时间从500ms降至350ms
  * 设计并实现订单状态机

项目2：支付网关
- 角色：技术负责人
- 时间：2023.06 - 至今
- 技术栈：Spring Cloud, Kubernetes, ElasticSearch
- 描述：
  负责支付网关的架构设计和开发。
  对接10+支付渠道，处理日均千万级交易。
- 亮点：
  * 系统可用性达到99.9%
  * 实现幂等性和分布式事务
  * 实时监控和告警系统

教育背景：
- XX大学 | 计算机科学与技术 | 本科 | 2018年毕业
"""

# ========== 示例JD ==========

SAMPLE_JD_TEXT = """
公司：某金融科技公司
职位：Senior Java Engineer
地点：北京
薪资范围：30k-50k

必须技能：
- 5年以上Java开发经验
- 精通Java基础，理解JVM原理
- 熟悉Spring Boot, Spring Cloud等微服务框架
- 熟悉Redis, Kafka等中间件
- 熟悉MySQL等关系型数据库
- 有分布式系统开发经验

加分技能：
- 熟悉ElasticSearch, ClickHouse等
- 有大数据处理经验
- 有金融行业经验
- 有团队管理经验

岗位职责：
1. 负责核心交易系统的后端开发
2. 参与系统架构设计和技术选型
3. 解决高并发、高可用场景下的技术问题
4. 指导初中级工程师，进行代码审查

经验要求：
- 本科及以上学历
- 5年以上Java开发经验
- 有大型分布式系统经验
"""

# ========== 边界测试数据 ==========

EMPTY_RESUME_TEXT = """
姓名：测试
工作经验：0年
"""

EMPTY_JD_TEXT = """
公司：测试公司
职位：测试职位
"""

MINIMAL_RESUME_TEXT = """
Java开发工程师，会Java和MySQL
"""

MINIMAL_JD_TEXT = """
招聘Java工程师，要求会Java
"""

# ========== 完全匹配的简历和JD ==========

PERFECT_MATCH_RESUME = """
Java开发工程师
技能：Java, Spring Boot, MySQL, Redis
"""

PERFECT_MATCH_JD = """
Java开发工程师招聘
要求：Java, Spring Boot, MySQL, Redis
"""

# ========== 完全不匹配的简历和JD ==========

NO_MATCH_RESUME = """
Python开发工程师
技能：Python, Django, PostgreSQL
"""

NO_MATCH_JD = """
Golang开发工程师招聘
要求：Go, Gin, MongoDB
"""

# ========== 多技能简历和JD ==========

MULTI_SKILL_RESUME = """
全栈工程师
技能：
- 后端：Java, Spring Boot, MySQL
- 前端：React, TypeScript
- 运维：Docker, K8s
"""

MULTI_SKILL_JD = """
后端工程师招聘
必须技能：
- Java, Spring, MySQL
- Redis, Kafka
加分技能：
- 微服务经验
- 高并发处理经验
"""
