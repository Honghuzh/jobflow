"""技能管理路由 — /api/skills 端点。"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "packages" / "harness"))

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/skills", tags=["skills"])

# Skills 目录（相对于仓库根）
_SKILLS_PATH = Path(__file__).parent.parent.parent.parent.parent.parent / "skills"


@router.get("")
async def list_skills() -> dict:
    """列出所有可用的 Skill。"""
    try:
        from jobflow.skills.loader import load_skills

        skills = load_skills(str(_SKILLS_PATH))
        return {
            "skills": [
                {
                    "name": s.name,
                    "description": s.description,
                    "author": s.author,
                    "version": s.version,
                    "allowed_tools": s.allowed_tools,
                }
                for s in skills
            ]
        }
    except Exception as exc:
        logger.warning("加载 Skills 失败: %s", exc)
        return {"skills": []}


@router.get("/{name}")
async def get_skill(name: str) -> dict:
    """获取指定 Skill 的详情。"""
    try:
        from jobflow.skills.loader import load_skills

        skills = load_skills(str(_SKILLS_PATH))
        for s in skills:
            if s.name == name:
                return {
                    "name": s.name,
                    "description": s.description,
                    "author": s.author,
                    "version": s.version,
                    "allowed_tools": s.allowed_tools,
                    "content": s.content,
                    "source_path": s.source_path,
                }
        raise HTTPException(status_code=404, detail=f"Skill '{name}' 不存在")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("获取 Skill 失败: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
