"""FastAPI Gateway — JobFlow 后端主入口。"""
from __future__ import annotations

import sys
from pathlib import Path

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 确保 harness 包可被导入
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "harness"))

from app.gateway.routers.chat import router as chat_router
from app.gateway.routers.jobs import router as jobs_router
from app.gateway.routers.models_route import router as models_router
from app.gateway.routers.resume import router as resume_router
from app.gateway.routers.skills import router as skills_router
from app.gateway.routers.tracker import router as tracker_router

app = FastAPI(
    title="JobFlow API",
    description="智能求职 Agent 后端 API",
    version="0.2.0",
)

# CORS — 通过环境变量控制允许的来源，默认允许所有（开发阶段）
# 生产部署时应设置 CORS_ORIGINS 环境变量，例如：CORS_ORIGINS="https://example.com,https://app.example.com"
_cors_origins_env = os.getenv("CORS_ORIGINS", "")
_allowed_origins = [o.strip() for o in _cors_origins_env.split(",") if o.strip()] or ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(chat_router)
app.include_router(jobs_router)
app.include_router(tracker_router)
app.include_router(resume_router)
app.include_router(skills_router)
app.include_router(models_router)


@app.get("/health")
async def health_check() -> dict:
    """健康检查端点。"""
    return {"status": "ok", "service": "jobflow-gateway"}


@app.get("/api/config")
async def get_config() -> dict:
    """返回当前配置信息（不含敏感信息）。"""
    try:
        from jobflow.config.app_config import get_app_config

        cfg = get_app_config()
        return {
            "models": [{"name": m.get("name", ""), "display_name": m.get("display_name", "")} for m in (cfg.get("models", []) if isinstance(cfg.get("models"), list) else [])],
            "memory_enabled": bool(cfg.get("memory", {}).get("enabled", False)),
            "subagents_enabled": bool(cfg.get("subagents", {}).get("enabled", False)),
        }
    except Exception:
        return {"models": [], "memory_enabled": False, "subagents_enabled": False}
