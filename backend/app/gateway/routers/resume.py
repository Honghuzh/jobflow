"""简历管理路由 — /api/resume 端点。"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, UploadFile

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "packages" / "harness"))

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/resume", tags=["resume"])


@router.post("/upload")
async def upload_resume(file: UploadFile, thread_id: str = "default") -> dict:
    """上传简历文件并保存。"""
    try:
        from app.gateway.uploads import save_upload

        saved_path = await save_upload(file, thread_id)
        return {"saved_path": saved_path, "filename": file.filename, "thread_id": thread_id}
    except ValueError as exc:
        return {"error": str(exc)}
    except Exception as exc:
        logger.error("上传简历失败: %s", exc)
        return {"error": str(exc)}


@router.post("/parse")
async def parse_resume_endpoint(file: UploadFile, thread_id: str = "default") -> dict:
    """上传并解析简历文件，返回结构化数据，并关联到线程。"""
    try:
        from app.gateway.uploads import save_upload

        saved_path = await save_upload(file, thread_id)
    except ValueError as exc:
        return {"error": str(exc)}
    except Exception as exc:
        logger.error("保存简历失败: %s", exc)
        return {"error": str(exc)}

    try:
        from jobflow.tools.builtins.resume_parser import parse_resume

        result = parse_resume.invoke({"file_path": saved_path})
        # 将解析结果持久化到线程状态中
        from app.gateway.thread_manager import get_thread_manager

        get_thread_manager().update_state(thread_id, {"resume_data": result})
        return result
    except Exception as exc:
        logger.error("解析简历失败: %s", exc)
        return {"error": str(exc), "raw_text": ""}


@router.get("/current")
async def get_current_resume(thread_id: str = "default") -> dict:
    """获取指定线程的当前解析简历数据。"""
    from app.gateway.thread_manager import get_thread_manager

    state = get_thread_manager().get_state(thread_id)
    if state is None or state.get("resume_data") is None:
        return {"resume_data": None, "message": "暂无简历数据"}
    return {"resume_data": state["resume_data"]}
