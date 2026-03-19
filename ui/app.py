"""
Interview Coach - Streamlit UI

面试模拟器的Web界面。

使用InterviewOrchestrator进行统一的状态管理和Agent路由。
"""
import streamlit as st
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    settings,
    INTERVIEWER_LEVELS,
    INTERVIEWER_STYLES,
    FOCUS_AREAS,
)
from agents import InterviewOrchestrator, create_orchestrator
from models import InterviewConfig


# ========== 页面配置 ==========
st.set_page_config(
    page_title="Interview Coach",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ========== 初始化Session State ==========
def init_session_state():
    """初始化Session State"""
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = create_orchestrator()

    if "stage" not in st.session_state:
        st.session_state.stage = "setup"  # setup, interview, report

    if "messages" not in st.session_state:
        st.session_state.messages = []  # 对话消息历史

    if "current_response" not in st.session_state:
        st.session_state.current_response = None

    if "error" not in st.session_state:
        st.session_state.error = None


# ========== API Key 检查 ==========
def check_api_key():
    """检查API密钥是否配置"""
    if not settings.glm_api_key:
        st.error("""
        ## ⚠️ API密钥未配置

        请在 **Streamlit Cloud → Settings → Secrets** 中添加以下环境变量：

        ```
        GLM_API_KEY=your_api_key_here
        ```

        配置完成后，请刷新页面。
        """)
        st.stop()


check_api_key()


init_session_state()


# ========== 侧边栏 ==========
def render_sidebar():
    """渲染侧边栏"""
    st.sidebar.title("🤖 Interview Coach")

    # 阶段指示
    stages = {
        "setup": "📝 配置",
        "interview": "💬 面试",
        "report": "📊 报告"
    }

    current_stage = st.session_state.stage
    for stage_key, stage_name in stages.items():
        if stage_key == current_stage:
            st.sidebar.markdown(f"**➤ {stage_name}**")
        else:
            st.sidebar.markdown(f"  {stage_name}")

    st.sidebar.markdown("---")

    # 显示当前状态
    state = st.session_state.orchestrator.get_state()
    if state:
        st.sidebar.subheader("当前状态")
        status_items = [
            ("简历解析", state["is_resume_parsed"]),
            ("JD解析", state["is_jd_parsed"]),
            ("Gap分析", state["has_gap_analysis"]),
            ("面试中", state["interview_started"]),
            ("已完成", state["has_report"]),
        ]
        for label, value in status_items:
            icon = "✅" if value else "⭕"
            st.sidebar.markdown(f"{icon} {label}")

    # 对话历史
    if st.session_state.stage == "interview" and state["conversation_turns"] > 0:
        st.sidebar.markdown("---")
        st.sidebar.metric("对话轮次", state["conversation_turns"])

    # 重置按钮
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 重新开始", use_container_width=True):
        # 重置orchestrator
        st.session_state.orchestrator.reset()
        st.session_state.messages = []
        st.session_state.current_response = None
        st.session_state.stage = "setup"
        st.rerun()


# ========== 页面：配置 ==========
def render_setup_page():
    """渲染配置页面"""
    st.header("📝 面试配置")

    # 使用Tab分步骤
    tab1, tab2, tab3 = st.tabs(["1. 简历 & JD", "2. Gap分析", "3. 面试配置"])

    with tab1:
        st.subheader("粘贴简历")

        # 使用 session_state 保存简历输入
        if "resume_input_text" not in st.session_state:
            st.session_state.resume_input_text = ""

        resume_text = st.text_area(
            "简历内容",
            placeholder="请粘贴简历文本内容...",
            height=400,
            key="resume_input_area",
            value=st.session_state.resume_input_text,
            max_chars=10000
        )

        # 更新 session_state
        if resume_text != st.session_state.resume_input_text:
            st.session_state.resume_input_text = resume_text

        st.subheader("粘贴JD")

        # 使用 session_state 保存JD输入
        if "jd_input_text" not in st.session_state:
            st.session_state.jd_input_text = ""

        jd_text = st.text_area(
            "JD内容",
            placeholder="请粘贴职位描述...",
            height=400,
            key="jd_input_area",
            value=st.session_state.jd_input_text,
            max_chars=10000
        )

        # 更新 session_state
        if jd_text != st.session_state.jd_input_text:
            st.session_state.jd_input_text = jd_text

        # 统一解析按钮
        st.markdown("---")
        if st.button("🚀 开始智能解析", type="primary", use_container_width=True):
            if not resume_text or not jd_text:
                st.warning("请先同时粘贴简历和JD内容")
            else:
                with st.spinner("正在深度分析简历和JD，请稍候（可能需要20-30秒）..."):
                    # 同时更新简历和JD
                    st.session_state.orchestrator.update_resume_text(resume_text)
                    st.session_state.orchestrator.update_jd_text(jd_text)

                    # 执行解析（会自动进行Gap分析）
                    result = st.session_state.orchestrator.route_and_execute()

                    if result.get("status") == "success" and result.get("agent") == "parser":
                        st.success("✅ 解析完成！")

                        # 显示解析结果摘要
                        col1, col2, col3 = st.columns(3)

                        # 从orchestrator.state直接获取解析结果
                        state = st.session_state.orchestrator.state
                        resume = state.resume
                        jd = state.jd
                        gap = state.gap_analysis

                        with col1:
                            if resume and resume.name:
                                st.metric("候选人", resume.name)
                        with col2:
                            if jd and jd.position:
                                st.metric("职位", jd.position)
                        with col3:
                            if gap:
                                st.metric("匹配度", f"{gap.match_percentage*100:.0f}%")

                        # 显示详细结果
                        with st.expander("📄 查看简历解析详情", expanded=False):
                            if resume:
                                st.json({
                                    "name": resume.name,
                                    "phone": resume.phone,
                                    "email": resume.email,
                                    "experience_years": resume.experience_years,
                                    "current_role": resume.current_role,
                                    "technical_skills": {
                                        "languages": resume.technical_skills.languages,
                                        "frameworks": resume.technical_skills.frameworks,
                                        "middleware": resume.technical_skills.middleware,
                                        "databases": resume.technical_skills.databases,
                                        "devops": resume.technical_skills.devops,
                                    },
                                    "projects": [
                                        {
                                            "name": p.name,
                                            "role": p.role,
                                            "duration": p.duration,
                                            "tech_stack": p.tech_stack,
                                            "description": p.description,
                                            "highlights": p.highlights,
                                        }
                                        for p in resume.projects
                                    ],
                                    "education": [
                                        {
                                            "school": e.school,
                                            "degree": e.degree,
                                            "major": e.major,
                                            "graduation_year": e.graduation_year,
                                        }
                                        for e in resume.education
                                    ]
                                })

                        with st.expander("📋 查看JD解析详情", expanded=False):
                            if jd:
                                st.json({
                                    "company": jd.company,
                                    "position": jd.position,
                                    "location": jd.location,
                                    "salary_range": jd.salary_range,
                                    "required_skills": jd.required_skills,
                                    "preferred_skills": jd.preferred_skills,
                                    "min_experience": jd.min_experience,
                                    "preferred_experience": jd.preferred_experience,
                                    "responsibilities": jd.responsibilities,
                                    "business_domain": jd.business_domain,
                                    "level": jd.level,
                                })

                        # Gap分析完成提示
                        if state.has_gap_analysis:
                            st.info("📊 Gap分析已完成！请切换到「Gap分析」标签页查看详细匹配情况")

                            # 在当前页面也显示Gap分析摘要
                            with st.expander("🔍 查看Gap分析详情", expanded=False):
                                if gap:
                                    col1, col2, col3 = st.columns(3)
                                    col1.metric("匹配度", f"{gap.match_percentage*100:.1f}%")
                                    col2.metric("匹配项", len(gap.matched_items))
                                    col3.metric("差距项", len(gap.gap_items))

                                    st.markdown("---")
                                    if gap.matched_items:
                                        st.markdown("✅ **匹配项**")
                                    for item in gap.matched_items[:10]:
                                        st.markdown(f"- {item}")

                                    if gap.gap_items:
                                        st.markdown("⚠️ **差距项（重点考察）**")
                                    for item in gap.gap_items[:10]:
                                        st.markdown(f"- {item}")

                                    if gap.interview_focus:
                                        st.markdown("---")
                                        st.markdown("🎯 **建议考察重点**")
                                    for item in gap.interview_focus[:10]:
                                        st.markdown(f"- {item}")

                    elif result.get("status") == "error":
                        st.error(result.get("message", "解析失败"))
                        with st.expander("如何配置GLM API密钥"):
                            st.markdown("""
                            1. 打开 `.env` 文件
                            2. 设置 `GLM_API_KEY=your_actual_api_key`
                            3. 从 https://open.bigmodel.cn/ 获取API密钥
                            4. 重启应用
                            """)
                    else:
                        st.error(f"解析失败: {result.get('message', '未知错误')}")

    with tab2:
        st.subheader("Gap分析")

        # 检查状态
        state = st.session_state.orchestrator.get_state()
        can_do_gap = state["is_resume_parsed"] and state["is_jd_parsed"]
        has_gap = state["has_gap_analysis"]

        # 如果Gap分析已完成，直接显示结果
        if has_gap:
            st.success("✅ Gap分析已完成！")

            # 从orchestrator获取Gap分析结果
            gap = st.session_state.orchestrator.state.gap_analysis
            if gap:
                col1, col2, col3 = st.columns(3)
                col1.metric("匹配度", f"{gap.match_percentage*100:.1f}%")
                col2.metric("匹配项", len(gap.matched_items))
                col3.metric("差距项", len(gap.gap_items))

                st.markdown("---")

                # 显示匹配项
                if gap.matched_items:
                    st.markdown("✅ **匹配项**")
                    for item in gap.matched_items[:10]:
                        st.markdown(f"- {item}")

                # 显示差距项
                if gap.gap_items:
                    st.markdown("⚠️ **差距项（重点考察）**")
                    for item in gap.gap_items[:10]:
                        st.markdown(f"- {item}")

                # 显示考察重点
                if gap.interview_focus:
                    st.markdown("---")
                    st.markdown("🎯 **建议考察重点**")
                    for item in gap.interview_focus[:10]:
                        st.markdown(f"- {item}")

        elif can_do_gap:
            if st.button("开始Gap分析", use_container_width=True, type="primary"):
                result = st.session_state.orchestrator.route_and_execute()

                if result.get("status") == "success" and "gap_analysis" in result:
                    gap = result["gap_analysis"]

                    col1, col2, col3 = st.columns(3)
                    col1.metric("匹配度", f"{gap['match_percentage']*100:.1f}%")
                    col2.metric("匹配项", len(result.get("matched_items", [])))
                    col3.metric("差距项", len(result.get("gap_items", [])))

                    st.markdown("---")

                    # 显示匹配项
                    if result.get("matched_items"):
                        st.markdown("✅ **匹配项**")
                        for item in result["matched_items"][:10]:
                            st.markdown(f"- {item}")

                    # 显示差距项
                    if result.get("gap_items"):
                        st.markdown("⚠️ **差距项（重点考察）**")
                        for item in result["gap_items"][:10]:
                            st.markdown(f"- {item}")
                else:
                    st.warning("Gap分析未完成，请重试")
        else:
            st.info("👈 请先在[简历 & JD]标签页解析简历和JD")

    with tab3:
        st.subheader("面试配置")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**面试官级别**")
            level = st.selectbox(
                "选择面试官级别",
                options=list(INTERVIEWER_LEVELS.keys()),
                format_func=lambda x: INTERVIEWER_LEVELS[x].split("，")[0],
                index=1,
                key="interviewer_level"
            )

            st.markdown("**面试风格**")
            style = st.selectbox(
                "选择面试风格",
                options=list(INTERVIEWER_STYLES.keys()),
                format_func=lambda x: {
                    "friendly": "😊 友好轻松",
                    "professional": "👔 专业严谨",
                    "challenging": "💪 高压挑战",
                    "open": "🌟 开放探讨"
                }.get(x, x),
                index=1,
                key="interviewer_style"
            )

        with col2:
            st.markdown("**考察重点**")
            focus = st.multiselect(
                "选择考察重点（可多选）",
                options=list(FOCUS_AREAS.keys()),
                format_func=lambda x: FOCUS_AREAS[x],
                default=["technical_basics", "project_experience"],
                key="focus_areas"
            )

            st.markdown("**面试参数**")
            col2_1, col2_2 = st.columns(2)
            duration = col2_1.slider("时长（分钟）", 15, 90, 45, key="duration")
            language = col2_2.selectbox("语言", ["zh", "en", "mixed"],
                format_func={"zh": "中文", "en": "English", "mixed": "混合"}.get,
                index=0,
                key="language")

        # 创建配置
        config = InterviewConfig(
            interviewer_level=level,
            interviewer_style=style,
            focus_areas=focus,
            duration=duration,
            language=language
        )

        # 保存配置到orchestrator
        st.session_state.orchestrator.update_config(config)

        st.markdown("---")

        # 检查是否可以开始面试
        state = st.session_state.orchestrator.get_state()
        can_start = (
            state["is_resume_parsed"]
            and state["is_jd_parsed"]
            and state["has_gap_analysis"]
            and len(focus) > 0
        )

        if can_start:
            if st.button("🚀 开始面试", type="primary", use_container_width=True):
                st.session_state.stage = "interview"
                st.rerun()
        else:
            missing = []
            if not state["is_resume_parsed"]:
                missing.append("解析简历")
            if not state["is_jd_parsed"]:
                missing.append("解析JD")
            if not state["has_gap_analysis"]:
                missing.append("完成Gap分析")
            if len(focus) == 0:
                missing.append("选择考察重点")

            st.warning(f"请完成: {', '.join(missing)}")


# ========== 页面：面试 ==========
def render_interview_page():
    """渲染面试页面"""
    st.header("💬 面试进行中")

    orchestrator = st.session_state.orchestrator

    # 显示对话历史
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 用户输入
    state = orchestrator.get_state()
    if not state["interview_ended"]:
        user_input = st.chat_input("请回答...")

        if user_input:
            # 显示用户消息
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })

            # 获取路由和执行
            result = orchestrator.route_and_execute(user_input)

            # 显示响应
            if result.get("status") == "success" and result.get("agent") == "interviewer":
                response = result.get("response", "")

                with st.chat_message("assistant"):
                    st.markdown(response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

                # 检查是否结束
                if result.get("interview_ended"):
                    st.success("面试已结束！点击下方按钮生成评估报告。")
                    if st.button("📊 生成评估报告", type="primary", key="gen_report_ended"):
                        st.session_state.stage = "report"
                        st.rerun()

            elif result.get("status") == "waiting":
                st.info(result.get("message", "等待输入..."))
            else:
                st.error(f"处理失败: {result.get('message', '未知错误')}")

    else:
        st.info("面试已结束，请生成评估报告。")
        if st.button("📊 生成评估报告", type="primary", key="gen_report_final"):
            st.session_state.stage = "report"
            st.rerun()

    # 侧边栏信息
    if state.get("conversation_turns", 0) > 0:
        with st.sidebar:
            st.markdown("---")
            st.subheader("对话统计")
            st.metric("轮次", state["conversation_turns"])

            if state.get("has_gap_analysis"):
                gap = orchestrator.state.gap_analysis
                if gap and gap.gap_items:
                    st.markdown("**重点考察**")
                    for item in gap.gap_items[:5]:
                        st.markdown(f"- {item}")


# ========== 页面：报告 ==========
def render_report_page():
    """渲染报告页面"""
    st.header("📊 面试评估报告")

    orchestrator = st.session_state.orchestrator

    # 生成报告
    if not orchestrator.state.has_report:
        with st.spinner("生成报告中..."):
            result = orchestrator.route_and_execute()

            if result.get("status") == "success" and result.get("agent") == "evaluator":
                st.success("✅ 报告生成完成！")
            else:
                st.error("报告生成失败")
                st.markdown("---")
                if st.button("返回配置页面", use_container_width=True):
                    st.session_state.stage = "setup"
                    st.rerun()
                return

    report = orchestrator.state.report

    if report:
        # 总体评分
        col1, col2, col3 = st.columns(3)
        col1.metric("总体评分", f"{report.overall_score:.1f}")
        col2.metric("等级", report.overall_grade)
        col3.metric("录用建议", _format_recommendation(report.recommendation))

        st.markdown("---")

        # 维度评分
        st.subheader("维度评分")
        if report.dimension_scores:
            cols = st.columns(len(report.dimension_scores))
            for i, (dim, score) in enumerate(report.dimension_scores.items()):
                with cols[i]:
                    st.metric(
                        _format_dimension(dim),
                        f"{score.score:.0f}",
                        delta=f"等级: {score.grade}"
                    )

        st.markdown("---")

        # 优势与弱项
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("✅ 优势")
            for strength in report.strengths:
                st.markdown(f"- {strength}")

        with col2:
            st.subheader("⚠️ 待改进")
            for weakness in report.weaknesses:
                st.markdown(f"- {weakness}")

        st.markdown("---")

        # 学习建议
        if report.learning_suggestions:
            st.subheader("💡 学习建议")
            for suggestion in report.learning_suggestions:
                st.markdown(f"- {suggestion}")

        # 推荐资源
        if report.recommended_resources:
            st.subheader("📚 推荐资源")
            for resource in report.recommended_resources:
                st.markdown(f"- {resource}")

        st.markdown("---")

        # 操作按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 复制报告", use_container_width=True):
                report_text = _format_report_text(report)
                st.text_area("报告文本", report_text, height=300)
                st.success("已生成报告文本，可复制")

        with col2:
            if st.button("🔄 重新面试", use_container_width=True):
                # 重置并返回配置页面
                orchestrator.reset()
                st.session_state.messages = []
                st.session_state.stage = "setup"
                st.rerun()
    else:
        st.warning("报告未生成，请重试")
        if st.button("返回面试页面", use_container_width=True):
            st.session_state.stage = "interview"
            st.rerun()


# ========== 辅助函数 ==========
def _format_recommendation(rec: str) -> str:
    """格式化录用建议"""
    return {
        "HIRE": "✅ 录用",
        "NO_HIRE": "❌ 不录用",
        "HIRE_WITH_CONDITIONS": "⚠️ 条件录用"
    }.get(rec, rec)


def _format_dimension(dim: str) -> str:
    """格式化维度名称"""
    return {
        "technical_depth": "技术深度",
        "project_experience": "项目经验",
        "problem_solving": "问题解决",
        "communication": "沟通表达",
        "learning_ability": "学习能力"
    }.get(dim, dim)


def _format_report_text(report) -> str:
    """格式化报告为文本"""
    lines = [
        "# 面试评估报告",
        f"生成时间：{report.generated_at}",
        "",
        "## 总体评分",
        f"- 评分：{report.overall_score:.1f}",
        f"- 等级：{report.overall_grade}",
        f"- 录用建议：{_format_recommendation(report.recommendation)}",
        "",
        "## 维度评分"
    ]

    for dim, score in report.dimension_scores.items():
        lines.append(f"- {_format_dimension(dim)}：{score.score:.0f} ({score.grade})")

    lines.extend([
        "",
        "## 优势"
    ])
    lines.extend([f"- {s}" for s in report.strengths])

    lines.extend([
        "",
        "## 待改进"
    ])
    lines.extend([f"- {w}" for w in report.weaknesses])

    lines.extend([
        "",
        "## 学习建议"
    ])
    lines.extend([f"- {s}" for s in report.learning_suggestions])

    return "\n".join(lines)


# ========== 主程序 ==========
def main():
    """主函数"""
    render_sidebar()

    # 根据阶段渲染不同页面
    if st.session_state.stage == "setup":
        render_setup_page()
    elif st.session_state.stage == "interview":
        render_interview_page()
    elif st.session_state.stage == "report":
        render_report_page()


if __name__ == "__main__":
    main()
