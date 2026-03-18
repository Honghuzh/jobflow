# 🎯 JobFlow — Intelligent Job-Seeking Agent Framework

> Inspired by DeerFlow's Super Agent Harness architecture, built for job-seeking scenarios

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://github.com/langchain-ai/langgraph)

## Introduction

JobFlow is an intelligent agent framework for job seekers, inspired by ByteDance's DeerFlow (GitHub Trending #1) Super Agent Harness architecture. It applies multi-agent coordination, Middleware chains, and skill systems to the job-seeking domain.

## Key Features

- 🤖 **4 Expert Sub-Agents**: JD Analyst, Resume Optimizer, Cover Letter Writer, Mock Interviewer
- 🔗 **7-Layer Middleware Chain**: Resume parsing, job context injection, progress tracking, and more
- 📚 **5 Built-in Skills**: JD Analysis, Resume Optimization, Cover Letter, Mock Interview, Salary Negotiation
- 🧠 **Job-Seeking Memory**: Persistent job preferences, skill profile, and interview experience across sessions
- 🛠️ **4 Core Tools**: JD Parser, Resume Parser, Match Scorer, Job Tracker
- 💬 **Next.js Frontend**: SSE streaming chat, Kanban application board, resume upload management

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Frontend (Next.js 15 + React 19 + Tailwind CSS v4)          │
│  ├── 💬 Chat Interface (SSE Streaming + Markdown rendering)  │
│  ├── 📊 Application Board (Kanban 5-column)                  │
│  ├── 📄 Resume Management (drag-and-drop upload + preview)   │
│  └── 📈 Context Panel (match score + resume summary)         │
├──────────────────────────────────────────────────────────────┤
│  Backend (FastAPI + LangGraph + LangChain)                   │
│  ├── Career Agent (StateGraph + ToolNode)                    │
│  ├── 7-Layer Middleware Chain                                │
│  ├── 4 Expert SubAgents (JD / Resume / CL / Interview)       │
│  ├── 4 Core Tools (JD parser / resume parser / match / track)│
│  └── Job-Seeking Memory System (JSON persistence)            │
└──────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

