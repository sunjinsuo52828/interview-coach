"""
Interview Coach 数据模型

定义项目中使用的数据结构。
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


# ========== 枚举定义 ==========

class InterviewerLevel(Enum):
    """面试官级别"""
    JUNIOR_ENGINEER = "junior_engineer"
    SENIOR_ENGINEER = "senior_engineer"
    TECH_LEAD = "tech_lead"
    STAFF_ENGINEER = "staff_engineer"
    ARCHITECT = "architect"
    ENGINEERING_MANAGER = "engineering_manager"
    DIRECTOR = "director"
    VP_CTO = "vp_cto"
    HR = "hr"


class InterviewerStyle(Enum):
    """面试风格"""
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    CHALLENGING = "challenging"
    OPEN = "open"


class FocusArea(Enum):
    """考察重点"""
    TECHNICAL_BASICS = "technical_basics"
    SOURCE_CODE = "source_code"
    PROJECT_EXPERIENCE = "project_experience"
    SYSTEM_DESIGN = "system_design"
    ALGORITHM = "algorithm"
    BEHAVIORAL = "behavioral"
    BUSINESS = "business"
    CULTURE_FIT = "culture_fit"


class Difficulty(Enum):
    """难度级别"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class AnswerGrade(Enum):
    """评分等级"""
    A = "A"  # 优秀
    B = "B"  # 良好
    C = "C"  # 及格
    D = "D"  # 不及格


class Recommendation(Enum):
    """录用建议"""
    HIRE = "HIRE"
    NO_HIRE = "NO_HIRE"
    HIRE_WITH_CONDITIONS = "HIRE_WITH_CONDITIONS"


# ========== 解析相关模型 ==========

@dataclass
class TechnicalSkills:
    """技术栈"""
    languages: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    middleware: List[str] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    devops: List[str] = field(default_factory=list)

    def to_list(self) -> List[str]:
        """转换为列表"""
        return (
            self.languages +
            self.frameworks +
            self.middleware +
            self.databases +
            self.devops
        )


@dataclass
class Project:
    """项目经验"""
    name: str = ""
    role: str = ""
    duration: str = ""
    tech_stack: List[str] = field(default_factory=list)
    description: str = ""
    highlights: List[str] = field(default_factory=list)


@dataclass
class Education:
    """教育背景"""
    school: str = ""
    degree: str = ""
    major: str = ""
    graduation_year: int = 0


@dataclass
class ParsedResume:
    """解析后的简历"""
    # 基本信息
    name: str = ""
    phone: str = ""
    email: str = ""
    experience_years: int = 0
    current_role: str = ""

    # 技术栈
    technical_skills: TechnicalSkills = field(default_factory=TechnicalSkills)

    # 项目经验
    projects: List[Project] = field(default_factory=list)

    # 教育背景
    education: List[Education] = field(default_factory=list)

    # 原始文本
    raw_text: str = ""

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "experience_years": self.experience_years,
            "current_role": self.current_role,
            "skills": self.technical_skills.to_list(),
            "projects": [p.name for p in self.projects],
        }


@dataclass
class ParsedJD:
    """解析后的JD"""
    # 基本信息
    company: str = ""
    position: str = ""
    location: str = ""
    salary_range: str = ""

    # 技能要求
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)

    # 经验要求
    min_experience: int = 0
    preferred_experience: int = 0

    # 岗位职责
    responsibilities: List[str] = field(default_factory=list)

    # 业务领域
    business_domain: str = ""

    # 岗位级别
    level: str = ""

    # 原始文本
    raw_text: str = ""

    def get_all_skills(self) -> List[str]:
        """获取所有技能"""
        return list(set(self.required_skills + self.preferred_skills))


@dataclass
class MatchDetail:
    """匹配详情"""
    category: str = ""
    required: str = ""
    has_match: bool = False
    match_score: float = 0.0
    notes: str = ""  # 匹配分析说明


@dataclass
class GapAnalysis:
    """Gap分析结果"""
    # 匹配度
    match_percentage: float = 0.0

    # 匹配项
    matched_items: List[str] = field(default_factory=list)

    # 差距项
    gap_items: List[str] = field(default_factory=list)

    # 加分项
    bonus_items: List[str] = field(default_factory=list)

    # 面试重点建议
    interview_focus: List[str] = field(default_factory=list)

    # 匹配详情
    match_details: Dict[str, MatchDetail] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "match_percentage": self.match_percentage,
            "matched_items": self.matched_items,
            "gap_items": self.gap_items,
            "bonus_items": self.bonus_items,
            "interview_focus": self.interview_focus,
            "match_details": {
                k: {
                    "category": v.category,
                    "required": v.required,
                    "has_match": v.has_match,
                    "match_score": v.match_score,
                    "notes": v.notes,
                }
                for k, v in self.match_details.items()
            }
        }


