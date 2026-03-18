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
- 💬 **Next.js 前端**：SSE 流式对话、Kanban 投递看板、简历上传管理

## 架构图

```
┌──────────────────────────────────────────────────────────────┐
│  前端 (Next.js 15 + React 19 + Tailwind CSS v4)              │
│  ├── 💬 对话界面（SSE 流式 + Markdown 渲染）                  │
│  ├── 📊 投递看板（Kanban 5 列）                               │
│  ├── 📄 简历管理（拖拽上传 + 解析预览）                        │
│  └── 📈 上下文面板（匹配度评分 + 简历摘要）                    │
├──────────────────────────────────────────────────────────────┤
│  后端 (FastAPI + LangGraph + LangChain)                      │
│  ├── Career Agent（StateGraph + ToolNode）                   │
│  ├── 7 层 Middleware Chain                                   │
│  ├── 4 个专家 SubAgent（JD分析/简历优化/CL/模面）             │
│  ├── 4 个核心工具（JD解析/简历解析/匹配评分/进度追踪）         │
│  └── 求职记忆系统（JSON 持久化）                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 环境要求

| 工具 | 版本要求 | 安装方式 |
|------|---------|---------|
| Python | >= 3.12 | [python.org](https://www.python.org/downloads/) |
| uv | 最新版 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | >= 18 | [nodejs.org](https://nodejs.org/) |
| npm | >= 9 | 随 Node.js 一起安装 |
| OpenAI API Key | 可选 | 没有时系统使用占位模式运行 |

---

## 快速开始

### 第一步：克隆项目

```bash
git clone https://github.com/Honghuzh/jobflow.git
cd jobflow
```

### 第二步：配置环境

```bash
cp .env.example .env
cp config.example.yaml config.yaml
```

编辑 `.env` 填入你的 API Key（可选，没有也能运行）：

```
OPENAI_API_KEY=sk-your-key-here
TAVILY_API_KEY=your-tavily-key-here
```

### 第三步：启动后端

```bash
cd backend
uv sync                    # 安装 Python 依赖（自动创建虚拟环境）
uv run uvicorn app.gateway.app:app --host 0.0.0.0 --port 8001 --reload
```

验证后端是否启动成功：

```bash
curl http://localhost:8001/health
# 返回：{"status":"ok","service":"jobflow-gateway"}
```

### 第四步：启动前端（新终端）

```bash
cd frontend
npm install
npm run dev
```

### 第五步：打开浏览器

- 前端页面：[http://localhost:3000](http://localhost:3000)
- 后端 API 文档：[http://localhost:8001/docs](http://localhost:8001/docs)

---

## Makefile 命令

在**项目根目录**运行：

| 命令 | 说明 |
|------|------|
| `make check` | 检查 Python、uv 等前置依赖 |
| `make install` | 安装后端 Python 依赖（`uv sync`） |
| `make dev` | 启动后端开发服务器 |
| `make test` | 运行全部测试 |
| `make gateway` | 启动 FastAPI Gateway（端口 8001） |
| `make frontend-install` | 安装前端 npm 依赖 |
| `make frontend-dev` | 启动前端开发服务器（端口 3000） |
| `make frontend-build` | 构建前端生产包 |

在 **`backend/` 目录**运行：

| 命令 | 说明 |
|------|------|
| `make install` | `uv sync` |
| `make dev` | 启动后端 |
| `make test` | `uv run pytest tests/ -v` |
| `make lint` | `uv run ruff check .` |
| `make format` | `uv run ruff format .` |
| `make gateway` | 启动 uvicorn 监听 8001 端口 |

---

## API 端点

后端 Gateway 运行后，通过 `http://localhost:8001` 访问：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/config` | GET | 获取配置信息 |
| `/api/chat` | POST | 与 Career Agent 对话 |
| `/api/chat/stream` | POST | SSE 流式对话 |
| `/api/jobs/parse-jd` | POST | 解析 JD 文本 |
| `/api/jobs/match` | POST | 计算简历-JD 匹配度 |
| `/api/resume/upload` | POST | 上传简历文件 |
| `/api/resume/parse` | POST | 解析简历 |
| `/api/resume/current` | GET | 获取当前简历数据 |
| `/api/tracker/update` | POST | 更新投递状态 |
| `/api/tracker/stats` | GET | 获取投递统计 |
| `/api/tracker/list` | GET | 获取所有投递记录 |
| `/api/skills` | GET | 列出所有 Skill |
| `/api/skills/{name}` | GET | 获取指定 Skill 详情 |
| `/api/models` | GET | 列出可用模型 |

