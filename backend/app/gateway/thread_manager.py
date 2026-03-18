"""ThreadManager — 管理对话线程（内存存储）。"""
from __future__ import annotations

import uuid
from typing import Any


class ThreadManager:
    """管理对话线程的生命周期与状态。

    内存存储实现，Phase 3 可替换为 Redis / 数据库。
    """

    def __init__(self) -> None:
        self._threads: dict[str, dict[str, Any]] = {}

    def create_thread(self) -> str:
        """创建新线程，返回 UUID 字符串。"""
        thread_id = str(uuid.uuid4())
        self._threads[thread_id] = {"messages": [], "resume_data": None, "target_job": None, "artifacts": []}
        return thread_id

    def get_state(self, thread_id: str) -> dict[str, Any] | None:
        """获取线程状态，线程不存在时返回 None。"""
        return self._threads.get(thread_id)

    def update_state(self, thread_id: str, updates: dict[str, Any]) -> None:
        """更新线程状态，线程不存在时自动创建。"""
        if thread_id not in self._threads:
            self._threads[thread_id] = {"messages": [], "resume_data": None, "target_job": None, "artifacts": []}
        self._threads[thread_id].update(updates)

    def list_threads(self) -> list[str]:
        """列出所有线程 ID。"""
        return list(self._threads.keys())


# 全局单例
_thread_manager: ThreadManager | None = None


def get_thread_manager() -> ThreadManager:
    """获取全局 ThreadManager 单例。"""
    global _thread_manager
    if _thread_manager is None:
        _thread_manager = ThreadManager()
    return _thread_manager
