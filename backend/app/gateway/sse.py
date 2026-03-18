"""SSEFormatter — Server-Sent Events 格式化与流式响应。"""
from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator

logger = logging.getLogger(__name__)


class SSEFormatter:
    """格式化 SSE 事件。

    事件格式：``data: {json}\n\n``
    """

    @staticmethod
    def format_event(event_type: str, content: Any) -> str:
        """将事件类型和内容序列化为 SSE 格式字符串。

        Args:
            event_type: 事件类型（token / tool_call / tool_result / status / done / error）
            content: 事件内容（str 或可序列化对象）

        Returns:
            SSE 格式字符串，以 ``\\n\\n`` 结尾
        """
        payload = {"type": event_type, "content": content}
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    @staticmethod
    def format_done() -> str:
        """生成 done 事件。"""
        return SSEFormatter.format_event("done", "")

    @staticmethod
    def format_error(message: str) -> str:
        """生成 error 事件。"""
        return SSEFormatter.format_event("error", message)


async def stream_agent_response(agent: Any, state: dict, config: dict | None = None) -> AsyncIterator[str]:
    """逐 token 流式返回 Agent 响应。

    如果 Agent 支持 ``astream`` 则使用流式模式；否则 fallback 到 ``ainvoke``，
    最终以单 token 事件推送完整回复。

    Args:
        agent: 编译好的 Career Agent（CompiledGraph 或占位对象）
        state: 当前对话状态
        config: LangGraph runnable config

    Yields:
        SSE 格式字符串
    """
    cfg = config or {}
    formatter = SSEFormatter()
    try:
        if hasattr(agent, "astream"):
            async for chunk in agent.astream(state, cfg):
                # chunk 可能是 dict（状态更新）或 AIMessage
                if isinstance(chunk, dict):
                    # 从 agent 节点输出提取消息内容
                    for node_output in chunk.values():
                        if isinstance(node_output, dict):
                            messages = node_output.get("messages", [])
                            for msg in messages:
                                content = getattr(msg, "content", None) or (msg.get("content") if isinstance(msg, dict) else None)
                                if content:
                                    yield formatter.format_event("token", content)
                                tool_calls = getattr(msg, "tool_calls", None)
                                if tool_calls:
                                    for tc in tool_calls:
                                        yield formatter.format_event("tool_call", {"name": tc.get("name", ""), "args": tc.get("args", {})})
                else:
                    content = getattr(chunk, "content", None)
                    if content:
                        yield formatter.format_event("token", content)
        else:
            # Fallback：ainvoke 再推送
            result = await agent.ainvoke(state, cfg)
            messages = result.get("messages", []) if isinstance(result, dict) else []
            if messages:
                last = messages[-1]
                content = getattr(last, "content", None) or (last.get("content") if isinstance(last, dict) else None)
                if content:
                    yield formatter.format_event("token", content)
    except Exception as exc:
        logger.error("stream_agent_response 出错: %s", exc)
        yield formatter.format_error(str(exc))

    yield formatter.format_done()
