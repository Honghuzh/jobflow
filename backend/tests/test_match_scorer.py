"""测试 match_scorer — 匹配度评分工具。"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "harness"))

from jobflow.tools.builtins.match_scorer import _extract_tech_keywords, _match_score_impl


class TestExtractTechKeywords:
    """测试技术关键词提取。"""

    def test_extract_python(self):
        """从文本中提取 python。"""
        keywords = _extract_tech_keywords("我熟悉 Python 开发，使用过 Django 和 FastAPI")
        assert "python" in keywords

    def test_extract_multiple(self):
        """提取多个关键词。"""
        keywords = _extract_tech_keywords("技术栈：Python, Go, Redis, Docker, Kubernetes")
        assert "python" in keywords
        assert "go" in keywords
        assert "redis" in keywords
        assert "docker" in keywords
        assert "kubernetes" in keywords

    def test_case_insensitive(self):
        """不区分大小写。"""
        keywords = _extract_tech_keywords("使用 PYTHON 和 JAVA 开发")
        assert "python" in keywords
        assert "java" in keywords

    def test_no_false_positive_go(self):
        """'go' 不应匹配到 'good' 等单词。"""
        keywords = _extract_tech_keywords("I am good at communication")
        assert "go" not in keywords

    def test_empty_text(self):
        """空文本返回空列表。"""
        assert _extract_tech_keywords("") == []

    def test_no_tech_keywords(self):
        """无技术关键词时返回空列表。"""
        keywords = _extract_tech_keywords("我喜欢读书、旅行、摄影")
        assert keywords == []

    def test_extract_react(self):
        """提取前端框架关键词。"""
        keywords = _extract_tech_keywords("擅长 React 和 TypeScript 前端开发")
        assert "react" in keywords
        assert "typescript" in keywords


class TestMatchScore:
    """测试匹配度评分。"""

    def test_perfect_match(self):
        """简历和 JD 关键词完全重叠时，分数应较高。"""
        resume = "Python 工程师，熟悉 Django, Redis, Docker, Git"
        jd = "要求：Python 3年以上，熟悉 Django，了解 Redis 和 Docker"
        result = _match_score_impl(resume, jd)
        assert result["overall_score"] >= 60
        assert len(result["matched_keywords"]) >= 3

    def test_no_match(self):
        """简历和 JD 关键词完全不重叠时，分数应较低。"""
        resume = "我喜欢烹饪和园艺，有丰富的农业经验"
        jd = "要求：Kubernetes, AWS, Terraform, Go 语言"
        result = _match_score_impl(resume, jd)
        assert result["overall_score"] < 60
        assert len(result["missing_keywords"]) > 0

    def test_empty_resume_returns_zero(self):
        """空简历返回 0 分。"""
        result = _match_score_impl("", "要求：Python")
        assert result["overall_score"] == 0

    def test_empty_jd_returns_zero(self):
        """空 JD 返回 0 分。"""
        result = _match_score_impl("Python 工程师", "")
        assert result["overall_score"] == 0

    def test_both_empty_returns_zero(self):
        """双空返回 0 分。"""
        result = _match_score_impl("", "")
        assert result["overall_score"] == 0

    def test_result_structure(self):
        """返回值包含所有必要字段。"""
        result = _match_score_impl("Python Go Docker", "Python Kubernetes")
        required_keys = {"overall_score", "dimensions", "matched_keywords", "missing_keywords", "suggestions"}
        assert required_keys.issubset(result.keys())

    def test_score_range(self):
        """总分在 0-100 范围内。"""
        result = _match_score_impl("Python Django Redis", "Python FastAPI AWS Docker")
        assert 0 <= result["overall_score"] <= 100

    def test_suggestions_not_empty(self):
        """应至少提供一条建议。"""
        result = _match_score_impl("Python 工程师", "要求 Python Go AWS Kubernetes Docker")
        assert len(result["suggestions"]) >= 1

    def test_matched_in_both(self):
        """matched_keywords 应该是简历和 JD 的交集。"""
        result = _match_score_impl("Python Go Redis", "Python Kubernetes Redis")
        matched = set(result["matched_keywords"])
        assert "python" in matched
        assert "redis" in matched

    def test_dimensions_present(self):
        """dimensions 字段包含多个维度评分。"""
        result = _match_score_impl("Python 工程师，3年经验", "要求：Python，本科以上")
        assert len(result["dimensions"]) >= 2
        for score in result["dimensions"].values():
            assert 0 <= score <= 100
