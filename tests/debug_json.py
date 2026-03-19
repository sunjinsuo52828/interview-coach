"""
Debug JSON parsing issue
"""
import sys
sys.path.insert(0, '.')

from agents.parser_agent import ParserAgent
import json

agent = ParserAgent()

# 直接测试call_claude方法
resume_text = '张伟，高级Java工程师，5年经验。技能: Java, Spring, MySQL'

# 模拟parser的prompt
prompt = f'''请解析以下简历，提取结构化信息。

简历内容：
{resume_text}

请提取以下信息（JSON格式）：
{{
    "name": "姓名",
    "experience_years": 工作年限(数字),
    "current_role": "当前职位",
    "technical_skills": {{
        "languages": ["编程语言列表"]
    }}
}}

只返回JSON，不要其他内容。'''

print('发送请求...')
response = agent.call_claude(
    messages=[{'role': 'user', 'content': prompt}],
    max_tokens=2000,
    temperature=0.3
)

print(f'\n原始响应长度: {len(response)} 字符')
print(f'原始响应:\n{response}')

# 测试JSON解析
try:
    # 尝试直接解析
    data = json.loads(response)
    print(f'\n直接解析成功: {data}')
except json.JSONDecodeError as e:
    print(f'\n直接解析失败: {e}')

    # 尝试去除markdown格式
    cleaned = response.strip()
    if cleaned.startswith('```'):
        parts = cleaned.split('```')
        cleaned = parts[1] if len(parts) > 1 else cleaned
        if cleaned.startswith('json'):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()

    print(f'\n清理后的内容: {cleaned}')

    try:
        data = json.loads(cleaned)
        print(f'清理后解析成功: {data}')
    except Exception as e2:
        print(f'清理后仍然失败: {e2}')
