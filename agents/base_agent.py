"""
Agent基类 - 定义统一的Agent接口

所有Agent都应该继承这个基类，实现统一的方法。
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests

from config import settings
from models import (
    AgentMessage,
    AgentThought,
    AgentResponse,
    InterviewState,
)


class BaseAgent(ABC):
    """Agent基类"""

    def __init__(self, name: str = ""):
        """
        初始化Agent

        Args:
            name: Agent名称
        """
        self.name = name or self.__class__.__name__
        self.api_key = settings.glm_api_key
        self.model = settings.glm_model
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

        # 统计信息
        self.total_tokens_used = 0
        self.total_calls = 0

    @abstractmethod
    def execute(self, action: str, context: Dict[str, Any]) -> Any:
        """
        执行动作

        Args:
            action: 动作名称
            context: 上下文信息

        Returns:
            执行结果
        """
        pass

    @abstractmethod
    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        获取System Prompt

        Args:
            context: 上下文信息

        Returns:
            System Prompt字符串
        """
        pass

    def call_claude(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> str:
        """
        调用GLM API (支持GLM-5)

        Args:
            messages: 消息列表
            system_prompt: System Prompt
            max_tokens: 最大token数
            temperature: 温度参数

        Returns:
            GLM响应内容
        """
        # 构建请求体
        payload = {
            "model": self.model,
            "messages": [],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        # 添加system prompt
        if system_prompt:
            payload["messages"].append({
                "role": "system",
                "content": system_prompt
            })

        # 添加用户消息
        payload["messages"].extend(messages)

        # 发送请求
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            self.api_url,
            json=payload,
            headers=headers,
            timeout=60
        )

        # 检查响应
        if response.status_code != 200:
            error_msg = response.text
            raise Exception(f"GLM API Error ({response.status_code}): {error_msg}")

        data = response.json()

        # 提取内容
        content = data["choices"][0]["message"]["content"]

        # 更新统计
        usage = data.get("usage", {})
        self.total_tokens_used += usage.get("total_tokens", 0)
        self.total_calls += 1

        return content

    def create_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> AgentMessage:
        """
        创建Agent消息

        Args:
            role: 消息角色
            content: 消息内容
            metadata: 元数据

        Returns:
            AgentMessage对象
        """
        return AgentMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )

    def create_thought(
        self,
        thought: str,
        action: str = "",
        action_input: Optional[Dict] = None,
        observation: str = ""
    ) -> AgentThought:
        """
        创建Agent思考记录（ReAct）

        Args:
            thought: 思考内容
            action: 行动
            action_input: 行动输入
            observation: 观察结果

        Returns:
            AgentThought对象
        """
        return AgentThought(
            thought=thought,
            action=action,
            action_input=action_input or {},
            observation=observation,
            timestamp=datetime.now().isoformat()
        )

    def get_stats(self) -> Dict[str, Any]:
        """
        获取Agent统计信息

        Returns:
            统计信息字典
        """
        return {
            "name": self.name,
            "total_calls": self.total_calls,
            "total_tokens_used": self.total_tokens_used,
            "avg_tokens_per_call": (
                self.total_tokens_used / self.total_calls
                if self.total_calls > 0 else 0
            )
        }

    def reset_stats(self):
        """重置统计信息"""
        self.total_tokens_used = 0
        self.total_calls = 0


class ToolEnabledAgent(BaseAgent):
    """支持工具调用的Agent基类"""

    def __init__(self, name: str = ""):
        super().__init__(name)
        self.tools: Dict[str, callable] = {}
        self._setup_tools()

    def _setup_tools(self):
        """设置工具（子类重写）"""
        pass

    def register_tool(self, name: str, func: callable):
        """
        注册工具

        Args:
            name: 工具名称
            func: 工具函数
        """
        self.tools[name] = func

    def call_tool(self, name: str, **kwargs) -> Any:
        """
        调用工具

        Args:
            name: 工具名称
            **kwargs: 工具参数

        Returns:
            工具执行结果
        """
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")

        return self.tools[name](**kwargs)

    def get_tools_description(self) -> str:
        """
        获取工具描述（用于Prompt）

        Returns:
            工具描述字符串
        """
        if not self.tools:
            return "没有可用工具"

        descriptions = []
        for name, func in self.tools.items():
            doc = func.__doc__ or "无描述"
            descriptions.append(f"- {name}: {doc}")

        return "\n".join(descriptions)


class StatefulAgent(ToolEnabledAgent):
    """有状态的Agent基类（支持记忆）"""

    def __init__(self, name: str = ""):
        super().__init__(name)
        self.state: InterviewState = InterviewState()
        self.memory: List[AgentMessage] = []

    def update_state(self, **kwargs):
        """更新状态"""
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)

    def add_to_memory(self, message: AgentMessage):
        """添加到记忆"""
        self.memory.append(message)

    def get_memory(self, last_n: Optional[int] = None) -> List[AgentMessage]:
        """
        获取记忆

        Args:
            last_n: 获取最近N条，None表示全部

        Returns:
            消息列表
        """
        if last_n is None:
            return self.memory
        return self.memory[-last_n:]

    def clear_memory(self):
        """清空记忆"""
        self.memory = []
