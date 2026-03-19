"""
Automated End-to-End Test for Interview Coach
"""
import sys
sys.path.insert(0, '.')

from agents.parser_agent import ParserAgent
from agents import InterviewOrchestrator, create_orchestrator
from models import InterviewConfig
import json

print('='*60)
print('Interview Coach - 自动化端到端测试')
print('='*60)

# Read resume
with open(r'C:\Users\jason\Desktop\Sun Jinsuo.txt', 'r', encoding='utf-8') as f:
    resume_text = f.read()

print(f'\n[1] 简历读取成功，长度: {len(resume_text)} 字符')

# JD content
jd_text = """VP, Engineering Lead, WRB Tech

About Us
At Standard Chartered, we are committed to building a sustainable business by creating long-term value for our stakeholders, customers, employees, investors and the wider society.

We are looking for high-calibre professionals to join our Technology team based in China.

Job Title
VP, Engineering Lead, WRB Tech

Role Description
The Technology function at Standard Chartered enables and empowers the Bank with a vision to be the world's most innovative and digital client-centric Bank.

Business
- Identify opportunities to improve business agility through process improvements and automation
- Contribute to the development of the business strategy and roadmap
- Collaborate with stakeholders to define and implement technology solutions that meet business needs
- Manage the delivery of technology projects and services

Processes
- Ensure compliance with the Bank's policies, procedures and regulatory requirements
- Implement and maintain robust processes for software development, deployment and support
- Drive continuous improvement in software development practices
- Manage risks and issues related to technology projects

People & Talent
- Build and lead high-performing technology teams
- Foster a culture of innovation, collaboration and continuous learning
- Develop talent and create succession plans
- Manage performance and provide coaching and feedback

Risk Management
- Identify and mitigate technology risks
- Ensure compliance with regulatory requirements
- Implement and maintain effective controls
- Manage incidents and problems related to technology

Governance
- Ensure adherence to the Bank's governance framework
- Maintain effective relationships with regulators and auditors
- Implement and maintain effective governance processes

Requirements
- Bachelor's or master's degree in computer science or related field
- Professional certifications are preferred
- Experience with Agile/SAFe methodologies
- Experience with cloud platforms (Azure, AWS, GCP)
- Experience with DevOps practices and tools
- Strong problem-solving and technical aptitude skills
- Application delivery experience in financial services preferred"""

print(f'[2] JD内容准备完成，长度: {len(jd_text)} 字符')

# Create orchestrator
print('\n[3] 创建 Orchestrator...')
orchestrator = create_orchestrator()

# Parse resume
print('\n[4] 解析简历...')
orchestrator.update_resume_text(resume_text)
result = orchestrator.route_and_execute()

print(f'   Result: {result}')

if result.get('status') == 'success':
    print('   [OK] 简历解析成功')
    resume = orchestrator.state.resume
    print(f'   姓名: {resume.name}')
    print(f'   工作年限: {resume.experience_years} 年')
    print(f'   技术栈: {len(resume.technical_skills.to_list())} 项')
else:
    print(f'   [FAIL] 简历解析失败: {result}')
    sys.exit(1)

# Parse JD
print('\n[5] 解析JD...')
orchestrator.update_jd_text(jd_text)
result = orchestrator.route_and_execute()

if result.get('status') == 'success':
    print('   [OK] JD解析成功')
    jd = orchestrator.state.jd
    print(f'   职位: {jd.position}')
    print(f'   必须技能: {len(jd.required_skills)} 项')
else:
    print(f'   [FAIL] JD解析失败: {result}')
    sys.exit(1)

# Gap Analysis
print('\n[6] Gap分析...')
state = orchestrator.get_state()
if state['has_gap_analysis']:
    print('   [OK] Gap分析已完成')
    gap = orchestrator.state.gap_analysis
    print(f'   匹配度: {gap.match_percentage*100:.1f}%')
    print(f'   匹配项: {len(gap.matched_items)} 项')
    print(f'   差距项: {len(gap.gap_items)} 项')
else:
    print('   [WARN] Gap分析未完成，尝试触发...')
    result = orchestrator.route_and_execute()
    if result.get('gap_analysis'):
        gap = result['gap_analysis']
        print(f'   [OK] Gap分析完成: {gap.match_percentage*100:.1f}%')

# Configure interview
print('\n[7] 配置面试...')
config = InterviewConfig(
    interviewer_level='senior_engineer',
    interviewer_style='professional',
    focus_areas=['technical_basics', 'project_experience', 'problem_solving'],
    duration=30,
    language='mixed'
)
orchestrator.update_config(config)
print('   [OK] 面试配置完成')

# Start interview
print('\n[8] 开始面试...')
result = orchestrator.route_and_execute()

if result.get('status') == 'success' and result.get('action') == 'start_interview':
    print('   [OK] 面试已启动')
    first_question = result.get('response', '')
    print(f'   首个问题: {first_question[:200]}...')
    print(f'   Turn: {result.get("turn", 1)}')
else:
    print(f'   [FAIL] 面试启动失败: {result}')

print('\n' + '='*60)
print('测试完成！')
print('='*60)
