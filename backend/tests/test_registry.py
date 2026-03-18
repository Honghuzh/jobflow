"""测试 SubAgentRegistry — 注册中心的注册、查找、实例化功能。"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "harness"))

from jobflow.subagents.registry import AgentCapability, SubAgentRegistry


def make_registry() -> SubAgentRegistry:
    """创建一个干净的注册中心（避免全局状态污染）。"""
    return SubAgentRegistry()


class TestSubAgentRegistry:
    """测试 SubAgentRegistry 的核心功能。"""

    def test_register_and_get(self):
        """注册 Agent 后可以通过 get 获取能力声明。"""
        reg = make_registry()
        cap = AgentCapability(name="test_agent", description="测试 Agent", tags=["test"])
        reg.register(cap, lambda: "agent_instance")
        result = reg.get("test_agent")
        assert result is not None
        assert result.name == "test_agent"

    def test_get_nonexistent_returns_none(self):
        """获取未注册的 Agent 返回 None。"""
        reg = make_registry()
        assert reg.get("not_exist") is None

    def test_register_duplicate_overwrites(self):
        """重复注册同名 Agent 会覆盖（不报错）。"""
        reg = make_registry()
        cap1 = AgentCapability(name="dup", description="第一版")
        cap2 = AgentCapability(name="dup", description="第二版")
        reg.register(cap1, lambda: "v1")
        reg.register(cap2, lambda: "v2")
        assert reg.get("dup").description == "第二版"

    def test_list_agents_empty(self):
        """空注册中心返回空列表。"""
        reg = make_registry()
        assert reg.list_agents() == []

    def test_list_agents_multiple(self):
        """list_agents 返回所有注册的 Agent。"""
        reg = make_registry()
        for i in range(3):
            cap = AgentCapability(name=f"agent_{i}", description=f"Agent {i}")
            reg.register(cap, lambda i=i: f"instance_{i}")
        agents = reg.list_agents()
        assert len(agents) == 3
        names = [a.name for a in agents]
        assert "agent_0" in names
        assert "agent_2" in names

    def test_create_existing_agent(self):
        """create 调用工厂函数返回实例。"""
        reg = make_registry()
        cap = AgentCapability(name="factory_test", description="测试工厂")
        reg.register(cap, lambda **kw: {"created": True, **kw})
        instance = reg.create("factory_test", param="value")
        assert instance["created"] is True
        assert instance["param"] == "value"

    def test_create_nonexistent_raises_keyerror(self):
        """create 不存在的 Agent 抛出 KeyError。"""
        reg = make_registry()
        with pytest.raises(KeyError):
            reg.create("ghost_agent")

    def test_match_by_description_keywords(self):
        """match 通过 Agent 描述关键词匹配任务。"""
        reg = make_registry()
        cap = AgentCapability(name="jd_analyst", description="JD 分析师：深度解析职位描述", tags=["jd"])
        reg.register(cap, lambda: None)
        # "职位描述" 出现在 Agent 描述中
        matches = reg.match("我需要分析一个职位描述")
        assert "jd_analyst" in matches

    def test_match_by_tags(self):
        """match 通过 tags 过滤。"""
        reg = make_registry()
        cap_a = AgentCapability(name="agent_a", description="A", tags=["resume"])
        cap_b = AgentCapability(name="agent_b", description="B", tags=["interview"])
        reg.register(cap_a, lambda: None)
        reg.register(cap_b, lambda: None)
        # 只匹配有 "resume" tag 的
        matches = reg.match("需要帮助", tags=["resume"])
        assert "agent_a" in matches
        assert "agent_b" not in matches

    def test_match_no_match_returns_empty(self):
        """没有匹配时返回空列表。"""
        reg = make_registry()
        cap = AgentCapability(name="special", description="非常特殊的 Agent", tags=["xyz"])
        reg.register(cap, lambda: None)
        matches = reg.match("完全不相关的任务", tags=["abc"])
        assert matches == []

    def test_agent_capability_defaults(self):
        """AgentCapability 的默认值。"""
        cap = AgentCapability(name="test", description="desc")
        assert cap.tags == []
        assert cap.max_concurrency == 3
        assert cap.timeout_seconds == 900
