"""简历解析工具 — 将简历文件解析为结构化数据。"""
from __future__ import annotations

import logging
import os
import re

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def parse_resume(file_path: str) -> dict:
    """解析简历文件为结构化数据。

    支持 .md 和 .txt 格式（Phase 2 扩展 PDF/Word 支持）。

    Args:
        file_path: 简历文件路径

    Returns:
        包含 name, contact, education, experience, skills, projects 的字典
    """
    return _parse_resume_impl(file_path)


def _parse_resume_impl(file_path: str) -> dict:
    """简历解析的内部实现（可在测试中直接调用）。"""
    result: dict = {
        "name": "",
        "contact": {},
        "education": [],
        "experience": [],
        "skills": {},
        "projects": [],
        "raw_text": "",
    }

    if not os.path.exists(file_path):
        logger.warning("parse_resume: 文件不存在 — %s", file_path)
        result["raw_text"] = f"[文件不存在: {file_path}]"
        return result

    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext in (".md", ".txt"):
            with open(file_path, encoding="utf-8") as f:
                text = f.read()
            result["raw_text"] = text
            result.update(_parse_text_resume(text))
        elif ext == ".pdf":
            result.update(_parse_pdf(file_path, result))
        elif ext in (".docx", ".doc"):
            result.update(_parse_docx(file_path, result))
        else:
            logger.warning("parse_resume: 暂不支持 %s 格式", ext)
            result["raw_text"] = f"[不支持的格式: {file_path}]"
    except Exception as exc:
        logger.error("parse_resume: 解析失败 — %s", exc)
        result["raw_text"] = f"[解析失败: {exc}]"

    return result


def _parse_text_resume(text: str) -> dict:
    """解析纯文本/Markdown 格式简历。"""
    result: dict = {"name": "", "contact": {}, "education": [], "experience": [], "skills": {}, "projects": []}

    lines = text.strip().splitlines()
    if not lines:
        return result

    # 名字通常在第一行（# 标题或直接文字）
    first_line = lines[0].strip().lstrip("#").strip()
    if first_line and len(first_line) < 30:
        result["name"] = first_line

    # 联系方式提取（邮箱、电话、GitHub）
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]+", text)
    if email_match:
        result["contact"]["email"] = email_match.group()

    phone_match = re.search(r"(?:1[3-9]\d{9}|\+86\s?1[3-9]\d{9})", text)
    if phone_match:
        result["contact"]["phone"] = phone_match.group()

    github_match = re.search(r"github\.com/[\w-]+", text)
    if github_match:
        result["contact"]["github"] = github_match.group()

    # 技能关键词提取（从技能 section）
    skill_section_match = re.search(r"(?:技能|skills)[^\n]*\n(.*?)(?=\n#|\Z)", text, re.IGNORECASE | re.DOTALL)
    if skill_section_match:
        skill_text = skill_section_match.group(1)
        # 简单提取：按逗号/分号/换行分割
        skill_items = re.split(r"[,，;；\n|]", skill_text)
        skills = [s.strip().lstrip("-•*").strip() for s in skill_items if s.strip() and len(s.strip()) < 50]
        if skills:
            result["skills"]["technical"] = [s for s in skills if s]

    return result


def _parse_pdf(file_path: str, result: dict) -> dict:
    """尝试用 pymupdf 解析 PDF，未安装时返回文件名占位。"""
    try:
        import fitz  # pymupdf

        text_parts = []
        with fitz.open(file_path) as doc:
            for page in doc:
                text_parts.append(page.get_text())
        text = "\n".join(text_parts)
        result["raw_text"] = text
        result.update(_parse_text_resume(text))
    except ImportError:
        logger.warning("parse_resume: pymupdf 未安装，无法解析 PDF，请运行 pip install pymupdf")
        result["raw_text"] = f"[PDF 文件: {file_path}（需安装 pymupdf 才能解析）]"
    except Exception as exc:
        logger.error("parse_resume: PDF 解析失败 — %s", exc)
        result["raw_text"] = f"[PDF 解析失败: {exc}]"
    return result


def _parse_docx(file_path: str, result: dict) -> dict:
    """尝试用 python-docx 解析 DOCX/DOC，未安装时返回文件名占位。"""
    try:
        from docx import Document

        doc = Document(file_path)
        text = "\n".join(para.text for para in doc.paragraphs)
        result["raw_text"] = text
        result.update(_parse_text_resume(text))
    except ImportError:
        logger.warning("parse_resume: python-docx 未安装，无法解析 Word 文档，请运行 pip install python-docx")
        result["raw_text"] = f"[Word 文件: {file_path}（需安装 python-docx 才能解析）]"
    except Exception as exc:
        logger.error("parse_resume: DOCX 解析失败 — %s", exc)
        result["raw_text"] = f"[DOCX 解析失败: {exc}]"
    return result
