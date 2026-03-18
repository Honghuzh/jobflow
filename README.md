# 🎯 JobFlow — 基于 Agent 的智能求职助手框架

> 借鉴 DeerFlow 的 Super Agent Harness 架构理念，面向求职场景构建的多 Agent 协同框架

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://github.com/langchain-ai/langgraph)

## 简介

JobFlow 是一个面向求职场景的智能 Agent 框架，借鉴了字节跳动 DeerFlow（GitHub Trending #1）的 Super Agent Harness 架构理念，将多 Agent 协同调度、Middleware 链、技能系统等设计模式应用于求职助手场景。

## 核心特性

- 🤖 **4 大求职专家 Sub-Agent**：JD 分析师、简历优化师、Cover Letter 撰写师、模拟面试官
- 🔗 **7 层求职 Middleware Chain**：简历解析、岗位上下文、进度追踪等横切关注点
- 📚 **5 个内置 Skill**：JD 分析、简历优化、Cover Letter、模拟面试、薪资谈判
- 🧠 **求职记忆系统**：跨 Session 的求职意向、技能画像、面试经验持久化
- 🛠️ **4 个核心工具**：JD 解析、简历解析、匹配度评分、投递进度追踪

## 架构图

```
                  ┌──────────────────────────────────────┐
                  │        Career Agent (Lead)           │
                  │           求职总教练                   │
                  └───────────┬──────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
          ┌──────────┐ ┌──────────┐ ┌──────────┐
          │Middleware │ │Sub-Agents│ │  Tools   │
          │ Chain(7) │ │  (4专家) │ │  (4工具) │
          └──────────┘ └──────────┘ └──────────┘

  Middleware Chain（从上到下执行）:
  ┌─────────────────────────────────────┐
  │ 1. ResumeParseMiddleware            │  解析上传的简历文件
  │ 2. JobContextMiddleware             │  注入岗位上下文
  │ 3. ProgressMiddleware               │  追踪投递进度
  │ 4. MemoryMiddleware (TODO Phase 2)  │  注入长期记忆
  │ 5. RateLimitMiddleware (TODO)       │  API 限流
  │ 6. AuditMiddleware (TODO)           │  审计日志
  │ 7. TelemetryMiddleware (TODO)       │  遥测追踪
  └─────────────────────────────────────┘

  Sub-Agents（专家池）:
  ┌──────────────────┐  ┌──────────────────┐
  │  JD Analyst      │  │ Resume Optimizer │
  │  JD 深度分析师    │  │  简历优化师       │
  └──────────────────┘  └──────────────────┘
  ┌──────────────────┐  ┌──────────────────┐
  │ Cover Letter     │  │ Mock Interviewer │
  │  Writer          │  │  模拟面试官       │
  └──────────────────┘  └──────────────────┘
```

## 与 DeerFlow 的设计理念对比

| 模块 | DeerFlow | JobFlow |
|------|----------|---------|
| Lead Agent | Lead Agent（通用研究助手）| Career Agent（求职总教练）|
| Middleware Chain | 9 层通用 Middleware | 7 层求职场景 Middleware |
| Sub-Agents | General + Bash Agent | 4 个求职专家 Agent |
| Skills | 通用研究/报告 Skill | JD 分析/简历优化/Cover Letter 等 |
| 记忆系统 | 通用长期记忆 | 求职意向/技能/面试经验记忆 |
| 工具集 | 网络搜索/代码执行 | JD 解析/简历解析/匹配评分/进度追踪 |

## Quick Start

### 1. 安装依赖

```bash
# 需要 Python 3.12+, uv
make install
```

### 2. 配置

```bash
cp config.example.yaml config.yaml
cp .env.example .env
# 编辑 .env，填入 API Key
```

### 3. 运行

```bash
make dev
```

### 4. 前端

```bash
make frontend-install
make frontend-dev
# 访问 http://localhost:3000
```

## 目录结构

```
jobflow/
├── README.md
├── README_en.md
├── Makefile
├── config.example.yaml
├── .env.example
├── .gitignore
│
├── backend/
│   ├── Makefile
│   ├── pyproject.toml
│   ├── packages/harness/jobflow/
│   │   ├── agents/
│   │   │   ├── career_agent/    # Career Agent（Lead Agent）
│   │   │   ├── middlewares/     # 7 层 Middleware Chain
│   │   │   └── memory/          # 求职记忆系统
│   │   ├── subagents/           # 4 个求职专家 Sub-Agent
│   │   ├── tools/               # 4 个核心工具
│   │   ├── models/              # LLM 模型工厂
│   │   ├── skills/              # Skill 加载器
│   │   ├── config/              # 配置系统
│   │   └── sandbox/             # 沙箱抽象
│   └── tests/                   # 单元测试
│
├── skills/
│   ├── public/                  # 内置 Skill 定义
│   └── custom/                  # 自定义 Skill（用户扩展）
│
└── frontend/                    # 前端（Phase 2）
```

## 开发路线图

### Phase 1（当前）— 项目骨架
- [x] 核心架构设计
- [x] Career Agent（Lead Agent）
- [x] 7 层 Middleware Chain 骨架
- [x] 4 个 Sub-Agent 定义
- [x] 4 个核心工具
- [x] 5 个内置 Skill
- [x] 求职记忆系统骨架

### Phase 2 — 后端完整实现
- [ ] FastAPI Gateway
- [ ] 完整的 LLM 集成
- [ ] PDF/Word 简历解析
- [ ] 完整的记忆系统
- [ ] SSE 流式输出

### Phase 3 — 前端
- [x] Next.js + React 界面
- [x] 对话式交互
- [x] 简历/JD 上传
- [x] 投递进度看板

### Phase 4 — 增强
- [ ] 多租户支持
- [ ] 定时任务（招聘信息监控）
- [ ] 更多求职平台集成

## 技术栈

- **Python 3.12+** — 后端语言
- **LangGraph** — Agent 编排框架
- **LangChain** — LLM 集成
- **FastAPI** — API 网关
- **uv** — Python 包管理

## License

MIT License — 详见 [LICENSE](LICENSE)
