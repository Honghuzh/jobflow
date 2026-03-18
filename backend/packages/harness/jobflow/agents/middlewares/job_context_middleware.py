"""JobContextMiddleware — 将岗位信息格式化并注入 prompt 上下文。"""
from __future__ import annotations

import json
import logging
from typing import Any

from .base import Middleware

logger = logging.getLogger(__name__)


class JobContextMiddleware(Middleware):
    """在 Agent 执行前，将 target_job 格式化为 XML 标签注入 prompt。"""

    async def before_agent(self, state: dict, config: dict) -> dict | None:
        """将 target_job 格式化为 job_context 字符串。"""
        target_job = state.get("target_job")
        if not target_job:
            logger.debug("JobContextMiddleware: 无 target_job，跳过")
            return None

        # 将岗位信息序列化为可读文本
        job_lines = []
        if title := target_job.get("title"):
            job_lines.append(f"职位：{title}")
        if company := target_job.get("company"):
            job_lines.append(f"公司：{company}")
        if location := target_job.get("location"):
            job_lines.append(f"地点：{location}")
        if salary := target_job.get("salary_range"):
            job_lines.append(f"薪资：{salary}")
        if requirements := target_job.get("requirements"):
            job_lines.append("要求：")
            job_lines.extend(f"  - {r}" for r in requirements)
        if responsibilities := target_job.get("responsibilities"):
            job_lines.append("职责：")
            job_lines.extend(f"  - {r}" for r in responsibilities)

        job_context_text = "\n".join(job_lines)
        logger.info("JobContextMiddleware: 已注入岗位上下文（%s @ %s）", target_job.get("title", "?"), target_job.get("company", "?"))

        return {"job_context_text": job_context_text}

    async def after_agent(self, state: dict, response: Any, config: dict) -> Any:
        """无后处理逻辑。"""
        return response
