"""测试 Middleware Chain — 中间件顺序执行和各领域中间件。"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "harness"))

from jobflow.agents.middlewares.base import Middleware, MiddlewareChain
from jobflow.agents.middlewares.job_context_middleware import JobContextMiddleware
from jobflow.agents.middlewares.progress_middleware import ProgressMiddleware
from jobflow.agents.middlewares.resume_parse_middleware import ResumeParseMiddleware


# ── 测试工具：可记录调用顺序的中间件 ──────────────────────────────────


class OrderTrackingMiddleware(Middleware):
    """记录调用顺序的测试中间件。"""

    def __init__(self, label: str, log: list):
        self.label = label
        self.log = log

    async def before_agent(self, state: dict, config: dict) -> dict | None:
        self.log.append(f"before:{self.label}")
        return None

    async def after_agent(self, state: dict, response, config: dict):
        self.log.append(f"after:{self.label}")
        return response


# ── MiddlewareChain 测试 ──────────────────────────────────────────────


class TestMiddlewareChain:
    """测试 MiddlewareChain 的核心行为。"""

    @pytest.mark.asyncio
    async def test_before_order(self):
        """before_agent 按注册顺序执行（A→B→C）。"""
        log = []
        chain = MiddlewareChain([
            OrderTrackingMiddleware("A", log),
            OrderTrackingMiddleware("B", log),
            OrderTrackingMiddleware("C", log),
        ])
        await chain.run_before({}, {})
        assert log == ["before:A", "before:B", "before:C"]

    @pytest.mark.asyncio
    async def test_after_order(self):
        """after_agent 按逆序执行（C→B→A）。"""
        log = []
        chain = MiddlewareChain([
            OrderTrackingMiddleware("A", log),
            OrderTrackingMiddleware("B", log),
            OrderTrackingMiddleware("C", log),
        ])
        await chain.run_after({}, {}, {})
        assert log == ["after:C", "after:B", "after:A"]

    @pytest.mark.asyncio
    async def test_state_update_merge(self):
        """before_agent 返回的更新应合并到 state。"""

        class AddKeyMiddleware(Middleware):
            async def before_agent(self, state: dict, config: dict) -> dict | None:
                return {"new_key": "new_value"}

            async def after_agent(self, state: dict, response, config: dict):
                return response

        chain = MiddlewareChain([AddKeyMiddleware()])
        updated = await chain.run_before({"existing": 1}, {})
        assert updated["new_key"] == "new_value"
        assert updated["existing"] == 1

    def test_add_method(self):
        """add() 方法支持链式调用。"""
        log = []
        chain = MiddlewareChain()
        chain.add(OrderTrackingMiddleware("X", log)).add(OrderTrackingMiddleware("Y", log))
        assert len(chain.middlewares) == 2

    @pytest.mark.asyncio
    async def test_empty_chain(self):
        """空 chain 不报错，直接返回原 state。"""
        chain = MiddlewareChain()
        state = {"key": "value"}
        result = await chain.run_before(state, {})
        assert result == state


# ── ResumeParseMiddleware 测试 ──────────────────────────────────────


class TestResumeParseMiddleware:
    """测试简历解析中间件。"""

    def test_is_resume_file_pdf(self):
        """PDF 文件应被识别为简历文件。"""
        assert ResumeParseMiddleware._is_resume_file("resume.pdf") is True

    def test_is_resume_file_docx(self):
        """DOCX 文件应被识别为简历文件。"""
        assert ResumeParseMiddleware._is_resume_file("my_resume.docx") is True

    def test_is_resume_file_doc(self):
        """DOC 文件应被识别为简历文件。"""
        assert ResumeParseMiddleware._is_resume_file("cv.doc") is True

    def test_is_resume_file_md(self):
        """Markdown 文件应被识别为简历文件。"""
        assert ResumeParseMiddleware._is_resume_file("resume.md") is True

    def test_is_resume_file_txt(self):
        """TXT 文件应被识别为简历文件。"""
        assert ResumeParseMiddleware._is_resume_file("cv.txt") is True

    def test_is_resume_file_jpg(self):
        """图片文件不应被识别为简历文件。"""
        assert ResumeParseMiddleware._is_resume_file("photo.jpg") is False

    def test_is_resume_file_xlsx(self):
        """Excel 文件不应被识别为简历文件。"""
        assert ResumeParseMiddleware._is_resume_file("data.xlsx") is False

    def test_is_resume_file_case_insensitive(self):
        """扩展名应不区分大小写。"""
        assert ResumeParseMiddleware._is_resume_file("Resume.PDF") is True

    @pytest.mark.asyncio
    async def test_skip_if_resume_data_exists(self):
        """如果 state 已有 resume_data，跳过解析。"""
        mw = ResumeParseMiddleware()
        state = {"resume_data": {"name": "existing"}, "uploaded_files": ["resume.pdf"]}
        result = await mw.before_agent(state, {})
        assert result is None

    @pytest.mark.asyncio
    async def test_skip_if_no_uploaded_files(self):
        """没有上传文件时，跳过解析。"""
        mw = ResumeParseMiddleware()
        result = await mw.before_agent({}, {})
        assert result is None


# ── JobContextMiddleware 测试 ─────────────────────────────────────────


class TestJobContextMiddleware:
    """测试岗位上下文中间件。"""

    @pytest.mark.asyncio
    async def test_no_target_job_returns_none(self):
        """没有 target_job 时，不更新 state。"""
        mw = JobContextMiddleware()
        result = await mw.before_agent({}, {})
        assert result is None

    @pytest.mark.asyncio
    async def test_with_target_job_generates_context(self):
        """有 target_job 时，生成 job_context_text。"""
        mw = JobContextMiddleware()
        state = {
            "target_job": {
                "title": "Python 工程师",
                "company": "字节跳动",
                "location": "北京",
                "requirements": ["Python 3年以上"],
            }
        }
        result = await mw.before_agent(state, {})
        assert result is not None
        assert "job_context_text" in result
        assert "Python 工程师" in result["job_context_text"]
        assert "字节跳动" in result["job_context_text"]

    @pytest.mark.asyncio
    async def test_after_agent_passthrough(self):
        """after_agent 直接返回响应，不修改。"""
        mw = JobContextMiddleware()
        response = {"some": "response"}
        result = await mw.after_agent({}, response, {})
        assert result is response


# ── ProgressMiddleware 测试 ────────────────────────────────────────────


class TestProgressMiddleware:
    """测试投递进度中间件。"""

    @pytest.mark.asyncio
    async def test_before_agent_returns_none(self):
        """before_agent 不做任何处理。"""
        mw = ProgressMiddleware()
        result = await mw.before_agent({}, {})
        assert result is None

    @pytest.mark.asyncio
    async def test_detect_applied_status(self):
        """检测到"已投递"关键词，更新状态。"""
        mw = ProgressMiddleware()
        state = {
            "messages": [{"content": "我已投递了字节跳动Python工程师职位"}],
            "job_applications": [],
        }
        response = {"messages": state["messages"]}
        result = await mw.after_agent(state, response, {})
        # 触发了状态检测（不强制要求提取到公司，但不能报错）
        assert result is not None

    @pytest.mark.asyncio
    async def test_no_messages_passthrough(self):
        """没有消息时，直接返回响应。"""
        mw = ProgressMiddleware()
        state = {"messages": []}
        response = {"data": "test"}
        result = await mw.after_agent(state, response, {})
        assert result == response

    def test_detect_status_offer(self):
        """检测 offer 关键词。"""
        status = ProgressMiddleware._detect_status("恭喜！我收到了 offer！")
        assert status == "offer"

    def test_detect_status_rejected(self):
        """检测 rejected 关键词。"""
        status = ProgressMiddleware._detect_status("收到了拒信，很遗憾")
        assert status == "rejected"

    def test_detect_status_none(self):
        """普通文本不触发状态检测。"""
        status = ProgressMiddleware._detect_status("今天天气不错")
        assert status is None
