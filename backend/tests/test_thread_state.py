"""测试 ThreadState — 求职场景状态定义。"""
import sys
from pathlib import Path

# 确保 harness 包可以被导入
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "harness"))

from jobflow.agents.thread_state import JobApplication, JobData, JobFlowThreadState, ResumeData, ThreadDataState


class TestResumeData:
    """测试 ResumeData TypedDict。"""

    def test_resume_data_all_fields(self):
        """测试 ResumeData 可以包含所有字段。"""
        data: ResumeData = {
            "name": "张三",
            "contact": {"email": "zhangsan@example.com", "phone": "13800138000"},
            "education": [{"school": "某大学", "degree": "本科", "major": "计算机"}],
            "experience": [{"company": "某公司", "title": "工程师", "duration": "2年"}],
            "skills": {"technical": ["Python", "Go"], "soft": ["沟通"]},
            "projects": [{"name": "项目A", "description": "..."}],
            "raw_text": "原始简历文本",
        }
        assert data["name"] == "张三"
        assert len(data["education"]) == 1
        assert "Python" in data["skills"]["technical"]

    def test_resume_data_partial(self):
        """测试 ResumeData 支持部分字段（total=False）。"""
        data: ResumeData = {"name": "李四"}
        assert data["name"] == "李四"
        assert "contact" not in data


class TestJobData:
    """测试 JobData TypedDict。"""

    def test_job_data_all_fields(self):
        """测试 JobData 包含所有字段。"""
        job: JobData = {
            "title": "Python 工程师",
            "company": "字节跳动",
            "location": "北京",
            "salary_range": "25k-35k",
            "requirements": ["Python 3年以上", "熟悉 Django"],
            "responsibilities": ["负责后端开发"],
            "jd_url": "https://job.example.com/123",
            "analysis": {"match_score": 80},
        }
        assert job["title"] == "Python 工程师"
        assert len(job["requirements"]) == 2

    def test_job_data_minimal(self):
        """测试 JobData 仅有必要字段。"""
        job: JobData = {"title": "前端工程师"}
        assert job["title"] == "前端工程师"


class TestJobApplication:
    """测试 JobApplication TypedDict。"""

    def test_valid_statuses(self):
        """测试所有有效的投递状态。"""
        valid_statuses = ["wishlist", "applied", "phone_screen", "interview", "offer", "rejected"]
        for status in valid_statuses:
            app: JobApplication = {"company": "公司A", "position": "工程师", "status": status}
            assert app["status"] == status

    def test_job_application_with_notes(self):
        """测试带备注的投递记录。"""
        app: JobApplication = {
            "company": "某大厂",
            "position": "高级工程师",
            "status": "interview",
            "applied_at": "2024-01-15T10:00:00",
            "notes": "二面已通过",
        }
        assert app["notes"] == "二面已通过"


class TestJobFlowThreadState:
    """测试 JobFlowThreadState 主状态 Schema。"""

    def test_thread_state_empty(self):
        """测试 JobFlowThreadState 可以不带可选字段。"""
        # MessagesState 要求 messages 键
        state: JobFlowThreadState = {"messages": []}
        assert state["messages"] == []

    def test_thread_state_with_resume(self):
        """测试带简历数据的状态。"""
        state: JobFlowThreadState = {
            "messages": [],
            "resume_data": {"name": "王五", "raw_text": "简历文本"},
        }
        assert state["resume_data"]["name"] == "王五"

    def test_thread_state_with_job_applications(self):
        """测试带投递记录的状态。"""
        state: JobFlowThreadState = {
            "messages": [],
            "job_applications": [
                {"company": "A 公司", "position": "工程师", "status": "applied"},
                {"company": "B 公司", "position": "架构师", "status": "interview"},
            ],
        }
        assert len(state["job_applications"]) == 2

    def test_thread_state_interview_mode(self):
        """测试面试模式标志。"""
        state: JobFlowThreadState = {"messages": [], "interview_mode": True}
        assert state["interview_mode"] is True

    def test_thread_state_thread_data(self):
        """测试线程数据路径字段。"""
        td: ThreadDataState = {
            "workspace_path": "/tmp/ws",
            "uploads_path": "/tmp/uploads",
            "outputs_path": "/tmp/outputs",
        }
        state: JobFlowThreadState = {"messages": [], "thread_data": td}
        assert state["thread_data"]["workspace_path"] == "/tmp/ws"
