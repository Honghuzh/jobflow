"""投递进度路由 — /api/tracker 端点。"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "packages" / "harness"))

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tracker", tags=["tracker"])


class UpdateTrackerRequest(BaseModel):
    """更新投递状态请求体。"""

    company: str
    position: str
    status: str
    notes: str = ""


@router.post("/update")
async def update_tracker(request: UpdateTrackerRequest) -> dict:
    """更新投递状态。"""
    try:
        from jobflow.tools.builtins.job_tracker import update_job_status

        result = update_job_status.invoke({"company": request.company, "position": request.position, "status": request.status, "notes": request.notes})
        return result
    except Exception as exc:
        logger.error("update_job_status 调用失败: %s", exc)
        return {"error": str(exc)}


@router.get("/stats")
async def get_stats() -> dict:
    """获取投递统计数据。"""
    try:
        from jobflow.tools.builtins.job_tracker import get_job_stats

        result = get_job_stats.invoke({})
        return result
    except Exception as exc:
        logger.error("get_job_stats 调用失败: %s", exc)
        return {"error": str(exc), "total": 0, "by_status": {}, "recent_activities": []}


@router.get("/list")
async def list_applications() -> dict:
    """获取所有投递记录。"""
    import json
    from pathlib import Path as P

    tracker_path = P(".jobflow/tracker.json")
    if not tracker_path.exists():
        return {"applications": []}
    try:
        with open(tracker_path, encoding="utf-8") as f:
            data = json.load(f)
        return {"applications": data.get("applications", [])}
    except Exception as exc:
        logger.error("读取 tracker.json 失败: %s", exc)
        return {"applications": [], "error": str(exc)}
