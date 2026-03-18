"""模型管理路由 — /api/models 端点。"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from fastapi import APIRouter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "packages" / "harness"))

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("")
async def list_models() -> dict:
    """列出可用的 LLM 模型配置。"""
    try:
        from jobflow.config.app_config import get_app_config

        cfg = get_app_config()
        models_cfg = cfg.get("models", [])
        models = []
        for m in models_cfg if isinstance(models_cfg, list) else []:
            models.append(
                {
                    "name": m.get("name", ""),
                    "display_name": m.get("display_name", m.get("name", "")),
                    "use": m.get("use", ""),
                }
            )
        return {"models": models}
    except Exception as exc:
        logger.warning("加载模型配置失败: %s", exc)
        return {"models": []}
