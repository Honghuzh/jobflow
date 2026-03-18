"""ProgressMiddleware — 自动追踪求职投递进度。"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

from .base import Middleware

logger = logging.getLogger(__name__)

# 投递状态流转定义
APPLICATION_STATUS_FLOW = ["wishlist", "applied", "phone_screen", "interview", "offer", "rejected"]

# 状态触发关键词（用于从对话中检测状态变化）
_STATUS_KEYWORDS: dict[str, list[str]] = {
    "applied": ["已投递", "投递了", "submit", "applied", "发送简历"],
    "phone_screen": ["电话面试", "初筛", "phone screen", "hr 电话", "打来电话"],
    "interview": ["现场面试", "技术面试", "面试邀请", "interview", "面试通知"],
    "offer": ["offer", "录用", "拿到 offer", "录取通知"],
    "rejected": ["拒信", "拒了", "没过", "rejected", "不合适"],
}


class ProgressMiddleware(Middleware):
    """在 Agent 响应后，检测对话内容并自动更新投递进度。"""

    async def before_agent(self, state: dict, config: dict) -> dict | None:
        """无前处理逻辑。"""
        return None

    async def after_agent(self, state: dict, response: Any, config: dict) -> Any:
        """检查响应内容，自动更新 job_applications。"""
        # 获取最新消息文本
        messages = state.get("messages", [])
        if not messages:
            return response

        last_message = messages[-1]
        text = self._extract_text(last_message)
        if not text:
            return response

        # 检测是否有状态变化
        detected_status = self._detect_status(text)
        if not detected_status:
            return response

        # 检测公司和职位信息（简单正则，Phase 2 用 LLM 替换）
        company = self._extract_company(text)
        position = self._extract_position(text)

        if company or position:
            applications: list[dict] = list(state.get("job_applications", []))
            # 更新或新增投递记录
            existing = next((a for a in applications if a.get("company") == company and a.get("position") == position), None)
            if existing:
                existing["status"] = detected_status
                logger.info("ProgressMiddleware: 更新投递状态 %s @ %s → %s", position, company, detected_status)
            else:
                applications.append(
                    {
                        "company": company or "未知公司",
                        "position": position or "未知职位",
                        "status": detected_status,
                        "applied_at": datetime.now(timezone.utc).isoformat(),
                        "notes": "",
                    }
                )
                logger.info("ProgressMiddleware: 新增投递记录 %s @ %s，状态 %s", position, company, detected_status)

            # 将更新写回 response（附加到 state 更新）
            if isinstance(response, dict):
                response["job_applications"] = applications

        return response

    @staticmethod
    def _extract_text(message: Any) -> str:
        """从消息对象中提取文本内容。"""
        if isinstance(message, str):
            return message
        if isinstance(message, dict):
            return message.get("content", "")
        if hasattr(message, "content"):
            content = message.content
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                return " ".join(c.get("text", "") if isinstance(c, dict) else str(c) for c in content)
        return ""

    @staticmethod
    def _detect_status(text: str) -> str | None:
        """从文本中检测投递状态关键词。"""
        text_lower = text.lower()
        for status, keywords in _STATUS_KEYWORDS.items():
            if any(kw.lower() in text_lower for kw in keywords):
                return status
        return None

    @staticmethod
    def _extract_company(text: str) -> str | None:
        """从文本中提取公司名称（简单启发式，Phase 2 用 LLM）。"""
        # 匹配"在 XXX 公司"或"XXX 公司的"等模式
        patterns = [r"在(.{2,10}?)(?:公司|集团|企业|科技|有限)", r"(.{2,10}?)(?:公司|集团|企业|科技|有限)"]
        for pat in patterns:
            match = re.search(pat, text)
            if match:
                return match.group(1).strip()
        return None

    @staticmethod
    def _extract_position(text: str) -> str | None:
        """从文本中提取职位名称（简单启发式，Phase 2 用 LLM）。"""
        patterns = [r"(?:应聘|投递|面试)(.{2,20}?)(?:职位|岗位|工程师|开发|设计|运营|产品|经理)", r"(.{2,20}?)(?:工程师|开发|设计师|运营|产品经理)"]
        for pat in patterns:
            match = re.search(pat, text)
            if match:
                return match.group(1).strip() + (match.group(0).replace(match.group(1), "").split("职位")[0] if "职位" in match.group(0) else "")
        return None
