"""测试 FastAPI Gateway 路由。"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import pytest_asyncio

# 确保 harness 和 app 都可被导入
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "harness"))
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from fastapi.testclient import TestClient

from app.gateway.app import app


# ── 同步测试客户端 ─────────────────────────────────────────────────────────


@pytest.fixture
def client():
    """返回 TestClient 实例。"""
    return TestClient(app)


# ── 健康检查 ─────────────────────────────────────────────────────────────


class TestHealthCheck:
    """测试 /health 端点。"""

    def test_health_ok(self, client):
        """GET /health 应返回 200 和 status=ok。"""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "service" in data

    def test_config_endpoint(self, client):
        """GET /api/config 应返回 200。"""
        resp = client.get("/api/config")
        assert resp.status_code == 200
        data = resp.json()
        assert "models" in data
        assert "memory_enabled" in data


# ── 对话路由 ─────────────────────────────────────────────────────────────


class TestChatRouter:
    """测试 /api/chat 端点。"""

    def test_chat_returns_thread_id(self, client):
        """POST /api/chat 应返回 thread_id 和 response。"""
        resp = client.post("/api/chat", json={"message": "你好，帮我分析一下这个职位"})
        assert resp.status_code == 200
        data = resp.json()
        assert "thread_id" in data
        assert "response" in data
        assert "artifacts" in data
        assert isinstance(data["thread_id"], str)
        assert len(data["thread_id"]) > 0

    def test_chat_with_thread_id(self, client):
        """POST /api/chat 传入 thread_id 时应复用该线程。"""
        # 第一次对话创建线程
        resp1 = client.post("/api/chat", json={"message": "第一条消息"})
        thread_id = resp1.json()["thread_id"]

        # 第二次对话使用同一线程
        resp2 = client.post("/api/chat", json={"message": "第二条消息", "thread_id": thread_id})
        assert resp2.status_code == 200
        assert resp2.json()["thread_id"] == thread_id

    def test_chat_with_resume_data(self, client):
        """POST /api/chat 带简历数据应正常处理。"""
        resp = client.post(
            "/api/chat",
            json={
                "message": "分析我的简历",
                "resume_data": {"name": "张三", "raw_text": "Python工程师，5年经验"},
            },
        )
        assert resp.status_code == 200

    def test_chat_stream_returns_event_stream(self, client):
        """POST /api/chat/stream 应返回 text/event-stream。"""
        with client.stream("POST", "/api/chat/stream", json={"message": "测试流式输出"}) as resp:
            assert resp.status_code == 200
            assert "text/event-stream" in resp.headers.get("content-type", "")


# ── 岗位路由 ─────────────────────────────────────────────────────────────


class TestJobsRouter:
    """测试 /api/jobs 端点。"""

    def test_parse_jd_text(self, client):
        """POST /api/jobs/parse-jd 应解析 JD 文本。"""
        jd_text = """
        Python 工程师
        字节跳动 | 北京 | 25k-35k

        职位要求：
        - Python 3年以上经验
        - 熟悉 Django / FastAPI
        - 了解 Docker、Kubernetes

        工作职责：
        - 负责后端服务开发
        - 参与系统架构设计
        """
        resp = client.post("/api/jobs/parse-jd", json={"text": jd_text})
        assert resp.status_code == 200
        data = resp.json()
        assert "raw_text" in data or "title" in data

    def test_parse_jd_empty_returns_error(self, client):
        """POST /api/jobs/parse-jd 无内容时返回错误。"""
        resp = client.post("/api/jobs/parse-jd", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "error" in data

    def test_match_score(self, client):
        """POST /api/jobs/match 应返回匹配度评分。"""
        resp = client.post(
            "/api/jobs/match",
            json={
                "resume_text": "Python 工程师，5年经验，熟悉 Django、React、MySQL、Docker",
                "jd_text": "要求：Python 3年以上，熟悉 Django 或 FastAPI，了解 Docker",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "overall_score" in data
        assert isinstance(data["overall_score"], (int, float))
        assert 0 <= data["overall_score"] <= 100


# ── 投递追踪路由 ──────────────────────────────────────────────────────────


class TestTrackerRouter:
    """测试 /api/tracker 端点。"""

    def test_get_stats(self, client):
        """GET /api/tracker/stats 应返回统计数据。"""
        resp = client.get("/api/tracker/stats")
        assert resp.status_code == 200
        data = resp.json()
        # 允许 total 字段或 error 字段（无数据文件时）
        assert "total" in data or "error" in data

    def test_list_applications(self, client):
        """GET /api/tracker/list 应返回投递记录列表。"""
        resp = client.get("/api/tracker/list")
        assert resp.status_code == 200
        data = resp.json()
        assert "applications" in data
        assert isinstance(data["applications"], list)

    def test_update_tracker(self, client):
        """POST /api/tracker/update 应更新投递状态。"""
        resp = client.post(
            "/api/tracker/update",
            json={
                "company": "测试公司",
                "position": "Python 工程师",
                "status": "applied",
                "notes": "已投递",
            },
        )
        assert resp.status_code == 200


# ── 技能路由 ─────────────────────────────────────────────────────────────


class TestSkillsRouter:
    """测试 /api/skills 端点。"""

    def test_list_skills(self, client):
        """GET /api/skills 应返回技能列表。"""
        resp = client.get("/api/skills")
        assert resp.status_code == 200
        data = resp.json()
        assert "skills" in data
        assert isinstance(data["skills"], list)

    def test_get_skill_not_found(self, client):
        """GET /api/skills/{name} 不存在时应返回 404。"""
        resp = client.get("/api/skills/nonexistent_skill_xyz")
        assert resp.status_code == 404


# ── 模型路由 ─────────────────────────────────────────────────────────────


class TestModelsRouter:
    """测试 /api/models 端点。"""

    def test_list_models(self, client):
        """GET /api/models 应返回模型列表。"""
        resp = client.get("/api/models")
        assert resp.status_code == 200
        data = resp.json()
        assert "models" in data
        assert isinstance(data["models"], list)
