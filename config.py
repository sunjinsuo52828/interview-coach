"""
Interview Coach 配置管理
"""
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ========== GLM API ==========
    glm_api_key: str
    glm_model: str = "glm-4-air"  # 使用GLM-4.5-air (106B参数，深度分析更强)

    # ========== 应用配置 ==========
    app_env: str = "development"
    app_port: int = 8501
    app_log_level: str = "DEBUG"

    # ========== 数据存储 ==========
    data_dir: Path = Path("./data")
    interview_dir: Path = Path("./data/interviews")
    question_bank_dir: Path = Path("./data/question_bank")
    knowledge_base_dir: Path = Path("./data/knowledge_base")
    chroma_db_dir: Path = Path("./data/chroma_db")

    # ========== Agent配置 ==========
    max_context_length: int = 180000
    summary_interval: int = 10
    max_follow_up_depth: int = 3

    # ========== 默认配置 ==========
    default_interviewer_level: str = "senior_engineer"
    default_interview_duration: int = 45
    default_language: str = "zh"

    @property
    def is_development(self) -> bool:
        """是否开发环境"""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """是否生产环境"""
        return self.app_env == "production"


# ========== 面试官角色定义 ==========
INTERVIEWER_LEVELS = {
    "junior_engineer": "初级工程师，第一次当面试官，提问偏基础，语气友好",
    "senior_engineer": "5年经验的高级工程师，关注代码质量和工程实践",
    "tech_lead": "技术负责人，关注技术深度和项目管理能力，会深挖项目细节",
    "staff_engineer": "技术专家，关注系统级思维和技术影响力，提问偏原理和设计",
    "architect": "首席架构师，关注架构设计、技术选型权衡、非功能需求",
    "engineering_manager": "工程经理，兼顾技术能力和团队管理，会问带人经验",
    "director": "技术总监，关注技术战略、组织能力、业务理解",
    "vp_cto": "VP/CTO，关注大局观、文化匹配、职业规划、领导力",
    "hr": "HR，关注文化匹配、团队协作、薪资期望、稳定性",
}

# ========== 面试风格定义 ==========
INTERVIEWER_STYLES = {
    "friendly": "面试风格轻松友好，鼓励候选人放松表达",
    "professional": "面试风格专业严谨，追求准确和深度",
    "challenging": "面试风格有一定压力，会挑战候选人的回答，考察抗压能力",
    "open": "面试风格开放探讨，没有标准答案，关注思维过程",
}

# ========== 考察重点定义 ============
FOCUS_AREAS = {
    "technical_basics": "技术基础（语言特性、数据结构、常用API）",
    "source_code": "源码原理（框架底层实现、设计模式）",
    "project_experience": "项目经验（STAR法则深挖）",
    "system_design": "系统设计（架构设计、容量规划、高可用）",
    "algorithm": "算法编程（手写代码、复杂度分析）",
    "behavioral": "行为面试（团队协作、冲突处理、领导力）",
    "business": "业务理解（行业知识、产品思维）",
    "culture_fit": "文化匹配（价值观、工作方式、职业规划）",
}

# ========== 题库领域定义 ==========
QUESTION_DOMAINS = {
    "java_core": {"name": "Java核心", "subdomains": ["集合", "并发", "IO/NIO", "JVM"]},
    "spring": {"name": "Spring框架", "subdomains": ["Spring Core", "Spring Boot", "Spring Cloud"]},
    "database": {"name": "数据库", "subdomains": ["MySQL", "Redis", "SQL优化"]},
    "middleware": {"name": "中间件", "subdomains": ["Kafka", "RabbitMQ", "Elasticsearch"]},
    "distributed": {"name": "分布式系统", "subdomains": ["CAP", "一致性", "分布式锁"]},
    "system_design": {"name": "系统设计", "subdomains": ["高并发", "高可用", "架构设计"]},
    "algorithm": {"name": "算法编程", "subdomains": ["数据结构", "算法", "复杂度"]},
    "behavioral": {"name": "行为面试", "subdomains": ["团队协作", "冲突处理", "领导力"]},
}

