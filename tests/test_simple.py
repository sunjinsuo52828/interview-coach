# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import InterviewOrchestrator, create_orchestrator
from models import InterviewConfig

# Read resume
with open(r'C:\Users\jason\Desktop\Sun Jinsuo.txt', 'r', encoding='utf-8') as f:
    resume_text = f.read()

# JD content
jd_text = '''VP, Engineering Lead, WRB Tech
Requirements: Agile/SAFe, cloud platforms (Azure/AWS/GCP), DevOps, financial services experience'''

# Create orchestrator
orchestrator = create_orchestrator()

# Step 1: Parse resume
print('[Step 1/6] Parsing resume...')
orchestrator.update_resume_text(resume_text)
result = orchestrator.route_and_execute()
assert result['status'] == 'success'
resume = orchestrator.state.resume
print(f'  [OK] Name: {resume.name}')
print(f'  [OK] Experience: {resume.experience_years} years')

# Step 2: Parse JD
print('[Step 2/6] Parsing JD...')
orchestrator.update_jd_text(jd_text)
result = orchestrator.route_and_execute()
assert result['status'] == 'success'
jd = orchestrator.state.jd
print(f'  [OK] Position: {jd.position}')

# Step 3: Gap analysis
print('[Step 3/6] Gap analysis...')
state = orchestrator.get_state()
assert state['has_gap_analysis']
gap = orchestrator.state.gap_analysis
print(f'  [OK] Match: {gap.match_percentage*100:.0f}%')
print(f'  [OK] Matched: {len(gap.matched_items)}, Gap: {len(gap.gap_items)}')

# Step 4: Configure interview
print('[Step 4/6] Configuring interview...')
config = InterviewConfig(
    interviewer_level='senior_engineer',
    interviewer_style='professional',
    focus_areas=['technical_basics', 'project_experience'],
    duration=20,
    language='mixed'
)
orchestrator.update_config(config)
print('  [OK] Configured')

# Step 5: Start interview
print('[Step 5/6] Starting interview...')
result = orchestrator.route_and_execute()
assert result['status'] == 'success'
question = result.get('response', '')
print(f'  [OK] Q1: {question[:80]}...')

# Step 6: Simulate conversation
print('[Step 6/6] Simulating conversation...')
answer = 'I have 19 years of experience in fintech, leading teams at Citi.'
result = orchestrator.route_and_execute(answer)
print(f'  [OK] Response received')

# Status
state = orchestrator.get_state()
print('')
print('='*50)
print(f'[RESULT] Turns: {state["conversation_turns"]}')
print('[SUCCESS] All E2E tests passed!')
print('='*50)
print('UI running at http://localhost:8501')
