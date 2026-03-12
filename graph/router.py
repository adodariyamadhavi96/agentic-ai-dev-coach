from __future__ import annotations

from typing import Callable

from config import settings
from graph.state import AgentState


def route_after_user_proxy(state: AgentState) -> str:
    """Always moves to Architect after intake."""

    return "architect"


def route_after_architect(state: AgentState) -> str:
    """If intent is explain/general, skip coding and go to Teacher."""

    if state.get("parsed_intent") in ["explain", "general"]:
        return "teacher"
    return "coder"


def route_after_reviewer(state: AgentState) -> str:
    """Loop back to coder if review failed; otherwise proceed to teacher."""

    if state.get("review_passed"):
        return "teacher"

    if state.get("review_loops_count", 0) >= settings.MAX_REVIEW_LOOPS:
        return "teacher"

    return "coder"


def router_factory(max_loops: int) -> Callable[[AgentState], str]:
    def router(state: AgentState) -> str:
        return "teacher" if state.get("review_loops_count", 0) >= max_loops or state.get("review_passed") else "coder"

    return router