| Tool | Version | How to Install |
|------|---------|---------------|
| Python | >= 3.12 | [python.org](https://www.python.org/downloads/) |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | >= 18 | [nodejs.org](https://nodejs.org/) |
| npm | >= 9 | Bundled with Node.js |
| OpenAI API Key | optional | System runs in placeholder mode without it |

---

## Quick Start

### Step 1: Clone the repository

```bash
git clone https://github.com/Honghuzh/jobflow.git
cd jobflow
```

### Step 2: Configure environment

```bash
cp .env.example .env
cp config.example.yaml config.yaml
```

Edit `.env` and add your API keys (optional — the system runs without them):

```
OPENAI_API_KEY=sk-your-key-here
TAVILY_API_KEY=your-tavily-key-here
```

### Step 3: Start the backend

```bash
cd backend
uv sync                    # Install Python dependencies (auto-creates virtual environment)
uv run uvicorn app.gateway.app:app --host 0.0.0.0 --port 8001 --reload
```

Verify the backend is running:

```bash
curl http://localhost:8001/health
# Returns: {"status":"ok","service":"jobflow-gateway"}
```

### Step 4: Start the frontend (new terminal)

```bash
cd frontend
npm install
npm run dev
```

### Step 5: Open your browser

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API docs: [http://localhost:8001/docs](http://localhost:8001/docs)

---

## Makefile Commands

From the **project root**:

| Command | Description |
|---------|-------------|
| `make check` | Check prerequisites (Python, uv) |
| `make install` | Install backend Python dependencies (`uv sync`) |
| `make dev` | Start backend dev server |
| `make test` | Run all tests |
| `make gateway` | Start FastAPI Gateway (port 8001) |
| `make frontend-install` | Install frontend npm dependencies |
| `make frontend-dev` | Start frontend dev server (port 3000) |
| `make frontend-build` | Build frontend for production |

From the **`backend/` directory**:

| Command | Description |
|---------|-------------|
| `make install` | `uv sync` |
| `make dev` | Start backend |
| `make test` | `uv run pytest tests/ -v` |
| `make lint` | `uv run ruff check .` |
| `make format` | `uv run ruff format .` |
| `make gateway` | Start uvicorn on port 8001 |

---

## API Endpoints

After the backend Gateway starts at `http://localhost:8001`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/config` | GET | Get configuration |
| `/api/chat` | POST | Chat with Career Agent |
| `/api/chat/stream` | POST | SSE streaming chat |
| `/api/jobs/parse-jd` | POST | Parse job description |
| `/api/jobs/match` | POST | Calculate resume-JD match score |
| `/api/resume/upload` | POST | Upload resume file |
| `/api/resume/parse` | POST | Parse resume |
| `/api/resume/current` | GET | Get current resume data |
| `/api/tracker/update` | POST | Update application status |
| `/api/tracker/stats` | GET | Get tracking statistics |
| `/api/tracker/list` | GET | List all applications |
| `/api/skills` | GET | List available skills |
| `/api/skills/{name}` | GET | Get skill details |
| `/api/models` | GET | List available models |

Interactive API docs: [http://localhost:8001/docs](http://localhost:8001/docs)

---

## Project Structure

```
jobflow/
├── .env.example               # Environment variable template
├── config.example.yaml        # Model & tool configuration template
├── Makefile                   # Root Makefile
├── README.md                  # Chinese documentation
├── README_en.md               # This file (English documentation)
│
├── backend/
│   ├── Makefile               # Backend Makefile
│   ├── pyproject.toml         # Python dependencies (managed by uv)
│   ├── app/
│   │   └── gateway/           # FastAPI Gateway
│   │       ├── app.py         # FastAPI main entry point
│   │       ├── sse.py         # SSE streaming
│   │       ├── uploads.py     # File upload handling
│   │       ├── thread_manager.py # Thread management
│   │       └── routers/       # Route modules (chat/jobs/tracker/resume/skills/models)
│   ├── packages/harness/jobflow/
│   │   ├── agents/
│   │   │   ├── career_agent/  # Career Agent (Lead Agent)
│   │   │   ├── middlewares/   # 7-Layer Middleware Chain
│   │   │   └── memory/        # Job-seeking memory system
│   │   ├── subagents/         # 4 Expert Sub-Agents
│   │   ├── tools/             # 4 Core tools
│   │   ├── models/            # LLM model factory
│   │   ├── skills/            # Skill loader
│   │   ├── config/            # Configuration system
│   │   └── sandbox/           # Sandbox abstraction
│   └── tests/                 # Unit tests
│
├── frontend/
│   ├── package.json           # Node.js dependencies
│   ├── next.config.ts         # Next.js config (API proxy to port 8001)
│   └── src/
│       ├── app/               # Next.js App Router
│       ├── components/        # React components
│       ├── lib/               # API client utilities
│       └── store/             # Zustand state management
│
└── skills/
    ├── public/                # Built-in Skill definitions (SKILL.md)
    └── custom/                # Custom skills (user extensions)
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend Language** | Python 3.12+ |
| **Web Framework** | FastAPI |
| **Agent Orchestration** | LangGraph |
| **LLM Integration** | LangChain + LangChain-OpenAI |
| **Package Manager** | uv |
| **Frontend Framework** | Next.js 15 + React 19 |
| **Language** | TypeScript |
| **Styling** | Tailwind CSS v4 |
| **State Management** | Zustand |
| **AI Model** | OpenAI GPT-4o (configurable) |
| **Search Tool** | Tavily Search (optional) |

---

## Running Tests

```bash
cd backend
uv run pytest -v
```

Run specific test files:

```bash
uv run pytest tests/test_career_agent.py -v
uv run pytest tests/test_gateway.py -v
```

---

## Troubleshooting

### `uv: command not found`

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# or
pip install uv
```

### `ModuleNotFoundError: No module named 'jobflow'`

Make sure to run `uv run` from the `backend/` directory. The `app.py` gateway automatically adds the harness package to `sys.path`:

```bash
cd backend
uv run uvicorn app.gateway.app:app --host 0.0.0.0 --port 8001 --reload
```

### `config.yaml not found`

```bash
cp config.example.yaml config.yaml
```

### `OPENAI_API_KEY not set` warning

This is not a fatal error. The system runs in placeholder mode and basic API endpoints remain functional. To enable LLM features, edit your `.env` file and add a valid API key.

### `npm install` fails

Make sure Node.js >= 18 is installed:

```bash
node --version   # should show v18.x or higher
npm install
```

### Frontend cannot connect to backend

Make sure the backend is running on port 8001. The `next.config.ts` automatically proxies all `/api/*` requests to `http://localhost:8001`.

---

## License

MIT License — see [LICENSE](LICENSE)
