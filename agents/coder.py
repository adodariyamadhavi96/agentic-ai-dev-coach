from __future__ import annotations

import logging
# FIXED: Added Any to the imports to prevent NameError in type hints
from typing import Dict, Any 

import google.generativeai as genai

from config import settings
from graph.state import AgentState
from prompts.coder_prompt import (
    CODER_PROMPT_TEMPLATE,
    CODER_REWRITE_PROMPT_TEMPLATE,
    CODER_SYSTEM_PROMPT,
)
from utils.code_extractor import CodeExtractor
# IMPORT the retry strategy from your base agent
from agents.base_agent import gemini_retry_strategy

logger = logging.getLogger(__name__)


class CoderAgent:
    """Generates production-grade code following the architect's blueprint."""

    def __init__(self, model_name: str = "gemini-3.1-flash-lite-preview") -> None:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=CODER_SYSTEM_PROMPT,
        )
        self.extractor = CodeExtractor()

    @gemini_retry_strategy  # <--- CRITICAL: Wraps the method in exponential backoff logic
    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        version = state.get("code_version") or 0
        logger.info("Coder: Generating code (Attempt %s)...", version + 1)

        prompt = self._select_prompt(state)

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.3},
            )
            response_text = response.text or ""

            extraction = self.extractor.extract_code(response_text)

            state["generated_code"] = extraction.get("code", "")
            state["code_language"] = extraction.get("language", state.get("programming_language", ""))
            state["code_explanation"] = extraction.get("explanation", "")

            deps = extraction.get("dependencies", []) or []
            state.setdefault("dependencies", []).extend(deps)

            state["code_version"] = version + 1
            state.setdefault("agents_involved", []).append("coder")
            state["activeAgent"] = "coder"  # For frontend visualization
            logger.info("Coder: Code version %s generated.", state["code_version"])

        except Exception as exc: 
            # FIXED: Re-raise the error so the decorator can catch it and retry.
            # If you just log it here, the retry logic is skipped!
            if "429" in str(exc) or "quota" in str(exc).lower():
                logger.warning("Coder: Rate limit hit. Retrying...")
                raise exc
                
            logger.error("Coder error: %s", exc)
            state.setdefault("agents_involved", []).append("coder_error")

        return state

    def _select_prompt(self, state: AgentState) -> str:
        """Choose initial or rewrite prompt based on code_version."""
        version = state.get("code_version") or 0
        if version > 0:
            return CODER_REWRITE_PROMPT_TEMPLATE.format(
                code_version=version + 1,
                reviewer_feedback=state.get("reviewer_feedback", "Fix all previous issues."),
                architecture_plan=state.get("architecture_plan", ""),
                rag_context=state.get("rag_context", "Refer to standard docs."),
            )

        return CODER_PROMPT_TEMPLATE.format(
            clarified_query=state.get("clarified_query", ""),
            architecture_plan=state.get("architecture_plan", ""),
            implementation_steps="\n".join(state.get("implementation_steps", [])),
            programming_language=state.get("programming_language", "unknown"),
            difficulty_level=state.get("difficulty_level", "intermediate"),
            rag_context=state.get("rag_context", "Refer to standard docs."),
        )