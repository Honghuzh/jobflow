"""Career Agent — 求职总教练（Lead Agent）实现。"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .prompts import apply_prompt_template

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# 默认工具列表（Phase 2 完整实现时替换为真实工具）
_DEFAULT_TOOLS: list[Any] = []


def make_career_agent(config: dict | None = None):
    """构建并返回编译好的 Career Agent Graph。

    借鉴 DeerFlow 的 make_agent 模式，组装 Middleware Chain 并返回 CompiledGraph。

    Args:
        config: Agent 配置字典，包含模型设置、工具列表等

    Returns:
        编译好的 LangGraph CompiledGraph 实例（Phase 2 完整实现）
    """
    cfg = config or {}

    # 构建系统提示词
    system_prompt = apply_prompt_template(
        resume_data=cfg.get("resume_data", "（暂无简历数据）"),
        job_context=cfg.get("job_context", "（暂无岗位信息）"),
        memory=cfg.get("memory", "（暂无历史记忆）"),
    )

    # 组装 Middleware Chain
    from jobflow.agents.middlewares.base import MiddlewareChain
    from jobflow.agents.middlewares.job_context_middleware import JobContextMiddleware
    from jobflow.agents.middlewares.progress_middleware import ProgressMiddleware
    from jobflow.agents.middlewares.resume_parse_middleware import ResumeParseMiddleware

    middleware_chain = MiddlewareChain(
        middlewares=[
            ResumeParseMiddleware(),
            JobContextMiddleware(),
            ProgressMiddleware(),
        ]
    )

    # 工具列表（可通过 config 覆盖）
    tools = cfg.get("tools", _DEFAULT_TOOLS)

    logger.info("Career Agent 构建完成，已加载 %d 个工具，%d 层 Middleware", len(tools), len(middleware_chain.middlewares))

    # Phase 2: 接入真实 LLM 并返回 CompiledGraph
    # 当前返回骨架对象，占位用
    return _CareerAgentPlaceholder(
        system_prompt=system_prompt,
        middleware_chain=middleware_chain,
        tools=tools,
    )


class _CareerAgentPlaceholder:
    """Career Agent 占位实现，Phase 2 替换为真实 LangGraph CompiledGraph。"""

    def __init__(self, system_prompt: str, middleware_chain: Any, tools: list):
        self.system_prompt = system_prompt
        self.middleware_chain = middleware_chain
        self.tools = tools

    async def ainvoke(self, state: dict, config: dict | None = None) -> dict:
        """模拟 Agent 调用（占位）。"""
        cfg = config or {}
        state = await self.middleware_chain.run_before(state, cfg)
        # Phase 2: 调用真实 LLM
        response = {"messages": state.get("messages", []), "status": "placeholder"}
        response = await self.middleware_chain.run_after(state, response, cfg)
        return response
