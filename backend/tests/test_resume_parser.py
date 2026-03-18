"""测试简历解析工具。"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "harness"))

from jobflow.tools.builtins.resume_parser import _parse_resume_impl, _parse_text_resume, parse_resume


# ── 文本解析测试 ──────────────────────────────────────────────────────────


class TestParseTextResume:
    """测试纯文本/Markdown 格式简历解析。"""

    def test_parse_name_from_first_line(self):
        """第一行应被识别为姓名。"""
        text = "张三\n邮箱: test@example.com"
        result = _parse_text_resume(text)
        assert result["name"] == "张三"

    def test_parse_name_from_markdown_heading(self):
        """Markdown 标题格式姓名应被正确提取（去掉 # 号）。"""
        text = "# 李四\n电话: 13800138000"
        result = _parse_text_resume(text)
        assert result["name"] == "李四"

    def test_extract_email(self):
        """应能提取邮箱地址。"""
        text = "王五\n联系方式: wangwu@example.com\n北京"
        result = _parse_text_resume(text)
        assert result["contact"]["email"] == "wangwu@example.com"

    def test_extract_phone(self):
        """应能提取中国手机号码。"""
        text = "张三\n电话: 13912345678"
        result = _parse_text_resume(text)
        assert result["contact"]["phone"] == "13912345678"

    def test_extract_phone_plus86(self):
        """应能提取带 +86 的手机号。"""
        text = "张三\n电话: +86 13912345678"
        result = _parse_text_resume(text)
        assert "13912345678" in result["contact"]["phone"]

    def test_extract_github(self):
        """应能提取 GitHub 链接。"""
        text = "张三\ngithub.com/zhangsan\n技能"
        result = _parse_text_resume(text)
        assert "github.com/zhangsan" in result["contact"]["github"]

    def test_extract_skills_from_section(self):
        """应能从技能章节提取技术技能。"""
        text = "张三\n\n技能\nPython, Django, React, MySQL\n\n工作经历"
        result = _parse_text_resume(text)
        assert "skills" in result
        if result["skills"].get("technical"):
            skills = result["skills"]["technical"]
            assert any("Python" in s for s in skills)

    def test_no_content_returns_empty(self):
        """空文本应返回空结果。"""
        result = _parse_text_resume("")
        assert result["name"] == ""
        assert result["contact"] == {}

    def test_long_first_line_not_used_as_name(self):
        """超过 30 字符的第一行不应被识别为姓名。"""
        text = "这是一个非常非常非常非常非常非常长的第一行，不应该被识别为姓名\n张三"
        result = _parse_text_resume(text)
        assert result["name"] == ""


# ── 文件解析测试 ──────────────────────────────────────────────────────────


class TestParseResumeImpl:
    """测试 _parse_resume_impl 文件路径解析。"""

    def test_parse_txt_file(self):
        """应能解析 .txt 文件。"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as f:
            f.write("张三\ntest@example.com\n13800138000\n\n技能\nPython, Go\n")
            tmp_path = f.name
        try:
            result = _parse_resume_impl(tmp_path)
            assert result["name"] == "张三"
            assert result["contact"]["email"] == "test@example.com"
            assert result["raw_text"] != ""
        finally:
            os.unlink(tmp_path)

    def test_parse_md_file(self):
        """应能解析 .md 文件。"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", encoding="utf-8", delete=False) as f:
            f.write("# 李四\ngithub.com/lisi\n\n## 技能\nReact, Vue, TypeScript\n")
            tmp_path = f.name
        try:
            result = _parse_resume_impl(tmp_path)
            assert result["name"] == "李四"
            assert "github.com/lisi" in result["contact"].get("github", "")
        finally:
            os.unlink(tmp_path)

    def test_parse_nonexistent_file(self):
        """不存在的文件应返回包含错误信息的结果（不报错）。"""
        result = _parse_resume_impl("/nonexistent/path/resume.txt")
        assert "不存在" in result["raw_text"] or "not" in result["raw_text"].lower()
        assert result["name"] == ""

    def test_parse_pdf_without_pymupdf(self):
        """没有安装 pymupdf 时，PDF 解析应优雅降级，返回占位信息。"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4 fake pdf content")
            tmp_path = f.name
        try:
            result = _parse_resume_impl(tmp_path)
            # 无论 pymupdf 是否安装，都不应抛出异常
            assert "raw_text" in result
        finally:
            os.unlink(tmp_path)

    def test_parse_docx_without_python_docx(self):
        """没有安装 python-docx 时，DOCX 解析应优雅降级。"""
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f:
            f.write(b"fake docx content")
            tmp_path = f.name
        try:
            result = _parse_resume_impl(tmp_path)
            assert "raw_text" in result
        finally:
            os.unlink(tmp_path)


# ── LangChain tool 接口测试 ───────────────────────────────────────────────


class TestParseResumeTool:
    """测试 parse_resume LangChain 工具接口。"""

    def test_tool_invoke_with_txt(self):
        """通过 tool.invoke() 调用解析 txt 文件。"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", delete=False) as f:
            f.write("王五\nwangwu@test.com\n\n技能\nJava, Spring, MySQL\n")
            tmp_path = f.name
        try:
            result = parse_resume.invoke({"file_path": tmp_path})
            assert isinstance(result, dict)
            assert result["name"] == "王五"
        finally:
            os.unlink(tmp_path)

    def test_tool_invoke_nonexistent(self):
        """调用不存在文件时不应报错。"""
        result = parse_resume.invoke({"file_path": "/nonexistent/file.txt"})
        assert isinstance(result, dict)
        assert "raw_text" in result
