"""匹配度评分工具 — 计算简历与 JD 的匹配程度。"""
from __future__ import annotations

import re

from langchain_core.tools import tool

# 常见技术关键词列表（用于关键词提取）
_TECH_KEYWORDS = [
    # 编程语言
    "python", "java", "go", "golang", "javascript", "typescript", "rust", "c++", "c#", "swift", "kotlin",
    # 框架
    "react", "vue", "angular", "django", "fastapi", "flask", "spring", "springboot", "nextjs",
    # 数据库
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "clickhouse", "hive",
    # 云/基础设施
    "aws", "gcp", "azure", "docker", "kubernetes", "k8s", "terraform", "ansible",
    # 大数据/AI
    "spark", "flink", "kafka", "hadoop", "pytorch", "tensorflow", "langchain", "langgraph",
    # 工具
    "git", "ci/cd", "jenkins", "github actions", "linux", "nginx", "grpc", "restful",
]


@tool
def match_score(resume_text: str, jd_text: str) -> dict:
    """计算简历与 JD 的匹配度评分。

    Args:
        resume_text: 简历文本内容
        jd_text: 职位描述文本内容

    Returns:
        包含 overall_score, dimensions, matched_keywords, missing_keywords, suggestions 的字典
    """
    return _match_score_impl(resume_text, jd_text)


def _match_score_impl(resume_text: str, jd_text: str) -> dict:
    """匹配度计算的内部实现（可在测试中直接调用）。"""
    if not resume_text or not jd_text:
        return {
            "overall_score": 0,
            "dimensions": {},
            "matched_keywords": [],
            "missing_keywords": [],
            "suggestions": ["请提供简历和 JD 内容"],
        }

    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()

    # 提取关键词
    resume_keywords = set(_extract_tech_keywords(resume_text))
    jd_keywords = set(_extract_tech_keywords(jd_text))

    # 计算关键词匹配
    matched = resume_keywords & jd_keywords
    missing = jd_keywords - resume_keywords

    keyword_score = (len(matched) / len(jd_keywords) * 100) if jd_keywords else 0

    # 多维度评分
    dimensions = {
        "技术关键词匹配": round(keyword_score),
        "工作经验相关性": _estimate_experience_relevance(resume_lower, jd_lower),
        "教育背景": _estimate_education_match(resume_lower, jd_lower),
    }

    overall_score = round(sum(dimensions.values()) / len(dimensions))

    # 改进建议
    suggestions = []
    if missing:
        top_missing = sorted(missing)[:5]
        suggestions.append(f"建议在简历中添加以下技能关键词：{', '.join(top_missing)}")
    if dimensions["工作经验相关性"] < 60:
        suggestions.append("建议补充与 JD 职责更相关的工作经验描述")
    if overall_score >= 70:
        suggestions.append("整体匹配度良好，建议重点优化 Cover Letter 的个性化程度")
    elif overall_score >= 50:
        suggestions.append("匹配度中等，建议针对 JD 关键词定向优化简历")
    else:
        suggestions.append("匹配度偏低，建议重新评估是否适合该岗位，或大幅补充相关技能")

    return {
        "overall_score": overall_score,
        "dimensions": dimensions,
        "matched_keywords": sorted(matched),
        "missing_keywords": sorted(missing),
        "suggestions": suggestions,
    }


def _extract_tech_keywords(text: str) -> list[str]:
    """从文本中提取技术关键词。"""
    text_lower = text.lower()
    found = []
    for keyword in _TECH_KEYWORDS:
        # 使用词边界匹配，避免误匹配（如 "go" 匹配到 "good"）
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, text_lower):
            found.append(keyword)
    return found


def _estimate_experience_relevance(resume_lower: str, jd_lower: str) -> int:
    """估算工作经验相关性评分（0-100）。"""
    # 简单启发式：统计 JD 中的动词在简历中出现的比例
    action_verbs = ["开发", "设计", "负责", "主导", "优化", "implement", "develop", "design", "lead", "optimize", "build", "manage", "architect"]
    jd_verbs = [v for v in action_verbs if v in jd_lower]
    if not jd_verbs:
        return 60  # 无法判断时给默认中等分
    matched_verbs = sum(1 for v in jd_verbs if v in resume_lower)
    return min(100, round(matched_verbs / len(jd_verbs) * 100 + 20))  # 基础分 20


def _estimate_education_match(resume_lower: str, jd_lower: str) -> int:
    """估算教育背景匹配评分（0-100）。"""
    # 检查学历要求
    degree_map = [
        (["本科", "bachelor"], 60),
        (["硕士", "master"], 80),
        (["博士", "phd", "doctor"], 90),
    ]
    jd_requires = 0
    resume_has = 0
    for keywords, level in degree_map:
        if any(kw in jd_lower for kw in keywords):
            jd_requires = level
        if any(kw in resume_lower for kw in keywords):
            resume_has = max(resume_has, level)

    if jd_requires == 0:
        return 80  # JD 无要求，给较高分
    if resume_has >= jd_requires:
        return 90
    return max(40, 90 - (jd_requires - resume_has))
