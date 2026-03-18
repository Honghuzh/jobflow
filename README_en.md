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

## Architecture

```
                  ┌──────────────────────────────────────┐
                  │        Career Agent (Lead)           │
                  │         Your Career Coach            │
                  └───────────┬──────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
          ┌──────────┐ ┌──────────┐ ┌──────────┐
          │Middleware │ │Sub-Agents│ │  Tools   │
          │ Chain(7) │ │  (4 exp) │ │  (4 tools│
          └──────────┘ └──────────┘ └──────────┘
```

## Comparison with DeerFlow

| Module | DeerFlow | JobFlow |
|--------|----------|---------|
| Lead Agent | General research assistant | Career coaching agent |
| Middleware Chain | 9-layer general middleware | 7-layer job-seeking middleware |
| Sub-Agents | General + Bash Agent | 4 domain-expert agents |
| Skills | Research/report skills | JD analysis/resume/cover letter skills |
| Memory | General long-term memory | Job preferences/skills/interview memory |
| Tools | Web search/code execution | JD parser/resume parser/match scorer/tracker |

## Quick Start

```bash
# Install dependencies (requires Python 3.12+ and uv)
make install

# Configure
cp config.example.yaml config.yaml
cp .env.example .env
# Edit .env and fill in your API keys

# Run
make dev
```

## Roadmap

- **Phase 1** (Current): Project skeleton — Career Agent, Middleware chain, Sub-agents, Tools, Skills
- **Phase 2**: Full backend — FastAPI Gateway, LLM integration, PDF parsing, streaming
- **Phase 3**: Frontend — Next.js UI, file upload, progress dashboard
- **Phase 4**: Enhancements — Multi-tenancy, scheduled tasks, job platform integrations

## Tech Stack

- **Python 3.12+** — Backend language
- **LangGraph** — Agent orchestration
- **LangChain** — LLM integration
- **FastAPI** — API gateway
- **uv** — Python package management

## License

MIT License — see [LICENSE](LICENSE)
