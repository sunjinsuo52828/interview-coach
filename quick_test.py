"""直接验证Python代码"""
import sys
sys.path.insert(0, r'C:\Practice\learning\interview-coach')

print("验证代码...")

# 1. 验证parser_agent
try:
    from agents import parser_agent
    print(f"✅ parser_agent导入成功")
    print(f"   - 有logger: {hasattr(parser_agent, 'logger')}")

    agent = parser_agent.ParserAgent()
    print(f"   - 实例化成功")

    # 验证_parse_resume_data
    result = agent._parse_resume_data({}, "")
    print(f"   - _parse_resume_data正常工作")
except Exception as e:
    print(f"❌ parser_agent失败: {e}")

# 2. 验证interview_agent
try:
    from agents import interview_agent
    print(f"✅ interview_agent导入成功")
    print(f"   - 有logger: {hasattr(interview_agent, 'logger')}")

    agent = interview_agent.InterviewerAgent()
    print(f"   - 实例化成功")

    # 验证_build_messages边界
    agent.memory = []
    agent.state = type('State', (), {'summary': None})()
    messages = agent._build_messages()
    print(f"   - _build_messages边界检查通过")
except Exception as e:
    print(f"❌ interview_agent失败: {e}")

# 3. 验证evaluator_agent
try:
    from agents import evaluator_agent
    print(f"✅ evaluator_agent导入成功")
    print(f"   - 有logger: {hasattr(evaluator_agent, 'logger')}")

    agent = evaluator_agent.EvaluatorAgent()
    print(f"   - 实例化成功")

    # 验证_format_conversation边界
    result = agent._format_conversation([])
    print(f"   - _format_conversation边界检查通过")
except Exception as e:
    print(f"❌ evaluator_agent失败: {e}")

# 4. 验证models
try:
    from models import ParsedResume, ParsedJD, GapAnalysis, TechnicalSkills
    print(f"✅ models导入成功")

    resume = ParsedResume(name="测试", technical_skills=TechnicalSkills())
    jd = ParsedJD(position="测试", required_skills=["Java"])
    gap = GapAnalysis(match_percentage=0.5, matched_items=["Java"], gap_items=[])
    print(f"   - 模型创建成功")
except Exception as e:
    print(f"❌ models失败: {e}")

print("\n验证完成！")
