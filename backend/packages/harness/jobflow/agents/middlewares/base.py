"""中间件基类 — 借鉴 DeerFlow 的 AgentMiddleware 模式。"""
from abc import ABC, abstractmethod
from typing import Any


class Middleware(ABC):
    """所有中间件的基类，定义 before_agent/after_agent 生命周期。"""

    @abstractmethod
    async def before_agent(self, state: dict, config: dict) -> dict | None:
        """Agent 执行前的钩子，返回要合并到 state 的更新，或 None。"""
        return None

    @abstractmethod
    async def after_agent(self, state: dict, response: Any, config: dict) -> Any:
        """Agent 执行后的钩子。"""
        return response


class MiddlewareChain:
    """有序中间件链 — 严格按注册顺序执行。"""

    def __init__(self, middlewares: list[Middleware] | None = None):
        self.middlewares = middlewares or []

    def add(self, middleware: Middleware) -> "MiddlewareChain":
        """追加一个中间件到链的末尾。"""
        self.middlewares.append(middleware)
        return self

    async def run_before(self, state: dict, config: dict) -> dict:
        """按顺序执行所有中间件的 before_agent 钩子。"""
        for mw in self.middlewares:
            update = await mw.before_agent(state, config)
            if update:
                state = {**state, **update}
        return state

    async def run_after(self, state: dict, response: Any, config: dict) -> Any:
        """按逆序执行所有中间件的 after_agent 钩子。"""
        for mw in reversed(self.middlewares):
            response = await mw.after_agent(state, response, config)
        return response
