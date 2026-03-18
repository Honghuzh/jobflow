"""对话路由 — /api/chat 端点。"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "packages" / "harness"))

from app.gateway.thread_manager import get_thread_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """对话请求体。"""

    message: str
    thread_id: str | None = None
    resume_data: dict | None = None
    target_job: dict | None = None


class ChatResponse(BaseModel):
    """对话响应体。"""

    response: str
    thread_id: str
    artifacts: list = []


def _get_agent(config: dict | None = None) -> Any:
    """获取 Career Agent 实例（带 fallback）。"""
    try:
        from jobflow.agents.career_agent.agent import make_career_agent

        return make_career_agent(config)
    except Exception as exc:
        logger.warning("无法创建 Career Agent: %s，使用占位模式", exc)
        return None


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """接收用户消息，调用 Career Agent，返回响应。"""
    tm = get_thread_manager()

    # 获取或创建线程
    thread_id = request.thread_id or tm.create_thread()
    state = tm.get_state(thread_id) or {}

    # 构建消息状态
    from langchain_core.messages import HumanMessage

    messages = state.get("messages", [])
    messages.append(HumanMessage(content=request.message))

    agent_state: dict[str, Any] = {
        "messages": messages,
        "resume_data": request.resume_data or state.get("resume_data"),
        "target_job": request.target_job or state.get("target_job"),
        "artifacts": state.get("artifacts", []),
    }

    agent = _get_agent()
    if agent is not None:
        try:
            result = await agent.ainvoke(agent_state)
            result_messages = result.get("messages", messages) if isinstance(result, dict) else messages
            last_msg = result_messages[-1] if result_messages else None
            response_text = (getattr(last_msg, "content", None) or (last_msg.get("content") if isinstance(last_msg, dict) else None) or "") if last_msg else ""
            artifacts = result.get("artifacts", []) if isinstance(result, dict) else []
        except Exception as exc:
            logger.error("Agent 调用失败: %s", exc)
            response_text = f"（Agent 暂时不可用: {exc}）"
            artifacts = []
    else:
        response_text = "（Career Agent 未配置，请检查 API Key）"
        artifacts = []

    # 更新线程状态
    tm.update_state(thread_id, {"messages": messages, "resume_data": agent_state.get("resume_data"), "target_job": agent_state.get("target_job"), "artifacts": artifacts})

    return ChatResponse(response=response_text, thread_id=thread_id, artifacts=artifacts)


@router.post("/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """SSE 流式对话端点。"""
    tm = get_thread_manager()
    thread_id = request.thread_id or tm.create_thread()
    state = tm.get_state(thread_id) or {}

    from langchain_core.messages import HumanMessage

    messages = list(state.get("messages", []))
    messages.append(HumanMessage(content=request.message))

    agent_state: dict[str, Any] = {
        "messages": messages,
        "resume_data": request.resume_data or state.get("resume_data"),
        "target_job": request.target_job or state.get("target_job"),
        "artifacts": state.get("artifacts", []),
    }

    agent = _get_agent()

    from app.gateway.sse import SSEFormatter, stream_agent_response

    async def event_generator():
        if agent is None:
            yield SSEFormatter.format_event("token", "（Career Agent 未配置，请检查 API Key）")
            yield SSEFormatter.format_done()
            return
        async for chunk in stream_agent_response(agent, agent_state):
            yield chunk

    return StreamingResponse(event_generator(), media_type="text/event-stream")
