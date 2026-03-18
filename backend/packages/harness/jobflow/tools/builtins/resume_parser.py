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
        else:
            # Phase 2: 支持 PDF/Word
            logger.warning("parse_resume: 暂不支持 %s 格式，Phase 2 实现", ext)
            with open(file_path, "rb") as f:
                result["raw_text"] = f"[二进制文件: {file_path}，Phase 2 支持解析]"
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
