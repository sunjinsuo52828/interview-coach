# GLM-4.5 API 迁移指南

## 概述

Interview Coach 已从 Claude API 迁移到 GLM-4.5 API（智谱AI）。

## 变更内容

### 1. 配置文件变更

**.env 文件：**
```bash
# 旧配置 (Claude API)
ANTHROPIC_API_KEY=sk-ant-xxxxx
CLAUDE_MODEL=claude-sonnet-4-20250514

# 新配置 (GLM-4.5)
GLM_API_KEY=your_glm_api_key_here
GLM_MODEL=glm-4.5
```

### 2. 代码变更

**config.py：**
```python
# 旧配置
anthropic_api_key: str
claude_model: str = "claude-sonnet-4-20250514"

# 新配置
glm_api_key: str
glm_model: str = "glm-4.5"
```

**base_agent.py：**
- 从 `anthropic` SDK 改为使用 `requests` 直接调用 GLM API
- API 端点: `https://open.bigmodel.cn/api/paas/v4/chat/completions`
- 响应格式: OpenAI 兼容格式

### 3. API 调用方式

GLM-4.5 API 使用标准的 OpenAI 格式：

```python
{
    "model": "glm-4.5",
    "messages": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."}
    ],
    "max_tokens": 2000,
    "temperature": 0.7
}
```

## 获取 GLM API 密钥

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册账号并登录
3. 进入 API 密钥管理页面
4. 创建新的 API 密钥
5. 将密钥复制到 `.env` 文件中的 `GLM_API_KEY`

## 兼容性说明

- 方法名 `call_claude` 保持不变，以确保向后兼容
- 所有 Agent 代码无需修改
- 测试代码无需修改（mock 方式不变）

## 测试验证

运行测试确保迁移成功：

```bash
# 运行单元测试
pytest tests/unit/ -v

# 运行集成测试
pytest tests/integration/ -v
```

## 故障排除

### 错误：API 密钥无效
```
GLM API Error (401): Unauthorized
```
**解决方案**：检查 `.env` 文件中的 `GLM_API_KEY` 是否正确。

### 错误：请求超时
```
requests.exceptions.Timeout
```
**解决方案**：检查网络连接，确保可以访问 `open.bigmodel.cn`。

### 错误：配额不足
```
GLM API Error (429): Insufficient quota
```
**解决方案**：登录智谱AI平台检查账户余额和配额。

## GLM-4.5 模型特性

- 上下文长度: 最大 128K tokens
- 支持功能: 聊天、函数调用、长文本理解
- 适用场景: 复杂对话、文档解析、代码生成

## 回滚到 Claude API

如需回滚，恢复以下配置：

1. **.env 文件**
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
CLAUDE_MODEL=claude-sonnet-4-20250514
```

2. **config.py**
```python
anthropic_api_key: str
claude_model: str = "claude-sonnet-4-20250514"
```

3. **base_agent.py**
```python
import anthropic

self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
```

## 技术支持

- 智谱AI文档: https://open.bigmodel.cn/dev/api
- GitHub Issues: https://github.com/your-repo/issues
