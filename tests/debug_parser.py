"""
Debug parser in detail
"""
import sys
sys.path.insert(0, '.')

import json
import logging
from agents.parser_agent import ParserAgent

logging.basicConfig(level=logging.DEBUG)

agent = ParserAgent()

resume_text = '张伟，Java工程师，5年经验。技能: Java, Spring, MySQL'

print('=== 步骤1: 调用API ===')
response = agent.call_claude(
    messages=[{'role': 'user', 'content': f'请解析以下简历并返回JSON: {resume_text}'}],
    max_tokens=2000
)

print(f'\n=== 步骤2: API响应 ===')
print(f'响应内容: {response}')
print(f'响应类型: {type(response)}')
print(f'响应长度: {len(response)}')

print(f'\n=== 步骤3: 尝试JSON解析 ===')
try:
    data = json.loads(response)
    print(f'JSON解析成功!')
    print(f'数据: {data}')
except json.JSONDecodeError as e:
    print(f'JSON解析失败: {e}')
    print(f'响应前100字符: {response[:100]}')
    print(f'响应后100字符: {response[-100:]}')

print(f'\n=== 步骤4: 调用完整parse_resume ===')
result = agent.parse_resume(resume_text)
print(f'姓名: "{result.name}"')
print(f'原始文本长度: {len(result.raw_text)}')
