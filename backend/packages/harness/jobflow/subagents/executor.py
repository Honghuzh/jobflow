"""SubAgent 并发执行引擎 — 借鉴 DeerFlow SubagentExecutor 模式。"""
from __future__ import annotations

import concurrent.futures
import logging
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger(__name__)

MAX_CONCURRENT_SUBAGENTS = 3
SUBAGENT_TIMEOUT = 900  # 15 分钟


class TaskStatus(str, Enum):
    """Sub-Agent 任务状态。"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


@dataclass
class TaskRecord:
    """任务执行记录。"""

    task_id: str
    agent_name: str
    status: TaskStatus = TaskStatus.PENDING
    future: Future | None = field(default=None, repr=False)
    result: Any = None
    error: str | None = None
    submitted_at: float = field(default_factory=time.time)
    completed_at: float | None = None


class SubAgentExecutor:
    """Sub-Agent 并发执行引擎。

    使用 ThreadPoolExecutor 管理并发执行，支持状态查询和超时控制。
    """

    def __init__(
        self,
        max_workers: int = MAX_CONCURRENT_SUBAGENTS,
        timeout_seconds: int = SUBAGENT_TIMEOUT,
    ):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._timeout = timeout_seconds
        self._tasks: dict[str, TaskRecord] = {}
        self._task_counter = 0

    def submit(self, agent_name: str, fn: Callable, *args, **kwargs) -> str:
        """提交一个 Sub-Agent 任务异步执行。

        Args:
            agent_name: Agent 名称（用于日志/追踪）
            fn: 要执行的函数
            *args, **kwargs: 传递给 fn 的参数

        Returns:
            task_id: 任务 ID，用于后续 poll/get_result
        """
        self._task_counter += 1
        task_id = f"{agent_name}-{self._task_counter}"

        record = TaskRecord(task_id=task_id, agent_name=agent_name)
        self._tasks[task_id] = record

        future = self._executor.submit(self._run_with_status, task_id, fn, *args, **kwargs)
        record.future = future
        record.status = TaskStatus.RUNNING

        logger.info("SubAgentExecutor: 提交任务 %s", task_id)
        return task_id

    def _run_with_status(self, task_id: str, fn: Callable, *args, **kwargs) -> Any:
        """包装执行函数，自动更新任务状态。"""
        record = self._tasks[task_id]
        try:
            result = fn(*args, **kwargs)
            record.status = TaskStatus.COMPLETED
            record.result = result
            record.completed_at = time.time()
            logger.info("SubAgentExecutor: 任务 %s 完成", task_id)
            return result
        except Exception as exc:
            record.status = TaskStatus.FAILED
            record.error = str(exc)
            record.completed_at = time.time()
            logger.error("SubAgentExecutor: 任务 %s 失败 — %s", task_id, exc)
            raise

    def poll(self, task_id: str) -> TaskStatus:
        """查询任务当前状态。"""
        record = self._tasks.get(task_id)
        if not record:
            raise KeyError(f"任务 '{task_id}' 不存在")

        # 检查超时
        if record.status == TaskStatus.RUNNING:
            elapsed = time.time() - record.submitted_at
            if elapsed > self._timeout:
                record.status = TaskStatus.TIMED_OUT
                if record.future:
                    record.future.cancel()
                logger.warning("SubAgentExecutor: 任务 %s 超时（%.1fs > %ds）", task_id, elapsed, self._timeout)

        return record.status

    def get_result(self, task_id: str, wait: bool = False) -> Any:
        """获取任务结果。

        Args:
            task_id: 任务 ID
            wait: 是否等待完成（阻塞）

        Returns:
            任务结果

        Raises:
            RuntimeError: 任务未完成或失败
        """
        record = self._tasks.get(task_id)
        if not record:
            raise KeyError(f"任务 '{task_id}' 不存在")

        if wait and record.future:
            try:
                record.future.result(timeout=self._timeout)
            except concurrent.futures.TimeoutError:
                record.status = TaskStatus.TIMED_OUT

        status = self.poll(task_id)
        if status == TaskStatus.COMPLETED:
            return record.result
        elif status == TaskStatus.FAILED:
            raise RuntimeError(f"任务 {task_id} 失败：{record.error}")
        elif status == TaskStatus.TIMED_OUT:
            raise TimeoutError(f"任务 {task_id} 超时")
        else:
            raise RuntimeError(f"任务 {task_id} 尚未完成（状态：{status}）")

    def shutdown(self, wait: bool = True) -> None:
        """关闭执行引擎。"""
        self._executor.shutdown(wait=wait)
        logger.info("SubAgentExecutor: 已关闭")
