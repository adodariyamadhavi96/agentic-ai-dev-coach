from __future__ import annotations

import json
import logging
from typing import Dict

import google.generativeai as genai

from config import settings
from graph.state import AgentState
from prompts.reviewer_prompt import REVIEWER_PROMPT_TEMPLATE, REVIEWER_SYSTEM_PROMPT
from agents.base_agent import gemini_retry_strategy

logger = logging.getLogger(__name__)


class ReviewerAgent:
    """Quality control layer that reviews code for bugs, security, and style."""

    def __init__(self, model_name: str = "gemini-3.1-flash-lite-preview") -> None:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=REVIEWER_SYSTEM_PROMPT,
        )
        self.max_loops = settings.MAX_REVIEW_LOOPS

    @gemini_retry_strategy  # <--- Add this decorator here
    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Reviewer: Inspecting code version %s...", state.get("code_version", 0))

        prompt = REVIEWER_PROMPT_TEMPLATE.format(
            clarified_query=state.get("clarified_query", ""),
            architecture_plan=state.get("architecture_plan", ""),
            generated_code=state.get("generated_code", ""),
            code_language=state.get("code_language", ""),
            code_version=state.get("code_version", 0),
            review_loops_count=state.get("review_loops_count", 0),
            max_loops=self.max_loops,
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
            )

            data: Dict = json.loads(response.text)

            state["review_passed"] = data.get("review_passed", False)
            state["review_score"] = data.get("review_score", 0)
            state["reviewer_feedback"] = data.get("reviewer_feedback", "")
            state["bugs_found"] = data.get("bugs_found", [])
            state["security_issues"] = data.get("security_issues", [])
            state["style_issues"] = data.get("style_issues", [])

            # Force pass if loop limit reached
            if self._should_force_pass(state):
                state["review_passed"] = True
                state["reviewer_feedback"] += "\n(Note: Max review loops reached. Force-passing.)"

            # Increment loop counter when not passed
            if not state["review_passed"]:
                state["review_loops_count"] = (state.get("review_loops_count") or 0) + 1

            state.setdefault("agents_involved", []).append("reviewer")
            state["activeAgent"] = "reviewer"  # For frontend visualization
            logger.info("Reviewer: Score %s/100. Passed: %s", state.get("review_score"), state.get("review_passed"))

        except Exception as exc: 
            # ADD THIS: Re-raise the error so the decorator can retry!
            if "429" in str(exc) or "quota" in str(exc).lower():
                raise exc
                
            logger.error("Reviewer error: %s", exc)
            state.setdefault("agents_involved", []).append("reviewer_error")

        return state

    def _should_force_pass(self, state: AgentState) -> bool:
        """Return True when review loop cap is hit."""

        return (state.get("review_loops_count") or 0) >= self.max_loops
