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
    """上传并【解析】简历。"""
    try:
        from app.gateway.uploads import save_upload
        from jobflow.tools.builtins.resume_parser import parse_resume
        from app.gateway.thread_manager import get_thread_manager

        # 1. 保存
        saved_path = await save_upload(file, thread_id)
        
        # 2. 解析 (把 parse 的逻辑挪过来)
        result = parse_resume.invoke({"file_path": saved_path})
        
        # 3. 持久化到线程
        get_thread_manager().update_state(thread_id, {"resume_data": result})
        
        # 4. 返回完整结果（包含 content/text），这样前端 Payload 就不再只是路径了
        return result 
    except Exception as exc:
        logger.error("上传并解析简历失败: %s", exc)
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
