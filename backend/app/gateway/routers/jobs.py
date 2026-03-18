"""岗位管理路由 — /api/jobs 端点。"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "packages" / "harness"))

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


class ParseJDRequest(BaseModel):
    """解析 JD 请求体（支持文本或 URL）。"""

    text: str | None = None
    url: str | None = None


class MatchRequest(BaseModel):
    """匹配度计算请求体。"""

    resume_text: str
    jd_text: str


@router.post("/parse-jd")
async def parse_jd_endpoint(request: ParseJDRequest) -> dict:
    """解析 JD 文本，返回结构化数据。"""
    text = request.text or ""
    if not text and request.url:
        # Phase 3: 抓取 URL 内容
        text = f"（URL 抓取暂不支持: {request.url}）"

    if not text:
        return {"error": "请提供 text 或 url"}

    try:
        from jobflow.tools.builtins.jd_parser import parse_jd

        result = parse_jd.invoke({"text": text})
        return result
    except Exception as exc:
        logger.error("parse_jd 调用失败: %s", exc)
        return {"error": str(exc), "raw_text": text}


@router.post("/match")
async def match_endpoint(request: MatchRequest) -> dict:
    """计算简历与 JD 的匹配度。"""
    try:
        from jobflow.tools.builtins.match_scorer import match_score

        result = match_score.invoke({"resume_text": request.resume_text, "jd_text": request.jd_text})
        return result
    except Exception as exc:
        logger.error("match_score 调用失败: %s", exc)
        return {"error": str(exc), "overall_score": 0}
