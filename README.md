# 🤖 Agentic AI Developer Coach

<div align="center">

![GitHub License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.10%2B-green.svg)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)
![React](https://img.shields.io/badge/Frontend-React-61DAFB.svg)
![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-8E75B2.svg)

**A professional-grade multi-agent RAG system built on LangGraph to plan, code, verify, and explain complex software solutions.**

[Explore Features](#-key-features) • [View Architecture](#-system-architecture--workflow) • [Technical Challenges](#-technical-challenges--solutions) • [Getting Started](#-setup--execution)

</div>

---

## 📖 Overview

The **Agentic AI Developer Coach** acts as a senior pair programmer and architectural consultant. Built on **LangGraph**, it orchestrates a specialized team of AI agents—User Proxy, Architect, Coder, Reviewer, and Teacher—to transform high-level requirements into production-ready software.

Unlike basic linear chatbots, this system utilizes a **cyclic state machine** where a Reviewer agent enforces quality standards, triggering automated rewrites until the solution meets industry criteria.

---

## ✨ Key Features

* **Stateful Multi-Agent Orchestration:** Manages complex agent handoffs and persistent history using LangGraph.
* **Self-Correcting Review Loops:** Automated quality gates where the Reviewer agent identifies bugs and forces refactoring.
* **Context-Aware Design (RAG):** Grounds architectural blueprints in real-time, indexed documentation using ChromaDB.
* **Production-Grade Resiliency:** Integrated exponential backoff to navigate API rate limits and ensure 100% workflow completion.
* **Glassmorphism Dashboard:** A modern React UI featuring real-time agent tracking and deep-key data mapping for stable visuals.

---

## 🖥️ Pro Dashboard
![Dashboard Preview](assets/dashboard%20preview.png)
*Real-time visualization of the agentic state machine, featuring deep-key data mapping and RAG-grounded outputs.*

---

## 🏗️ System Architecture & Workflow

The system follows a stateful directed graph workflow to ensure predictable transitions and reliable software engineering.

![Agentic Workflow Diagram](assets/agent%20workflow%20diagram.png)

1. **Intake (User Proxy):** Clarifies user requirements and detects project intent.
2. **Design (Architect + RAG):** Retrieves relevant documentation and creates a structural blueprint.
3. **Code (Coder):** Generates implementation based on the architectural plan.
4. **Review (Reviewer):** Performs automated code review for bugs, security, and style.
5. **Coach (Teacher):** Synthesizes the technical journey into an educational walkthrough.

![AI Code Generation](assets/ai%20code%20generation.png)
*Example of the AI Coder agent generating production-ready code based on architectural blueprints.*

---

## 🛠️ Technical Challenges & Solutions

### 🚀 Handling Production Rate Limits
**Challenge:** Using the Gemini Free Tier frequently resulted in `429 Resource Exhausted` errors during high-intensity agent loops.
**Solution:** Implemented a robust reliability layer using **Exponential Backoff** via the `tenacity` library. Agents now automatically pause and retry requests, ensuring the workflow completes even under strict API quotas.

### 🔍 UI Stability & Data Integrity
**Challenge:** Complex multi-agent responses often returned deeply nested or inconsistent JSON structures, causing frontend display failures.
**Solution:** Developed a **Deep-Key Data Mapping** algorithm in the React frontend that recursively scans payloads to guarantee architectural plans and code are always rendered correctly.

---

## 📁 Project Structure

```
ai-dev-coach/
├── agents/           # Agent implementations (Base, Architect, Coder, etc.)
├── graph/            # LangGraph orchestration, state definitions, and routing
├── rag/              # RAG utilities (VectorStore, embedding logic, loaders)
├── api/              # FastAPI application, routes, and streaming logic
├── prompts/          # Specialized system prompts for each agent persona
├── utils/            # Shared utilities (Code extraction, logging, retry logic)
├── data/             # Persistent storage for Vector DB and session history
├── scripts/          # Setup helpers for environment and RAG indexing
├── tests/            # Pytest suite for agent and graph validation
├── frontend/         # React-based Pro Dashboard (Single-file SPA)
├── config.py         # Pydantic-based Settings Management
├── main.py           # CLI entry point and server runner
└── requirements.txt  # Pinned dependency manifest
```
## 🧰 Setup Instructions
1. **Clone & enter:** `git clone <repo-url> && cd ai-dev-coach`
2. **Python env:** `python -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`)
3. **Install deps:** `pip install -r requirements.txt`
4. **Configure env:** `cp .env.example .env` and fill `GEMINI_API_KEY` and `TAVILY_API_KEY`.
5. **Initialize RAG:** `python scripts/setup_rag.py` (requires keys set; downloads and indexes docs).
6. **Run tests (optional):** `pytest`.

## ▶️ How to Run
- **CLI:** `python main.py --query "Build a FastAPI CRUD app"`
- **API:** `uvicorn api.main:app --reload`
- **Frontend:** Start the API, then open `frontend/index.html` in your browser (or serve via simple HTTP server).

## 🤝 Agent Workflow (ASCII Diagram)
```
[User]
  |
  v
[User Proxy] --> captures intent
  |
  v
[Architect + RAG] -- retrieves docs --> [Context]
  |
  v
[Coder] ---> code draft ----> [Reviewer] ---(fail)-> back to [Coder]
                                    |
                                    v
                               (pass/loops max)
                                    |
                                    v
                                [Teacher]
                                    |
                                    v
                                   [User]
```

## 🧪 Example Usage
- **CLI:** `python main.py -q "Generate a Python function that sums a list safely"`
- **API (curl):** `curl -X POST http://localhost:8000/v1/query -H "Content-Type: application/json" -d '{"query": "Explain dependency injection in FastAPI"}'`
- **Frontend:** Enter a prompt like "Refactor this Flask app to FastAPI" and view Plan, Approved Code, and Explanation panels.
