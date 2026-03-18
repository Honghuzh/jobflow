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
            # Fallback：使用简单关键词提取
            logger.debug("MemoryUpdater.update: LLM 未配置，使用关键词提取 fallback")
            extracted = _extract_memory_by_keywords(conversation)
            if extracted:
                updated = self._deep_merge(current, extracted)
                self._save(updated)
                self._memory = updated
                return updated
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


# ── 关键词提取 Fallback ──────────────────────────────────────────────────


# 技术技能关键词列表
_TECH_KEYWORDS = [
    "Python", "Java", "Go", "JavaScript", "TypeScript", "Rust", "C++", "C#", "Swift", "Kotlin",
    "React", "Vue", "Angular", "Django", "FastAPI", "Flask", "Spring",
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
    "AWS", "GCP", "Azure", "Docker", "Kubernetes",
    "Spark", "Flink", "Kafka", "PyTorch", "TensorFlow", "LangChain",
    "Git", "Linux", "Nginx",
]

# 城市关键词
_CITY_KEYWORDS = ["北京", "上海", "深圳", "杭州", "广州", "成都", "武汉", "南京", "西安", "重庆"]

# 职位关键词
_ROLE_KEYWORDS = ["工程师", "开发", "架构师", "产品经理", "数据分析", "算法", "前端", "后端", "全栈", "运维", "测试"]


def _extract_memory_by_keywords(conversation: str) -> dict:
    """使用关键词匹配从对话中提取简单记忆（LLM fallback）。"""
    import re

    result: dict[str, Any] = {}
    text = conversation

    # 提取技术技能
    found_skills = [kw for kw in _TECH_KEYWORDS if kw.lower() in text.lower()]
    if found_skills:
        result.setdefault("skill_profile", {})["technical_skills"] = found_skills

    # 提取目标城市
    found_cities = [city for city in _CITY_KEYWORDS if city in text]
    if found_cities:
        result.setdefault("job_preference", {})["target_cities"] = found_cities

    # 提取目标职位
    found_roles = [role for role in _ROLE_KEYWORDS if role in text]
    if found_roles:
        result.setdefault("job_preference", {})["target_roles"] = found_roles

    # 提取薪资期望（如 "20k-30k", "25K", "月薪 20000"）
    salary_match = re.search(r"(\d+[kK万](?:\s*[-~]\s*\d+[kK万])?|月薪\s*\d+)", text)
    if salary_match:
        result.setdefault("job_preference", {})["salary_expectation"] = salary_match.group()

    # 提取工作年限（如 "3年经验", "5年工作经验"）
    exp_match = re.search(r"(\d+)\s*年(?:工作|开发|编程)?经验", text)
    if exp_match:
        result.setdefault("skill_profile", {})["years_of_experience"] = int(exp_match.group(1))

    return result
