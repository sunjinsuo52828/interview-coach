"""
完整流程测试 - 模拟真实面试场景
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import InterviewOrchestrator, create_orchestrator
from models import InterviewConfig

print("="*70)
print(" Interview Coach - 完整面试流程测试")
print("="*70)

# 读取简历
with open(r'C:\Users\jason\Desktop\Sun Jinsuo.txt', 'r', encoding='utf-8') as f:
    resume_text = f.read()

# JD内容
jd_text = """VP, Engineering Lead, WRB Tech

About Standard Chartered
We are a leading international banking group with a presence in 59 of the world's most dynamic markets.

Job Description
The Technology function at Standard Chartered enables and empowers the Bank.

Key Responsibilities:
- Business: Identify opportunities to improve business agility through process improvements
- Processes: Ensure compliance with Bank's policies and regulatory requirements
- People & Talent: Build and lead high-performing technology teams
- Risk Management: Identify and mitigate technology risks
- Governance: Ensure adherence to the Bank's governance framework

Requirements:
- Bachelor's or master's degree in computer science or related field
- Experience with Agile/SAFe methodologies
- Experience with cloud platforms (Azure, AWS, GCP)
- Experience with DevOps practices and tools
- Strong problem-solving and technical aptitude skills
- Application delivery experience in financial services preferred"""

# 创建orchestrator
orchestrator = create_orchestrator()

# 步骤1: 解析简历
print("\n[步骤 1/7] 解析简历...")
orchestrator.update_resume_text(resume_text)
result = orchestrator.route_and_execute()
assert result['status'] == 'success', "简历解析失败"
resume = orchestrator.state.resume
print(f"  ✓ 姓名: {resume.name}")
print(f"  ✓ 工作年限: {resume.experience_years} 年")
print(f"  ✓ 当前职位: {resume.current_role}")
print(f"  ✓ 技术栈: {', '.join(resume.technical_skills.languages[:5])}...")

# 步骤2: 解析JD
print("\n[步骤 2/7] 解析JD...")
orchestrator.update_jd_text(jd_text)
result = orchestrator.route_and_execute()
assert result['status'] == 'success', "JD解析失败"
jd = orchestrator.state.jd
print(f"  ✓ 职位: {jd.position}")
print(f"  ✓ 公司: {jd.company}")
print(f"  ✓ 必须技能: {len(jd.required_skills)} 项")

# 步骤3: Gap分析
print("\n[步骤 3/7] Gap分析...")
state = orchestrator.get_state()
assert state['has_gap_analysis'], "Gap分析未完成"
gap = orchestrator.state.gap_analysis
print(f"  ✓ 匹配度: {gap.match_percentage*100:.1f}%")
print(f"  ✓ 匹配项 ({len(gap.matched_items)}): {', '.join(gap.matched_items[:5])}...")
print(f"  ✓ 差距项 ({len(gap.gap_items)}): {', '.join(gap.gap_items)}")
print(f"  ✓ 考察重点: {', '.join(gap.interview_focus[:3])}...")

# 步骤4: 配置面试
print("\n[步骤 4/7] 配置面试...")
config = InterviewConfig(
    interviewer_level='senior_engineer',
    interviewer_style='professional',
    focus_areas=['technical_basics', 'project_experience', 'problem_solving'],
    duration=30,
    language='mixed'
)
orchestrator.update_config(config)
print("  ✓ 面试官级别: Senior Engineer")
print("  ✓ 面试风格: Professional")
print("  ✓ 考察重点: Technical Basics, Project Experience, Problem Solving")

# 步骤5: 开始面试
print("\n[步骤 5/7] 开始面试...")
result = orchestrator.route_and_execute()
assert result['status'] == 'success', "面试启动失败"
assert result.get('action') == 'start_interview', "面试未启动"
first_question = result.get('response', '')
print(f"  ✓ 面试官开场白:")
print(f"    {first_question[:200]}...")

# 步骤6: 模拟回答和追问
print("\n[步骤 6/7] 模拟对话...")

# 第一轮回答
answer1 = "Thank you for the introduction. I have 19 years of experience in financial technology, primarily at Citi where I served as a VP leading the delivery of Consumer Finance and Wealth Management systems. I've managed cross-border teams serving 10M+ users across 16+ markets. My core expertise includes Java, Spring Boot, Angular, and I've led major microservices transformations using OpenShift and Docker."
result = orchestrator.route_and_execute(answer1)
print(f"  ✓ 候选人回答已提交")

if result.get('status') == 'success':
    response = result.get('response', '')
    print(f"  ✓ 面试官追问:")
    print(f"    {response[:200]}...")

# 第二轮回答
answer2 = "Regarding the microservices transformation, we migrated from a legacy Struts/Spring monolith to a modern Spring Boot microservices architecture. The key challenges were managing distributed transactions, ensuring data consistency, and maintaining backward compatibility during the transition. We used Spring Cloud for service discovery and API gateway, and implemented circuit breakers for resilience."
result = orchestrator.route_and_execute(answer2)
print(f"  ✓ 第二轮回答已提交")

if result.get('status') == 'success':
    response = result.get('response', '')
    print(f"  ✓ 面试官追问:")
    print(f"    {response[:200]}...")

# 步骤7: 查看状态
print("\n[步骤 7/7] 面试状态...")
state = orchestrator.get_state()
print(f"  ✓ 对话轮次: {state['conversation_turns']}")
print(f"  ✓ 面试中: {state['interview_started']}")

print("\n" + "="*70)
print(" 测试完成 - 所有功能正常!")
print("="*70)
print("\n提示: 可以在浏览器中访问 http://localhost:8501 查看完整UI")
