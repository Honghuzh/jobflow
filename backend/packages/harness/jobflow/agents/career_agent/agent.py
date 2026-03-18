"""Career Agent — 求职总教练（Lead Agent）实现。"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .prompts import apply_prompt_template

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# 默认工具列表
_DEFAULT_TOOLS: list[Any] = []


def make_career_agent(config: dict | None = None):
    """构建并返回编译好的 Career Agent Graph。"""
    cfg = config or {}

    # --- 修改点 1：移除这里的静态 system_prompt 生成 ---
    # 不再在这里调用 apply_prompt_template

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

    # 内置工具列表
    from jobflow.tools.builtins.jd_parser import parse_jd 
    from jobflow.tools.builtins.job_tracker import get_job_stats, update_job_status
    from jobflow.tools.builtins.match_scorer import match_score
    from jobflow.tools.builtins.resume_parser import parse_resume

    builtin_tools = [parse_jd, match_score, update_job_status, get_job_stats, parse_resume]
    tools = cfg.get("tools", builtin_tools)

    # 尝试构建真实 LangGraph Agent
    model_name = cfg.get("model_name", "gpt-5.1-codex")
    
    # --- 修改点 2：不再传递 system_prompt，让内部动态生成 ---
    compiled_graph = _try_build_langgraph(tools, model_name)

    if compiled_graph is not None:
        return _CareerAgentWithMiddleware(graph=compiled_graph, middleware_chain=middleware_chain)

    # Fallback
    return _CareerAgentPlaceholder(
        system_prompt="Fallback Prompt", 
        middleware_chain=middleware_chain,
        tools=tools,
    )


def _try_build_langgraph(tools: list, model_name: str) -> Any | None:
    """尝试构建真实的 LangGraph StateGraph。"""
    try:
        from langchain_core.messages import SystemMessage
        from langgraph.graph import END, StateGraph
        from langgraph.prebuilt import ToolNode

        from jobflow.agents.thread_state import JobFlowThreadState
        from jobflow.models.factory import create_chat_model

        llm = create_chat_model(name=model_name)
        llm_with_tools = llm.bind_tools(tools)

        def should_continue(state: dict) -> str:
            messages = state.get("messages", [])
            last = messages[-1] if messages else None
            if last and hasattr(last, "tool_calls") and last.tool_calls:
                return "tools"
            return END

        # --- 修改点 3：核心动态注入逻辑 ---
        def agent_node(state: dict, config: Any = None) -> dict:  # 加上 = None 变成可选参数
            messages = state.get("messages", [])
    
            # 增加一层防御性逻辑
            configurable = {}
            if config and hasattr(config, "get"):
                configurable = config.get("configurable", {})
    
            # 获取简历数据
            resume_data = configurable.get("resume_data")
    
            # 动态生成 System Prompt
            dynamic_system_prompt = apply_prompt_template(
                resume_data=resume_data if resume_data else "（用户尚未上传简历数据）",
                job_context=configurable.get("job_context", "（暂无岗位信息）"),
                memory=configurable.get("memory", "（暂无历史记忆）"),
            )
    
            system_msg = SystemMessage(content=dynamic_system_prompt)
            response = llm_with_tools.invoke([system_msg] + messages)
            return {"messages": [response]}

        graph = StateGraph(JobFlowThreadState)
        graph.add_node("agent", agent_node)
        graph.add_node("tools", ToolNode(tools))
        graph.set_entry_point("agent")
        graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
        graph.add_edge("tools", "agent")

        return graph.compile()
    except Exception as exc:
        logger.error("!!! 核心报错：构建 LangGraph 失败 !!!", exc_info=True)
        return None


class _CareerAgentWithMiddleware:
    """包装 LangGraph CompiledGraph，加入 Middleware Chain 支持。"""

    def __init__(self, graph: Any, middleware_chain: Any):
        self.graph = graph
        self.middleware_chain = middleware_chain

    async def ainvoke(self, state: dict, config: dict | None = None) -> dict:
        """执行 Middleware → Graph → Middleware 完整流程。"""
        cfg = config or {}
        state = await self.middleware_chain.run_before(state, cfg)
        result = await self.graph.ainvoke(state, cfg)
        result = await self.middleware_chain.run_after(state, result, cfg)
        return result

    async def astream(self, state: dict, config: dict | None = None):
        """流式执行（代理到底层 graph.astream）。"""
        cfg = config or {}
        state = await self.middleware_chain.run_before(state, cfg)
        async for chunk in self.graph.astream(state, cfg):
            yield chunk


class _CareerAgentPlaceholder:
    """Career Agent 占位实现（LLM 不可用时使用）。"""

    def __init__(self, system_prompt: str, middleware_chain: Any, tools: list):
        self.system_prompt = system_prompt
        self.middleware_chain = middleware_chain
        self.tools = tools

    async def ainvoke(self, state: dict, config: dict | None = None) -> dict:
        """模拟 Agent 调用（占位）。"""
        cfg = config or {}
        state = await self.middleware_chain.run_before(state, cfg)
        response = {"messages": state.get("messages", []), "status": "placeholder"}
        response = await self.middleware_chain.run_after(state, response, cfg)
        
        
        return response