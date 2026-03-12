from __future__ import annotations

import logging
from typing import Dict

import google.generativeai as genai

from config import settings
from graph.state import AgentState
from prompts.teacher_prompt import TEACHER_PROMPT_TEMPLATE, TEACHER_SYSTEM_PROMPT
from agents.base_agent import gemini_retry_strategy

logger = logging.getLogger(__name__)


class TeacherAgent:
    """Synthesizes the journey into an educational, user-friendly explanation."""

    def __init__(self, model_name: str = "gemini-3.1-flash-lite-preview") -> None:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=TEACHER_SYSTEM_PROMPT,
        )

    @gemini_retry_strategy  # <--- Add this decorator here
    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Teacher: Preparing final explanation and walkthrough...")

        prompt = TEACHER_PROMPT_TEMPLATE.format(
            clarified_query=state.get("clarified_query", ""),
            difficulty_level=state.get("difficulty_level", "intermediate"),
            final_code=state.get("generated_code", ""),
            code_language=state.get("code_language", "unknown"),
            architecture_plan=state.get("architecture_plan", ""),
            bugs_that_were_fixed=", ".join(state.get("bugs_found", []) or ["None"]),
            security_issues_resolved=", ".join(state.get("security_issues", []) or ["None"]),
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.7},
            )

            state["teaching_explanation"] = response.text or ""
            state["how_to_run"] = state.get("how_to_run", "Follow the 'How to Run It' section above.")
            state["final_code"] = state.get("generated_code", state.get("final_code", ""))
            state["final_response"] = self._assemble_final_response(state)
            state.setdefault("agents_involved", []).append("teacher")
            state["activeAgent"] = "teacher"  # For frontend visualization
            logger.info("Teacher: Final response assembled.")

        except Exception as exc: 
            # ADD THIS CHECK: Re-raise the error so the decorator can retry!
            if "429" in str(exc) or "quota" in str(exc).lower():
                raise exc
                
            logger.error("Teacher error: %s", exc)
            state.setdefault("agents_involved", []).append("teacher_error")

        return state

    def _assemble_final_response(self, state: AgentState) -> Dict:
        """Combine all agent outputs into a structured payload."""

        summary_text = state.get("teaching_explanation", "")
        summary_preview = f"{summary_text[:200]}..." if summary_text else ""

        return {
            "summary": summary_preview,
            "full_explanation": summary_text,
            "architecture_plan": state.get("architecture_plan", ""),
            "final_code": state.get("generated_code", ""),
            "code_language": state.get("code_language", ""),
            "dependencies": state.get("dependencies", []),
            "review_score": state.get("review_score", 0),
            "review_loops": state.get("review_loops_count", 0),
            "agents_used": state.get("agents_involved", []),
            "how_to_run": state.get("how_to_run", "Follow the 'How to Run It' section above."),
            "metadata": {
                "session_id": state.get("session_id", ""),
                "tokens_used": state.get("total_tokens_used", 0),
                "execution_time": state.get("execution_time_seconds", 0),
            },
        }
