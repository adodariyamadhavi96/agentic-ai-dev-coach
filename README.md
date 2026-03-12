# 🤖 Agentic AI Developer Coach

The **Agentic AI Developer Coach** is a professional-grade multi-agent system built to act as a senior pair programmer and architectural consultant. Built on **LangGraph**, it orchestrates a specialized team of AI agents—User Proxy, Architect, Coder, Reviewer, and Teacher—to plan, implement, verify, and explain complex software solutions.

Unlike basic chatbots, this system utilizes a **cyclic state machine** where a Reviewer agent enforces quality standards, forcing code rewrites until the solution meets production-grade criteria. Every interaction is grounded with **RAG (Retrieval-Augmented Generation)** over indexed documentation so guidance stays accurate and current.

---

## 🤝 Agent Workflow

The system follows a stateful directed graph workflow:

1.  **Intake (User Proxy):** Clarifies user requirements and detects project intent.
2.  **Design (Architect + RAG):** Retrieves relevant documentation and creates a structural blueprint.
3.  **Code (Coder):** Generates implementation based on the architectural plan.
4.  **Review (Reviewer):** Performs automated code review for bugs, security, and style.
5.  **Coach (Teacher):** Synthesizes the technical journey into an educational walkthrough.



---

## 📁 Project Structure

```text
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
├── config.py         # Pydantic-based settings and environment management
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
