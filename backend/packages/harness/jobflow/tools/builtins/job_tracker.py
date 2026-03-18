"""求职进度追踪工具 — 管理投递记录。"""
from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

_DEFAULT_TRACKER_PATH = ".jobflow/tracker.json"

VALID_STATUSES = {"wishlist", "applied", "phone_screen", "interview", "offer", "rejected"}


@tool
def update_job_status(company: str, position: str, status: str, notes: str = "") -> dict:
    """更新求职投递进度。

    Args:
        company: 公司名称
        position: 职位名称
        status: 投递状态（wishlist/applied/phone_screen/interview/offer/rejected）
        notes: 备注信息

    Returns:
        更新后的投递记录
    """
    return _update_job_status_impl(company, position, status, notes)


@tool
def get_job_stats() -> dict:
    """获取求职进度统计。

    Returns:
        包含 total, by_status, recent_activities 的统计字典
    """
    return _get_job_stats_impl()


def _update_job_status_impl(company: str, position: str, status: str, notes: str = "", tracker_path: str = _DEFAULT_TRACKER_PATH) -> dict:
    """update_job_status 的内部实现。"""
    if status not in VALID_STATUSES:
        return {"error": f"无效状态 '{status}'，有效值：{sorted(VALID_STATUSES)}"}

    tracker = _load_tracker(tracker_path)
    applications = tracker.get("applications", [])

    # 查找现有记录（公司+职位为 key）
    existing = next((a for a in applications if a.get("company") == company and a.get("position") == position), None)
    now = datetime.now(timezone.utc).isoformat()

    if existing:
        old_status = existing.get("status", "")
        existing["status"] = status
        existing["updated_at"] = now
        if notes:
            existing["notes"] = notes
        if old_status != status:
            existing.setdefault("history", []).append({"from": old_status, "to": status, "at": now})
        record = existing
    else:
        record = {
            "company": company,
            "position": position,
            "status": status,
            "applied_at": now,
            "updated_at": now,
            "notes": notes,
            "history": [{"from": "", "to": status, "at": now}],
        }
        applications.append(record)

    tracker["applications"] = applications
    _save_tracker(tracker, tracker_path)
    logger.info("update_job_status: %s @ %s → %s", position, company, status)
    return record


def _get_job_stats_impl(tracker_path: str = _DEFAULT_TRACKER_PATH) -> dict:
    """get_job_stats 的内部实现。"""
    tracker = _load_tracker(tracker_path)
    applications = tracker.get("applications", [])

    by_status: dict[str, int] = {s: 0 for s in VALID_STATUSES}
    for app in applications:
        s = app.get("status", "")
        if s in by_status:
            by_status[s] += 1

    # 最近活动（最近 5 条，按 updated_at 排序）
    sorted_apps = sorted(applications, key=lambda a: a.get("updated_at", ""), reverse=True)
    recent = [{"company": a.get("company"), "position": a.get("position"), "status": a.get("status"), "updated_at": a.get("updated_at")} for a in sorted_apps[:5]]

    return {
        "total": len(applications),
        "by_status": by_status,
        "recent_activities": recent,
    }


def _load_tracker(tracker_path: str = _DEFAULT_TRACKER_PATH) -> dict:
    """从文件加载投递记录，文件不存在时返回空字典。"""
    path = Path(tracker_path)
    if not path.exists():
        return {"applications": []}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.error("_load_tracker: 读取失败 — %s", exc)
        return {"applications": []}


def _save_tracker(data: dict, tracker_path: str = _DEFAULT_TRACKER_PATH) -> None:
    """原子写入投递记录文件（temp file + rename）。"""
    path = Path(tracker_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=".tracker_", suffix=".json")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        os.unlink(tmp_path)
        raise
