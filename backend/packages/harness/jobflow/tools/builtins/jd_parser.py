"""JD 解析工具 — 将职位描述文本解析为结构化数据。"""
from __future__ import annotations

import re

from langchain_core.tools import tool


@tool
def parse_jd(text: str) -> dict:
    """将 JD 文本解析为结构化数据。

    Args:
        text: 职位描述原始文本

    Returns:
        包含 title, company, location, salary, requirements, responsibilities, benefits 的字典
    """
    return _parse_jd_impl(text)


def _parse_jd_impl(text: str) -> dict:
    """JD 解析的内部实现（可在测试中直接调用）。"""
    result: dict = {
        "title": "",
        "company": "",
        "location": "",
        "salary": "",
        "requirements": [],
        "responsibilities": [],
        "benefits": [],
        "raw_text": text,
    }

    lines = text.strip().splitlines()
    if not lines:
        return result

    # 提取职位名称（通常在第一行或 "职位：" 后）
    for line in lines[:5]:
        line = line.strip()
        if line and not any(kw in line for kw in ["公司", "地点", "薪资", "要求", "职责"]):
            if not result["title"]:
                result["title"] = line
                break

    # 提取各字段
    current_section = None
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 检测 section 标题
        lower = line.lower()
        if any(kw in lower for kw in ["job requirements", "任职要求", "岗位要求", "requirements"]):
            current_section = "requirements"
            continue
        elif any(kw in lower for kw in ["responsibilities", "工作职责", "岗位职责", "job duties"]):
            current_section = "responsibilities"
            continue
        elif any(kw in lower for kw in ["benefits", "福利", "待遇"]):
            current_section = "benefits"
            continue

        # 提取字段值
        if "公司" in line or "company" in lower:
            match = re.search(r"[:：]\s*(.+)", line)
            if match:
                result["company"] = match.group(1).strip()
        elif "地点" in line or "location" in lower or "城市" in line:
            match = re.search(r"[:：]\s*(.+)", line)
            if match:
                result["location"] = match.group(1).strip()
        elif "薪资" in line or "salary" in lower or "薪酬" in line:
            match = re.search(r"[:：]\s*(.+)", line)
            if match:
                result["salary"] = match.group(1).strip()
        elif current_section and (line.startswith("-") or line.startswith("•") or line.startswith("*") or (len(line) > 2 and line[0].isdigit())):
            # 列表项
            item = re.sub(r"^[-•*\d.]\s*", "", line).strip()
            if item:
                result[current_section].append(item)

    return result
