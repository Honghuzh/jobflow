"""MemoryUpdater — 求职记忆的读写与更新。"""
from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

from .prompt import MEMORY_UPDATE_PROMPT

logger = logging.getLogger(__name__)

_DEFAULT_MEMORY_PATH = ".jobflow/memory.json"

_EMPTY_MEMORY: dict[str, Any] = {
    "job_preference": {
        "target_roles": [],
        "target_industries": [],
        "target_cities": [],
        "salary_expectation": "",
        "company_size_preference": "",
        "work_mode_preference": "",
    },
    "skill_profile": {
        "technical_skills": [],
        "soft_skills": [],
        "years_of_experience": 0,
        "education_level": "",
        "certifications": [],
    },
    "interview_experience": {
        "companies_interviewed": [],
        "common_questions": [],
        "strengths": [],
        "weaknesses": [],
        "tips": [],
    },
    "personal_preference": {
        "work_style": "",
        "career_goals": "",
        "values": [],
        "avoid_factors": [],
    },
}


class MemoryUpdater:
    """管理求职记忆的读取、更新和持久化。

    存储路径默认为 .jobflow/memory.json，使用原子写入保证数据安全。
    """

    def __init__(self, storage_path: str = _DEFAULT_MEMORY_PATH):
        self.storage_path = Path(storage_path)
        self._memory: dict[str, Any] = {}

    def update(self, conversation: str, llm: Any = None) -> dict[str, Any]:
        """从对话中提取并更新记忆。

        Args:
            conversation: 对话文本
            llm: LangChain ChatModel 实例（Phase 2 使用，当前占位）

        Returns:
            更新后的记忆字典
        """
        current = self._load()

        if llm is None:
            # Phase 2: 使用 LLM 提取记忆
            # 当前占位：直接返回现有记忆
            logger.debug("MemoryUpdater.update: LLM 未配置，跳过提取")
            return current

        prompt = MEMORY_UPDATE_PROMPT.format(
            conversation=conversation,
            current_memory=json.dumps(current, ensure_ascii=False, indent=2),
        )

        try:
            response = llm.invoke(prompt)
            content = response.content if hasattr(response, "content") else str(response)
            # 提取 JSON 块
            import re

            json_match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group(1))
            else:
                extracted = json.loads(content)

            # 深度合并
            updated = self._deep_merge(current, extracted)
            self._save(updated)
            self._memory = updated
            logger.info("MemoryUpdater: 记忆更新完成")
            return updated
        except Exception as exc:
            logger.error("MemoryUpdater.update: 提取失败 — %s", exc)
            return current

    def get_context(self) -> str:
        """获取格式化的记忆上下文字符串，用于注入 prompt。"""
        memory = self._load()
        lines = []

        pref = memory.get("job_preference", {})
        if pref.get("target_roles"):
            lines.append(f"目标职位：{', '.join(pref['target_roles'])}")
        if pref.get("target_cities"):
            lines.append(f"目标城市：{', '.join(pref['target_cities'])}")
        if pref.get("salary_expectation"):
            lines.append(f"薪资期望：{pref['salary_expectation']}")

        skill = memory.get("skill_profile", {})
        if skill.get("technical_skills"):
            lines.append(f"技术技能：{', '.join(skill['technical_skills'])}")
        if skill.get("years_of_experience"):
            lines.append(f"工作年限：{skill['years_of_experience']} 年")

        interview = memory.get("interview_experience", {})
        if interview.get("strengths"):
            lines.append(f"面试亮点：{', '.join(interview['strengths'])}")

        return "\n".join(lines) if lines else "（暂无历史记忆）"

    def _load(self) -> dict[str, Any]:
        """从文件加载记忆，文件不存在时返回空记忆。"""
        if not self.storage_path.exists():
            return dict(_EMPTY_MEMORY)
        try:
            with open(self.storage_path, encoding="utf-8") as f:
                data = json.load(f)
            self._memory = data
            return data
        except Exception as exc:
            logger.error("MemoryUpdater._load: 读取失败 — %s", exc)
            return dict(_EMPTY_MEMORY)

    def _save(self, memory: dict[str, Any]) -> None:
        """原子写入记忆文件（temp file + rename）。"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            tmp_fd, tmp_path = tempfile.mkstemp(dir=self.storage_path.parent, prefix=".memory_", suffix=".json")
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                json.dump(memory, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self.storage_path)
        except Exception as exc:
            logger.error("MemoryUpdater._save: 写入失败 — %s", exc)
            raise

    @staticmethod
    def _deep_merge(base: dict, update: dict) -> dict:
        """递归合并两个字典，update 的值覆盖/追加到 base。"""
        result = dict(base)
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = MemoryUpdater._deep_merge(result[key], value)
            elif key in result and isinstance(result[key], list) and isinstance(value, list):
                # 列表去重合并
                existing = result[key]
                result[key] = existing + [v for v in value if v not in existing]
            elif value:  # 非空值才覆盖
                result[key] = value
        return result
