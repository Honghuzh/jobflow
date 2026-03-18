"""JobFlow ThreadState — 求职场景的状态定义。

借鉴 DeerFlow 的 ThreadState 设计模式，扩展了求职场景特有的状态字段。
"""
from typing import NotRequired, TypedDict

from langgraph.graph import MessagesState


class ResumeData(TypedDict, total=False):
    """结构化简历数据。"""

    name: str
    contact: dict
    education: list[dict]
    experience: list[dict]
    skills: dict
    projects: list[dict]
    raw_text: str


class JobData(TypedDict, total=False):
    """目标岗位数据。"""

    title: str
    company: str
    location: str
    salary_range: str
    requirements: list[str]
    responsibilities: list[str]
    jd_url: str
    analysis: dict


class JobApplication(TypedDict, total=False):
    """投递记录。"""

    company: str
    position: str
    status: str  # wishlist/applied/phone_screen/interview/offer/rejected
    applied_at: str
    notes: str


class ThreadDataState(TypedDict, total=False):
    """线程数据目录。"""

    workspace_path: str
    uploads_path: str
    outputs_path: str


class JobFlowThreadState(MessagesState):
    """JobFlow 的主 State Schema。"""

    # 基础字段（借鉴 DeerFlow）
    thread_data: NotRequired[ThreadDataState | None]
    title: NotRequired[str | None]
    artifacts: NotRequired[list[dict]]
    uploaded_files: NotRequired[list[str] | None]
    # 求职场景特有字段
    resume_data: NotRequired[ResumeData | None]
    target_job: NotRequired[JobData | None]
    job_applications: NotRequired[list[JobApplication]]
    interview_mode: NotRequired[bool]
