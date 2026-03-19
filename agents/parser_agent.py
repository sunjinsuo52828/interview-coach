"""
ParserAgent - 解析Agent

负责解析简历、JD和Gap分析。
"""
from typing import Dict, Any, List
import json
import logging

from agents.base_agent import ToolEnabledAgent, BaseAgent
from config import settings
from models import (
    ParsedResume,
    ParsedJD,
    GapAnalysis,
    TechnicalSkills,
    Project,
    Education,
    MatchDetail,
)

logger = logging.getLogger(__name__)


class ParserAgent(ToolEnabledAgent):
    """解析Agent"""

    def __init__(self):
        super().__init__(name="ParserAgent")

    def _setup_tools(self):
        """设置工具"""
        self.register_tool("parse_resume", self.parse_resume)
        self.register_tool("parse_jd", self.parse_jd)
        self.register_tool("gap_analysis", self.gap_analysis)

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """获取System Prompt"""
        return """你是专业的简历和JD解析专家。你的任务是从非结构化文本中提取结构化信息。

解析规则：
1. 提取所有相关技术栈（语言、框架、中间件、数据库、DevOps）
2. 识别项目经验（项目名、角色、技术栈、亮点）
3. 识别JD中的技能要求（必须技能、加分技能）
4. 分析匹配度和差距

输出必须是有效的JSON格式。
"""

    def execute(self, action: str, context: Dict[str, Any]) -> Any:
        """执行动作"""
        if action == "parse_resume":
            return self.parse_resume(context.get("text", ""))
        elif action == "parse_jd":
            return self.parse_jd(context.get("text", ""))
        elif action == "gap_analysis":
            return self.gap_analysis(
                context.get("resume"),
                context.get("jd")
            )
        else:
            raise ValueError(f"Unknown action: {action}")

    # ========== 工具方法 ==========

    def parse_resume(self, text: str) -> ParsedResume:
        """
        解析简历文本（使用Chain of Thought深度分析）

        Args:
            text: 简历文本

        Returns:
            ParsedResume对象
        """
        prompt = f"""请深度解析以下简历，逐步思考并提取结构化信息。

简历内容：
{text}

请按以下步骤思考（Chain of Thought）：

**步骤1：候选人画像分析**
- 分析候选人的职业发展轨迹（从初级到高级的演进）
- 识别核心领域和专业方向
- 评估工作年限的真实性（考虑项目重叠、晋升时间）

**步骤2：技术栈深度分析**
- 区分"精通"、"熟练"、"了解"等不同层级
- 识别技术栈的关联性（如Java→Spring→微服务）
- 发现隐藏的技能（从项目描述中推断）

**步骤3：项目经验深度挖掘**
- 识别项目规模（团队大小、用户量、业务影响）
- 分析候选人的实际贡献（不只是参与，而是主导/核心）
- 提取可量化的成果（性能提升、成本降低、效率提高）
- 识别技术难点和解决方案

**步骤4：教育背景分析**
- 评估学历与职位的匹配度
- 识别持续学习的证据

基于以上分析，提取以下信息（JSON格式）：
{{
    "name": "姓名",
    "phone": "电话",
    "email": "邮箱",
    "experience_years": 工作年限(数字，精确到小数点后1位),
    "current_role": "当前职位（全称，包含级别）",
    "technical_skills": {{
        "languages": ["编程语言列表，按熟练度排序"],
        "frameworks": ["框架列表，按熟练度排序"],
        "middleware": ["中间件列表"],
        "databases": ["数据库列表"],
        "devops": ["DevOps工具列表"]
    }},
    "projects": [
        {{
            "name": "项目名",
            "role": "角色（具体：如Tech Lead/Senior Developer）",
            "duration": "时长",
            "tech_stack": ["技术栈，按重要程度排序"],
            "description": "描述（1-2句话概括项目目标和规模）",
            "highlights": ["亮点（具体可量化成果）"]
        }}
    ],
    "education": [
        {{
            "school": "学校",
            "degree": "学位",
            "major": "专业",
            "graduation_year": 年份(数字)
        }}
    ]
}}

只返回JSON，不要其他内容。
"""

        response = self.call_claude(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.3  # 低温度确保准确解析
        )

        try:
            # 清理可能的Markdown格式
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                # 移除markdown代码块标记
                parts = cleaned_response.split("```")
                if len(parts) >= 2:
                    cleaned_response = parts[1]
                    # 移除语言标识符 (如 "json")
                    if cleaned_response.startswith("json"):
                        cleaned_response = cleaned_response[4:]
                    elif cleaned_response.startswith("JSON"):
                        cleaned_response = cleaned_response[4:]
            cleaned_response = cleaned_response.strip()

            data = json.loads(cleaned_response)
            return self._parse_resume_data(data, text)
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"JSON解析失败: {e}, 响应: {response[:200]}")
            # 解析失败，返回空对象
            return ParsedResume(raw_text=text)

    def parse_jd(self, text: str) -> ParsedJD:
        """
        解析JD文本（使用Chain of Thought深度分析）

        Args:
            text: JD文本

        Returns:
            ParsedJD对象
        """
        prompt = f"""请深度解析以下JD（职位描述），逐步思考并提取结构化信息。

JD内容：
{text}

请按以下步骤思考（Chain of Thought）：

**步骤1：岗位定位分析**
- 识别岗位级别（Junior/Senior/Lead/VP等）
- 分析汇报线和团队规模
- 判断岗位性质（技术路线/管理路线/混合）

**步骤2：技能要求深度分析**
- 区分"必须"（硬性要求）和"加分"（软性要求）技能
- 识别技能的优先级（核心技能 vs 辅助技能）
- 发现隐含技能要求（从职责描述中推断）
- 分析技能组合（如"微服务"可能包含Docker/K8s/Service Mesh等）

**步骤3：职责与期望分析**
- 识别核心职责（日常做什么是核心）
- 分析业务领域和上下文
- 发现潜在挑战（从职责中推断工作难点）

**步骤4：匹配度关键因素**
- 识别哪些是"一票否决"的条件（如必须技能、最低经验）
- 识别哪些是"加分项"（可以弥补其他不足）

基于以上分析，提取以下信息（JSON格式）：
{{
    "company": "公司名",
    "position": "职位名称（完整，包含级别）",
    "location": "地点",
    "salary_range": "薪资范围",
    "required_skills": ["必须技能列表，按优先级排序"],
    "preferred_skills": ["加分技能列表，按优先级排序"],
    "min_experience": 最低工作年限(数字),
    "preferred_experience": 期望工作年限(数字),
    "responsibilities": ["岗位职责列表，按重要性排序"],
    "business_domain": "业务领域",
    "level": "岗位级别（具体：Senior/Lead/VP等）"
}}

只返回JSON，不要其他内容。
"""

        response = self.call_claude(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.3
        )

        try:
            # 清理可能的Markdown格式
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                parts = cleaned_response.split("```")
                if len(parts) >= 2:
                    cleaned_response = parts[1]
                    if cleaned_response.startswith("json"):
                        cleaned_response = cleaned_response[4:]
            cleaned_response = cleaned_response.strip()

            data = json.loads(cleaned_response)
            return self._parse_jd_data(data, text)
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"JD JSON解析失败: {e}, 响应: {response[:200]}")
            return ParsedJD(raw_text=text)

    def gap_analysis(
        self,
        resume: ParsedResume,
        jd: ParsedJD
    ) -> GapAnalysis:
        """
        Gap分析（使用Chain of Thought深度分析）

        Args:
            resume: 解析后的简历
            jd: 解析后的JD

        Returns:
            GapAnalysis对象
        """
        resume_skills = resume.technical_skills.to_list()
        jd_required = jd.required_skills
        jd_all = jd.get_all_skills()

        # 构建更丰富的上下文
        resume_summary = f"""
候选人: {resume.name}, {resume.experience_years}年经验
当前职位: {resume.current_role}
核心项目: {[p.name for p in resume.projects[:3]]}
技术栈: {resume_skills[:10]}
"""

        jd_summary = f"""
职位: {jd.position}
公司: {jd.company}
级别: {jd.level}
必须技能: {jd_required}
工作年限要求: {jd.min_experience}+年
核心职责: {jd.responsibilities[:3] if jd.responsibilities else []}
"""

        prompt = f"""请深度分析以下简历和JD的匹配度，逐步思考。

{resume_summary}

{jd_summary}

请按以下步骤思考（Chain of Thought）：

**步骤1：整体匹配度评估**
- 工作年限匹配：候选人{resume.experience_years}年 vs 要求{jd.min_experience}+年
- 职级匹配：{resume.current_role} vs {jd.level}
- 领域相关性：候选人的行业经验与JD业务领域的匹配度

**步骤2：技术栈深度对比**
- 直接匹配：简历中的技能与JD要求的直接对应
- 间接匹配：相关技能可迁移（如Spring→Spring Boot）
- 缺失分析：JD要求但简历未体现的技能
- 超预期：简历有但JD没要求的技能（加分项）

**步骤3：项目经验相关性**
- 项目规模：候选人的项目规模与JD期望的匹配度
- 技术深度：候选人是否展示了JD所需的技术深度
- 业务相似性：候选人项目经验与JD业务领域的相关性

**步骤4：潜在风险识别**
- 技能差距是否为核心关键技能
- 经验年限是否真实反映能力水平
- 职业发展轨迹是否与岗位匹配

**步骤5：面试策略建议**
- 重点考察哪些技术领域
- 深挖哪些项目经验
- 验证哪些软技能

基于以上分析，输出以下结果（JSON格式）：
{{
    "match_percentage": 匹配百分比(0-100的数字，综合考虑所有因素),
    "matched_items": ["简历满足的技能列表，包括直接和间接匹配"],
    "gap_items": ["JD要求但简历未体现的技能列表，标注是否为核心技能"],
    "bonus_items": ["简历有但JD没要求的技能列表"],
    "interview_focus": [
        "应该重点考察的具体领域（格式：领域名称-考察原因）",
        "例如：微服务架构-候选人项目提到但未深入说明技术选型和挑战"
    ],
    "match_details": {{
        "experience_match": {{"category": "经验匹配", "has_match": true/false, "notes": "具体分析"}},
        "technical_match": {{"category": "技术匹配", "has_match": true/false, "notes": "具体分析"}},
        "project_match": {{"category": "项目匹配", "has_match": true/false, "notes": "具体分析"}},
        "level_match": {{"category": "级别匹配", "has_match": true/false, "notes": "具体分析"}}
    }}
}}

只返回JSON，不要其他内容。
"""

        response = self.call_claude(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,  # 增加以支持更详细的CoT分析
            temperature=0.3
        )

        try:
            # 清理可能的Markdown格式
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                parts = cleaned_response.split("```")
                if len(parts) >= 2:
                    cleaned_response = parts[1]
                    if cleaned_response.startswith("json"):
                        cleaned_response = cleaned_response[4:]
            cleaned_response = cleaned_response.strip()

            data = json.loads(cleaned_response)
            return self._parse_gap_data(data)
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f"Gap分析JSON解析失败: {e}, 响应: {response[:200]}")
            return GapAnalysis()

    # ========== 辅助方法 ==========

    def _parse_resume_data(self, data: Dict, raw_text: str) -> ParsedResume:
        """解析简历数据

        Args:
            data: Claude返回的JSON数据
            raw_text: 原始文本

        Returns:
            ParsedResume对象
        """
        # 解析技术栈
        skills_data = data.get("technical_skills", {})
        technical_skills = TechnicalSkills(
            languages=skills_data.get("languages", []),
            frameworks=skills_data.get("frameworks", []),
            middleware=skills_data.get("middleware", []),
            databases=skills_data.get("databases", []),
            devops=skills_data.get("devops", []),
        )

        # 解析项目 - 带异常处理
        projects: List[Project] = []
        for i, p in enumerate(data.get("projects", [])):
            try:
                projects.append(Project(**p))
            except (TypeError, KeyError) as e:
                logger.warning(f"跳过第{i+1}个项目数据: {p}, 错误: {e}")

        # 解析教育 - 带异常处理
        education: List[Education] = []
        for i, e in enumerate(data.get("education", [])):
            try:
                education.append(Education(**e))
            except (TypeError, KeyError) as err:
                logger.warning(f"跳过第{i+1}个教育经历: {e}, 错误: {err}")

        return ParsedResume(
            name=data.get("name", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            experience_years=data.get("experience_years", 0),
            current_role=data.get("current_role", ""),
            technical_skills=technical_skills,
            projects=projects,
            education=education,
            raw_text=raw_text
        )

    def _parse_jd_data(self, data: Dict, raw_text: str) -> ParsedJD:
        """解析JD数据"""
        return ParsedJD(
            company=data.get("company", ""),
            position=data.get("position", ""),
            location=data.get("location", ""),
            salary_range=data.get("salary_range", ""),
            required_skills=data.get("required_skills", []),
            preferred_skills=data.get("preferred_skills", []),
            min_experience=data.get("min_experience", 0),
            preferred_experience=data.get("preferred_experience", 0),
            responsibilities=data.get("responsibilities", []),
            business_domain=data.get("business_domain", ""),
            level=data.get("level", ""),
            raw_text=raw_text
        )

    def _parse_gap_data(self, data: Dict) -> GapAnalysis:
        """解析Gap数据"""
        return GapAnalysis(
            match_percentage=data.get("match_percentage", 0) / 100,
            matched_items=data.get("matched_items", []),
            gap_items=data.get("gap_items", []),
            bonus_items=data.get("bonus_items", []),
            interview_focus=data.get("interview_focus", []),
            match_details={
                k: MatchDetail(**v) if isinstance(v, dict) else v
                for k, v in data.get("match_details", {}).items()
            }
        )


# ========== 便捷函数 ==========

def parse_resume(text: str) -> ParsedResume:
    """便捷函数：解析简历"""
    agent = ParserAgent()
    return agent.parse_resume(text)


def parse_jd(text: str) -> ParsedJD:
    """便捷函数：解析JD"""
    agent = ParserAgent()
    return agent.parse_jd(text)


def gap_analysis(resume: ParsedResume, jd: ParsedJD) -> GapAnalysis:
    """便捷函数：Gap分析"""
    agent = ParserAgent()
    return agent.gap_analysis(resume, jd)
