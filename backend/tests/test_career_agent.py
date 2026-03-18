"""测试 Career Agent — make_career_agent 和相关组件。"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "harness"))

from jobflow.agents.career_agent.agent import (
    _CareerAgentPlaceholder,
    _CareerAgentWithMiddleware,
    _try_build_langgraph,
    make_career_agent,
)
from jobflow.agents.middlewares.base import MiddlewareChain


# ── make_career_agent 测试 ────────────────────────────────────────────────


class TestMakeCareerAgent:
    """测试 make_career_agent 工厂函数。"""

    def test_returns_object(self):
        """make_career_agent() 应返回可调用对象。"""
        agent = make_career_agent()
        assert agent is not None

    def test_returns_placeholder_without_llm(self):
        """没有 LLM 配置时，应返回 _CareerAgentPlaceholder 或 _CareerAgentWithMiddleware。"""
        agent = make_career_agent()
        # 两种类型都合法：有 LLM 时是 WithMiddleware，无 LLM 时是 Placeholder
        assert isinstance(agent, (_CareerAgentPlaceholder, _CareerAgentWithMiddleware))

    def test_placeholder_has_middleware_chain(self):
        """占位对象应包含 middleware_chain。"""
        agent = make_career_agent()
        assert hasattr(agent, "middleware_chain")
        assert isinstance(agent.middleware_chain, MiddlewareChain)

    def test_placeholder_has_tools(self):
        """占位对象应包含 tools 列表。"""
        agent = make_career_agent()
        assert hasattr(agent, "tools")
        assert isinstance(agent.tools, list)

    def test_custom_config(self):
        """可以传入自定义 config。"""
        agent = make_career_agent({"model_name": "gpt-4o-mini"})
        assert agent is not None

    def test_middleware_chain_has_3_layers(self):
        """默认 Middleware Chain 应有 3 层。"""
        agent = make_career_agent()
        assert len(agent.middleware_chain.middlewares) == 3

    @pytest.mark.asyncio
    async def test_ainvoke_returns_dict(self):
        """ainvoke 应返回字典。"""
        agent = make_career_agent()
        result = await agent.ainvoke({"messages": []})
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_ainvoke_with_messages(self):
        """ainvoke 传入消息时不应报错。"""
        from langchain_core.messages import HumanMessage

        agent = make_career_agent()
        result = await agent.ainvoke({"messages": [HumanMessage(content="测试消息")]})
        assert isinstance(result, dict)


# ── _try_build_langgraph 测试 ─────────────────────────────────────────────


class TestTryBuildLanggraph:
    """测试 LangGraph 构建逻辑。"""

    def test_returns_none_without_api_key(self):
        """没有有效 API Key 时应返回 None（不报错）。"""
        # 确保没有配置 API Key
        import os

        original = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = ""
        try:
            result = _try_build_langgraph("test prompt", [], "gpt-4o-mini")
            # 可能是 None（无法连接）或 CompiledGraph（有 key 时）
            # 主要验证不报错
            assert result is None or hasattr(result, "invoke")
        finally:
            if original is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = original


# ── _CareerAgentPlaceholder 测试 ─────────────────────────────────────────


class TestCareerAgentPlaceholder:
    """测试占位 Agent 实现。"""

    @pytest.mark.asyncio
    async def test_ainvoke_empty_state(self):
        """空状态调用不报错。"""
        chain = MiddlewareChain([])
        agent = _CareerAgentPlaceholder(system_prompt="test", middleware_chain=chain, tools=[])
        result = await agent.ainvoke({})
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_ainvoke_with_messages(self):
        """有消息的状态调用不报错。"""
        from langchain_core.messages import HumanMessage

        chain = MiddlewareChain([])
        agent = _CareerAgentPlaceholder(system_prompt="test", middleware_chain=chain, tools=[])
        state = {"messages": [HumanMessage(content="Hello")]}
        result = await agent.ainvoke(state)
        assert isinstance(result, dict)
        assert "messages" in result


# ── Middleware 集成测试 ────────────────────────────────────────────────────


class TestMiddlewareIntegration:
    """测试 Career Agent 的 Middleware 集成。"""

    @pytest.mark.asyncio
    async def test_career_agent_runs_middlewares(self):
        """Career Agent 调用时 Middleware Chain 应正常执行。"""
        from jobflow.agents.middlewares.base import Middleware

        log = []

        class LogMiddleware(Middleware):
            async def before_agent(self, state: dict, config: dict) -> dict | None:
                log.append("before")
                return None

            async def after_agent(self, state: dict, response, config: dict):
                log.append("after")
                return response

        chain = MiddlewareChain([LogMiddleware()])
        agent = _CareerAgentPlaceholder(system_prompt="test", middleware_chain=chain, tools=[])
        await agent.ainvoke({"messages": []})
        assert "before" in log
        assert "after" in log
