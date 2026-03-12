from __future__ import annotations

import operator
from datetime import datetime
from typing import Annotated, Dict, List

from typing_extensions import TypedDict


class AgentState(TypedDict):
    """Shared state for the AI Developer Coach."""

    # ── User Input (replaced each run) ──────────────────────
    user_query: str
    session_id: str
    timestamp: str
    query_type: str
    programming_language: str
    difficulty_level: str

    # ── User Proxy Output (replaced) ────────────────────────
    parsed_intent: str
    clarified_query: str
    requires_rag: bool

    # ⬇ APPENDED across agents/loops — use Annotated + operator.add
    relevant_topics: Annotated[List[str], operator.add]

    # ── Architect Agent Output (replaced) ───────────────────
    architecture_plan: str
    rag_context: str
    tech_stack_recommendation: str

    # ⬇ APPENDED — each loop adds new sources/steps
    rag_sources: Annotated[List[str], operator.add]
    implementation_steps: Annotated[List[str], operator.add]

    # ── Coder Agent Output (replaced each rewrite) ──────────
    generated_code: str
    code_language: str
    code_explanation: str
    code_version: int

    # ⬇ APPENDED — dependencies may grow across rewrites
    dependencies: Annotated[List[str], operator.add]

    # ── Reviewer Agent Output (replaced each review) ─────────
    review_passed: bool
    review_score: int
    reviewer_feedback: str
    review_loops_count: int
    final_code: str

    # ⬇ APPENDED — each review loop adds its findings to history
    bugs_found: Annotated[List[str], operator.add]
    security_issues: Annotated[List[str], operator.add]
    style_issues: Annotated[List[str], operator.add]

    # ── Teacher Agent Output (replaced) ─────────────────────
    teaching_explanation: str
    how_to_run: str

    # ⬇ APPENDED
    key_concepts: Annotated[List[str], operator.add]
    code_walkthrough: Annotated[List[dict], operator.add]
    common_mistakes: Annotated[List[str], operator.add]
    next_steps: Annotated[List[str], operator.add]
    resources: Annotated[List[dict], operator.add]

    # ── Final Output (replaced) ──────────────────────────────
    final_response: dict
    total_tokens_used: int
    execution_time_seconds: float

    # ⬇ APPENDED — each agent appends its own name when it finishes
    agents_involved: Annotated[List[str], operator.add]


def create_initial_state(user_query: str, session_id: str) -> AgentState:
    """Return a fresh AgentState with defaults populated."""

    return {
        "user_query": user_query,
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "query_type": "general",
        "programming_language": "unknown",
        "difficulty_level": "intermediate",
        "parsed_intent": "",
        "clarified_query": "",
        "requires_rag": False,
        "relevant_topics": [],
        "architecture_plan": "",
        "rag_context": "",
        "tech_stack_recommendation": "",
        "rag_sources": [],
        "implementation_steps": [],
        "generated_code": "",
        "code_language": "",
        "code_explanation": "",
        "code_version": 0,
        "dependencies": [],
        "review_passed": False,
        "review_score": 0,
        "reviewer_feedback": "",
        "review_loops_count": 0,
        "final_code": "",
        "bugs_found": [],
        "security_issues": [],
        "style_issues": [],
        "teaching_explanation": "",
        "how_to_run": "",
        "key_concepts": [],
        "code_walkthrough": [],
        "common_mistakes": [],
        "next_steps": [],
        "resources": [],
        "final_response": {},
        "total_tokens_used": 0,
        "execution_time_seconds": 0.0,
        "agents_involved": [],
    }


def state_to_dict(state: AgentState) -> Dict:
    """Convert state to a plain dict for serialization."""

    return dict(state)


def get_state_summary(state: AgentState) -> str:
    """Return a concise, human-readable summary of the run."""

    agents = ", ".join(state.get("agents_involved", []))
    loops = state.get("review_loops_count", 0)
    passed = "successfully passed review" if state.get("review_passed") else "finished with suggestions"
    score = state.get("review_score", 0)

    summary = (
        f"Session {state['session_id']} processed a {state['query_type']} request "
        f"for {state['programming_language']}. The workflow involved the following agents: {agents}. "
        f"After {loops} review cycles, the code {passed} with a final quality score of {score}/100."
    )
    return summary
