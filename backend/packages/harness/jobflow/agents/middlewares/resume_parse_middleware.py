"""ResumeParseMiddleware — 自动解析上传的简历文件。"""
from __future__ import annotations

import logging
from typing import Any

from .base import Middleware

logger = logging.getLogger(__name__)

# 支持的简历文件扩展名
_RESUME_EXTENSIONS = {".pdf", ".docx", ".doc", ".md", ".txt"}


class ResumeParseMiddleware(Middleware):
    """在 Agent 执行前，自动检测并解析上传的简历文件。

    如果 state 中已有 resume_data 则跳过，避免重复解析。
    """

    async def before_agent(self, state: dict, config: dict) -> dict | None:
        """检测 uploaded_files 中的简历文件并解析。"""
        # 如果已有解析结果，跳过
        if state.get("resume_data"):
            logger.debug("ResumeParseMiddleware: 已有 resume_data，跳过解析")
            return None

        uploaded_files: list[str] | None = state.get("uploaded_files")
        if not uploaded_files:
            return None

        # 找到第一个简历文件
        resume_file = next((f for f in uploaded_files if self._is_resume_file(f)), None)
        if not resume_file:
            logger.debug("ResumeParseMiddleware: 未找到简历文件")
            return None

        logger.info("ResumeParseMiddleware: 正在解析简历文件 %s", resume_file)
        try:
            from jobflow.tools.builtins.resume_parser import parse_resume

            resume_data = parse_resume.invoke({"file_path": resume_file})
            logger.info("ResumeParseMiddleware: 简历解析完成")
            return {"resume_data": resume_data}
        except Exception as exc:
            logger.error("ResumeParseMiddleware: 解析失败 — %s", exc)
            return None

    async def after_agent(self, state: dict, response: Any, config: dict) -> Any:
        """无后处理逻辑。"""
        return response

    @staticmethod
    def _is_resume_file(file_path: str) -> bool:
        """判断文件路径是否为简历文件（根据扩展名）。"""
        import os

        ext = os.path.splitext(file_path)[1].lower()
        return ext in _RESUME_EXTENSIONS