# ========== 面试相关模型 ==========

@dataclass
class InterviewConfig:
    """面试配置"""
    # 面试官配置
    interviewer_level: str = InterviewerLevel.SENIOR_ENGINEER.value
    interviewer_style: str = InterviewerStyle.PROFESSIONAL.value
    custom_title: Optional[str] = None

    # 考察重点
    focus_areas: List[str] = field(default_factory=lambda: [
        FocusArea.TECHNICAL_BASICS.value,
        FocusArea.PROJECT_EXPERIENCE.value
    ])

    # 面试参数
    duration: int = 45  # 分钟
    language: str = "zh"  # zh, en, mixed

    # 难度
    difficulty: str = Difficulty.MEDIUM.value


@dataclass
class ConversationTurn:
    """单轮对话"""
    turn_number: int = 0  # 第几轮对话
    turn_id: str = ""
    timestamp: str = ""

    # 问题
    question_id: str = ""
    question_text: str = ""
    question_domain: str = ""

    # 回答
    user_answer: str = ""

    # 评估
    score: str = AnswerGrade.B.value
    follow_up_count: int = 0
    evaluation_notes: List[str] = field(default_factory=list)


@dataclass
class InterviewState:
    """面试状态"""
    session_id: str = ""
    config: InterviewConfig = field(default_factory=InterviewConfig)
    resume: ParsedResume = field(default_factory=ParsedResume)
    jd: ParsedJD = field(default_factory=ParsedJD)
    gap: GapAnalysis = field(default_factory=GapAnalysis)

    # 进度
    started_at: str = ""
    current_turn: int = 0
    estimated_total_turns: int = 0
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
    summary: str = ""


# ========== 题目相关模型 ==========

@dataclass
class Question:
    """面试题"""
    id: str = ""
    domain: str = ""
    subdomain: str = ""
    difficulty: str = Difficulty.MEDIUM.value

    question: str = ""
    reference_answer: str = ""
    key_points: List[str] = field(default_factory=list)

    follow_ups: List[str] = field(default_factory=list)

    # 适用场景
    suitable_levels: List[str] = field(default_factory=list)
    suitable_rounds: List[str] = field(default_factory=list)

    # 元数据
    tags: List[str] = field(default_factory=list)
    created_at: str = ""


# ========== 评估相关模型 ==========

@dataclass
class DimensionScore:
    """维度评分"""
    dimension: str = ""
    score: float = 0.0  # 0-100
    grade: str = AnswerGrade.B.value
    evidence: List[str] = field(default_factory=list)


@dataclass
class QuestionResult:
    """单题结果"""
    question_id: str = ""
    question_text: str = ""
    domain: str = ""
    user_answer: str = ""
    score: str = AnswerGrade.B.value
    evaluator_notes: str = ""
    follow_ups: List[str] = field(default_factory=list)


@dataclass
class InterviewReport:
    """面试评估报告"""
    session_id: str = ""
    generated_at: str = ""

    # 总体评分
    overall_score: float = 0.0
    overall_grade: str = AnswerGrade.B.value
    recommendation: str = Recommendation.HIRE.value

    # 维度评分
    dimension_scores: Dict[str, DimensionScore] = field(default_factory=dict)

    # 题目详情
    question_results: List[QuestionResult] = field(default_factory=list)

    # 优势与弱项
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)

    # 学习建议
    learning_suggestions: List[str] = field(default_factory=list)
    recommended_resources: List[str] = field(default_factory=list)


# ========== Agent相关模型 ==========

@dataclass
class AgentMessage:
    """Agent消息"""
    role: str = ""  # "user", "assistant", "system"
    content: str = ""
    timestamp: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentThought:
    """Agent思考过程（ReAct）"""
    thought: str = ""
    action: str = ""
    action_input: Dict[str, Any] = field(default_factory=dict)
    observation: str = ""
    timestamp: str = ""


@dataclass
class AgentResponse:
    """Agent响应"""
    content: str = ""
    thoughts: List[AgentThought] = field(default_factory=list)
    tool_calls: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# ========== 知识库相关模型 ==========

@dataclass
class KnowledgeChunk:
    """知识片段"""
    id: str = ""
    content: str = ""
    domain: str = ""
    topic: str = ""
    source: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