完整的交互式 API 文档：[http://localhost:8001/docs](http://localhost:8001/docs)

---

## 目录结构

```
jobflow/
├── .env.example               # 环境变量模板
├── config.example.yaml        # 模型与工具配置模板
├── Makefile                   # 根 Makefile
├── README.md                  # 本文档（中文）
├── README_en.md               # 英文文档
│
├── backend/
│   ├── Makefile               # 后端 Makefile
│   ├── pyproject.toml         # Python 依赖（uv 管理）
│   ├── app/
│   │   └── gateway/           # FastAPI Gateway
│   │       ├── app.py         # FastAPI 主入口
│   │       ├── sse.py         # SSE 流式输出
│   │       ├── uploads.py     # 文件上传处理
│   │       ├── thread_manager.py # 线程管理
│   │       └── routers/       # 路由模块（chat/jobs/tracker/resume/skills/models）
│   ├── packages/harness/jobflow/
│   │   ├── agents/
│   │   │   ├── career_agent/  # Career Agent（Lead Agent）
│   │   │   ├── middlewares/   # 7 层 Middleware Chain
│   │   │   └── memory/        # 求职记忆系统
│   │   ├── subagents/         # 4 个求职专家 Sub-Agent
│   │   ├── tools/             # 4 个核心工具
│   │   ├── models/            # LLM 模型工厂
│   │   ├── skills/            # Skill 加载器
│   │   ├── config/            # 配置系统
│   │   └── sandbox/           # 沙箱抽象
│   └── tests/                 # 单元测试
│
├── frontend/
│   ├── package.json           # Node.js 依赖
│   ├── next.config.ts         # Next.js 配置（API 代理到 8001）
│   └── src/
│       ├── app/               # Next.js App Router
│       ├── components/        # React 组件
│       ├── lib/               # API 客户端工具
│       └── store/             # Zustand 状态管理
│
└── skills/
    ├── public/                # 内置 Skill 定义（SKILL.md）
    └── custom/                # 自定义 Skill（用户扩展）
```

---

## 技术栈

| 层级 | 技术 |
|------|------|
| **后端语言** | Python 3.12+ |
| **Web 框架** | FastAPI |
| **Agent 编排** | LangGraph |
| **LLM 集成** | LangChain + LangChain-OpenAI |
| **包管理** | uv |
| **前端框架** | Next.js 15 + React 19 |
| **语言** | TypeScript |
| **样式** | Tailwind CSS v4 |
| **状态管理** | Zustand |
| **AI 模型** | OpenAI GPT-4o（可配置） |
| **搜索工具** | Tavily Search（可选） |

---

## 运行测试

```bash
cd backend
uv run pytest -v
```

运行特定测试文件：

```bash
uv run pytest tests/test_career_agent.py -v
uv run pytest tests/test_gateway.py -v
```

---

## 常见问题

### `uv: command not found`

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# 或
pip install uv
```

### `ModuleNotFoundError: No module named 'jobflow'`

确保在 `backend/` 目录下运行 `uv run` 命令，uv 会自动将 harness 包加入 Python 路径：

```bash
cd backend
uv run uvicorn app.gateway.app:app --host 0.0.0.0 --port 8001 --reload
```

### `config.yaml not found`

```bash
cp config.example.yaml config.yaml
```

### `OPENAI_API_KEY not set` 警告

这不是致命错误。系统会使用占位模式运行，基础 API 端点仍然可用。
如需 LLM 功能，编辑 `.env` 文件填入真实的 API Key。

### `npm install` 失败

确保 Node.js >= 18：

```bash
node --version   # 应显示 v18.x 或更高
npm install
```

### 前端无法连接后端

确保后端已启动并监听 8001 端口。前端的 `next.config.ts` 会自动将 `/api/*` 请求代理到 `http://localhost:8001`。

---

## License

MIT License — 详见 [LICENSE](LICENSE)