# ========== 追问策略定义 ============
FOLLOW_UP_STRATEGIES = {
    "complete_correct": {
        "type": "level_up",
        "action": "升维追问 - 考察更高难度或更广视角",
        "depth_questions": [
            "底层原理：那它的底层实现原理是怎样的？",
            "对比分析：和其他方案相比，优劣是什么？",
            "场景扩展：在XX场景下会遇到什么问题？如何解决？",
            "边界条件：什么情况下这个方案会失效？",
            "性能优化：如果要处理10倍流量，如何优化？"
        ],
        "domain_specific": {
            "technical_basics": [
                "概念清楚了，那说说实际项目中的应用场景？",
                "这个技术选型的优缺点是什么？什么场景用最合适？"
            ],
            "source_code": [
                "源码层面，它是怎么实现的？关键设计在哪里？",
                "这个框架的设计模式是什么？为什么要这样设计？"
            ],
            "project_experience": [
                "这个项目中最大的技术挑战是什么？",
                "如果重新设计，你会怎么改进？"
            ],
            "system_design": [
                "这个方案的瓶颈在哪里？如何扩展？",
                "如果服务挂了，容灾方案是什么？"
            ]
        },
        "examples": [
            "HashMap讲得很好，那ConcurrentHashMap的源码实现了解吗？",
            "单机Redis理解了，那Redis Cluster的架构设计呢？",
            "SpringBoot自动配置原理讲一下？"
        ]
    },
    "partial_correct": {
        "type": "guided_completion",
        "action": "定向补全 - 引导补充缺失要点",
        "prompts": [
            "你提到了A，那B呢？",
            "还有其他考虑因素吗？",
            "这个方案的缺点是什么？",
            "如果XX情况发生，会怎么样？"
        ],
        "examples": [
            "你提到了数组+链表，跳表了解吗？",
            "MySQL索引讲了一些，那索引失效的场景呢？",
            "提到微服务，那服务间通信的几种方式各有什么特点？"
        ]
    },
    "correct_but_vague": {
        "type": "detail_drill",
        "action": "细节深挖 - 要求举例/给数据/讲场景",
        "prompts": [
            "能具体说说在你的项目中是怎么做的吗？",
            "这个数据量大概多少？QPS多少？",
            "遇到的最大问题是什么？怎么解决的？",
            "你的具体贡献是什么？"
        ],
        "examples": [
            "你说做过性能优化，具体优化了多少？怎么做的？",
            "提到微服务改造，具体的拆分策略是什么？",
            "这个项目的团队规模多大？你的角色是什么？"
        ]
    },
    "wrong": {
        "type": "corrective_guidance",
        "action": "纠正引导 - 给提示，再给一次机会",
        "prompts": [
            "思路不太对，提示一下：考虑并发场景...",
            "再想想：如果多个客户端同时操作会怎样？",
            "这个方案有个问题：数据一致性怎么保证？"
        ],
        "examples": [
            "不对，HashMap不是线程安全的，多线程场景会有问题",
            "TCP握手是三次，但断开是四次，原因是什么？",
            "这里考虑得不够全面，再想想边界情况..."
        ]
    },
    "no_answer": {
        "type": "provide_answer",
        "action": "给参考答案 + 标记弱项 + 下一题",
        "prompts": [
            "没关系，这道题考察的是...",
            "这个知识点确实比较冷门，简单说一下：...",
            "看来这块不太熟悉，我们换一个话题"
        ],
        "examples": [
            "红黑树的插入过程是这样的...建议你回头了解一下",
            "分布式事务有几种方案：XA、TCC、本地消息表...建议重点学习",
            "CAP理论在分布式系统中的应用..."
        ]
    }
}

# ========== 技术领域追问模板 ==========
TECHNICAL_FOLLOW_UP_TEMPLATES = {
    "Java": {
        "Collection": ["ArrayList vs LinkedList源码差异？", "ConcurrentHashMap实现原理？"],
        "JVM": ["GC算法了解吗？", "OOM的场景有哪些？", "类加载机制是怎样的？"],
        "Concurrency": ["线程池参数如何配置？", "ThreadLocal原理和应用？", "volatile和synchronized区别？"]
    },
    "Spring": {
        "Core": ["IOC容器启动流程？", "AOP实现原理？", "Bean生命周期？"],
        "Boot": ["自动配置原理？", "starter实现方式？", "内嵌Tomcat原理？"],
        "Cloud": ["服务发现怎么实现？", "配置中心如何工作？", "网关的作用是什么？"]
    },
    "Database": {
        "MySQL": ["索引实现原理？", "事务隔离级别？", "MVCC机制？", "锁的类型和区别？"],
        "Redis": ["数据结构底层实现？", "持久化机制？", "集群方案？", "缓存穿透/击穿/雪崩？"]
    },
    "Middleware": {
        "Kafka": ["高吞吐量原理？", " Exactly Once语义？", "Rebalance机制？"],
        "MQ": ["消息丢失怎么解决？", "顺序消费怎么保证？", "消息积压怎么处理？"]
    },
    "Architecture": {
        "HighConcurrency": ["限流方案？", "降级策略？", "熔断机制？"],
        "HighAvailability": ["主从切换？", "数据同步？", "灾备方案？"],
        "Microservices": ["服务拆分原则？", "分布式事务？", "服务网格？"]
    }
}


# ========== 全局设置实例 ============
settings = Settings()
