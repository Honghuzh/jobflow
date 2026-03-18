"""SubAgent 注册中心 — 管理求职专家 Sub-Agent 的注册与发现。"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)


def _has_ngram_overlap(a: str, b: str, min_len: int = 2) -> bool:
    """检查 a 中是否有长度 >= min_len 的子串出现在 b 中（支持中文）。"""
    for i in range(len(a)):
        for j in range(i + min_len, min(i + 20, len(a)) + 1):
            if a[i:j] in b:
                return True
    return False


@dataclass
class AgentCapability:
    """Sub-Agent 能力声明。"""

    name: str
    description: str
    tags: list[str] = field(default_factory=list)
    max_concurrency: int = 3
    timeout_seconds: int = 900


class SubAgentRegistry:
    """Sub-Agent 注册中心 — 支持注册、查找和实例化。"""

    def __init__(self):
        self._agents: dict[str, tuple[AgentCapability, Callable]] = {}

    def register(self, capability: AgentCapability, factory: Callable) -> None:
        """注册一个 Sub-Agent。

        Args:
            capability: Agent 能力声明
            factory: 创建 Agent 实例的工厂函数
        """
        if capability.name in self._agents:
            logger.warning("SubAgentRegistry: 覆盖已注册的 Agent '%s'", capability.name)
        self._agents[capability.name] = (capability, factory)
        logger.info("SubAgentRegistry: 注册 Agent '%s'，tags=%s", capability.name, capability.tags)

    def match(self, task_description: str, tags: list[str] | None = None) -> list[str]:
        """根据任务描述和标签查找匹配的 Agent 名称列表。

        当 tags 参数提供时，只返回拥有这些标签的 Agent（标签精确过滤）。
        未提供 tags 时，通过任务描述与 Agent 描述/标签的关键词匹配来筛选。

        Args:
            task_description: 任务描述文本（用于关键词匹配）
            tags: 可选的标签精确过滤列表

        Returns:
            匹配的 Agent 名称列表（按注册顺序）
        """
        results = []
        desc_lower = task_description.lower()

        for name, (cap, _) in self._agents.items():
            if tags:
                # 明确指定标签时，只要 Agent 包含任意一个请求标签即匹配
                if any(t in cap.tags for t in tags):
                    results.append(name)
            else:
                # 无标签过滤时，通过关键词匹配：
                # 1. Agent 的任意标签出现在任务描述中
                # 2. 任务描述中的英文词语出现在 Agent 描述中，或反之
                # 3. 子串匹配：Agent 描述中的任意 2+ 字符子串出现在任务描述中
                cap_desc_lower = cap.description.lower()
                tag_match = any(tag.lower() in desc_lower for tag in cap.tags)
                word_match = any(keyword in desc_lower for keyword in cap_desc_lower.split() if len(keyword) > 1) or any(word in cap_desc_lower for word in desc_lower.split() if len(word) > 1)
                substr_match = _has_ngram_overlap(cap_desc_lower, desc_lower, min_len=2)
                if tag_match or word_match or substr_match:
                    results.append(name)

        return results

    def create(self, name: str, **kwargs) -> Any:
        """创建 Sub-Agent 实例。

        Args:
            name: Agent 名称
            **kwargs: 传递给工厂函数的参数

        Returns:
            Agent 实例

        Raises:
            KeyError: Agent 未注册
        """
        if name not in self._agents:
            raise KeyError(f"Sub-Agent '{name}' 未注册。可用列表：{list(self._agents.keys())}")
        _, factory = self._agents[name]
        return factory(**kwargs)

    def list_agents(self) -> list[AgentCapability]:
        """列出所有已注册的 Agent 能力。"""
        return [cap for cap, _ in self._agents.values()]

    def get(self, name: str) -> AgentCapability | None:
        """获取 Agent 能力声明，不存在返回 None。"""
        entry = self._agents.get(name)
        return entry[0] if entry else None


# 全局注册中心
registry = SubAgentRegistry()
