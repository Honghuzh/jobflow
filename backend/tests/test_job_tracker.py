"""测试 job_tracker — 求职进度追踪工具。"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "harness"))

from jobflow.tools.builtins.job_tracker import (
    VALID_STATUSES,
    _get_job_stats_impl,
    _load_tracker,
    _save_tracker,
    _update_job_status_impl,
)


class TestUpdateJobStatus:
    """测试 update_job_status 工具。"""

    def test_create_new_application(self, tmp_path):
        """创建新的投递记录。"""
        tracker_file = str(tmp_path / "tracker.json")
        record = _update_job_status_impl("字节跳动", "Python 工程师", "applied", tracker_path=tracker_file)
        assert record["company"] == "字节跳动"
        assert record["position"] == "Python 工程师"
        assert record["status"] == "applied"
        assert "applied_at" in record

    def test_update_existing_application(self, tmp_path):
        """更新已有投递记录的状态。"""
        tracker_file = str(tmp_path / "tracker.json")
        _update_job_status_impl("腾讯", "前端工程师", "applied", tracker_path=tracker_file)
        record = _update_job_status_impl("腾讯", "前端工程师", "interview", tracker_path=tracker_file)
        assert record["status"] == "interview"

    def test_status_history_tracked(self, tmp_path):
        """状态变化历史被记录。"""
        tracker_file = str(tmp_path / "tracker.json")
        _update_job_status_impl("阿里巴巴", "Java 工程师", "applied", tracker_path=tracker_file)
        record = _update_job_status_impl("阿里巴巴", "Java 工程师", "phone_screen", tracker_path=tracker_file)
        assert len(record.get("history", [])) >= 2

    def test_invalid_status_returns_error(self, tmp_path):
        """无效状态返回错误信息。"""
        tracker_file = str(tmp_path / "tracker.json")
        result = _update_job_status_impl("某公司", "工程师", "invalid_status", tracker_path=tracker_file)
        assert "error" in result

    def test_all_valid_statuses(self, tmp_path):
        """所有合法状态都可以正常创建记录。"""
        for i, status in enumerate(VALID_STATUSES):
            tracker_file = str(tmp_path / f"tracker_{i}.json")
            record = _update_job_status_impl(f"公司{i}", "岗位", status, tracker_path=tracker_file)
            assert record["status"] == status

    def test_notes_saved(self, tmp_path):
        """备注信息被正确保存。"""
        tracker_file = str(tmp_path / "tracker.json")
        record = _update_job_status_impl("美团", "产品经理", "interview", notes="三面，聊了1小时", tracker_path=tracker_file)
        assert record["notes"] == "三面，聊了1小时"

    def test_persisted_to_file(self, tmp_path):
        """投递记录被持久化到文件。"""
        tracker_file = str(tmp_path / "tracker.json")
        _update_job_status_impl("百度", "算法工程师", "offer", tracker_path=tracker_file)
        # 重新加载验证持久化
        tracker = _load_tracker(tracker_file)
        apps = tracker.get("applications", [])
        assert any(a["company"] == "百度" and a["status"] == "offer" for a in apps)


class TestGetJobStats:
    """测试 get_job_stats 统计功能。"""

    def test_empty_stats(self, tmp_path):
        """无投递记录时，统计为空。"""
        tracker_file = str(tmp_path / "tracker.json")
        stats = _get_job_stats_impl(tracker_path=tracker_file)
        assert stats["total"] == 0
        assert all(v == 0 for v in stats["by_status"].values())

    def test_total_count(self, tmp_path):
        """total 正确统计总数。"""
        tracker_file = str(tmp_path / "tracker.json")
        _update_job_status_impl("公司A", "岗位1", "applied", tracker_path=tracker_file)
        _update_job_status_impl("公司B", "岗位2", "interview", tracker_path=tracker_file)
        _update_job_status_impl("公司C", "岗位3", "offer", tracker_path=tracker_file)
        stats = _get_job_stats_impl(tracker_path=tracker_file)
        assert stats["total"] == 3

    def test_by_status_counts(self, tmp_path):
        """by_status 正确统计各状态数量。"""
        tracker_file = str(tmp_path / "tracker.json")
        _update_job_status_impl("公司1", "岗位", "applied", tracker_path=tracker_file)
        _update_job_status_impl("公司2", "岗位", "applied", tracker_path=tracker_file)
        _update_job_status_impl("公司3", "岗位", "offer", tracker_path=tracker_file)
        stats = _get_job_stats_impl(tracker_path=tracker_file)
        assert stats["by_status"]["applied"] == 2
        assert stats["by_status"]["offer"] == 1

    def test_recent_activities_limit(self, tmp_path):
        """recent_activities 最多返回 5 条。"""
        tracker_file = str(tmp_path / "tracker.json")
        for i in range(8):
            _update_job_status_impl(f"公司{i}", f"岗位{i}", "applied", tracker_path=tracker_file)
        stats = _get_job_stats_impl(tracker_path=tracker_file)
        assert len(stats["recent_activities"]) <= 5

    def test_stats_structure(self, tmp_path):
        """统计结果包含所有必要字段。"""
        tracker_file = str(tmp_path / "tracker.json")
        stats = _get_job_stats_impl(tracker_path=tracker_file)
        assert "total" in stats
        assert "by_status" in stats
        assert "recent_activities" in stats

    def test_by_status_includes_all_statuses(self, tmp_path):
        """by_status 包含所有合法状态的计数。"""
        tracker_file = str(tmp_path / "tracker.json")
        stats = _get_job_stats_impl(tracker_path=tracker_file)
        for status in VALID_STATUSES:
            assert status in stats["by_status"]


class TestLoadSaveTracker:
    """测试底层文件读写。"""

    def test_load_nonexistent_returns_empty(self, tmp_path):
        """加载不存在的文件返回空数据。"""
        tracker_file = str(tmp_path / "nonexistent.json")
        tracker = _load_tracker(tracker_file)
        assert tracker == {"applications": []}

    def test_save_and_load_roundtrip(self, tmp_path):
        """保存后再加载，数据一致。"""
        tracker_file = str(tmp_path / "tracker.json")
        data = {"applications": [{"company": "测试公司", "status": "applied"}]}
        _save_tracker(data, tracker_file)
        loaded = _load_tracker(tracker_file)
        assert loaded["applications"][0]["company"] == "测试公司"

    def test_atomic_write_creates_parent_dir(self, tmp_path):
        """保存时自动创建父目录。"""
        tracker_file = str(tmp_path / "nested" / "deep" / "tracker.json")
        _save_tracker({"applications": []}, tracker_file)
        assert Path(tracker_file).exists()
