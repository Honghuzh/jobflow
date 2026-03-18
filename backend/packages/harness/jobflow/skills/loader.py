"""Skill 加载器 — 扫描并解析 SKILL.md 文件。"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """已加载的 Skill 定义。"""

    name: str
    description: str = ""
    author: str = ""
    version: str = "1.0.0"
    allowed_tools: list[str] = field(default_factory=list)
    content: str = ""  # SKILL.md 的 Markdown 正文
    source_path: str = ""


def load_skills(skills_path: str | Path = "skills") -> list[Skill]:
    """递归扫描指定目录下的所有 SKILL.md 文件并解析。

    Args:
        skills_path: skills 根目录路径（扫描 public/ 和 custom/ 子目录）

    Returns:
        解析成功的 Skill 列表
    """
    root = Path(skills_path)
    if not root.exists():
        logger.warning("load_skills: 目录不存在 — %s", root)
        return []

    skills: list[Skill] = []
    skill_files = list(root.rglob("SKILL.md"))

    for skill_file in sorted(skill_files):
        try:
            skill = _parse_skill_file(skill_file)
            skills.append(skill)
            logger.info("load_skills: 加载 Skill '%s'（%s）", skill.name, skill_file)
        except Exception as exc:
            logger.error("load_skills: 解析 %s 失败 — %s", skill_file, exc)

    logger.info("load_skills: 共加载 %d 个 Skill", len(skills))
    return skills


def _parse_skill_file(path: Path) -> Skill:
    """解析单个 SKILL.md 文件。"""
    text = path.read_text(encoding="utf-8")

    # 解析 YAML frontmatter
    frontmatter: dict = {}
    content = text

    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        content = fm_match.group(2).strip()
        frontmatter = _parse_simple_yaml(fm_text)

    name = frontmatter.get("name", path.parent.name)
    description = frontmatter.get("description", "")
    author = frontmatter.get("author", "")
    version = str(frontmatter.get("version", "1.0.0"))

    # allowed-tools 可以是字符串或列表
    allowed_tools_raw = frontmatter.get("allowed-tools", [])
    if isinstance(allowed_tools_raw, str):
        allowed_tools = [t.strip() for t in allowed_tools_raw.split(",") if t.strip()]
    elif isinstance(allowed_tools_raw, list):
        allowed_tools = [str(t).strip() for t in allowed_tools_raw]
    else:
        allowed_tools = []

    return Skill(
        name=name,
        description=description,
        author=author,
        version=version,
        allowed_tools=allowed_tools,
        content=content,
        source_path=str(path),
    )


def _parse_simple_yaml(text: str) -> dict:
    """简单 YAML 解析（仅支持基本 key: value 和列表）。"""
    result: dict = {}
    current_key: str | None = None
    current_list: list | None = None

    for line in text.splitlines():
        # 列表项
        if line.startswith("  - ") and current_key and current_list is not None:
            current_list.append(line[4:].strip())
            continue

        # key: value 或 key:（列表开始）
        kv_match = re.match(r"^([\w-]+):\s*(.*)", line)
        if kv_match:
            # 保存上一个列表
            if current_key and current_list is not None:
                result[current_key] = current_list

            current_key = kv_match.group(1)
            value = kv_match.group(2).strip()

            if value == "":
                # 后续为列表
                current_list = []
            else:
                # 移除引号
                value = value.strip("\"'")
                result[current_key] = value
                current_list = None
        elif line.startswith("- ") and current_key and current_list is not None:
            current_list.append(line[2:].strip())

    # 保存最后一个列表
    if current_key and current_list is not None:
        result[current_key] = current_list

    return result
